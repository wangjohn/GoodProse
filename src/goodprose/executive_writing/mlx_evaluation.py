"""Matched MLX base-versus-adapter inference on the frozen B1 benchmark."""

from __future__ import annotations

import gc
import json
import statistics
import time
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.executive_writing.analysis import RescoredRun, paired_comparison
from goodprose.executive_writing.baseline import (
    BaselineConfig,
    Generation,
    GenerationStep,
    RetrievalExample,
    build_compact_ledger_prompt,
    build_ledger_draft_prompt,
    build_prompt,
    load_retrieval_examples,
)
from goodprose.executive_writing.baseline import (
    load_config as load_baseline_config,
)
from goodprose.executive_writing.benchmark import (
    BenchmarkCase,
    CaseScore,
    load_cases,
    score_output_v1_1,
)
from goodprose.jsonl import atomic_write, serialize_jsonl, sha256_bytes, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
GitRevision = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EvalBaseModel(StrictModel):
    repo_id: Literal["mlx-community/Qwen2.5-0.5B-Instruct-4bit"]
    revision: GitRevision
    weight_sha256: Sha256
    license: Literal["Apache-2.0"]


class EvalAdapter(StrictModel):
    training_experiment_id: Literal["qwen2.5-0.5b-mlx-lora-smoke-v1"]
    candidate_lineage: Literal["qwen2.5-0.5b-instruct-4bit-lora-smoke-v1"]
    adapter_sha256: Sha256
    training_code_revision: GitRevision


class EvalDecoding(StrictModel):
    temperature: Literal[0]
    seed: int
    direct_max_tokens: int = Field(ge=1)
    ledger_max_tokens: int = Field(ge=1)
    draft_max_tokens: int = Field(ge=1)


class MlxB1EvalConfig(StrictModel):
    version: Literal[1]
    experiment_id: NonEmpty
    benchmark_id: Literal["goodprose-b1-v1"]
    benchmark_cases_sha256: Sha256
    scorer_version: Literal["goodprose-deterministic-v1.1"]
    base_model: EvalBaseModel
    adapter: EvalAdapter
    strategies: tuple[Literal["profile", "ledger_draft"], ...]
    profile_config_path: NonEmpty
    retrieval_examples_path: NonEmpty
    decoding: EvalDecoding
    settled_cost_usd: Literal[0]

    @model_validator(mode="after")
    def required_strategies(self) -> Self:
        if self.strategies != ("profile", "ledger_draft"):
            raise ValueError("smoke comparison must run profile then ledger_draft")
        return self


class StepMetrics(StrictModel):
    prompt_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    prompt_tokens_per_second: float = Field(ge=0)
    generation_tokens_per_second: float = Field(ge=0)
    peak_memory_gb: float = Field(ge=0)
    finish_reason: Literal["stop", "length"]


class GeneratedStep(StrictModel):
    output: str
    latency_ms: float = Field(ge=0)
    metrics: StepMetrics


class MlxTextGenerator(Protocol):
    def generate(self, prompt: str, *, max_tokens: int) -> GeneratedStep: ...


class MlxClient:
    """Lazy-imported MLX generator so normal tests do not require Metal."""

    def __init__(self, *, model_path: Path, adapter_path: Path | None, seed: int) -> None:
        import mlx.core as mx
        from mlx_lm import load
        from mlx_lm.sample_utils import make_sampler

        mx.random.seed(seed)
        loaded = load(
            str(model_path),
            adapter_path=str(adapter_path) if adapter_path is not None else None,
        )
        self._model = loaded[0]
        self._tokenizer = loaded[1]
        self._sampler = make_sampler(temp=0.0)

    def generate(self, prompt: str, *, max_tokens: int) -> GeneratedStep:
        from mlx_lm import stream_generate

        rendered = self._tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )
        started = time.perf_counter()
        pieces: list[str] = []
        last: Any = None
        for response in stream_generate(
            self._model,
            self._tokenizer,
            rendered,
            max_tokens=max_tokens,
            sampler=self._sampler,
        ):
            pieces.append(response.text)
            last = response
        latency_ms = (time.perf_counter() - started) * 1000
        if last is None or last.finish_reason not in {"stop", "length"}:
            raise RuntimeError("MLX generation did not return terminal metrics")
        return GeneratedStep(
            output="".join(pieces).strip(),
            latency_ms=latency_ms,
            metrics=StepMetrics(
                prompt_tokens=int(last.prompt_tokens),
                output_tokens=int(last.generation_tokens),
                prompt_tokens_per_second=float(last.prompt_tps),
                generation_tokens_per_second=float(last.generation_tps),
                peak_memory_gb=float(last.peak_memory),
                finish_reason=last.finish_reason,
            ),
        )


