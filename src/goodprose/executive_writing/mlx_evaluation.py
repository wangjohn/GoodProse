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
from goodprose.jsonl import (
    atomic_write,
    canonical_json,
    load_jsonl,
    serialize_jsonl,
    sha256_bytes,
    sha256_file,
)

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
    training_experiment_id: Literal[
        "qwen2.5-0.5b-mlx-lora-smoke-v1",
        "qwen2.5-0.5b-mlx-lora-unified-pilot-v1",
    ]
    candidate_lineage: Literal[
        "qwen2.5-0.5b-instruct-4bit-lora-smoke-v1",
        "qwen2.5-0.5b-unified-pilot-lora-v1",
    ]
    adapter_sha256: Sha256
    training_code_revision: GitRevision

    @model_validator(mode="after")
    def pair_experiment_and_lineage(self) -> Self:
        expected = (
            "qwen2.5-0.5b-instruct-4bit-lora-smoke-v1"
            if self.training_experiment_id == "qwen2.5-0.5b-mlx-lora-smoke-v1"
            else "qwen2.5-0.5b-unified-pilot-lora-v1"
        )
        if self.candidate_lineage != expected:
            raise ValueError(
                f"candidate lineage {self.candidate_lineage!r} does not match training "
                f"experiment {self.training_experiment_id!r}"
            )
        return self


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
            raise ValueError("MLX comparison must run profile then ledger_draft")
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


def _adapter_slug(adapter: EvalAdapter) -> str:
    return (
        "smoke-lora"
        if adapter.training_experiment_id == "qwen2.5-0.5b-mlx-lora-smoke-v1"
        else "unified-pilot-lora"
    )


def _candidate_id(*, adapter: EvalAdapter, tuned: bool, strategy: str) -> str:
    state = _adapter_slug(adapter) if tuned else "base"
    return f"mlx-qwen2.5-0.5b-{state}-{strategy}-v1"


