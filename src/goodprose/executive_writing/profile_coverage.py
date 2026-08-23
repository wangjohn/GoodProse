"""Deterministic, source-text-free coverage runner for the descriptive profiles.

This module implements the frozen ``ox-profile-coverage-runner-v1`` contract:
twelve candidates (one GoodProse house-profile control plus eleven descriptive
profile-card candidates) each answering the same six project-authored B1 cases,
for exactly seventy-two local-generation calls. It is exploratory coverage
evidence only: no advancement winner, production gate, or training claim can
come from this run, and no third-party source text ever enters a model prompt.
"""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from goodprose.executive_writing.baseline import (
    PROFILE_CARD,
    BaselineConfig,
    Generation,
    OllamaClient,
    build_prompt,
    load_config,
)
from goodprose.executive_writing.benchmark import (
    BenchmarkCase,
    BenchmarkManifest,
    CaseScore,
    load_cases,
    score_output_v1_1,
)
from goodprose.executive_writing.sources import (
    COMMON_EVALUATION_CASE_IDS,
    EVALUATION_MANIFEST_ID,
    MANIFEST_ID,
    REQUESTED_PEOPLE,
    ProfileSpecification,
    ValidatedLayout,
    validate_repository_layout,
)
from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    load_jsonl,
    serialize_jsonl,
    sha256_file,
)

NonEmpty = Annotated[str, StringConstraints(min_length=1)]

EVALUATION_ID = "source-profile-coverage-v1"
ASSIGNMENT_ID = "ox-profile-coverage-runner-v1"
BENCHMARK_ID = "goodprose-b1-v1"
SCORER_VERSION_REQUIRED = "goodprose-deterministic-v1.1"
DESCRIPTIVE_PROMPT_VERSION = "descriptive-source-profile-v1"
EXPECTED_GENERATION_CALLS = len(COMMON_EVALUATION_CASE_IDS) * 12
COVERAGE_LIMITATIONS = (
    "Six project-authored cases provide plumbing-level coverage evidence only.",
    "Paired differences are exploratory; no advancement winner or production "
    "default may be set from this run.",
    "Topic-swap variants of the shared cases do not exist yet, so trait and "
    "topic effects are not separated.",
    "Leave-time-out evaluation is unavailable because collection dating "
    "metadata is not yet verified.",
    "All eleven descriptive profiles remain in the program regardless of score.",
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CoverageRunConfig(StrictModel):
    """Exact machine-readable configuration for one frozen coverage run."""

    version: Literal[1]
    evaluation_id: NonEmpty
    assignment_id: NonEmpty
    purpose: Literal["exploratory_profile_card_coverage_not_impersonation_or_endorsement"]
    named_source_manifest_path: NonEmpty
    source_profiles_eval_manifest_path: NonEmpty
    source_profiles_configs_dir: NonEmpty
    b1_cases_path: NonEmpty
    benchmark_manifest_path: NonEmpty
    baseline_config_path: NonEmpty
    scorer_correction_path: NonEmpty
    ox_assignment_path: NonEmpty
    house_control_candidate_id: NonEmpty
    descriptive_prompt_version: Literal["descriptive-source-profile-v1"]
    shared_case_ids: list[NonEmpty]
    expected_generation_calls: Literal[72]
    retrieval_enabled: Literal[False]
    no_third_party_text_in_prompts: Literal[True]
    settled_cost_usd: Literal[0]

    @model_validator(mode="after")
    def _frozen_posture(self) -> CoverageRunConfig:
        if self.evaluation_id != EVALUATION_ID or self.assignment_id != ASSIGNMENT_ID:
            raise ValueError("coverage config pins the frozen evaluation and assignment IDs")
        if self.descriptive_prompt_version != DESCRIPTIVE_PROMPT_VERSION:
            raise ValueError("descriptive prompt version is not frozen")
        if self.expected_generation_calls != EXPECTED_GENERATION_CALLS:
            raise ValueError("expected generation call count is not frozen at 72")
        if self.shared_case_ids != list(COMMON_EVALUATION_CASE_IDS):
            raise ValueError("shared_case_ids must equal the frozen six-case B1 selection in order")
        if self.retrieval_enabled:
            raise ValueError("retrieval must be disabled for profile-card coverage runs")
        if not self.no_third_party_text_in_prompts:
            raise ValueError("prompts must be free of third-party source text")
        if self.settled_cost_usd != 0:
            raise ValueError("settled provider cost must be exactly zero")
        return self


class GenerationClient(Protocol):
    """Structural type satisfied by :class:`OllamaClient` and test doubles."""

    def generate(
        self, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int | None]]: ...