def load_eval_config(path: Path) -> MlxB1EvalConfig:
    return MlxB1EvalConfig.model_validate_json(path.read_text(encoding="utf-8"))


def _generation_step(step_id: str, prompt: str, result: GeneratedStep) -> GenerationStep:
    return GenerationStep(
        step_id=step_id,
        prompt_sha256=sha256(prompt.encode()).hexdigest(),
        output=result.output,
        output_sha256=sha256(result.output.encode()).hexdigest(),
        latency_ms=result.latency_ms,
        prompt_tokens=result.metrics.prompt_tokens,
        output_tokens=result.metrics.output_tokens,
    )


def generate_case(
    *,
    case: BenchmarkCase,
    candidate_id: str,
    strategy: Literal["profile", "ledger_draft"],
    generator: MlxTextGenerator,
    profile_config: BaselineConfig,
    retrieval_examples: list[RetrievalExample],
    decoding: EvalDecoding,
) -> tuple[Generation, list[StepMetrics]]:
    if strategy == "profile":
        prompt = build_prompt(case, profile_config)
        result = generator.generate(prompt, max_tokens=decoding.direct_max_tokens)
        return (
            Generation(
                case_id=case.id,
                candidate_id=candidate_id,
                prompt_sha256=sha256(prompt.encode()).hexdigest(),
                output=result.output,
                output_sha256=sha256(result.output.encode()).hexdigest(),
                latency_ms=result.latency_ms,
                prompt_tokens=result.metrics.prompt_tokens,
                output_tokens=result.metrics.output_tokens,
            ),
            [result.metrics],
        )

    ledger_prompt = build_compact_ledger_prompt(case)
    ledger_result = generator.generate(ledger_prompt, max_tokens=decoding.ledger_max_tokens)
    draft_prompt = build_ledger_draft_prompt(case, ledger_result.output, retrieval_examples)
    draft_result = generator.generate(draft_prompt, max_tokens=decoding.draft_max_tokens)
    steps = (
        _generation_step("ledger", ledger_prompt, ledger_result),
        _generation_step("draft", draft_prompt, draft_result),
    )
    return (
        Generation(
            case_id=case.id,
            candidate_id=candidate_id,
            prompt_sha256=steps[-1].prompt_sha256,
            output=draft_result.output,
            output_sha256=steps[-1].output_sha256,
            latency_ms=sum(step.latency_ms for step in steps),
            prompt_tokens=sum(step.prompt_tokens or 0 for step in steps),
            output_tokens=sum(step.output_tokens or 0 for step in steps),
            pipeline_steps=steps,
        ),
        [ledger_result.metrics, draft_result.metrics],
    )


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def summarize_candidate(
    scores: list[CaseScore], generations: list[Generation], metrics: list[StepMetrics]
) -> dict[str, Any]:
    dimensions = {
        name: round(statistics.fmean(score.dimensions[name] for score in scores), 4)
        for name in scores[0].dimensions
    }
    errors = Counter(error for score in scores for error in score.errors)
    latencies = [generation.latency_ms for generation in generations]
    return {
        "candidate_id": scores[0].candidate_id,
        "evaluation_id": "goodprose-b1-v1.1",
        "scorer_version": "goodprose-deterministic-v1.1",
        "case_count": len(scores),
        "mean_development_score": round(
            statistics.fmean(score.development_score for score in scores), 4
        ),
        "median_development_score": round(
            statistics.median(score.development_score for score in scores), 4
        ),
        "hard_gate_pass_rate": round(
            statistics.fmean(float(score.passes_hard_gates) for score in scores), 4
        ),
        "dimension_means": dimensions,
        "error_counts": dict(sorted(errors.items())),
        "latency_ms": {
            "mean": round(statistics.fmean(latencies), 4),
            "median": round(statistics.median(latencies), 4),
            "p95": round(_percentile(latencies, 0.95), 4),
        },
        "prompt_tokens": sum(item.prompt_tokens or 0 for item in generations),
        "output_tokens": sum(item.output_tokens or 0 for item in generations),
        "peak_memory_gb": round(max(metric.peak_memory_gb for metric in metrics), 4),
        "length_finish_count": sum(metric.finish_reason == "length" for metric in metrics),
        "settled_cost_usd": 0,
    }


