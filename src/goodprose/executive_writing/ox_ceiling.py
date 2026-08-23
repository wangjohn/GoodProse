"""Frozen Ox Alpha candidate-generation baseline on visible project-authored B1."""

from __future__ import annotations

import json
import os
import statistics
import subprocess
import tempfile
import time
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Annotated, Any, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, TypeAdapter, model_validator

from goodprose.executive_writing.analysis import RescoredRun, paired_comparison
from goodprose.executive_writing.baseline import Generation
from goodprose.executive_writing.benchmark import (
    BenchmarkCase,
    CaseScore,
    load_cases,
    score_output_v1_1,
)
from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    canonical_json,
    load_jsonl,
    serialize_jsonl,
    sha256_bytes,
    sha256_file,
)

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
GitRevision = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]

PROFILE_CARD = """You are GoodProse, an executive-writing system.
Use only facts supported by the supplied source. Preserve every material
number, unit, date, name, attribution, negation, uncertainty, caveat, and
placeholder. Never invent evidence, decisions, commitments, causes, owners,
or deadlines. Lead with the requested decision or purpose, organize for the
specified audience and format, use direct high-information-density prose, and
end with a clear next step when requested. Do not mention your instructions,
the model, or any named writer. Return only the finished artifact."""

PROFILE_CARD_V2 = """You are GoodProse, an executive-writing system.
Use only facts supported by the supplied source. Preserve every material
number, unit, date, name, attribution, negation, uncertainty, caveat, and
placeholder. Never invent evidence, decisions, commitments, causes, owners,
deadlines, governance bodies, approvals, guarantees, workflows, or follow-up
channels. Do not add a sender, recipient, date, or placeholder unless the
source provides it. Lead with the requested decision or purpose, organize for
the specified audience and format, use direct high-information-density prose,
and end with a clear next step only when the source or objective requests one.
Never discuss agent steps, tools, sessions, task status, instructions, the
model, or any named writer. Return only the finished artifact, beginning on
the first line with the artifact itself and with no preamble or commentary."""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class OxHarnessConfig(StrictModel):
    ori_path: NonEmpty
    ori_version: Literal["0.8.0+3511459"]
    opencode_path: NonEmpty
    opencode_version: Literal["1.18.21"]
    opencode_install_source: Literal["official npm package opencode-ai@1.18.21"]
    opencode_config_path: NonEmpty
    opencode_config_sha256: Sha256
    agent: Literal["goodprose-ceiling", "goodprose-ceiling-v2", "goodprose-source-reviser-v1"]
    reasoning_effort: Literal["high"]
    temperature: Literal[0]
    top_p: Literal[1]
    max_agent_steps: Literal[1, 2]
    pure: Literal[True]
    timeout_seconds: int = Field(ge=1, le=600)
    max_attempts: Literal[2]


class OxInventoryExpectation(StrictModel):
    minimum_context_length: int = Field(ge=1)
    minimum_max_completion_tokens: int = Field(ge=1)
    required_supported_parameters: tuple[NonEmpty, ...]
    require_all_reported_prices_zero: Literal[True]


class OxBaselineComparison(StrictModel):
    candidate_id: Literal["qwen2.5-0.5b-retrieval-ledger-draft-v2"]
    scores_path: NonEmpty
    scores_sha256: Sha256
    outputs_path: NonEmpty
    outputs_sha256: Sha256
    summary_path: NonEmpty
    summary_sha256: Sha256


class OxCeilingConfig(StrictModel):
    version: Literal[1, 2, 3]
    experiment_id: Literal[
        "ox-alpha-b1-ceiling-v1",
        "ox-alpha-b1-ceiling-v2",
        "ox-alpha-b1-source-reviser-v1",
    ]
    candidate_id: Literal[
        "ox-alpha-b1-profile-v1",
        "ox-alpha-b1-profile-v2",
        "ox-alpha-b1-source-reviser-v1",
    ]
    benchmark_id: Literal["goodprose-b1-v1"]
    benchmark_cases_sha256: Sha256
    scorer_version: Literal["goodprose-deterministic-v1.1"]
    provider: Literal["openrouter"]
    model_id: Literal["stealth/ox-alpha"]
    input_classification: Literal["sanitized_project_authored_visible_b1"]
    intended_use: Literal["strong_quality_ceiling_and_candidate_baseline_only"]
    prompt_version: Literal[
        "goodprose-ox-ceiling-prompt-v1",
        "goodprose-ox-ceiling-prompt-v2",
        "goodprose-ox-source-reviser-prompt-v1",
    ]
    pipeline: Literal["single_pass", "draft_revise"] = "single_pass"
    harness: OxHarnessConfig
    inventory: OxInventoryExpectation
    comparison_baseline: OxBaselineComparison
    advancement_minimum_effect_points: float = Field(ge=2.0, le=2.0)
    require_no_hard_gate_regression: Literal[True]
    require_all_hard_gates_for_candidate_advancement: bool = False
    settled_cost_usd: Literal[0]

    @model_validator(mode="after")
    def decoding_matches_agent_config(self) -> Self:
        if self.harness.temperature != 0 or self.harness.top_p != 1:
            raise ValueError("Ox ceiling decoding must remain temperature 0 and top_p 1")
        expected = {
            1: (
                "ox-alpha-b1-ceiling-v1",
                "ox-alpha-b1-profile-v1",
                "goodprose-ox-ceiling-prompt-v1",
                "goodprose-ceiling",
                1,
                False,
                "single_pass",
            ),
            2: (
                "ox-alpha-b1-ceiling-v2",
                "ox-alpha-b1-profile-v2",
                "goodprose-ox-ceiling-prompt-v2",
                "goodprose-ceiling-v2",
                2,
                True,
                "single_pass",
            ),
            3: (
                "ox-alpha-b1-source-reviser-v1",
                "ox-alpha-b1-source-reviser-v1",
                "goodprose-ox-source-reviser-prompt-v1",
                "goodprose-source-reviser-v1",
                2,
                True,
                "draft_revise",
            ),
        }[self.version]
        actual = (
            self.experiment_id,
            self.candidate_id,
            self.prompt_version,
            self.harness.agent,
            self.harness.max_agent_steps,
            self.require_all_hard_gates_for_candidate_advancement,
            self.pipeline,
        )
        if actual != expected:
            raise ValueError("Ox ceiling version, candidate, prompt, agent, and gates drifted")
        return self


