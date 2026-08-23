"""Reproducible local baseline prompting, inference, scoring, and run manifests."""

from __future__ import annotations

import json
import re
import shutil
import statistics
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Literal, Protocol
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.executive_writing.benchmark import (
    BenchmarkCase,
    BenchmarkInput,
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


class PipelineTokenLimits(StrictModel):
    ledger: int = Field(ge=1)
    draft: int = Field(ge=1)


class LocalResourceLimits(StrictModel):
    minimum_available_disk_bytes: int = Field(ge=1)
    maximum_installed_model_bytes: int = Field(ge=1)


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
    strategy: Literal["minimal", "profile", "retrieval", "structured", "ledger_draft"]
    prompt_version: NonEmpty
    retrieval_examples_path: str | None = None
    pipeline_token_limits: PipelineTokenLimits | None = None
    resource_limits: LocalResourceLimits | None = None
    decoding: DecodingConfig
    request_timeout_seconds: int = Field(default=180, ge=1)

    @model_validator(mode="after")
    def local_endpoint_only(self) -> BaselineConfig:
        parsed = urlparse(self.endpoint)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("baseline endpoint must be local loopback HTTP")
        uses_retrieval = self.strategy in {"retrieval", "structured", "ledger_draft"}
        if uses_retrieval and not self.retrieval_examples_path:
            raise ValueError("retrieval and structured strategies require retrieval examples")
        if not uses_retrieval and self.retrieval_examples_path:
            raise ValueError("only retrieval-based strategies may use retrieval examples")
        if self.strategy == "ledger_draft" and self.pipeline_token_limits is None:
            raise ValueError("ledger_draft strategy requires pipeline token limits")
        if self.strategy != "ledger_draft" and self.pipeline_token_limits is not None:
            raise ValueError("only ledger_draft strategy may set pipeline token limits")
        return self


class LocalModelIdentity(StrictModel):
    model_id: NonEmpty
    ollama_version: NonEmpty
    manifest_sha256: Sha256
    blob_sha256: Sha256
    installed_size_bytes: int = Field(ge=1)
    format: NonEmpty
    architecture: NonEmpty
    parameter_count: int = Field(ge=1)
    quantization: NonEmpty
    context_length: int = Field(ge=1)
    license: Literal["Apache-2.0"]


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


class GenerationStep(StrictModel):
    step_id: NonEmpty
    prompt_sha256: Sha256
    output: str
    output_sha256: Sha256
    latency_ms: float = Field(ge=0)
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    total_duration_ns: int | None = None
    load_duration_ns: int | None = None


class Generation(StrictModel):
    case_id: NonEmpty
    candidate_id: NonEmpty
    prompt_sha256: Sha256
    output: str
    output_sha256: Sha256
    latency_ms: float = Field(ge=0)
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    total_duration_ns: int | None = None
    load_duration_ns: int | None = None
    pipeline_steps: tuple[GenerationStep, ...] = ()


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

    def generate(
        self, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int | None]]:
        options = self._config.decoding.model_dump(mode="json")
        if num_predict is not None:
            options["num_predict"] = num_predict
        payload = {
            "model": self._config.model_id,
            "prompt": prompt,
            "stream": False,
            "keep_alive": 0,
            "options": options,
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


class GenerationClient(Protocol):
    """Minimal generation boundary used by local runners and unit-test fakes."""

    def generate(
        self, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int | None]]: ...


