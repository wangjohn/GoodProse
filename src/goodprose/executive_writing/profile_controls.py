"""Paired topic-swap controls for source-text-free descriptive profile cards."""

from __future__ import annotations

import json
import shutil
import statistics
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from goodprose.executive_writing.baseline import (
    BaselineConfig,
    Generation,
    GenerationClient,
    LocalModelIdentity,
    OllamaClient,
    fetch_local_model_identity,
    load_config,
    validate_identity_matches_config,
    validate_local_resources,
)
from goodprose.executive_writing.benchmark import (
    BenchmarkCase,
    BenchmarkManifest,
    CaseScore,
    load_cases,
    score_output_v1_1,
)
from goodprose.executive_writing.profile_coverage import (
    CandidateSpec,
    assert_prompt_policy,
    build_descriptive_prompt,
    build_house_prompt,
)
from goodprose.executive_writing.sources import (
    MANIFEST_ID,
    NamedSourceManifest,
    load_named_source_manifest,
)
from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    load_jsonl,
    serialize_jsonl,
    sha256_file,
)

NonEmpty = Annotated[str, StringConstraints(min_length=1)]

EVALUATION_ID = "source-profile-topic-controls-v2"
SCORER_VERSION = "goodprose-deterministic-v1.1"
EXPECTED_CASE_COUNT = 6
EXPECTED_CANDIDATE_COUNT = 12
EXPECTED_GENERATION_CALLS = EXPECTED_CASE_COUNT * EXPECTED_CANDIDATE_COUNT


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class TopicPair(StrictModel):
    pair_id: NonEmpty
    case_ids: tuple[NonEmpty, NonEmpty]

    @model_validator(mode="after")
    def unique_cases(self) -> TopicPair:
        if self.case_ids[0] == self.case_ids[1]:
            raise ValueError("topic pair case IDs must differ")
        return self


class TopicPairManifest(StrictModel):
    version: Literal[1]
    evaluation_id: Literal["source-profile-topic-controls-v2"]
    pairs: tuple[TopicPair, TopicPair, TopicPair]
    content_control: NonEmpty
    leave_topic_out_posture: NonEmpty
    leave_time_out_posture: NonEmpty

    @model_validator(mode="after")
    def unique_membership(self) -> TopicPairManifest:
        pair_ids = [pair.pair_id for pair in self.pairs]
        case_ids = [case_id for pair in self.pairs for case_id in pair.case_ids]
        if len(pair_ids) != len(set(pair_ids)):
            raise ValueError("topic pair IDs must be unique")
        if len(case_ids) != EXPECTED_CASE_COUNT or len(case_ids) != len(set(case_ids)):
            raise ValueError("topic-control cases must appear in exactly one pair")
        return self


class TopicControlConfig(StrictModel):
    version: Literal[1]
    evaluation_id: Literal["source-profile-topic-controls-v2"]
    purpose: Literal["exploratory_topic_robustness_not_impersonation_or_endorsement"]
    named_source_manifest_path: NonEmpty
    cases_path: NonEmpty
    benchmark_manifest_path: NonEmpty
    pair_manifest_path: NonEmpty
    baseline_config_path: NonEmpty
    house_control_candidate_id: NonEmpty
    expected_generation_calls: Literal[72]
    retrieval_enabled: Literal[False]
    no_third_party_text_in_prompts: Literal[True]
    settled_cost_usd: Literal[0]


@dataclass(frozen=True)
class TopicControlInputs:
    config: TopicControlConfig
    source_manifest: NamedSourceManifest
    cases: tuple[BenchmarkCase, ...]
    benchmark_manifest: BenchmarkManifest
    pair_manifest: TopicPairManifest
    baseline_config: BaselineConfig
    input_file_hashes: dict[str, str]