def _candidate_id(*, tuned: bool, strategy: str) -> str:
    state = "smoke-lora" if tuned else "base"
    return f"mlx-qwen2.5-0.5b-{state}-{strategy}-v1"


def _run_candidate(
    *,
    cases: list[BenchmarkCase],
    generator: MlxTextGenerator,
    tuned: bool,
    strategy: Literal["profile", "ledger_draft"],
    profile_config: BaselineConfig,
    retrieval_examples: list[RetrievalExample],
    decoding: EvalDecoding,
) -> tuple[list[Generation], list[CaseScore], dict[str, Any]]:
    candidate_id = _candidate_id(tuned=tuned, strategy=strategy)
    generations: list[Generation] = []
    metrics: list[StepMetrics] = []
    for case in cases:
        generation, case_metrics = generate_case(
            case=case,
            candidate_id=candidate_id,
            strategy=strategy,
            generator=generator,
            profile_config=profile_config,
            retrieval_examples=retrieval_examples,
            decoding=decoding,
        )
        generations.append(generation)
        metrics.extend(case_metrics)
    scores = [
        score_output_v1_1(case, generation.output, candidate_id=candidate_id)
        for case, generation in zip(cases, generations, strict=True)
    ]
    return generations, scores, summarize_candidate(scores, generations, metrics)


def _rescored(scores: list[CaseScore], summary: dict[str, Any]) -> RescoredRun:
    return RescoredRun(
        candidate_id=summary["candidate_id"],
        scores=scores,
        generations=[],
        summary=summary,
        artifact_hashes={},
        source_artifact_hashes={},
    )