def _optional_int(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def load_config(path: Path) -> BaselineConfig:
    return BaselineConfig.model_validate_json(path.read_text(encoding="utf-8"))


def validate_local_model_identity(
    config: BaselineConfig,
    *,
    version_payload: dict[str, Any],
    tags_payload: dict[str, Any],
    show_payload: dict[str, Any],
) -> LocalModelIdentity:
    """Validate the exact installed manifest, primary blob, and model metadata."""

    if version_payload.get("version") != config.ollama_version:
        raise ValueError("Ollama runtime version drifted")
    models = tags_payload.get("models")
    if not isinstance(models, list):
        raise ValueError("Ollama tags response is missing models")
    matches = [item for item in models if item.get("name") == config.model_id]
    if len(matches) != 1:
        raise ValueError("configured Ollama model is missing or ambiguous")
    tag = matches[0]
    if tag.get("digest") != config.model_manifest_sha256:
        raise ValueError("Ollama model manifest digest drifted")
    installed_size = tag.get("size")
    if not isinstance(installed_size, int) or installed_size < 1:
        raise ValueError("Ollama model installed size is invalid")

    modelfile = show_payload.get("modelfile")
    if not isinstance(modelfile, str):
        raise ValueError("Ollama show response is missing the Modelfile")
    blob_match = re.search(r"(?m)^FROM .*/sha256-([0-9a-f]{64})$", modelfile)
    if blob_match is None or blob_match.group(1) != config.model_blob_sha256:
        raise ValueError("Ollama model primary blob digest drifted")

    details = show_payload.get("details")
    model_info = show_payload.get("model_info")
    if not isinstance(details, dict) or not isinstance(model_info, dict):
        raise ValueError("Ollama show response is missing model metadata")
    if str(model_info.get("general.license", "")).casefold() != "apache-2.0":
        raise ValueError("Ollama model license drifted")
    parameter_count = model_info.get("general.parameter_count")
    context_length = model_info.get("qwen2.context_length")
    if not isinstance(parameter_count, int) or not isinstance(context_length, int):
        raise ValueError("Ollama model parameter or context metadata is invalid")

    return LocalModelIdentity(
        model_id=config.model_id,
        ollama_version=config.ollama_version,
        manifest_sha256=config.model_manifest_sha256,
        blob_sha256=config.model_blob_sha256,
        installed_size_bytes=installed_size,
        format=str(details.get("format", "")),
        architecture=str(model_info.get("general.architecture", "")),
        parameter_count=parameter_count,
        quantization=str(details.get("quantization_level", "")),
        context_length=context_length,
        license="Apache-2.0",
    )


def fetch_local_model_identity(config: BaselineConfig) -> LocalModelIdentity:
    """Read and validate exact model identity from the loopback Ollama API."""

    endpoint = config.endpoint.rstrip("/")
    try:
        with urllib.request.urlopen(f"{endpoint}/api/version", timeout=10) as response:
            version_payload: Any = json.load(response)
        with urllib.request.urlopen(f"{endpoint}/api/tags", timeout=10) as response:
            tags_payload: Any = json.load(response)
        show_request = urllib.request.Request(
            f"{endpoint}/api/show",
            data=json.dumps({"model": config.model_id}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(show_request, timeout=30) as response:
            show_payload: Any = json.load(response)
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError(f"local Ollama identity check failed: {error}") from error
    if (
        not isinstance(version_payload, dict)
        or not isinstance(tags_payload, dict)
        or not isinstance(show_payload, dict)
    ):
        raise ValueError("Ollama identity responses must be JSON objects")
    return validate_local_model_identity(
        config,
        version_payload=version_payload,
        tags_payload=tags_payload,
        show_payload=show_payload,
    )


def validate_local_resources(
    config: BaselineConfig,
    identity: LocalModelIdentity,
    *,
    available_disk_bytes: int,
) -> dict[str, int | bool]:
    """Enforce optional pre-generation disk and installed-size bounds."""

    if available_disk_bytes < 0:
        raise ValueError("available disk bytes cannot be negative")
    limits = config.resource_limits
    if limits is None:
        return {
            "limits_required": False,
            "available_disk_bytes": available_disk_bytes,
            "installed_model_bytes": identity.installed_size_bytes,
        }
    if available_disk_bytes < limits.minimum_available_disk_bytes:
        raise RuntimeError("available disk is below the frozen local-model minimum")
    if identity.installed_size_bytes > limits.maximum_installed_model_bytes:
        raise RuntimeError("installed model size exceeds the frozen local-model maximum")
    return {
        "limits_required": True,
        "available_disk_bytes": available_disk_bytes,
        "installed_model_bytes": identity.installed_size_bytes,
        "minimum_available_disk_bytes": limits.minimum_available_disk_bytes,
        "maximum_installed_model_bytes": limits.maximum_installed_model_bytes,
    }


def validate_identity_matches_config(config: BaselineConfig, identity: LocalModelIdentity) -> None:
    """Reject an injected or fetched identity that does not match every frozen pin."""

    if identity.model_id != config.model_id:
        raise ValueError("local model identity does not match the config")
    if identity.ollama_version != config.ollama_version:
        raise ValueError("Ollama version does not match the config")
    if identity.manifest_sha256 != config.model_manifest_sha256:
        raise ValueError("local model manifest does not match the config")
    if identity.blob_sha256 != config.model_blob_sha256:
        raise ValueError("local model blob does not match the config")


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


def _task_words(task: BenchmarkInput, topic: str) -> set[str]:
    values = f"{task.task_family.value} {topic}"
    return set(values.replace("_", " ").casefold().split())


def retrieve_example(case: BenchmarkCase, examples: list[RetrievalExample]) -> RetrievalExample:
    return retrieve_example_for_input(case.input, case.provenance.topic, examples)


def retrieve_example_for_input(
    task: BenchmarkInput, topic: str, examples: list[RetrievalExample]
) -> RetrievalExample:
    """Select an approved example without requiring evaluation-only provenance."""

    if not examples:
        raise ValueError("retrieval example collection is empty")
    case_words = _task_words(task, topic)

    def key(example: RetrievalExample) -> tuple[int, int, int, str]:
        format_match = int(example.output_format == task.output_format)
        family_match = int(example.task_family == task.task_family)
        example_words = set(example.task_family.value.replace("_", " ").split())
        overlap = len(case_words & example_words)
        return (-format_match, -family_match, -overlap, example.id)

    return sorted(examples, key=key)[0]


def _task_prompt(case: BenchmarkCase) -> str:
    return task_prompt_from_input(case.input)


def task_prompt_from_input(task: BenchmarkInput) -> str:
    """Render the source-bound task section shared by evaluation and application."""

    constraints = "\n".join(f"- {item}" for item in task.constraints)
    return f"""Output format: {task.output_format.value}
Audience: {task.audience}
Objective: {task.objective}
Profile: {task.profile_id}
Constraints:
{constraints}

Source material:
{task.source_material}"""


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
    if config.strategy in {"structured", "ledger_draft"}:
        raise ValueError("structured strategy requires the multi-step pipeline")
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


def build_ledger_prompt(case: BenchmarkCase) -> str:
    """Build the rubric-isolated source-ledger extraction prompt."""

    return f"""You are extracting a source ledger for an executive-writing task.
Do not draft the artifact. Use only the supplied task and source. Return a
compact plain-text ledger with these headings:

SUPPORTED FACTS — exact numbers, units, dates, names, decisions, and owners
QUALIFIERS — negations, uncertainty, dependencies, scope, and caveats
DO NOT CLAIM — transformations directly contradicted by the source
PRESERVE — confidential placeholders and already-correct wording
DELIVERY — audience, format, objective, constraints, and requested next action

Do not invent facts or infer hidden requirements.

{_task_prompt(case)}"""


def build_compact_ledger_prompt(case: BenchmarkCase) -> str:
    """Build the iteration-two compact atomic-ledger prompt."""

    return build_compact_ledger_prompt_from_input(case.input)


def build_compact_ledger_prompt_from_input(task: BenchmarkInput) -> str:
    """Build the compact atomic-ledger prompt for a source-bound application task."""

    return f"""Extract a compact source ledger. Do not draft the artifact.
Use at most 192 tokens. Use plain lines, never a table and never boilerplate.
Copy exact source values; do not infer a year, cause, commitment, or fact.

Write one line for every atomic item using only these labels:
FACT — numbers, units, dates, names, decisions, owners, and supported claims
QUALIFIER — every negation, uncertainty, dependency, scope limit, and caveat
PRESERVE — every confidential placeholder and already-correct span
DELIVERY — audience, format, objective, constraint, and requested next action

Omitting a source item is worse than being terse. The source remains
authoritative if this ledger is wrong.

{task_prompt_from_input(task)}"""


def _example_prompt(case: BenchmarkCase, examples: list[RetrievalExample]) -> str:
    return example_prompt_from_input(case.input, case.provenance.topic, examples)


def example_prompt_from_input(
    task: BenchmarkInput, topic: str, examples: list[RetrievalExample]
) -> str:
    example = retrieve_example_for_input(task, topic, examples)
    example_constraints = "\n".join(f"- {item}" for item in example.constraints)
    return f"""Approved example for structure and abstract writing characteristics only.
Do not copy its facts or phrases into the new artifact.

Example format: {example.output_format.value}
Example audience: {example.audience}
Example objective: {example.objective}
Example constraints:
{example_constraints}
Example source:
{example.source_material}
Example output:
{example.output}"""


def build_structured_draft_prompt(
    case: BenchmarkCase, ledger: str, examples: list[RetrievalExample]
) -> str:
    return f"""{PROFILE_CARD}

{_example_prompt(case, examples)}

The extracted ledger below is a planning aid, not a new source. If it conflicts
with the authoritative source, follow the source.

SOURCE LEDGER:
{ledger}

Now draft the requested artifact.

{_task_prompt(case)}"""


def build_ledger_draft_prompt(
    case: BenchmarkCase, ledger: str, examples: list[RetrievalExample]
) -> str:
    return build_ledger_draft_prompt_from_input(case.input, case.provenance.topic, ledger, examples)


def build_ledger_draft_prompt_from_input(
    task: BenchmarkInput,
    topic: str,
    ledger: str,
    examples: list[RetrievalExample],
) -> str:
    return f"""{PROFILE_CARD}

{example_prompt_from_input(task, topic, examples)}

The compact ledger is a checklist, not a new source. Silently verify that the
artifact covers every supported FACT, QUALIFIER, PRESERVE, and DELIVERY item.
If the ledger conflicts with or omits source material, follow the authoritative
source. Preserve exact numbers, dates, names, negations, caveats, placeholders,
and requested actions. Output only the finished artifact.

COMPACT LEDGER:
{ledger}

TASK AND AUTHORITATIVE SOURCE:
{task_prompt_from_input(task)}"""


def build_verification_prompt(case: BenchmarkCase, ledger: str, draft: str) -> str:
    return f"""Audit the draft against the authoritative source and requested task.
Do not rewrite the artifact. Return a concise correction list only, or exactly
NO CORRECTIONS if none are needed. Check every number, unit, date, name,
decision, attribution, negation, uncertainty, caveat, scope limit, confidential
placeholder, format constraint, length constraint, and requested next action.
Flag omissions and unsupported transformations. The source overrides the
planning ledger.

TASK AND SOURCE:
{_task_prompt(case)}

SOURCE LEDGER:
{ledger}

DRAFT:
{draft}"""


def build_revision_prompt(case: BenchmarkCase, ledger: str, draft: str, verification: str) -> str:
    return f"""{PROFILE_CARD}

Revise the draft using the smallest changes necessary to satisfy the task and
authoritative source. Apply verifier notes only when the source supports them.
Do not add commentary about the revision. Output only the finished artifact.

TASK AND SOURCE:
{_task_prompt(case)}

SOURCE LEDGER:
{ledger}

DRAFT:
{draft}

VERIFIER NOTES:
{verification}"""


def _generate_step(
    client: GenerationClient,
    *,
    step_id: str,
    prompt: str,
    num_predict: int | None = None,
) -> tuple[str, GenerationStep]:
    start = time.perf_counter()
    output, metrics = client.generate(prompt, num_predict=num_predict)
    latency_ms = (time.perf_counter() - start) * 1000
    return output, GenerationStep(
        step_id=step_id,
        prompt_sha256=sha256(prompt.encode("utf-8")).hexdigest(),
        output=output,
        output_sha256=sha256(output.encode("utf-8")).hexdigest(),
        latency_ms=latency_ms,
        prompt_tokens=metrics["prompt_tokens"],
        output_tokens=metrics["output_tokens"],
        total_duration_ns=metrics["total_duration_ns"],
        load_duration_ns=metrics["load_duration_ns"],
    )


def _sum_optional(values: list[int | None]) -> int | None:
    present = [value for value in values if value is not None]
    return sum(present) if present else None


def run_structured_pipeline(
    case: BenchmarkCase,
    client: OllamaClient,
    retrieval_examples: list[RetrievalExample],
    *,
    candidate_id: str,
) -> Generation:
    """Run ledger, draft, audit, and minimal-revision calls for one case."""

    ledger_prompt = build_ledger_prompt(case)
    ledger, ledger_step = _generate_step(client, step_id="ledger", prompt=ledger_prompt)
    draft_prompt = build_structured_draft_prompt(case, ledger, retrieval_examples)
    draft, draft_step = _generate_step(client, step_id="draft", prompt=draft_prompt)
    verification_prompt = build_verification_prompt(case, ledger, draft)
    verification, verification_step = _generate_step(
        client, step_id="verify", prompt=verification_prompt
    )
    revision_prompt = build_revision_prompt(case, ledger, draft, verification)
    output, revision_step = _generate_step(client, step_id="revise", prompt=revision_prompt)
    steps = (ledger_step, draft_step, verification_step, revision_step)
    return Generation(
        case_id=case.id,
        candidate_id=candidate_id,
        prompt_sha256=revision_step.prompt_sha256,
        output=output,
        output_sha256=revision_step.output_sha256,
        latency_ms=sum(step.latency_ms for step in steps),
        prompt_tokens=_sum_optional([step.prompt_tokens for step in steps]),
        output_tokens=_sum_optional([step.output_tokens for step in steps]),
        total_duration_ns=_sum_optional([step.total_duration_ns for step in steps]),
        load_duration_ns=_sum_optional([step.load_duration_ns for step in steps]),
        pipeline_steps=steps,
    )


def run_ledger_draft_pipeline(
    case: BenchmarkCase,
    client: OllamaClient,
    retrieval_examples: list[RetrievalExample],
    *,
    candidate_id: str,
    token_limits: PipelineTokenLimits,
) -> Generation:
    """Run the bounded compact-ledger and single-draft iteration."""

    return run_ledger_draft_input(
        case.input,
        case.provenance.topic,
        case.id,
        client,
        retrieval_examples,
        candidate_id=candidate_id,
        token_limits=token_limits,
    )


def run_ledger_draft_input(
    task: BenchmarkInput,
    topic: str,
    request_id: str,
    client: GenerationClient,
    retrieval_examples: list[RetrievalExample],
    *,
    candidate_id: str,
    token_limits: PipelineTokenLimits,
) -> Generation:
    """Run the frozen compact-ledger pipeline for a non-evaluation input."""

    ledger_prompt = build_compact_ledger_prompt_from_input(task)
    ledger, ledger_step = _generate_step(
        client,
        step_id="ledger",
        prompt=ledger_prompt,
        num_predict=token_limits.ledger,
    )
    draft_prompt = build_ledger_draft_prompt_from_input(task, topic, ledger, retrieval_examples)
    output, draft_step = _generate_step(
        client,
        step_id="draft",
        prompt=draft_prompt,
        num_predict=token_limits.draft,
    )
    steps = (ledger_step, draft_step)
    return Generation(
        case_id=request_id,
        candidate_id=candidate_id,
        prompt_sha256=draft_step.prompt_sha256,
        output=output,
        output_sha256=draft_step.output_sha256,
        latency_ms=sum(step.latency_ms for step in steps),
        prompt_tokens=_sum_optional([step.prompt_tokens for step in steps]),
        output_tokens=_sum_optional([step.output_tokens for step in steps]),
        total_duration_ns=_sum_optional([step.total_duration_ns for step in steps]),
        load_duration_ns=_sum_optional([step.load_duration_ns for step in steps]),
        pipeline_steps=steps,
    )


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
    model_identity: LocalModelIdentity | None = None,
    available_disk_bytes: int | None = None,
) -> Path:
    """Run one matched local candidate and persist raw ignored artifacts."""

    config = load_config(config_path)
    resolved_model_identity = model_identity or fetch_local_model_identity(config)
    validate_identity_matches_config(config, resolved_model_identity)
    resolved_available_disk = (
        available_disk_bytes
        if available_disk_bytes is not None
        else shutil.disk_usage(config_path.resolve()).free
    )
    resource_validation = validate_local_resources(
        config,
        resolved_model_identity,
        available_disk_bytes=resolved_available_disk,
    )
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
        if config.strategy == "structured":
            generation = run_structured_pipeline(
                case, client, retrieval_examples, candidate_id=config.candidate_id
            )
            output = generation.output
        elif config.strategy == "ledger_draft":
            if config.pipeline_token_limits is None:
                raise AssertionError("validated ledger_draft config is missing token limits")
            generation = run_ledger_draft_pipeline(
                case,
                client,
                retrieval_examples,
                candidate_id=config.candidate_id,
                token_limits=config.pipeline_token_limits,
            )
            output = generation.output
        else:
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
                prompt_tokens=metrics["prompt_tokens"],
                output_tokens=metrics["output_tokens"],
                total_duration_ns=metrics["total_duration_ns"],
                load_duration_ns=metrics["load_duration_ns"],
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
        "strategy": config.strategy,
        "pipeline_step_ids": (
            ["ledger", "draft", "verify", "revise"]
            if config.strategy == "structured"
            else (["ledger", "draft"] if config.strategy == "ledger_draft" else ["generate"])
        ),
        "decoding": config.decoding.model_dump(mode="json"),
        "model_id": config.model_id,
        "model_manifest_sha256": config.model_manifest_sha256,
        "model_blob_sha256": config.model_blob_sha256,
        "model_license": config.model_license,
        "model_identity": resolved_model_identity.model_dump(mode="json"),
        "resource_validation": resource_validation,
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