def _repo_root(path: Path) -> Path:
    for parent in (path, *path.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    raise ValueError(f"cannot find repository root from {path}")


def _resolve(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _timestamp(value: str | None = None) -> str:
    if value is None:
        return datetime.now(UTC).isoformat().replace("+00:00", "Z")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.isoformat().replace("+00:00", "Z")


def load_topic_control_inputs(config_path: Path) -> TopicControlInputs:
    config = TopicControlConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
    repo_root = _repo_root(config_path)
    paths = {
        "named_source_manifest": _resolve(repo_root, config.named_source_manifest_path),
        "cases": _resolve(repo_root, config.cases_path),
        "benchmark_manifest": _resolve(repo_root, config.benchmark_manifest_path),
        "pair_manifest": _resolve(repo_root, config.pair_manifest_path),
        "baseline_config": _resolve(repo_root, config.baseline_config_path),
    }
    source_manifest = load_named_source_manifest(paths["named_source_manifest"])
    if source_manifest.manifest_id != MANIFEST_ID:
        raise ValueError("topic controls require the frozen named-source manifest")
    cases = tuple(load_cases(paths["cases"]))
    benchmark_manifest = BenchmarkManifest.model_validate_json(
        paths["benchmark_manifest"].read_text(encoding="utf-8")
    )
    if benchmark_manifest.benchmark_id != EVALUATION_ID:
        raise ValueError("topic-control benchmark ID is not frozen")
    if benchmark_manifest.case_count != EXPECTED_CASE_COUNT:
        raise ValueError("topic-control benchmark must contain exactly six cases")
    if benchmark_manifest.cases_sha256 != sha256_file(paths["cases"]):
        raise ValueError("topic-control cases do not match their manifest")
    pair_manifest = TopicPairManifest.model_validate_json(
        paths["pair_manifest"].read_text(encoding="utf-8")
    )
    by_id = {case.id: case for case in cases}
    paired_ids = [case_id for pair in pair_manifest.pairs for case_id in pair.case_ids]
    if set(paired_ids) != set(by_id):
        raise ValueError("pair manifest must cover every topic-control case exactly once")
    for pair in pair_manifest.pairs:
        left, right = (by_id[case_id] for case_id in pair.case_ids)
        if left.provenance.lineage_group != pair.pair_id:
            raise ValueError("left topic-control case has wrong pair lineage")
        if right.provenance.lineage_group != pair.pair_id:
            raise ValueError("right topic-control case has wrong pair lineage")
        if "topic_swap" not in left.adversarial_features:
            raise ValueError("left topic-control case is missing topic_swap tag")
        if "topic_swap" not in right.adversarial_features:
            raise ValueError("right topic-control case is missing topic_swap tag")
        controlled = (
            "task_family",
            "output_format",
            "objective",
            "constraints",
        )
        for field_name in controlled:
            if getattr(left.input, field_name) != getattr(right.input, field_name):
                raise ValueError(f"topic pair {pair.pair_id} changes {field_name}")
        left_expectations = [item.id for item in left.expected.required_facts]
        right_expectations = [item.id for item in right.expected.required_facts]
        if left_expectations != right_expectations:
            raise ValueError(f"topic pair {pair.pair_id} changes required-fact structure")
    baseline_config = load_config(paths["baseline_config"])
    if baseline_config.candidate_id != config.house_control_candidate_id:
        raise ValueError("house-control candidate ID does not match baseline config")
    if baseline_config.strategy != "profile" or baseline_config.retrieval_examples_path:
        raise ValueError("topic controls require the source-text-free profile baseline")
    if baseline_config.decoding.temperature != 0:
        raise ValueError("topic controls require temperature-zero decoding")
    return TopicControlInputs(
        config=config,
        source_manifest=source_manifest,
        cases=cases,
        benchmark_manifest=benchmark_manifest,
        pair_manifest=pair_manifest,
        baseline_config=baseline_config,
        input_file_hashes={
            **{name: sha256_file(path) for name, path in paths.items()},
            "run_config": sha256_file(config_path),
        },
    )


def plan_topic_control_candidates(inputs: TopicControlInputs) -> list[CandidateSpec]:
    candidates = [
        CandidateSpec(
            candidate_id=inputs.config.house_control_candidate_id,
            person=None,
            profile=None,
        )
    ]
    for entry in inputs.source_manifest.people:
        candidates.append(
            CandidateSpec(
                candidate_id=f"profile-topic-control-{entry.profile.profile_id}",
                person=entry.person,
                profile=entry.profile,
            )
        )
    if len(candidates) != EXPECTED_CANDIDATE_COUNT:
        raise ValueError("topic controls require one house control and eleven profiles")
    return candidates


def run_topic_controls(
    *,
    config_path: Path,
    output_root: Path,
    code_revision: str,
    model_identity: LocalModelIdentity | None = None,
    available_disk_bytes: int | None = None,
    client: GenerationClient | None = None,
    started_at: str | None = None,
) -> Path:
    """Run the 12-by-6 paired topic-control matrix and preserve raw evidence."""

    inputs = load_topic_control_inputs(config_path)
    run_dir = output_root / EVALUATION_ID
    if run_dir.exists():
        raise ValueError(f"raw run directory already exists: {run_dir}")
    if not code_revision.strip():
        raise ValueError("code revision must be non-empty")
    identity = model_identity or fetch_local_model_identity(inputs.baseline_config)
    validate_identity_matches_config(inputs.baseline_config, identity)
    disk_bytes = (
        available_disk_bytes
        if available_disk_bytes is not None
        else shutil.disk_usage(config_path.resolve()).free
    )
    resources = validate_local_resources(
        inputs.baseline_config, identity, available_disk_bytes=disk_bytes
    )
    candidates = plan_topic_control_candidates(inputs)
    route_ids = {
        route.source_id for entry in inputs.source_manifest.people for route in entry.source_routes
    }
    active_client = client or OllamaClient(inputs.baseline_config)
    generations: list[Generation] = []
    scores: list[CaseScore] = []
    start_time = _timestamp(started_at)
    for candidate in candidates:
        for case in inputs.cases:
            prompt = (
                build_house_prompt(case, inputs.baseline_config)
                if candidate.profile is None
                else build_descriptive_prompt(case, candidate.profile)
            )
            assert_prompt_policy(prompt, spec=candidate, route_ids=route_ids)
            start = time.perf_counter()
            output, metrics = active_client.generate(prompt)
            latency_ms = (time.perf_counter() - start) * 1000
            generation = Generation(
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
            generations.append(generation)
            scores.append(score_output_v1_1(case, output, candidate_id=candidate.candidate_id))
    if len(generations) != EXPECTED_GENERATION_CALLS:
        raise AssertionError("topic-control runner did not make exactly 72 calls")
    output_payload = serialize_jsonl(generations)
    score_payload = serialize_jsonl(scores)
    run_dir.mkdir(parents=True)
    atomic_write(run_dir / "outputs.jsonl", output_payload)
    atomic_write(run_dir / "scores.jsonl", score_payload)
    atomic_write_json(
        run_dir / "summary.json",
        {
            "evaluation_id": EVALUATION_ID,
            "generation_call_count": EXPECTED_GENERATION_CALLS,
            "candidate_count": EXPECTED_CANDIDATE_COUNT,
            "case_count": EXPECTED_CASE_COUNT,
            "topic_pair_count": 3,
            "purpose": inputs.config.purpose,
            "settled_cost_usd": 0,
        },
    )
    atomic_write_json(
        run_dir / "run-manifest.json",
        {
            "version": 1,
            "evaluation_id": EVALUATION_ID,
            "scorer_version": SCORER_VERSION,
            "code_revision": code_revision,
            "started_at": start_time,
            "completed_at": _timestamp(),
            "candidate_order": [item.candidate_id for item in candidates],
            "case_order": [case.id for case in inputs.cases],
            "pair_order": [pair.model_dump(mode="json") for pair in inputs.pair_manifest.pairs],
            "generation_call_count": EXPECTED_GENERATION_CALLS,
            "model_identity": identity.model_dump(mode="json"),
            "resource_validation": resources,
            "input_file_hashes": inputs.input_file_hashes,
            "retrieval_enabled": False,
            "no_third_party_text_in_prompts": True,
            "settled_cost_usd": 0,
            "artifact_hashes": {
                "outputs_jsonl": sha256(output_payload).hexdigest(),
                "scores_jsonl": sha256(score_payload).hexdigest(),
                "summary_json": sha256_file(run_dir / "summary.json"),
            },
        },
    )
    return run_dir


def _candidate_summary(
    candidate: CandidateSpec,
    scores: list[CaseScore],
    generations: list[Generation],
    pairs: tuple[TopicPair, TopicPair, TopicPair],
) -> dict[str, Any]:
    selected_scores = [item for item in scores if item.candidate_id == candidate.candidate_id]
    selected_generations = [
        item for item in generations if item.candidate_id == candidate.candidate_id
    ]
    by_case = {item.case_id: item for item in selected_scores}
    pair_diagnostics = []
    for pair in pairs:
        left, right = (by_case[case_id] for case_id in pair.case_ids)
        pair_diagnostics.append(
            {
                "pair_id": pair.pair_id,
                "case_ids": list(pair.case_ids),
                "signed_score_difference": round(
                    right.development_score - left.development_score, 4
                ),
                "absolute_score_difference": round(
                    abs(right.development_score - left.development_score), 4
                ),
                "hard_gate_agreement": left.passes_hard_gates == right.passes_hard_gates,
            }
        )
    errors: dict[str, int] = {}
    for score in selected_scores:
        for error in score.errors:
            errors[error] = errors.get(error, 0) + 1
    return {
        "candidate_id": candidate.candidate_id,
        "person": candidate.person,
        "profile_id": candidate.profile.profile_id if candidate.profile else None,
        "role": "house_control" if candidate.profile is None else "descriptive_profile",
        "case_count": len(selected_scores),
        "mean_development_score": round(
            statistics.fmean(item.development_score for item in selected_scores), 4
        ),
        "hard_gate_pass_rate": round(
            sum(item.passes_hard_gates for item in selected_scores) / len(selected_scores),
            4,
        ),
        "mean_absolute_topic_pair_score_difference": round(
            statistics.fmean(item["absolute_score_difference"] for item in pair_diagnostics),
            4,
        ),
        "hard_gate_disagreement_pair_count": sum(
            not item["hard_gate_agreement"] for item in pair_diagnostics
        ),
        "pair_diagnostics": pair_diagnostics,
        "error_counts": dict(sorted(errors.items())),
        "mean_latency_ms": round(
            statistics.fmean(item.latency_ms for item in selected_generations), 4
        ),
        "prompt_tokens": sum(item.prompt_tokens or 0 for item in selected_generations),
        "output_tokens": sum(item.output_tokens or 0 for item in selected_generations),
    }


def publish_topic_control_results(
    *,
    config_path: Path,
    run_dir: Path,
    results_path: Path,
    case_results_path: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Verify raw evidence and publish source-text-free topic-control summaries."""

    if results_path.exists() or case_results_path.exists():
        raise ValueError("committed topic-control results already exist")
    inputs = load_topic_control_inputs(config_path)
    candidates = plan_topic_control_candidates(inputs)
    manifest: dict[str, Any] = json.loads(
        (run_dir / "run-manifest.json").read_text(encoding="utf-8")
    )
    expected_values = {
        "version": 1,
        "evaluation_id": EVALUATION_ID,
        "scorer_version": SCORER_VERSION,
        "candidate_order": [item.candidate_id for item in candidates],
        "case_order": [case.id for case in inputs.cases],
        "pair_order": [pair.model_dump(mode="json") for pair in inputs.pair_manifest.pairs],
        "generation_call_count": EXPECTED_GENERATION_CALLS,
        "input_file_hashes": inputs.input_file_hashes,
        "retrieval_enabled": False,
        "no_third_party_text_in_prompts": True,
        "settled_cost_usd": 0,
    }
    for field_name, expected in expected_values.items():
        if manifest.get(field_name) != expected:
            raise ValueError(f"run manifest field {field_name} drifted")
    model_identity = LocalModelIdentity.model_validate(manifest.get("model_identity"))
    validate_identity_matches_config(inputs.baseline_config, model_identity)
    _timestamp(str(manifest.get("started_at", "")))
    _timestamp(str(manifest.get("completed_at", "")))
    if not str(manifest.get("code_revision", "")).strip():
        raise ValueError("run manifest code revision is missing")
    outputs_bytes = (run_dir / "outputs.jsonl").read_bytes()
    scores_bytes = (run_dir / "scores.jsonl").read_bytes()
    actual_hashes = {
        "outputs_jsonl": sha256(outputs_bytes).hexdigest(),
        "scores_jsonl": sha256(scores_bytes).hexdigest(),
        "summary_json": sha256_file(run_dir / "summary.json"),
    }
    if manifest.get("artifact_hashes") != actual_hashes:
        raise ValueError("raw topic-control artifact hash mismatch")
    generations = load_jsonl(run_dir / "outputs.jsonl", Generation)
    scores = load_jsonl(run_dir / "scores.jsonl", CaseScore)
    expected_order = [
        (candidate.candidate_id, case.id) for candidate in candidates for case in inputs.cases
    ]
    if [(item.candidate_id, item.case_id) for item in generations] != expected_order:
        raise ValueError("raw topic-control generation order drifted")
    if [(item.candidate_id, item.case_id) for item in scores] != expected_order:
        raise ValueError("raw topic-control score order drifted")
    case_by_id = {case.id: case for case in inputs.cases}
    recomputed = [
        score_output_v1_1(
            case_by_id[generation.case_id],
            generation.output,
            candidate_id=generation.candidate_id,
        )
        for generation in generations
    ]
    if recomputed != scores:
        raise ValueError("saved topic-control scores do not match v1.1 rescoring")
    case_results = [
        {
            "candidate_id": score.candidate_id,
            "case_id": score.case_id,
            "pair_id": case_by_id[score.case_id].provenance.lineage_group,
            "topic": case_by_id[score.case_id].provenance.topic,
            "development_score": score.development_score,
            "passes_hard_gates": score.passes_hard_gates,
            "errors": list(score.errors),
            "output_sha256": score.output_sha256,
        }
        for score in scores
    ]
    summaries = [
        _candidate_summary(candidate, scores, generations, inputs.pair_manifest.pairs)
        for candidate in candidates
    ]
    result = {
        "version": 1,
        "evaluation_id": EVALUATION_ID,
        "status": "completed_exploratory_coverage_only",
        "advancement_decision": "none_coverage_only",
        "generated_at": _timestamp(generated_at),
        "code_revision": manifest["code_revision"],
        "scorer_version": SCORER_VERSION,
        "generation_call_count": EXPECTED_GENERATION_CALLS,
        "topic_pair_count": 3,
        "topic_swap_posture": "completed_three_project_authored_paired_swaps",
        "leave_topic_out_posture": inputs.pair_manifest.leave_topic_out_posture,
        "leave_time_out_posture": inputs.pair_manifest.leave_time_out_posture,
        "content_control": inputs.pair_manifest.content_control,
        "retrieval_enabled": False,
        "no_third_party_text_in_prompts": True,
        "settled_cost_usd": 0,
        "input_file_hashes": inputs.input_file_hashes,
        "raw_artifact_hashes": actual_hashes,
        "model_identity": model_identity.model_dump(mode="json"),
        "candidates": summaries,
        "limitations": [
            "Three pairs are too small for confirmatory inference or profile selection.",
            "Deterministic lexical scores do not isolate semantic profile quality.",
            "No dated corpus is fit or retrieved, so this run cannot establish "
            "leave-time-out behavior for a future corpus-trained profile.",
        ],
    }
    atomic_write_json(case_results_path, case_results)
    atomic_write_json(results_path, result)
    return result