def _run_candidate(
    *,
    cases: list[BenchmarkCase],
    generator: MlxTextGenerator,
    adapter: EvalAdapter,
    tuned: bool,
    strategy: Literal["profile", "ledger_draft"],
    profile_config: BaselineConfig,
    retrieval_examples: list[RetrievalExample],
    decoding: EvalDecoding,
) -> tuple[list[Generation], list[CaseScore], dict[str, Any]]:
    candidate_id = _candidate_id(adapter=adapter, tuned=tuned, strategy=strategy)
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
                adapter=config.adapter,
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
        base_id = _candidate_id(adapter=config.adapter, tuned=False, strategy=strategy)
        tuned_id = _candidate_id(adapter=config.adapter, tuned=True, strategy=strategy)
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
            f"The genuine {_adapter_slug(config.adapter)} adapter changes B1 behavior under "
            "matched profile and ledger-draft inference; direction is exploratory, not a "
            "quality claim."
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
        "validity_status": f"visible_b1_exploratory_{_adapter_slug(config.adapter)}_comparison",
    }
    atomic_write(
        run_dir / "run-manifest.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    )
    return run_dir


def publish_mlx_b1_results(
    *,
    run_dir: Path,
    cases_path: Path,
    training_record_path: Path,
    results_path: Path,
    case_results_path: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Verify ignored artifacts and publish compact result evidence without raw text."""

    parsed_time = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    if parsed_time.tzinfo is None:
        raise ValueError("generated_at must include a timezone")
    manifest_path = run_dir / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed":
        raise ValueError("cannot publish an incomplete MLX evaluation")
    adapter = EvalAdapter.model_validate(manifest.get("adapter"))
    if manifest.get("cases_sha256") != sha256_file(cases_path):
        raise ValueError("MLX evaluation cases hash does not match publish input")
    training_record = json.loads(training_record_path.read_text(encoding="utf-8"))
    if training_record.get("experiment_id") != adapter.training_experiment_id:
        raise ValueError("training record experiment does not match evaluated adapter")
    if training_record.get("code_revision") != adapter.training_code_revision:
        raise ValueError("training record revision does not match evaluated adapter")
    training_adapter = training_record.get("adapter")
    if (
        not isinstance(training_adapter, dict)
        or training_adapter.get("safetensors_sha256") != adapter.adapter_sha256
    ):
        raise ValueError("training record hash does not match evaluated adapter")
    cases = load_cases(cases_path)

    ordered_ids = [
        _candidate_id(adapter=adapter, tuned=False, strategy="profile"),
        _candidate_id(adapter=adapter, tuned=False, strategy="ledger_draft"),
        _candidate_id(adapter=adapter, tuned=True, strategy="profile"),
        _candidate_id(adapter=adapter, tuned=True, strategy="ledger_draft"),
    ]
    summaries: list[dict[str, Any]] = []
    scores_by_candidate: dict[str, list[CaseScore]] = {}
    output_hashes_by_candidate: dict[str, dict[str, str]] = {}
    for candidate_id in ordered_ids:
        expected = manifest["candidate_artifacts"].get(candidate_id)
        if expected is None:
            raise ValueError(f"run manifest is missing candidate {candidate_id}")
        candidate_dir = run_dir / candidate_id
        actual_hashes = {
            "outputs_sha256": sha256_file(candidate_dir / "outputs.jsonl"),
            "scores_sha256": sha256_file(candidate_dir / "scores.jsonl"),
            "summary_sha256": sha256_file(candidate_dir / "summary.json"),
        }
        if any(expected.get(name) != value for name, value in actual_hashes.items()):
            raise ValueError(f"candidate artifact hash mismatch for {candidate_id}")
        generations = load_jsonl(candidate_dir / "outputs.jsonl", Generation)
        scores = load_jsonl(candidate_dir / "scores.jsonl", CaseScore)
        summary = json.loads((candidate_dir / "summary.json").read_text(encoding="utf-8"))
        if [item.case_id for item in generations] != [case.id for case in cases]:
            raise ValueError(f"generation case order mismatch for {candidate_id}")
        if [item.case_id for item in scores] != [case.id for case in cases]:
            raise ValueError(f"score case order mismatch for {candidate_id}")
        for generation in generations:
            if generation.output_sha256 != sha256(generation.output.encode()).hexdigest():
                raise ValueError(f"output hash mismatch for {generation.case_id}")
        summaries.append(summary)
        scores_by_candidate[candidate_id] = scores
        output_hashes_by_candidate[candidate_id] = {
            generation.case_id: generation.output_sha256 for generation in generations
        }

    comparison_path = run_dir / "paired-comparisons.json"
    if sha256_file(comparison_path) != manifest["paired_comparisons_sha256"]:
        raise ValueError("paired comparison hash does not match run manifest")
    comparisons = json.loads(comparison_path.read_text(encoding="utf-8"))

    case_rows: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        candidates: dict[str, Any] = {}
        for candidate_id in ordered_ids:
            score = scores_by_candidate[candidate_id][index]
            candidates[candidate_id] = {
                "development_score": score.development_score,
                "passes_hard_gates": score.passes_hard_gates,
                "errors": list(score.errors),
                "output_sha256": output_hashes_by_candidate[candidate_id][case.id],
            }
        case_rows.append(
            {
                "case_id": case.id,
                "task_family": case.input.task_family.value,
                "output_format": case.input.output_format.value,
                "candidates": candidates,
            }
        )
    case_payload = ("\n".join(canonical_json(row) for row in case_rows) + "\n").encode("utf-8")
    atomic_write(case_results_path, case_payload)

    profile_base = summaries[0]
    ledger_base = summaries[1]
    profile_tuned = summaries[2]
    ledger_tuned = summaries[3]
    is_smoke = adapter.training_experiment_id == "qwen2.5-0.5b-mlx-lora-smoke-v1"
    advances = [comparison for comparison in comparisons if comparison["meets_advancement_gate"]]
    if is_smoke:
        analysis_id = "mlx-qwen2.5-0.5b-smoke-b1-v1-analysis"
        status = "completed_reject_smoke_adapter"
        adapter_disposition = "reject_for_quality_use_retain_as_pipeline_evidence"
        leader = "qwen2.5-0.5b-retrieval-ledger-draft-v2"
        next_hypothesis = (
            "Training requires diverse task-aligned targets and explicit negative fidelity "
            "controls before another unified update; prioritize evaluation validity and "
            "rights-safe authentic pairs rather than more synthetic template fitting."
        )
        reviewed_patterns = [
            "template and heading repetition",
            "source-fact and requested-action omission",
            "retrieval-example fact leakage in an unrelated memo",
            "overlearned generic caveat language",
        ]
        review_status = "completed_permitted_output_review"
        limitations = [
            "B1 is visible and project-authored, so the result is exploratory.",
            "The lexical scorer misses some unsupported retrieval-example facts.",
            "The smoke corpus is intentionally small and templated and cannot test quality.",
            "Earlier Ollama runs use different packaging and are not exact weight controls.",
        ]
    else:
        analysis_id = "mlx-qwen2.5-0.5b-unified-pilot-b1-v1-analysis"
        status = (
            "completed_keep_unified_adapter_exploratory"
            if advances
            else "completed_reject_unified_adapter"
        )
        adapter_disposition = (
            "keep_for_cross_architecture_analysis_only"
            if advances
            else "reject_for_quality_use_retain_as_unified_training_evidence"
        )
        leader = "defer_to_cross_architecture_analysis"
        next_hypothesis = (
            "Compare the fixed unified adapter with the current retrieval and structured "
            "leaders, then use deterministic failures and a separate profile-control "
            "diagnostic to decide whether another data or architecture change is justified."
        )
        reviewed_patterns = []
        review_status = "deterministic_counts_only_pending_separate_permitted_output_review"
        limitations = [
            "B1 is visible and project-authored, so the result is exploratory.",
            "The lexical scorer can miss unsupported semantic claims and style collapse.",
            "The unified corpus is synthetic and renderer-structured and cannot establish quality.",
            "Earlier Ollama runs use different packaging and are architecture references, not "
            "exact weight controls.",
        ]
    analysis = {
        "version": 1,
        "analysis_id": analysis_id,
        "status": status,
        "validity_status": f"visible_b1_exploratory_{_adapter_slug(adapter)}_comparison",
        "generated_at": generated_at,
        "benchmark_id": "goodprose-b1-v1",
        "evaluation_id": "goodprose-b1-v1.1",
        "scorer_version": "goodprose-deterministic-v1.1",
        "cases_sha256": sha256_file(cases_path),
        "source_run_manifest_sha256": sha256_file(manifest_path),
        "training_record_sha256": sha256_file(training_record_path),
        "case_results_sha256": sha256_bytes(case_payload),
        "candidates": summaries,
        "comparisons": comparisons,
        "failure_analysis": {
            "profile": {
                "omission_case_change": profile_tuned["error_counts"].get("omission", 0)
                - profile_base["error_counts"].get("omission", 0),
                "placeholder_loss_case_change": profile_tuned["error_counts"].get(
                    "placeholder_loss", 0
                )
                - profile_base["error_counts"].get("placeholder_loss", 0),
                "poor_actionability_case_change": profile_tuned["error_counts"].get(
                    "poor_actionability", 0
                )
                - profile_base["error_counts"].get("poor_actionability", 0),
            },
            "ledger_draft": {
                "omission_case_change": ledger_tuned["error_counts"].get("omission", 0)
                - ledger_base["error_counts"].get("omission", 0),
                "placeholder_loss_case_change": ledger_tuned["error_counts"].get(
                    "placeholder_loss", 0
                )
                - ledger_base["error_counts"].get("placeholder_loss", 0),
                "poor_actionability_case_change": ledger_tuned["error_counts"].get(
                    "poor_actionability", 0
                )
                - ledger_base["error_counts"].get("poor_actionability", 0),
            },
            "reviewed_patterns": [
                *reviewed_patterns,
            ],
            "review_status": review_status,
        },
        "decision": {
            "adapter_disposition": adapter_disposition,
            "leader": leader,
            "next_hypothesis": next_hypothesis,
        },
        "settled_cost_usd": 0,
        "limitations": limitations,
    }
    atomic_write(
        results_path,
        (json.dumps(analysis, indent=2, sort_keys=True) + "\n").encode(),
    )
    return analysis
