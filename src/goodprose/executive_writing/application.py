"""Local, source-bound application interface for the provisional research leader."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from goodprose.executive_writing.baseline import (
    BaselineConfig,
    GenerationClient,
    LocalModelIdentity,
    OllamaClient,
    fetch_local_model_identity,
    load_config,
    load_retrieval_examples,
    run_ledger_draft_input,
    validate_identity_matches_config,
    validate_local_resources,
)
from goodprose.executive_writing.benchmark import BenchmarkInput, OutputFormat, TaskFamily
from goodprose.jsonl import atomic_write, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
BoundedText = Annotated[str, StringConstraints(min_length=1, max_length=20_000)]
BoundedField = Annotated[str, StringConstraints(min_length=1, max_length=1_000)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

SELECTED_CANDIDATE_ID = "qwen2.5-0.5b-retrieval-ledger-draft-v2"
SELECTED_PROMPT_VERSION = "retrieval-ledger-draft-v2"
SELECTED_PROFILE_ID = "executive-house-v1"
DEFAULT_CONFIG_RELATIVE_PATH = Path(
    "programs/executive-writing/configs/baselines/qwen2.5-0.5b-retrieval-ledger-draft-v2.json"
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ApplicationRequest(StrictModel):
    """Private, local-only input contract; source text is never copied to the result."""

    version: Literal[1]
    request_id: NonEmpty
    task_family: TaskFamily
    output_format: OutputFormat
    source_material: BoundedText
    audience: BoundedField
    objective: BoundedField
    constraints: tuple[BoundedField, ...] = Field(default=(), max_length=20)
    profile_id: Literal["executive-house-v1"] = SELECTED_PROFILE_ID
    topic: BoundedField = "general"


class ApplicationStep(StrictModel):
    step_id: NonEmpty
    prompt_sha256: Sha256
    output_sha256: Sha256
    latency_ms: float = Field(ge=0)
    prompt_tokens: int | None = None
    output_tokens: int | None = None


class ApplicationResult(StrictModel):
    """Auditable result that omits the private source and intermediate ledger text."""

    version: Literal[1]
    status: Literal["research_preview"]
    request_id: NonEmpty
    request_file_sha256: Sha256
    source_material_sha256: Sha256
    artifact: str
    artifact_sha256: Sha256
    candidate_id: Literal["qwen2.5-0.5b-retrieval-ledger-draft-v2"]
    profile_id: Literal["executive-house-v1"]
    provider: Literal["local_ollama"]
    config_sha256: Sha256
    retrieval_examples_sha256: Sha256
    prompt_version: Literal["retrieval-ledger-draft-v2"]
    model_identity: LocalModelIdentity
    resource_validation: dict[str, int | bool]
    pipeline_steps: tuple[ApplicationStep, ...]
    latency_ms: float = Field(ge=0)
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    settled_cost_usd: Literal[0]
    code_revision: NonEmpty
    working_tree_dirty: bool
    generated_at: datetime
    production_qualified: Literal[False]
    manual_factual_review_required: Literal[True]
    warnings: tuple[NonEmpty, ...]


def load_application_request(path: Path) -> ApplicationRequest:
    return ApplicationRequest.model_validate_json(path.read_text(encoding="utf-8"))


def resolve_git_state(repo_root: Path) -> tuple[str, bool]:
    """Return exact HEAD and whether local files differ, without mutating the checkout."""

    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if not revision:
        raise RuntimeError("git returned an empty code revision")
    return revision, bool(status.strip())


def _validate_selected_config(config: BaselineConfig) -> None:
    if config.candidate_id != SELECTED_CANDIDATE_ID:
        raise ValueError("application config is not the provisional selected candidate")
    if config.strategy != "ledger_draft":
        raise ValueError("application config must use the selected ledger_draft strategy")
    if config.prompt_version != SELECTED_PROMPT_VERSION:
        raise ValueError("application prompt version drifted from the selected pipeline")
    if config.pipeline_token_limits is None or config.retrieval_examples_path is None:
        raise ValueError("selected application config is missing pipeline resources")


def _retrieval_path(config_path: Path, config: BaselineConfig, repo_root: Path) -> Path:
    if config.retrieval_examples_path is None:
        raise AssertionError("validated selected config is missing retrieval examples")
    path = Path(config.retrieval_examples_path)
    return path if path.is_absolute() else repo_root / path


def run_application(
    *,
    request_path: Path,
    output_path: Path,
    config_path: Path,
    repo_root: Path,
    code_revision: str,
    working_tree_dirty: bool,
    model_identity: LocalModelIdentity | None = None,
    available_disk_bytes: int | None = None,
    client: GenerationClient | None = None,
    generated_at: datetime | None = None,
) -> ApplicationResult:
    """Apply the frozen research leader locally and write one non-overwriting result."""

    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_path}")
    request = load_application_request(request_path)
    config = load_config(config_path)
    _validate_selected_config(config)
    identity = model_identity or fetch_local_model_identity(config)
    validate_identity_matches_config(config, identity)
    disk_bytes = (
        available_disk_bytes
        if available_disk_bytes is not None
        else shutil.disk_usage(config_path.resolve()).free
    )
    resources = validate_local_resources(config, identity, available_disk_bytes=disk_bytes)
    retrieval_path = _retrieval_path(config_path, config, repo_root)
    examples = load_retrieval_examples(retrieval_path)
    task = BenchmarkInput(
        task_family=request.task_family,
        output_format=request.output_format,
        source_material=request.source_material,
        audience=request.audience,
        objective=request.objective,
        profile_id=request.profile_id,
        constraints=request.constraints,
    )
    if config.pipeline_token_limits is None:
        raise AssertionError("validated selected config is missing token limits")
    generation = run_ledger_draft_input(
        task,
        request.topic,
        request.request_id,
        client or OllamaClient(config),
        examples,
        candidate_id=config.candidate_id,
        token_limits=config.pipeline_token_limits,
    )
    result = ApplicationResult(
        version=1,
        status="research_preview",
        request_id=request.request_id,
        request_file_sha256=sha256_file(request_path),
        source_material_sha256=sha256(request.source_material.encode("utf-8")).hexdigest(),
        artifact=generation.output,
        artifact_sha256=generation.output_sha256,
        candidate_id=SELECTED_CANDIDATE_ID,
        profile_id=SELECTED_PROFILE_ID,
        provider="local_ollama",
        config_sha256=sha256_file(config_path),
        retrieval_examples_sha256=sha256_file(retrieval_path),
        prompt_version=SELECTED_PROMPT_VERSION,
        model_identity=identity,
        resource_validation=resources,
        pipeline_steps=tuple(
            ApplicationStep(
                step_id=step.step_id,
                prompt_sha256=step.prompt_sha256,
                output_sha256=step.output_sha256,
                latency_ms=step.latency_ms,
                prompt_tokens=step.prompt_tokens,
                output_tokens=step.output_tokens,
            )
            for step in generation.pipeline_steps
        ),
        latency_ms=generation.latency_ms,
        prompt_tokens=generation.prompt_tokens,
        output_tokens=generation.output_tokens,
        settled_cost_usd=0,
        code_revision=code_revision,
        working_tree_dirty=working_tree_dirty,
        generated_at=generated_at or datetime.now(UTC),
        production_qualified=False,
        manual_factual_review_required=True,
        warnings=(
            "This candidate is a research leader, not a production-qualified system.",
            "Verify every fact, number, name, date, caveat, and requested action "
            "against the source.",
            "The source and generation remain local to the configured loopback Ollama service.",
        ),
    )
    payload: dict[str, Any] = result.model_dump(mode="json")
    atomic_write(
        output_path,
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return result