@dataclass(frozen=True)
class CoverageInputs:
    config: CoverageRunConfig
    layout: ValidatedLayout
    baseline_config: BaselineConfig
    cases: tuple[BenchmarkCase, ...]
    benchmark_manifest: BenchmarkManifest
    input_file_hashes: dict[str, str]


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    person: str | None
    profile: ProfileSpecification | None


RUBRIC_MARKERS: tuple[str, ...] = (
    "required_facts",
    "forbidden_claims",
    "must_preserve_spans",
    "adversarial_features",
    "development_score",
    "hard gate",
    "scorer",
    "rubric",
)


def load_coverage_run_config(path: Path) -> CoverageRunConfig:
    return CoverageRunConfig.model_validate_json(path.read_text(encoding="utf-8"))


def _repo_root(path: Path) -> Path:
    for parent in (path, *path.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    raise ValueError(f"cannot find repository root from {path}")


def _resolve(repo_root: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else repo_root / candidate


def load_coverage_inputs(config_path: Path) -> CoverageInputs:
    """Load and cross-validate every artifact the coverage run depends on."""

    config = load_coverage_run_config(config_path)
    repo_root = _repo_root(config_path)
    manifest_path = _resolve(repo_root, config.named_source_manifest_path)
    eval_manifest_path = _resolve(repo_root, config.source_profiles_eval_manifest_path)
    configs_dir = _resolve(repo_root, config.source_profiles_configs_dir)
    cases_path = _resolve(repo_root, config.b1_cases_path)
    benchmark_manifest_path = _resolve(repo_root, config.benchmark_manifest_path)
    baseline_config_path = _resolve(repo_root, config.baseline_config_path)
    correction_path = _resolve(repo_root, config.scorer_correction_path)
    assignment_path = _resolve(repo_root, config.ox_assignment_path)

    layout = validate_repository_layout(manifest_path, eval_manifest_path, configs_dir)
    if layout.manifest.manifest_id != MANIFEST_ID:
        raise ValueError(f"unexpected source manifest {layout.manifest.manifest_id}")
    if layout.eval_manifest.eval_id != EVALUATION_MANIFEST_ID:
        raise ValueError(f"unexpected eval manifest {layout.eval_manifest.eval_id}")

    expected_ids = list(COMMON_EVALUATION_CASE_IDS)
    for entry in layout.manifest.people:
        if entry.evaluation_subset.case_ids != expected_ids:
            raise ValueError(
                f"profile {entry.profile.profile_id} does not select the frozen "
                "six-case sequence in manifest order"
            )

    benchmark_manifest = BenchmarkManifest.model_validate_json(
        benchmark_manifest_path.read_text(encoding="utf-8")
    )
    if benchmark_manifest.benchmark_id != BENCHMARK_ID:
        raise ValueError(f"unexpected benchmark {benchmark_manifest.benchmark_id}")
    if benchmark_manifest.case_count < len(expected_ids):
        raise ValueError("benchmark manifest reports fewer cases than required")

    all_cases = load_cases(cases_path)
    if benchmark_manifest.cases_sha256 != sha256_file(cases_path):
        raise ValueError("benchmark manifest does not match the B1 cases bytes")
    by_id = {case.id: case for case in all_cases}
    missing = [case_id for case_id in expected_ids if case_id not in by_id]
    if missing:
        raise ValueError(f"frozen shared cases missing from benchmark file: {missing}")
    cases = tuple(by_id[case_id] for case_id in expected_ids)

    baseline_config = load_config(baseline_config_path)
    if baseline_config.candidate_id != config.house_control_candidate_id:
        raise ValueError("baseline candidate ID does not match the declared house control")
    if baseline_config.strategy != "profile" or baseline_config.retrieval_examples_path:
        raise ValueError("house control must use the source-text-free profile strategy")
    if baseline_config.decoding.temperature != 0:
        raise ValueError("house-control decoding temperature must be exactly zero")

    input_file_hashes = {
        "named_source_manifest": sha256_file(manifest_path),
        "source_profiles_eval_manifest": sha256_file(eval_manifest_path),
        "b1_cases": sha256_file(cases_path),
        "benchmark_manifest": sha256_file(benchmark_manifest_path),
        "baseline_config": sha256_file(baseline_config_path),
        "scorer_correction": sha256_file(correction_path),
        "ox_assignment": sha256_file(assignment_path),
        "coverage_run_config": sha256_file(config_path),
    }
    for entry in layout.manifest.people:
        profile_id = entry.profile.profile_id
        input_file_hashes[f"source_profile_config:{profile_id}"] = sha256_file(
            configs_dir / f"{profile_id}.json"
        )
    return CoverageInputs(
        config=config,
        layout=layout,
        baseline_config=baseline_config,
        cases=cases,
        benchmark_manifest=benchmark_manifest,
        input_file_hashes=input_file_hashes,
    )


def plan_candidates(inputs: CoverageInputs) -> list[CandidateSpec]:
    """Return the deterministic twelve-candidate order: control first."""

    candidates = [
        CandidateSpec(
            candidate_id=inputs.config.house_control_candidate_id,
            person=None,
            profile=None,
        )
    ]
    seen = {candidates[0].candidate_id}
    for entry in inputs.layout.manifest.people:
        candidate_id = f"profile-coverage-{entry.profile.profile_id}"
        if candidate_id in seen:
            raise ValueError(f"duplicate candidate ID {candidate_id}")
        candidates.append(
            CandidateSpec(
                candidate_id=candidate_id,
                person=entry.person,
                profile=entry.profile,
            )
        )
        seen.add(candidate_id)
    return candidates


def _task_block(case: BenchmarkCase) -> str:
    constraints = "\n".join(f"- {item}" for item in case.input.constraints)
    return f"""Output format: {case.input.output_format.value}
Audience: {case.input.audience}
Objective: {case.input.objective}
Constraints:
{constraints}

Source material:
{case.input.source_material}"""


def build_house_prompt(case: BenchmarkCase, config: BaselineConfig) -> str:
    """Build the GoodProse house-profile control prompt."""

    return build_prompt(case, config)


def build_descriptive_prompt(case: BenchmarkCase, spec: ProfileSpecification) -> str:
    """Build a descriptive profile-card prompt free of identity and source text."""

    traits = "\n".join(f"- {trait.trait}" for trait in spec.traits)
    limits = "\n".join(f"- {limit}" for limit in spec.anti_impersonation_limits)
    return f"""You are GoodProse, an executive-writing system producing one artifact.

Descriptive writing profile (an abstract register, not a person):
Name: {spec.production_name}
Description: {spec.description}
Target abstract characteristics:
{traits}

The profile above is an abstract register specification only. Do not name any
real person, do not imitate any person, and do not imply any person's
endorsement.

Anti-impersonation limits:
{limits}

GoodProse safety rules:
{PROFILE_CARD}

Only the supplied project-authored task source below is authoritative. Use its
facts exclusively and never add outside material.

{_task_block(case)}"""


def assert_prompt_policy(
    prompt: str,
    *,
    spec: CandidateSpec,
    route_ids: set[str],
) -> None:
    """Reject identity leakage, source routing, URLs, and rubric exposure."""

    lowered = prompt.casefold()
    if spec.person is not None:
        for person in REQUESTED_PEOPLE:
            for token in person.casefold().split():
                if len(token) >= 4 and token in lowered:
                    raise ValueError(f"prompt leaks person identity token {token!r}")
    for source_id in sorted(route_ids):
        if source_id.casefold() in lowered:
            raise ValueError(f"prompt leaks source ID {source_id}")
    if "http://" in prompt or "https://" in prompt:
        raise ValueError("prompt must not contain source URLs")
    for marker in RUBRIC_MARKERS:
        if marker in lowered:
            raise ValueError(f"prompt exposes rubric material: {marker}")


def _sum_optional(values: list[int | None]) -> int | None:
    present = [value for value in values if value is not None]
    return sum(present) if present else None


def run_coverage(
    *,
    inputs: CoverageInputs,
    output_root: Path,
    code_revision: str,
    client: GenerationClient | None = None,
    started_at: str | None = None,
) -> Path:
    """Execute exactly 72 scored generation calls and persist raw artifacts."""

    if not code_revision.strip():
        raise ValueError("code revision must be non-empty")
    run_dir = output_root / EVALUATION_ID
    if run_dir.exists():
        raise ValueError(f"raw run directory already exists: {run_dir}")

    started = _normalized_timestamp(started_at) if started_at else _utc_now()

    candidates = plan_candidates(inputs)
    all_route_ids = {
        route.source_id for entry in inputs.layout.manifest.people for route in entry.source_routes
    }
    active_client = client if client is not None else OllamaClient(inputs.baseline_config)

    generations: list[Generation] = []
    scores: list[CaseScore] = []
    for candidate in candidates:
        for case in inputs.cases:
            if candidate.profile is None:
                prompt = build_house_prompt(case, inputs.baseline_config)
            else:
                prompt = build_descriptive_prompt(case, candidate.profile)
            assert_prompt_policy(prompt, spec=candidate, route_ids=all_route_ids)
            start = time.perf_counter()
            output, metrics = active_client.generate(prompt)
            latency_ms = (time.perf_counter() - start) * 1000
            generations.append(
                Generation(
                    case_id=case.id,
                    candidate_id=candidate.candidate_id,
                    prompt_sha256=sha256(prompt.encode("utf-8")).hexdigest(),
                    output=output,
                    output_sha256=sha256(output.encode("utf-8")).hexdigest(),
                    latency_ms=latency_ms,
                    prompt_tokens=metrics["prompt_tokens"],
                    output_tokens=metrics["output_tokens"],
                    total_duration_ns=metrics["total_duration_ns"],
                    load_duration_ns=metrics["load_duration_ns"],
                )
            )
            scores.append(score_output_v1_1(case, output, candidate_id=candidate.candidate_id))

    if len(generations) != EXPECTED_GENERATION_CALLS:
        raise AssertionError(
            f"expected {EXPECTED_GENERATION_CALLS} generation calls, made {len(generations)}"
        )

    completed = _utc_now()

    summaries = [_summarize_candidate(candidate, generations, scores) for candidate in candidates]
    summary_artifact = {
        "evaluation_id": EVALUATION_ID,
        "assignment_id": ASSIGNMENT_ID,
        "scorer_version": SCORER_VERSION_REQUIRED,
        "purpose": "exploratory profile-card coverage; not imitation, endorsement, "
        "training, standalone-adapter evidence, or a model-selection gate",
        "started_at": started,
        "completed_at": completed,
        "generation_call_count": len(generations),
        "retrieval_enabled": False,
        "settled_cost_usd": 0,
        "rights_posture": (
            "project-authored B1 tasks only; descriptive profiles are abstract "
            "registers; no third-party source text was prompted"
        ),
        "no_source_text_in_prompts": True,
        "candidates": summaries,
    }

    outputs_bytes = serialize_jsonl(generations)
    scores_bytes = serialize_jsonl(scores)
    run_dir.mkdir(parents=True)
    atomic_write(run_dir / "outputs.jsonl", outputs_bytes)
    atomic_write(run_dir / "scores.jsonl", scores_bytes)
    atomic_write_json(run_dir / "summary.json", summary_artifact)

    run_manifest = {
        "version": 1,
        "evaluation_id": EVALUATION_ID,
        "assignment_id": ASSIGNMENT_ID,
        "benchmark_id": BENCHMARK_ID,
        "scorer_version": SCORER_VERSION_REQUIRED,
        "code_revision": code_revision,
        "started_at": started,
        "completed_at": completed,
        "model_identity": _model_identity(inputs.baseline_config),
        "candidate_order": _candidate_order(candidates),
        "case_order": [case.id for case in inputs.cases],
        "generation_call_count": len(generations),
        "retrieval_enabled": False,
        "no_third_party_text_in_prompts": True,
        "rights_posture": summary_artifact["rights_posture"],
        "settled_cost_usd": 0,
        "input_file_hashes": inputs.input_file_hashes,
        "artifact_hashes": {
            "outputs_jsonl": sha256(outputs_bytes).hexdigest(),
            "scores_jsonl": sha256(scores_bytes).hexdigest(),
            "summary_json": sha256_file(run_dir / "summary.json"),
        },
    }
    atomic_write_json(run_dir / "run-manifest.json", run_manifest)
    return run_dir


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _normalized_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.isoformat().replace("+00:00", "Z")


def _model_identity(config: BaselineConfig) -> dict[str, Any]:
    return {
        "provider": config.provider,
        "endpoint": config.endpoint,
        "ollama_version": config.ollama_version,
        "model_id": config.model_id,
        "model_manifest_sha256": config.model_manifest_sha256,
        "model_blob_sha256": config.model_blob_sha256,
        "model_license": config.model_license,
        "house_prompt_version": config.prompt_version,
        "descriptive_prompt_version": DESCRIPTIVE_PROMPT_VERSION,
        "decoding": config.decoding.model_dump(mode="json"),
        "request_timeout_seconds": config.request_timeout_seconds,
    }


def _candidate_order(candidates: list[CandidateSpec]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": candidate.candidate_id,
            "person": candidate.person,
            "profile_id": candidate.profile.profile_id if candidate.profile else None,
            "role": "house_control" if candidate.profile is None else "descriptive_profile",
        }
        for candidate in candidates
    ]


def _summarize_candidate(
    candidate: CandidateSpec,
    generations: list[Generation],
    scores: list[CaseScore],
) -> dict[str, Any]:
    candidate_scores = [score for score in scores if score.candidate_id == candidate.candidate_id]
    candidate_generations = [
        item for item in generations if item.candidate_id == candidate.candidate_id
    ]
    error_counts: dict[str, int] = {}
    for score in candidate_scores:
        for error in score.errors:
            error_counts[error] = error_counts.get(error, 0) + 1
    return {
        "candidate_id": candidate.candidate_id,
        "person": candidate.person,
        "profile_id": candidate.profile.profile_id if candidate.profile else None,
        "role": "house_control" if candidate.profile is None else "descriptive_profile",
        "case_count": len(candidate_scores),
        "mean_development_score": round(
            sum(score.development_score for score in candidate_scores)
            / max(1, len(candidate_scores)),
            4,
        ),
        "hard_gate_pass_rate": round(
            sum(score.passes_hard_gates for score in candidate_scores)
            / max(1, len(candidate_scores)),
            4,
        ),
        "error_counts": dict(sorted(error_counts.items())),
        "mean_latency_ms": round(
            sum(item.latency_ms for item in candidate_generations)
            / max(1, len(candidate_generations)),
            4,
        ),
        "prompt_tokens": _sum_optional([item.prompt_tokens for item in candidate_generations]) or 0,
        "output_tokens": _sum_optional([item.output_tokens for item in candidate_generations]) or 0,
    }


def publish_coverage_results(
    *,
    config_path: Path,
    run_dir: Path,
    results_path: Path,
    case_results_path: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Verify raw artifacts, then publish compact source-text-free results."""

    if results_path.exists() or case_results_path.exists():
        raise ValueError("committed results already exist; refusing to overwrite evidence")

    generated_at = _normalized_timestamp(generated_at)
    inputs = load_coverage_inputs(config_path)
    candidates = plan_candidates(inputs)
    expected_candidate_order = _candidate_order(candidates)
    expected_case_order = [case.id for case in inputs.cases]
    expected_pairs = [
        (candidate.candidate_id, case.id) for candidate in candidates for case in inputs.cases
    ]
    manifest: dict[str, Any] = json.loads((run_dir / "run-manifest.json").read_text("utf-8"))
    exact_manifest_values = {
        "version": 1,
        "evaluation_id": EVALUATION_ID,
        "assignment_id": ASSIGNMENT_ID,
        "benchmark_id": BENCHMARK_ID,
        "scorer_version": SCORER_VERSION_REQUIRED,
        "generation_call_count": EXPECTED_GENERATION_CALLS,
        "retrieval_enabled": False,
        "no_third_party_text_in_prompts": True,
        "settled_cost_usd": 0,
        "candidate_order": expected_candidate_order,
        "case_order": expected_case_order,
        "model_identity": _model_identity(inputs.baseline_config),
        "input_file_hashes": inputs.input_file_hashes,
    }
    for name, expected in exact_manifest_values.items():
        if manifest.get(name) != expected:
            raise ValueError(f"run manifest field {name} does not match the frozen run")
    _normalized_timestamp(manifest.get("started_at", ""))
    _normalized_timestamp(manifest.get("completed_at", ""))
    if not str(manifest.get("code_revision", "")).strip():
        raise ValueError("run manifest code revision is missing")

    outputs_bytes = (run_dir / "outputs.jsonl").read_bytes()
    scores_bytes = (run_dir / "scores.jsonl").read_bytes()
    expected_hashes = manifest.get("artifact_hashes", {})
    actual_hashes = {
        "outputs_jsonl": sha256(outputs_bytes).hexdigest(),
        "scores_jsonl": sha256(scores_bytes).hexdigest(),
        "summary_json": sha256_file(run_dir / "summary.json"),
    }
    for name, digest in actual_hashes.items():
        if expected_hashes.get(name) != digest:
            raise ValueError(f"artifact hash mismatch for {name}; raw evidence tampered")

    generations = load_jsonl(run_dir / "outputs.jsonl", Generation)
    scores = load_jsonl(run_dir / "scores.jsonl", CaseScore)
    if len(generations) != EXPECTED_GENERATION_CALLS or len(scores) != EXPECTED_GENERATION_CALLS:
        raise ValueError("raw artifacts do not contain exactly 72 records each")

    order = [(item.candidate_id, item.case_id) for item in generations]
    score_order = [(score.candidate_id, score.case_id) for score in scores]
    if order != expected_pairs or score_order != expected_pairs:
        raise ValueError("raw candidate/case order does not match the frozen 72-pair plan")

    case_results: list[dict[str, Any]] = []
    case_by_id = {case.id: case for case in inputs.cases}
    candidate_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    all_route_ids = {
        route.source_id for entry in inputs.layout.manifest.people for route in entry.source_routes
    }
    for generation, score in zip(generations, scores, strict=True):
        recomputed = sha256(generation.output.encode("utf-8")).hexdigest()
        if generation.output_sha256 != recomputed:
            raise ValueError(
                f"output hash mismatch for {generation.candidate_id}/{generation.case_id}"
            )
        if score.output_sha256 != generation.output_sha256:
            raise ValueError(
                f"score/output hash mismatch for {generation.candidate_id}/{generation.case_id}"
            )
        if score.scorer_version != SCORER_VERSION_REQUIRED:
            raise ValueError("raw scores were not produced by the v1.1 scorer")
        case = case_by_id[generation.case_id]
        candidate = candidate_by_id[generation.candidate_id]
        prompt = (
            build_house_prompt(case, inputs.baseline_config)
            if candidate.profile is None
            else build_descriptive_prompt(case, candidate.profile)
        )
        assert_prompt_policy(prompt, spec=candidate, route_ids=all_route_ids)
        if generation.prompt_sha256 != sha256(prompt.encode("utf-8")).hexdigest():
            raise ValueError(
                f"prompt hash mismatch for {generation.candidate_id}/{generation.case_id}"
            )
        expected_score = score_output_v1_1(
            case,
            generation.output,
            candidate_id=generation.candidate_id,
        )
        if score.model_dump(mode="json") != expected_score.model_dump(mode="json"):
            raise ValueError(
                f"saved score does not match v1.1 rescoring for "
                f"{generation.candidate_id}/{generation.case_id}"
            )
        case_results.append(
            {
                "evaluation_id": EVALUATION_ID,
                "scorer_version": SCORER_VERSION_REQUIRED,
                "candidate_id": generation.candidate_id,
                "case_id": generation.case_id,
                "development_score": score.development_score,
                "passes_hard_gates": score.passes_hard_gates,
                "word_count": score.word_count,
                "errors": list(score.errors),
                "output_sha256": generation.output_sha256,
            }
        )

    summary_artifact: dict[str, Any] = json.loads((run_dir / "summary.json").read_text("utf-8"))
    candidate_summaries = [
        _summarize_candidate(candidate, generations, scores) for candidate in candidates
    ]
    if summary_artifact.get("candidates") != candidate_summaries:
        raise ValueError("saved candidate summaries do not match recomputed raw evidence")
    if (
        summary_artifact.get("evaluation_id") != EVALUATION_ID
        or summary_artifact.get("assignment_id") != ASSIGNMENT_ID
        or summary_artifact.get("scorer_version") != SCORER_VERSION_REQUIRED
        or summary_artifact.get("generation_call_count") != EXPECTED_GENERATION_CALLS
        or summary_artifact.get("retrieval_enabled") is not False
        or summary_artifact.get("no_source_text_in_prompts") is not True
        or summary_artifact.get("settled_cost_usd") != 0
    ):
        raise ValueError("saved summary posture does not match the frozen coverage run")

    control_id = candidates[0].candidate_id
    control_scores = {
        item["case_id"]: item["development_score"]
        for item in case_results
        if item["candidate_id"] == control_id
    }
    paired_comparisons = []
    for candidate in candidates[1:]:
        candidate_id = candidate.candidate_id
        candidate_scores = {
            item["case_id"]: item["development_score"]
            for item in case_results
            if item["candidate_id"] == candidate_id
        }
        deltas = [
            candidate_scores[case_id] - control_scores[case_id]
            for case_id in manifest["case_order"]
        ]
        wins = sum(delta > 0 for delta in deltas)
        ties = sum(delta == 0 for delta in deltas)
        losses = sum(delta < 0 for delta in deltas)
        paired_comparisons.append(
            {
                "candidate_id": candidate_id,
                "case_count": len(deltas),
                "paired_mean_difference": round(sum(deltas) / len(deltas), 4),
                "paired_median_difference": round(statistics.median(deltas), 4),
                "win_tie_loss": {"wins": wins, "ties": ties, "losses": losses},
            }
        )

    results = {
        "version": 1,
        "evaluation_id": EVALUATION_ID,
        "assignment_id": ASSIGNMENT_ID,
        "generated_at": generated_at,
        "code_revision": manifest["code_revision"],
        "model_identity": manifest["model_identity"],
        "status": "exploratory_coverage_complete",
        "advancement_decision": "none_coverage_only",
        "limitations": list(COVERAGE_LIMITATIONS),
        "input_file_hashes": manifest["input_file_hashes"],
        "source_artifact_hashes": {
            **expected_hashes,
            "run_manifest_json": sha256_file(run_dir / "run-manifest.json"),
        },
        "candidates": candidate_summaries,
        "paired_versus_house_control": paired_comparisons,
    }
    atomic_write_json(results_path, results)
    atomic_write_json(case_results_path, case_results)
    return results