class OxBaselineCorrection(StrictModel):
    version: Literal[1]
    correction_id: Literal["ox-alpha-b1-ceiling-baseline-v1.1-correction"]
    correction_type: Literal["evaluator_only_baseline_rescore_pin"]
    discovered_at: NonEmpty
    source_config_sha256: Sha256
    generation_affected: Literal[False]
    outputs_path: NonEmpty
    outputs_sha256: Sha256
    incorrect_scores_path: NonEmpty
    incorrect_scores_sha256: Sha256
    incorrect_summary_path: NonEmpty
    incorrect_summary_sha256: Sha256
    corrected_scores_path: NonEmpty
    corrected_scores_sha256: Sha256
    corrected_summary_path: NonEmpty
    corrected_summary_sha256: Sha256
    corrected_scorer_version: Literal["goodprose-deterministic-v1.1"]
    reason: NonEmpty


class OxRunMetadataCorrection(StrictModel):
    version: Literal[1]
    correction_id: Literal["ox-alpha-b1-ceiling-v2-code-revision-correction"]
    correction_type: Literal["operator_supplied_code_revision_metadata"]
    discovered_at: NonEmpty
    source_run_id: NonEmpty
    source_run_manifest_sha256: Sha256
    source_config_sha256: Sha256
    field: Literal["code_revision"]
    incorrect_value: GitRevision
    corrected_value: GitRevision
    generation_affected: Literal[False]
    evidence: Literal["clean_worktree_head_verified_during_active_run"]
    reason: NonEmpty


@dataclass(frozen=True)
class OxInvocation:
    output: str
    session_id: str
    raw_events: bytes
    latency_ms: float
    prompt_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    finish_reason: str
    cost_usd: Decimal
    model_id: str
    provider: str
    opencode_version: str


class OxInvoker(Protocol):
    def invoke(self, *, prompt: str, title: str, runtime_dir: Path) -> OxInvocation: ...


def load_ox_ceiling_config(path: Path, *, repo_root: Path) -> OxCeilingConfig:
    config = OxCeilingConfig.model_validate_json(path.read_text(encoding="utf-8"))
    opencode_config = repo_root / config.harness.opencode_config_path
    if sha256_file(opencode_config) != config.harness.opencode_config_sha256:
        raise ValueError("OpenCode agent config hash does not match Ox ceiling config")
    return config


def load_ox_baseline_correction(
    path: Path, *, config: OxCeilingConfig, config_path: Path, repo_root: Path
) -> OxBaselineCorrection:
    correction = OxBaselineCorrection.model_validate_json(path.read_text(encoding="utf-8"))
    baseline = config.comparison_baseline
    if correction.source_config_sha256 != sha256_file(config_path):
        raise ValueError("baseline correction does not bind the frozen Ox config")
    if (
        correction.outputs_path != baseline.outputs_path
        or correction.outputs_sha256 != baseline.outputs_sha256
        or correction.incorrect_scores_path != baseline.scores_path
        or correction.incorrect_scores_sha256 != baseline.scores_sha256
        or correction.incorrect_summary_path != baseline.summary_path
        or correction.incorrect_summary_sha256 != baseline.summary_sha256
    ):
        raise ValueError("baseline correction does not exactly bind the incorrect frozen pins")
    corrected_paths = (
        (correction.corrected_scores_path, correction.corrected_scores_sha256),
        (correction.corrected_summary_path, correction.corrected_summary_sha256),
        (correction.outputs_path, correction.outputs_sha256),
    )
    if any(sha256_file(repo_root / name) != digest for name, digest in corrected_paths):
        raise ValueError("baseline correction artifact hash mismatch")
    return correction