def run_mlx_b1_evaluation(
    *,
    config_path: Path,
    cases_path: Path,
    adapter_path: Path,
    model_path: Path,
    output_root: Path,
    repo_root: Path,
    code_revision: str,
    started_at: str,
) -> Path:
    config = load_eval_config(config_path)
    if sha256_file(cases_path) != config.benchmark_cases_sha256:
        raise ValueError("B1 cases hash does not match MLX evaluation config")
    adapter_file = adapter_path / "adapters.safetensors"
    if sha256_file(adapter_file) != config.adapter.adapter_sha256:
        raise ValueError("adapter hash does not match MLX evaluation config")
    weight_file = model_path / "model.safetensors"
    if sha256_file(weight_file) != config.base_model.weight_sha256:
        raise ValueError("base weight hash does not match MLX evaluation config")
    profile_path = repo_root / config.profile_config_path
    retrieval_path = repo_root / config.retrieval_examples_path
    profile_config = load_baseline_config(profile_path)
    retrieval_examples = load_retrieval_examples(retrieval_path)
    cases = load_cases(cases_path)

    parsed_start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    if parsed_start.tzinfo is None:
        raise ValueError("started_at must include a timezone")
    run_id = f"{config.experiment_id}-{parsed_start.strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = output_root / run_id
    if run_dir.exists():
        raise ValueError(f"refusing to overwrite existing MLX evaluation: {run_dir}")
    run_dir.mkdir(parents=True)

    artifacts: dict[str, dict[str, Any]] = {}
    started_timer = time.perf_counter()
    for tuned, current_adapter in ((False, None), (True, adapter_path)):
        load_started = time.perf_counter()
        generator = MlxClient(
            model_path=model_path,
            adapter_path=current_adapter,
            seed=config.decoding.seed,
        )
        load_seconds = time.perf_counter() - load_started
        for strategy in config.strategies:
            generations, scores, summary = _run_candidate(
                cases=cases,
                generator=generator,
                tuned=tuned,
                strategy=strategy,
                profile_config=profile_config,
                retrieval_examples=retrieval_examples,
                decoding=config.decoding,
            )
            summary["model_load_seconds"] = round(load_seconds, 6)
            candidate_id = summary["candidate_id"]
            generation_bytes = serialize_jsonl(generations)
            score_bytes = serialize_jsonl(scores)
            summary_bytes = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
            candidate_dir = run_dir / candidate_id
            atomic_write(candidate_dir / "outputs.jsonl", generation_bytes)
            atomic_write(candidate_dir / "scores.jsonl", score_bytes)
            atomic_write(candidate_dir / "summary.json", summary_bytes)
            artifacts[candidate_id] = {
                "strategy": strategy,
                "tuned": tuned,
                "outputs_sha256": sha256_bytes(generation_bytes),
                "scores_sha256": sha256_bytes(score_bytes),
                "summary_sha256": sha256_bytes(summary_bytes),
                "summary": summary,
                "scores": scores,
            }
        del generator
        gc.collect()
        import mlx.core as mx

        mx.clear_cache()

    comparisons: list[dict[str, Any]] = []
    for strategy in config.strategies:
        base_id = _candidate_id(tuned=False, strategy=strategy)
        tuned_id = _candidate_id(tuned=True, strategy=strategy)
        comparisons.append(
            paired_comparison(
                _rescored(artifacts[base_id]["scores"], artifacts[base_id]["summary"]),
                _rescored(artifacts[tuned_id]["scores"], artifacts[tuned_id]["summary"]),
            )
        )

    completed = datetime.now(UTC)
    comparison_payload = (json.dumps(comparisons, indent=2, sort_keys=True) + "\n").encode()
    atomic_write(run_dir / "paired-comparisons.json", comparison_payload)
    manifest = {
        "version": 1,
        "experiment_id": config.experiment_id,
        "run_id": run_id,
        "status": "completed",
        "hypothesis": (
            "A genuine smoke adapter changes B1 behavior under matched profile and "
            "ledger-draft inference; direction is exploratory, not a quality claim."
        ),
        "config_sha256": sha256_file(config_path),
        "cases_sha256": sha256_file(cases_path),
        "profile_config_sha256": sha256_file(profile_path),
        "retrieval_examples_sha256": sha256_file(retrieval_path),
        "base_model": config.base_model.model_dump(mode="json"),
        "adapter": config.adapter.model_dump(mode="json"),
        "decoding": config.decoding.model_dump(mode="json"),
        "code_revision": code_revision,
        "hardware": "Apple M3 Pro, 18 GiB unified memory",
        "started_at": started_at,
        "completed_at": completed.isoformat().replace("+00:00", "Z"),
        "elapsed_seconds": round(time.perf_counter() - started_timer, 6),
        "candidate_artifacts": {
            candidate_id: {
                key: value for key, value in artifact.items() if key not in {"summary", "scores"}
            }
            for candidate_id, artifact in artifacts.items()
        },
        "paired_comparisons_sha256": sha256_bytes(comparison_payload),
        "settled_cost_usd": 0,
        "validity_status": "visible_b1_exploratory_smoke_comparison",
    }
    atomic_write(
        run_dir / "run-manifest.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    )
    return run_dir
