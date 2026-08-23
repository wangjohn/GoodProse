"""Reproducible local baseline prompting, inference, scoring, and run manifests."""

from __future__ import annotations

import json
import statistics
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.executive_writing.benchmark import (
    BenchmarkCase,
    CaseScore,
    OutputFormat,
    TaskFamily,
    load_cases,
    score_output,
)
from goodprose.jsonl import atomic_write, serialize_jsonl, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DecodingConfig(StrictModel):
    temperature: float = Field(ge=0)
    seed: int
    num_predict: int = Field(ge=1)
    num_ctx: int = Field(ge=512)


class BaselineConfig(StrictModel):
    version: Literal[1]
    candidate_id: NonEmpty
    provider: Literal["local_ollama"]
    endpoint: NonEmpty
    ollama_version: NonEmpty
    model_id: NonEmpty
    model_manifest_sha256: Sha256
    model_blob_sha256: Sha256
    model_license: Literal["Apache-2.0"]
    strategy: Literal["minimal", "profile", "retrieval"]
    prompt_version: NonEmpty
    retrieval_examples_path: str | None = None
    decoding: DecodingConfig
    request_timeout_seconds: int = Field(default=180, ge=1)

    @model_validator(mode="after")
    def local_endpoint_only(self) -> BaselineConfig:
        parsed = urlparse(self.endpoint)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("baseline endpoint must be local loopback HTTP")
        if self.strategy == "retrieval" and not self.retrieval_examples_path:
            raise ValueError("retrieval strategy requires retrieval_examples_path")
        if self.strategy != "retrieval" and self.retrieval_examples_path:
            raise ValueError("only retrieval strategy may set retrieval_examples_path")
        return self


class RetrievalExample(StrictModel):
    version: Literal[1]
    id: NonEmpty
    task_family: TaskFamily
    output_format: OutputFormat
    source_material: NonEmpty
    audience: NonEmpty
    objective: NonEmpty
    constraints: tuple[str, ...]
    output: NonEmpty
    creation_method: Literal["project_authored"]
    rights_status: Literal["retrieval_approved_project_owned"]
    lineage_group: NonEmpty


class Generation(StrictModel):
    case_id: NonEmpty
    candidate_id: NonEmpty
    prompt_sha256: Sha256
    output: str
    output_sha256: Sha256
    latency_ms: float = Field(ge=0)
    prompt_tokens: int | None
    output_tokens: int | None
    total_duration_ns: int | None
    load_duration_ns: int | None


class RunSummary(StrictModel):
    experiment_id: NonEmpty
    candidate_id: NonEmpty
    benchmark_id: Literal["goodprose-b1-v1"]
    case_count: int
    mean_development_score: float
    median_development_score: float
    hard_gate_pass_rate: float
    dimension_means: dict[str, float]
    error_counts: dict[str, int]
    latency_ms: dict[str, float]
    prompt_tokens: int
    output_tokens: int
    settled_cost_usd: Literal[0]


PROFILE_CARD = """You are GoodProse, an executive-writing system.
Use only facts supported by the supplied source. Preserve every number, unit,
date, name, attribution, negation, uncertainty, caveat, and placeholder. Never
invent evidence, decisions, commitments, causes, or deadlines. Lead with the
decision or purpose, organize for the requested audience and format, use direct
high-information-density prose, and end with a clear next step when requested.
Do not mention or imitate any named writer. Output only the finished artifact."""


class OllamaClient:
    """Small standard-library client restricted to an already-running local service."""

    def __init__(self, config: BaselineConfig) -> None:
        self._config = config

    def generate(self, prompt: str) -> tuple[str, dict[str, int | None]]:
        payload = {
            "model": self._config.model_id,
            "prompt": prompt,
            "stream": False,
            "keep_alive": 0,
            "options": self._config.decoding.model_dump(mode="json"),
        }
        request = urllib.request.Request(
            f"{self._config.endpoint.rstrip('/')}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self._config.request_timeout_seconds
            ) as response:
                result: Any = json.load(response)
        except (urllib.error.URLError, TimeoutError) as error:
            raise RuntimeError(f"local Ollama request failed: {error}") from error
        if not isinstance(result, dict) or not isinstance(result.get("response"), str):
            raise RuntimeError("local Ollama response is missing text")
        metrics = {
            "prompt_tokens": _optional_int(result.get("prompt_eval_count")),
            "output_tokens": _optional_int(result.get("eval_count")),
            "total_duration_ns": _optional_int(result.get("total_duration")),
            "load_duration_ns": _optional_int(result.get("load_duration")),
        }
        return result["response"].strip(), metrics