def load_ox_run_metadata_correction(
    path: Path,
    *,
    config_path: Path,
    manifest_path: Path,
) -> OxRunMetadataCorrection:
    correction = OxRunMetadataCorrection.model_validate_json(path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if correction.source_run_manifest_sha256 != sha256_file(manifest_path):
        raise ValueError("run metadata correction does not bind the source manifest")
    if correction.source_config_sha256 != sha256_file(config_path):
        raise ValueError("run metadata correction does not bind the source config")
    if correction.source_run_id != manifest.get("run_id"):
        raise ValueError("run metadata correction run ID mismatch")
    if correction.incorrect_value != manifest.get(correction.field):
        raise ValueError("run metadata correction does not bind the incorrect value")
    if correction.corrected_value == correction.incorrect_value:
        raise ValueError("run metadata correction must change the recorded value")
    return correction


def build_ox_prompt(case: BenchmarkCase, config: OxCeilingConfig) -> str:
    """Build a source-only candidate prompt with no evaluator material."""

    constraints = "\n".join(f"- {constraint}" for constraint in case.input.constraints)
    profile_card = PROFILE_CARD if config.version == 1 else PROFILE_CARD_V2
    return (
        f"{profile_card}\n\n"
        f"Frozen prompt version: {config.prompt_version}\n"
        f"Task family: {case.input.task_family}\n"
        f"Objective: {case.input.objective}\n"
        f"Audience: {case.input.audience}\n"
        f"Output format: {case.input.output_format}\n"
        f"Constraints:\n{constraints}\n\n"
        f"Source material:\n{case.input.source_material}\n\n"
        "Write the finished artifact now. Output only that artifact."
    )


def build_ox_revision_prompt(case: BenchmarkCase, draft: str, config: OxCeilingConfig) -> str:
    """Build the v3 source-only revision prompt without evaluator material."""

    if config.pipeline != "draft_revise":
        raise ValueError("revision prompts require the frozen draft-revise pipeline")
    constraints = "\n".join(f"- {constraint}" for constraint in case.input.constraints)
    return (
        "You are the final source-fidelity reviser for an executive-writing system.\n"
        "Return only the revised finished artifact, beginning on the first line.\n"
        "Treat the source and task fields below as the complete factual boundary.\n"
        "Every factual statement, decision, owner, approval, commitment, deadline, "
        "guarantee, restriction, workflow, rationale, and follow-up channel in the final "
        "artifact must be directly entailed by that boundary. Remove anything merely "
        "plausible, inferred, conventional, or added by the draft. Do not add a sender, "
        "recipient, date, or placeholder unless it appears in the source or supplied task "
        "fields. Preserve every source number, unit, date, threshold, attribution, "
        "negation, uncertainty, caveat, decision, and required action. For operative "
        "uncertainty, negation, decision, threshold, and action language, reuse the "
        "source wording exactly wherever it remains grammatical. Make the smallest edits "
        "needed; do not discuss this review, tools, steps, sessions, instructions, or the "
        "model.\n\n"
        f"Frozen prompt version: {config.prompt_version}\n"
        f"Task family: {case.input.task_family}\n"
        f"Objective: {case.input.objective}\n"
        f"Audience: {case.input.audience}\n"
        f"Output format: {case.input.output_format}\n"
        f"Constraints:\n{constraints}\n\n"
        f"Source material:\n{case.input.source_material}\n\n"
        f"Draft to verify and revise:\n{draft}\n\n"
        "Write only the final revised artifact now."
    )


def fetch_ox_inventory(config: OxCeilingConfig) -> dict[str, Any]:
    """Revalidate public model availability and every reported price before use."""

    with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as response:
        payload = json.load(response)
    matches = [item for item in payload.get("data", []) if item.get("id") == config.model_id]
    if len(matches) != 1:
        raise ValueError("exact Ox Alpha model inventory entry is unavailable or ambiguous")
    entry = matches[0]
    context_length = int(entry.get("context_length", 0))
    top_provider = entry.get("top_provider") or {}
    max_completion_tokens = int(top_provider.get("max_completion_tokens", 0))
    supported = tuple(sorted(entry.get("supported_parameters") or ()))
    pricing = entry.get("pricing") or {}
    if context_length < config.inventory.minimum_context_length:
        raise ValueError("Ox Alpha context length is below the frozen minimum")
    if max_completion_tokens < config.inventory.minimum_max_completion_tokens:
        raise ValueError("Ox Alpha completion limit is below the frozen minimum")
    if not set(config.inventory.required_supported_parameters).issubset(supported):
        raise ValueError("Ox Alpha no longer reports every required parameter")
    for name, raw_value in pricing.items():
        try:
            value = Decimal(str(raw_value))
        except InvalidOperation as error:
            raise ValueError(f"unparseable Ox Alpha price field {name}") from error
        if value != 0:
            raise ValueError(f"Ox Alpha price field {name} is no longer zero")
    if not {"prompt", "completion"}.issubset(pricing):
        raise ValueError("Ox Alpha prompt/completion price fields are missing")
    return {
        "id": entry["id"],
        "name": entry.get("name"),
        "context_length": context_length,
        "max_completion_tokens": max_completion_tokens,
        "supported_parameters": list(supported),
        "pricing": dict(sorted(pricing.items())),
    }


class OpenCodeOxInvoker:
    def __init__(self, config: OxCeilingConfig, *, repo_root: Path) -> None:
        self._config = config
        self._opencode_config_path = repo_root / config.harness.opencode_config_path

    def invoke(self, *, prompt: str, title: str, runtime_dir: Path) -> OxInvocation:
        harness = self._config.harness
        command = [
            harness.ori_path,
            "opencode",
            "--model",
            self._config.model_id,
            "--reasoning-effort",
            harness.reasoning_effort,
            "run",
            "--pure",
            "--format",
            "json",
            "--agent",
            harness.agent,
            "--title",
            title,
            "--dir",
            str(runtime_dir),
            prompt,
        ]
        environment = dict(os.environ)
        environment["OPENCODE_CONFIG"] = str(self._opencode_config_path)
        started = time.perf_counter()
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=harness.timeout_seconds,
            env=environment,
        )
        latency_ms = (time.perf_counter() - started) * 1000
        if completed.returncode != 0:
            raise RuntimeError(f"Ox Alpha harness exited {completed.returncode}")
        events = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
        if not events:
            raise RuntimeError("Ox Alpha harness returned no JSON events")
        if any(event.get("type") in {"tool_use", "tool_result"} for event in events):
            raise RuntimeError("Ox Alpha ceiling candidate attempted a forbidden tool call")
        session_ids = {event.get("sessionID") for event in events if event.get("sessionID")}
        if len(session_ids) != 1:
            raise RuntimeError("Ox Alpha event stream has an ambiguous session ID")
        session_id = str(next(iter(session_ids)))
        text_parts = [
            str(event.get("part", {}).get("text", ""))
            for event in events
            if event.get("type") == "text"
        ]
        output = "".join(text_parts).strip()
        if not output:
            raise RuntimeError("Ox Alpha harness returned an empty candidate")
        finishes = [event["part"] for event in events if event.get("type") == "step_finish"]
        if len(finishes) != 1:
            raise RuntimeError("Ox Alpha event stream must contain exactly one finish event")
        finish = finishes[0]
        tokens = finish.get("tokens") or {}
        cost = Decimal(str(finish.get("cost", "-1")))

        exported = subprocess.run(
            [harness.opencode_path, "export", session_id],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
            env=environment,
        )
        session = json.loads(exported.stdout)
        info = session.get("info") or {}
        model = info.get("model") or {}
        if model.get("id") != self._config.model_id or model.get("providerID") != "openrouter":
            raise RuntimeError(
                "exported session model/provider does not match the frozen Ox config"
            )
        if info.get("version") != harness.opencode_version:
            raise RuntimeError("exported session OpenCode version does not match the frozen config")
        if Decimal(str(info.get("cost", "-1"))) != 0 or cost != 0:
            raise RuntimeError("Ox Alpha session reported nonzero or missing cost")
        if (info.get("summary") or {}).get("files", 0) != 0:
            raise RuntimeError("Ox Alpha ceiling session changed repository files")

        return OxInvocation(
            output=output,
            session_id=session_id,
            raw_events=completed.stdout.encode("utf-8"),
            latency_ms=latency_ms,
            prompt_tokens=int(tokens.get("input", 0)),
            output_tokens=int(tokens.get("output", 0)),
            cache_read_tokens=int((tokens.get("cache") or {}).get("read", 0)),
            cache_write_tokens=int((tokens.get("cache") or {}).get("write", 0)),
            finish_reason=str(finish.get("reason", "unknown")),
            cost_usd=cost,
            model_id=str(model["id"]),
            provider=str(model["providerID"]),
            opencode_version=str(info["version"]),
        )


def _run_id(started_at: str, experiment_id: str) -> str:
    stamp = started_at.replace("-", "").replace(":", "").replace("Z", "Z")
    return f"{experiment_id}-{stamp}"


def _failure_manifest(path: Path, manifest: dict[str, Any], error: Exception) -> None:
    manifest["status"] = "failed"
    manifest["failure"] = {"type": type(error).__name__, "message": str(error)[:500]}
    manifest["completed_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    atomic_write_json(path, manifest)


def run_ox_b1_ceiling(
    *,
    config_path: Path,
    cases_path: Path,
    output_root: Path,
    repo_root: Path,
    code_revision: str,
    started_at: str,
    invoker: OxInvoker | None = None,
    inventory: dict[str, Any] | None = None,
) -> Path:
    """Generate one frozen Ox candidate per visible B1 case with complete provenance."""

    TypeAdapter(GitRevision).validate_python(code_revision)
    config = load_ox_ceiling_config(config_path, repo_root=repo_root)
    if config.pipeline != "single_pass":
        raise ValueError("single-pass runner requires the single-pass pipeline")
    if sha256_file(cases_path) != config.benchmark_cases_sha256:
        raise ValueError("B1 cases hash does not match Ox ceiling config")
    run_id = _run_id(started_at, config.experiment_id)
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest_path = run_dir / "run-manifest.json"
    manifest: dict[str, Any] = {
        "version": 1,
        "experiment_id": config.experiment_id,
        "run_id": run_id,
        "status": "running",
        "started_at": started_at,
        "code_revision": code_revision,
        "config_sha256": sha256_file(config_path),
        "cases_sha256": sha256_file(cases_path),
        "candidate_id": config.candidate_id,
        "model_id": config.model_id,
        "provider": config.provider,
        "settled_cost_usd": 0,
        "sessions": [],
    }
    atomic_write_json(manifest_path, manifest)
    cases = load_cases(cases_path)
    generations: list[Generation] = []
    actual_invoker = invoker or OpenCodeOxInvoker(config, repo_root=repo_root)
    try:
        inventory_record = inventory or fetch_ox_inventory(config)
        manifest["inventory"] = inventory_record
        with tempfile.TemporaryDirectory(prefix="goodprose-ox-ceiling-") as runtime_name:
            runtime_dir = Path(runtime_name)
            for ordinal, case in enumerate(cases, start=1):
                prompt = build_ox_prompt(case, config)
                last_error: Exception | None = None
                invocation: OxInvocation | None = None
                for attempt in range(1, config.harness.max_attempts + 1):
                    try:
                        invocation = actual_invoker.invoke(
                            prompt=prompt,
                            title=f"GoodProse Ox B1 ceiling {case.id}",
                            runtime_dir=runtime_dir,
                        )
                        break
                    except (RuntimeError, subprocess.TimeoutExpired) as error:
                        last_error = error
                        if attempt == config.harness.max_attempts:
                            raise
                if invocation is None:
                    raise RuntimeError("Ox Alpha invocation failed") from last_error
                if invocation.cost_usd != 0:
                    raise RuntimeError("Ox Alpha invocation is not zero cost")
                prompt_hash = sha256_bytes(prompt.encode("utf-8"))
                output_hash = sha256_bytes(invocation.output.encode("utf-8"))
                raw_path = run_dir / "events" / f"{case.id}.jsonl"
                atomic_write(raw_path, invocation.raw_events)
                generations.append(
                    Generation(
                        case_id=case.id,
                        candidate_id=config.candidate_id,
                        prompt_sha256=prompt_hash,
                        output=invocation.output,
                        output_sha256=output_hash,
                        latency_ms=invocation.latency_ms,
                        prompt_tokens=invocation.prompt_tokens,
                        output_tokens=invocation.output_tokens,
                    )
                )
                manifest["sessions"].append(
                    {
                        "ordinal": ordinal,
                        "case_id": case.id,
                        "session_id": invocation.session_id,
                        "prompt_sha256": prompt_hash,
                        "output_sha256": output_hash,
                        "raw_events_sha256": sha256_file(raw_path),
                        "prompt_tokens": invocation.prompt_tokens,
                        "output_tokens": invocation.output_tokens,
                        "cache_read_tokens": invocation.cache_read_tokens,
                        "cache_write_tokens": invocation.cache_write_tokens,
                        "finish_reason": invocation.finish_reason,
                        "latency_ms": round(invocation.latency_ms, 4),
                        "model_id": invocation.model_id,
                        "provider": invocation.provider,
                        "opencode_version": invocation.opencode_version,
                        "settled_cost_usd": 0,
                    }
                )
                atomic_write_json(manifest_path, manifest)
        outputs_path = run_dir / "outputs.jsonl"
        atomic_write(outputs_path, serialize_jsonl(generations))
        manifest.update(
            {
                "status": "completed",
                "completed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "case_count": len(generations),
                "outputs_sha256": sha256_file(outputs_path),
                "aggregate_tokens": {
                    "input": sum(item.prompt_tokens or 0 for item in generations),
                    "output": sum(item.output_tokens or 0 for item in generations),
                    "cache_read": sum(item["cache_read_tokens"] for item in manifest["sessions"]),
                    "cache_write": sum(item["cache_write_tokens"] for item in manifest["sessions"]),
                },
                "elapsed_seconds": round(
                    sum(item["latency_ms"] for item in manifest["sessions"]) / 1000, 6
                ),
            }
        )
        atomic_write_json(manifest_path, manifest)
    except Exception as error:
        if generations:
            atomic_write(run_dir / "outputs.partial.jsonl", serialize_jsonl(generations))
        _failure_manifest(manifest_path, manifest, error)
        raise
    return run_dir


def _invoke_with_retry(
    *,
    invoker: OxInvoker,
    prompt: str,
    title: str,
    runtime_dir: Path,
    max_attempts: int,
) -> OxInvocation:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return invoker.invoke(prompt=prompt, title=title, runtime_dir=runtime_dir)
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            last_error = error
            if attempt == max_attempts:
                raise
    raise RuntimeError("Ox Alpha invocation failed") from last_error


def _stage_session_record(
    *,
    ordinal: int,
    case_id: str,
    stage: Literal["draft", "revision"],
    prompt_hash: str,
    output_hash: str,
    raw_path: Path,
    invocation: OxInvocation,
) -> dict[str, Any]:
    return {
        "ordinal": ordinal,
        "case_id": case_id,
        "stage": stage,
        "session_id": invocation.session_id,
        "prompt_sha256": prompt_hash,
        "output_sha256": output_hash,
        "raw_events_sha256": sha256_file(raw_path),
        "prompt_tokens": invocation.prompt_tokens,
        "output_tokens": invocation.output_tokens,
        "cache_read_tokens": invocation.cache_read_tokens,
        "cache_write_tokens": invocation.cache_write_tokens,
        "finish_reason": invocation.finish_reason,
        "latency_ms": round(invocation.latency_ms, 4),
        "model_id": invocation.model_id,
        "provider": invocation.provider,
        "opencode_version": invocation.opencode_version,
        "settled_cost_usd": 0,
    }


def run_ox_b1_source_reviser(
    *,
    config_path: Path,
    cases_path: Path,
    output_root: Path,
    repo_root: Path,
    code_revision: str,
    started_at: str,
    invoker: OxInvoker | None = None,
    inventory: dict[str, Any] | None = None,
) -> Path:
    """Generate fresh drafts and final source-verified revisions for B1."""

    TypeAdapter(GitRevision).validate_python(code_revision)
    config = load_ox_ceiling_config(config_path, repo_root=repo_root)
    if config.pipeline != "draft_revise":
        raise ValueError("source-reviser runner requires the draft-revise pipeline")
    if sha256_file(cases_path) != config.benchmark_cases_sha256:
        raise ValueError("B1 cases hash does not match Ox source-reviser config")
    run_id = _run_id(started_at, config.experiment_id)
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest_path = run_dir / "run-manifest.json"
    manifest: dict[str, Any] = {
        "version": 1,
        "experiment_id": config.experiment_id,
        "run_id": run_id,
        "status": "running",
        "pipeline": config.pipeline,
        "started_at": started_at,
        "code_revision": code_revision,
        "config_sha256": sha256_file(config_path),
        "cases_sha256": sha256_file(cases_path),
        "candidate_id": config.candidate_id,
        "model_id": config.model_id,
        "provider": config.provider,
        "settled_cost_usd": 0,
        "sessions": [],
    }
    atomic_write_json(manifest_path, manifest)
    cases = load_cases(cases_path)
    generations: list[Generation] = []
    draft_hashes: list[dict[str, str]] = []
    actual_invoker = invoker or OpenCodeOxInvoker(config, repo_root=repo_root)
    try:
        manifest["inventory"] = inventory or fetch_ox_inventory(config)
        with tempfile.TemporaryDirectory(prefix="goodprose-ox-source-reviser-") as runtime_name:
            runtime_dir = Path(runtime_name)
            for ordinal, case in enumerate(cases, start=1):
                draft_prompt = build_ox_prompt(case, config)
                draft_invocation = _invoke_with_retry(
                    invoker=actual_invoker,
                    prompt=draft_prompt,
                    title=f"GoodProse Ox source-reviser draft {case.id}",
                    runtime_dir=runtime_dir,
                    max_attempts=config.harness.max_attempts,
                )
                if draft_invocation.cost_usd != 0:
                    raise RuntimeError("Ox Alpha draft invocation is not zero cost")
                draft_prompt_hash = sha256_bytes(draft_prompt.encode("utf-8"))
                draft_output_hash = sha256_bytes(draft_invocation.output.encode("utf-8"))
                draft_raw_path = run_dir / "events" / f"{case.id}.draft.jsonl"
                atomic_write(draft_raw_path, draft_invocation.raw_events)
                draft_hashes.append({"case_id": case.id, "draft_output_sha256": draft_output_hash})
                manifest["sessions"].append(
                    _stage_session_record(
                        ordinal=ordinal,
                        case_id=case.id,
                        stage="draft",
                        prompt_hash=draft_prompt_hash,
                        output_hash=draft_output_hash,
                        raw_path=draft_raw_path,
                        invocation=draft_invocation,
                    )
                )
                atomic_write_json(manifest_path, manifest)

                revision_prompt = build_ox_revision_prompt(case, draft_invocation.output, config)
                revision_invocation = _invoke_with_retry(
                    invoker=actual_invoker,
                    prompt=revision_prompt,
                    title=f"GoodProse Ox source-reviser final {case.id}",
                    runtime_dir=runtime_dir,
                    max_attempts=config.harness.max_attempts,
                )
                if revision_invocation.cost_usd != 0:
                    raise RuntimeError("Ox Alpha revision invocation is not zero cost")
                revision_prompt_hash = sha256_bytes(revision_prompt.encode("utf-8"))
                revision_output_hash = sha256_bytes(revision_invocation.output.encode("utf-8"))
                revision_raw_path = run_dir / "events" / f"{case.id}.revision.jsonl"
                atomic_write(revision_raw_path, revision_invocation.raw_events)
                manifest["sessions"].append(
                    _stage_session_record(
                        ordinal=ordinal,
                        case_id=case.id,
                        stage="revision",
                        prompt_hash=revision_prompt_hash,
                        output_hash=revision_output_hash,
                        raw_path=revision_raw_path,
                        invocation=revision_invocation,
                    )
                )
                generations.append(
                    Generation(
                        case_id=case.id,
                        candidate_id=config.candidate_id,
                        prompt_sha256=revision_prompt_hash,
                        output=revision_invocation.output,
                        output_sha256=revision_output_hash,
                        latency_ms=(draft_invocation.latency_ms + revision_invocation.latency_ms),
                        prompt_tokens=(
                            draft_invocation.prompt_tokens + revision_invocation.prompt_tokens
                        ),
                        output_tokens=(
                            draft_invocation.output_tokens + revision_invocation.output_tokens
                        ),
                    )
                )
                atomic_write_json(manifest_path, manifest)
        outputs_path = run_dir / "outputs.jsonl"
        atomic_write(outputs_path, serialize_jsonl(generations))
        manifest.update(
            {
                "status": "completed",
                "completed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "case_count": len(generations),
                "stage_session_count": len(manifest["sessions"]),
                "draft_output_hashes_sha256": sha256_bytes(
                    canonical_json(draft_hashes).encode("utf-8")
                ),
                "outputs_sha256": sha256_file(outputs_path),
                "aggregate_tokens": {
                    "input": sum(item["prompt_tokens"] for item in manifest["sessions"]),
                    "output": sum(item["output_tokens"] for item in manifest["sessions"]),
                    "cache_read": sum(item["cache_read_tokens"] for item in manifest["sessions"]),
                    "cache_write": sum(item["cache_write_tokens"] for item in manifest["sessions"]),
                },
                "elapsed_seconds": round(
                    sum(item["latency_ms"] for item in manifest["sessions"]) / 1000,
                    6,
                ),
            }
        )
        atomic_write_json(manifest_path, manifest)
    except Exception as error:
        if generations:
            atomic_write(run_dir / "outputs.partial.jsonl", serialize_jsonl(generations))
        _failure_manifest(manifest_path, manifest, error)
        raise
    return run_dir


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _summary(
    config: OxCeilingConfig, scores: list[CaseScore], generations: list[Generation]
) -> dict[str, Any]:
    dimensions = scores[0].dimensions if scores else {}
    latencies = [item.latency_ms for item in generations]
    errors = Counter(error for score in scores for error in score.errors)
    return {
        "candidate_id": config.candidate_id,
        "case_count": len(scores),
        "evaluation_id": "goodprose-b1-v1.1",
        "scorer_version": config.scorer_version,
        "mean_development_score": round(statistics.fmean(s.development_score for s in scores), 4),
        "median_development_score": round(
            statistics.median(s.development_score for s in scores), 4
        ),
        "hard_gate_pass_rate": round(
            sum(score.passes_hard_gates for score in scores) / max(1, len(scores)), 4
        ),
        "dimension_means": {
            name: round(statistics.fmean(score.dimensions[name] for score in scores), 4)
            for name in dimensions
        },
        "error_counts": dict(sorted(errors.items())),
        "latency_ms": {
            "mean": round(statistics.fmean(latencies), 4),
            "median": round(statistics.median(latencies), 4),
            "p95": round(_percentile(latencies, 0.95), 4),
        },
        "prompt_tokens": sum(item.prompt_tokens or 0 for item in generations),
        "output_tokens": sum(item.output_tokens or 0 for item in generations),
        "settled_cost_usd": 0,
    }


def publish_ox_b1_ceiling_results(
    *,
    config_path: Path,
    run_dir: Path,
    cases_path: Path,
    repo_root: Path,
    results_path: Path,
    case_results_path: Path,
    generated_at: str,
    baseline_correction_path: Path | None = None,
    run_metadata_correction_path: Path | None = None,
) -> dict[str, Any]:
    """Score, compare, and publish the frozen Ox ceiling candidate."""

    if results_path.exists() or case_results_path.exists():
        raise FileExistsError("Ox ceiling result paths must not already exist")
    config = load_ox_ceiling_config(config_path, repo_root=repo_root)
    manifest_path = run_dir / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed":
        raise ValueError("Ox ceiling run must be completed before publication")
    if manifest.get("config_sha256") != sha256_file(config_path):
        raise ValueError("Ox ceiling run config hash mismatch")
    if manifest.get("cases_sha256") != sha256_file(cases_path):
        raise ValueError("Ox ceiling run cases hash mismatch")
    outputs_path = run_dir / "outputs.jsonl"
    if manifest.get("outputs_sha256") != sha256_file(outputs_path):
        raise ValueError("Ox ceiling outputs hash mismatch")
    run_metadata_correction = (
        load_ox_run_metadata_correction(
            run_metadata_correction_path,
            config_path=config_path,
            manifest_path=manifest_path,
        )
        if run_metadata_correction_path is not None
        else None
    )
    generations = load_jsonl(outputs_path, Generation)
    cases = load_cases(cases_path)
    by_case = {item.case_id: item for item in generations}
    if set(by_case) != {case.id for case in cases} or len(by_case) != len(generations):
        raise ValueError("Ox ceiling outputs must cover every B1 case exactly once")
    scores = [
        score_output_v1_1(case, by_case[case.id].output, candidate_id=config.candidate_id)
        for case in cases
    ]
    summary = _summary(config, scores, generations)
    scores_path = run_dir / "scores.jsonl"
    summary_path = run_dir / "summary.json"
    atomic_write(scores_path, serialize_jsonl(scores))
    atomic_write_json(summary_path, summary)

    baseline_config = config.comparison_baseline
    correction = (
        load_ox_baseline_correction(
            baseline_correction_path,
            config=config,
            config_path=config_path,
            repo_root=repo_root,
        )
        if baseline_correction_path is not None
        else None
    )
    baseline_scores_path = repo_root / (
        correction.corrected_scores_path if correction else baseline_config.scores_path
    )
    baseline_outputs_path = repo_root / baseline_config.outputs_path
    baseline_summary_path = repo_root / (
        correction.corrected_summary_path if correction else baseline_config.summary_path
    )
    expected_paths = (
        (
            baseline_scores_path,
            correction.corrected_scores_sha256 if correction else baseline_config.scores_sha256,
        ),
        (baseline_outputs_path, baseline_config.outputs_sha256),
        (
            baseline_summary_path,
            correction.corrected_summary_sha256 if correction else baseline_config.summary_sha256,
        ),
    )
    if any(sha256_file(path) != expected for path, expected in expected_paths):
        raise ValueError("frozen comparison-baseline artifact hash mismatch")
    baseline_scores = load_jsonl(baseline_scores_path, CaseScore)
    baseline_summary = json.loads(baseline_summary_path.read_text(encoding="utf-8"))
    if any(score.scorer_version != config.scorer_version for score in baseline_scores):
        raise ValueError("comparison baseline scores do not use the declared scorer version")
    if baseline_summary.get("scorer_version") != config.scorer_version:
        raise ValueError("comparison baseline summary does not use the declared scorer version")
    baseline_run = RescoredRun(
        candidate_id=baseline_config.candidate_id,
        scores=baseline_scores,
        generations=[],
        summary=baseline_summary,
        artifact_hashes={},
        source_artifact_hashes={},
    )
    candidate_run = RescoredRun(
        candidate_id=config.candidate_id,
        scores=scores,
        generations=generations,
        summary=summary,
        artifact_hashes={},
        source_artifact_hashes={},
    )
    comparison = paired_comparison(baseline_run, candidate_run)
    candidate_passes_every_gate = all(score.passes_hard_gates for score in scores)
    candidate_meets_advancement_gate = comparison["meets_advancement_gate"] and (
        candidate_passes_every_gate or not config.require_all_hard_gates_for_candidate_advancement
    )
    status = (
        "completed_advance_as_automated_ceiling_candidate"
        if candidate_meets_advancement_gate
        else "completed_no_automated_advancement"
    )
    compact_cases = [
        {
            "case_id": score.case_id,
            "task_family": case.input.task_family,
            "output_format": case.input.output_format,
            "output_sha256": by_case[case.id].output_sha256,
            "development_score": score.development_score,
            "passes_hard_gates": score.passes_hard_gates,
            "failed_critical_check_ids": [
                check.id for check in score.checks if check.critical and not check.passed
            ],
            "errors": list(score.errors),
        }
        for case, score in zip(cases, scores, strict=True)
    ]
    analysis: dict[str, Any] = {
        "version": 1,
        "analysis_id": f"{config.experiment_id}-analysis",
        "status": status,
        "validity_status": "visible_b1_exploratory_strong_ceiling_baseline",
        "generated_at": generated_at,
        "benchmark_id": config.benchmark_id,
        "evaluation_id": "goodprose-b1-v1.1",
        "scorer_version": config.scorer_version,
        "source_run_id": manifest["run_id"],
        "source_run_manifest_sha256": sha256_file(manifest_path),
        "recorded_code_revision": manifest["code_revision"],
        "effective_code_revision": (
            run_metadata_correction.corrected_value
            if run_metadata_correction
            else manifest["code_revision"]
        ),
        "run_metadata_correction_sha256": (
            sha256_file(run_metadata_correction_path) if run_metadata_correction_path else None
        ),
        "config_sha256": sha256_file(config_path),
        "baseline_correction_sha256": (
            sha256_file(baseline_correction_path) if baseline_correction_path else None
        ),
        "comparison_validity": (
            "corrected_evaluator_only_v1.1_baseline"
            if correction
            else "frozen_matching_scorer_baseline_pins"
        ),
        "outputs_sha256": sha256_file(outputs_path),
        "scores_sha256": sha256_file(scores_path),
        "summary_sha256": sha256_file(summary_path),
        "case_results_sha256": sha256_bytes(
            ("\n".join(canonical_json(row) for row in compact_cases) + "\n").encode("utf-8")
        ),
        "provider": config.provider,
        "model_id": config.model_id,
        "candidate": summary,
        "comparison": comparison,
        "candidate_passes_every_hard_gate": candidate_passes_every_gate,
        "candidate_meets_advancement_gate": candidate_meets_advancement_gate,
        "require_all_hard_gates_for_candidate_advancement": (
            config.require_all_hard_gates_for_candidate_advancement
        ),
        "decision": {
            "automated_ceiling_disposition": (
                "advance_for_common_frontier_comparison"
                if candidate_meets_advancement_gate
                else "retain_as_strong_ceiling_diagnostic_only"
            ),
            "production_disposition": (
                "not_decided_pending_privacy_deployment_sealed_and_human_gates"
            ),
        },
        "limitations": [
            "B1 is visible, small, and project-authored, so this is exploratory search evidence.",
            (
                "Ox Alpha is an externally hosted model with an unstable stealth "
                "identifier and availability."
            ),
            "Zero price at execution is not a durable deployment-cost guarantee.",
            (
                "The deterministic scorer cannot replace semantic, sealed, or "
                "intended-audience human review."
            ),
        ],
        "settled_cost_usd": 0,
    }
    atomic_write(
        case_results_path,
        ("\n".join(canonical_json(row) for row in compact_cases) + "\n").encode("utf-8"),
    )
    atomic_write_json(results_path, analysis)
    return analysis