def _optional_int(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def load_config(path: Path) -> BaselineConfig:
    return BaselineConfig.model_validate_json(path.read_text(encoding="utf-8"))


def load_retrieval_examples(path: Path) -> list[RetrievalExample]:
    value: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("retrieval examples must be a JSON list")
    examples = [RetrievalExample.model_validate(item) for item in value]
    ids = [example.id for example in examples]
    if len(ids) != len(set(ids)):
        raise ValueError("retrieval example IDs must be unique")
    return examples


def _repo_root(path: Path) -> Path:
    for parent in (path, *path.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    raise ValueError(f"cannot find repository root from {path}")


def _task_words(case: BenchmarkCase) -> set[str]:
    values = f"{case.input.task_family.value} {case.provenance.topic}"
    return set(values.replace("_", " ").casefold().split())


def retrieve_example(case: BenchmarkCase, examples: list[RetrievalExample]) -> RetrievalExample:
    if not examples:
        raise ValueError("retrieval example collection is empty")
    case_words = _task_words(case)

    def key(example: RetrievalExample) -> tuple[int, int, int, str]:
        format_match = int(example.output_format == case.input.output_format)
        family_match = int(example.task_family == case.input.task_family)
        example_words = set(example.task_family.value.replace("_", " ").split())
        overlap = len(case_words & example_words)
        return (-format_match, -family_match, -overlap, example.id)

    return sorted(examples, key=key)[0]


def _task_prompt(case: BenchmarkCase) -> str:
    constraints = "\n".join(f"- {item}" for item in case.input.constraints)
    return f"""Output format: {case.input.output_format.value}
Audience: {case.input.audience}
Objective: {case.input.objective}
Profile: {case.input.profile_id}
Constraints:
{constraints}

Source material:
{case.input.source_material}"""


def build_prompt(
    case: BenchmarkCase,
    config: BaselineConfig,
    retrieval_examples: list[RetrievalExample] | None = None,
) -> str:
    task = _task_prompt(case)
    if config.strategy == "minimal":
        return (
            "Transform the supplied source material into the requested artifact. "
            "Use only supported facts. Output only the artifact.\n\n" + task
        )
    if config.strategy == "profile":
        return f"{PROFILE_CARD}\n\n{task}"
    example = retrieve_example(case, retrieval_examples or [])
    example_constraints = "\n".join(f"- {item}" for item in example.constraints)
    return f"""{PROFILE_CARD}

Approved example for structure and abstract writing characteristics only. Do
not copy its facts or phrases into the new artifact.

Example format: {example.output_format.value}
Example audience: {example.audience}
Example objective: {example.objective}
Example constraints:
{example_constraints}
Example source:
{example.source_material}
Example output:
{example.output}

Now complete the new task. The new source is authoritative; the example is not.

{task}"""


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def summarize_run(
    experiment_id: str,
    config: BaselineConfig,
    scores: list[CaseScore],
    generations: list[Generation],
) -> RunSummary:
    dimension_names = scores[0].dimensions if scores else {}
    dimension_means = {
        name: statistics.fmean(score.dimensions[name] for score in scores)
        for name in dimension_names
    }
    errors = Counter(error for score in scores for error in score.errors)
    latencies = [generation.latency_ms for generation in generations]
    return RunSummary(
        experiment_id=experiment_id,
        candidate_id=config.candidate_id,
        benchmark_id="goodprose-b1-v1",
        case_count=len(scores),
        mean_development_score=round(
            statistics.fmean(score.development_score for score in scores), 4
        ),
        median_development_score=round(
            statistics.median(score.development_score for score in scores), 4
        ),
        hard_gate_pass_rate=round(
            sum(score.passes_hard_gates for score in scores) / max(1, len(scores)), 4
        ),
        dimension_means={name: round(value, 4) for name, value in dimension_means.items()},
        error_counts=dict(sorted(errors.items())),
        latency_ms={
            "mean": round(statistics.fmean(latencies), 4) if latencies else 0,
            "median": round(statistics.median(latencies), 4) if latencies else 0,
            "p95": round(_percentile(latencies, 0.95), 4),
        },
        prompt_tokens=sum(item.prompt_tokens or 0 for item in generations),
        output_tokens=sum(item.output_tokens or 0 for item in generations),
        settled_cost_usd=0,
    )


def run_baseline(
    *,
    config_path: Path,
    cases_path: Path,
    benchmark_manifest_path: Path,
    output_root: Path,
    code_revision: str,
) -> Path:
    """Run one matched local candidate and persist raw ignored artifacts."""

    config = load_config(config_path)
    cases = load_cases(cases_path)
    retrieval_examples: list[RetrievalExample] = []
    retrieval_sha256: str | None = None
    if config.retrieval_examples_path:
        retrieval_path = Path(config.retrieval_examples_path)
        if not retrieval_path.is_absolute():
            retrieval_path = _repo_root(config_path) / retrieval_path
        retrieval_examples = load_retrieval_examples(retrieval_path)
        retrieval_sha256 = sha256_file(retrieval_path)
    experiment_id = f"b1-v1-{config.candidate_id}"
    run_dir = output_root / experiment_id
    started = datetime.now(UTC)
    client = OllamaClient(config)
    generations: list[Generation] = []
    scores: list[CaseScore] = []
    for case in cases:
        prompt = build_prompt(case, config, retrieval_examples)
        start = time.perf_counter()
        output, metrics = client.generate(prompt)
        latency_ms = (time.perf_counter() - start) * 1000
        generation = Generation(
            case_id=case.id,
            candidate_id=config.candidate_id,
            prompt_sha256=sha256(prompt.encode("utf-8")).hexdigest(),
            output=output,
            output_sha256=sha256(output.encode("utf-8")).hexdigest(),
            latency_ms=latency_ms,
            **metrics,
        )
        generations.append(generation)
        scores.append(score_output(case, output, candidate_id=config.candidate_id))
    summary = summarize_run(experiment_id, config, scores, generations)
    completed = datetime.now(UTC)
    manifest = {
        "version": 1,
        "experiment_id": experiment_id,
        "hypothesis": (
            "Prompt construction changes deterministic fidelity and task compliance "
            "on matched B1 cases."
        ),
        "candidate_id": config.candidate_id,
        "baseline_ids": ["qwen2.5-0.5b-minimal-v1"],
        "benchmark_id": "goodprose-b1-v1",
        "benchmark_manifest_sha256": sha256_file(benchmark_manifest_path),
        "cases_sha256": sha256_file(cases_path),
        "config_sha256": sha256_file(config_path),
        "retrieval_examples_sha256": retrieval_sha256,
        "prompt_version": config.prompt_version,
        "decoding": config.decoding.model_dump(mode="json"),
        "model_id": config.model_id,
        "model_manifest_sha256": config.model_manifest_sha256,
        "model_blob_sha256": config.model_blob_sha256,
        "model_license": config.model_license,
        "provider": config.provider,
        "ollama_version": config.ollama_version,
        "code_revision": code_revision,
        "hardware": "Apple M3 Pro, 18 GiB unified memory",
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "completed_at": completed.isoformat().replace("+00:00", "Z"),
        "settled_cost_usd": 0,
        "artifact_hashes": {},
    }
    output_payload = serialize_jsonl(generations)
    score_payload = serialize_jsonl(scores)
    summary_payload = (
        json.dumps(summary.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
    ).encode()
    manifest["artifact_hashes"] = {
        "outputs_jsonl": sha256(output_payload).hexdigest(),
        "scores_jsonl": sha256(score_payload).hexdigest(),
        "summary_json": sha256(summary_payload).hexdigest(),
    }
    manifest_payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    atomic_write(run_dir / "outputs.jsonl", output_payload)
    atomic_write(run_dir / "scores.jsonl", score_payload)
    atomic_write(run_dir / "summary.json", summary_payload)
    atomic_write(run_dir / "run-manifest.json", manifest_payload)
    return run_dir
