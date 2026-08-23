"""Integrity checks for the common architecture frontier and hypothesis registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.jsonl import atomic_write_json, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceArtifact(StrictModel):
    path: NonEmpty
    sha256: Sha256


class FrontierCandidate(StrictModel):
    candidate_id: NonEmpty
    source_artifact: NonEmpty
    architecture_family: NonEmpty
    model_runtime: NonEmpty
    trained: bool
    external_provider: bool
    case_count: Literal[24]
    mean_development_score: float = Field(ge=0, le=100)
    hard_gate_pass_rate: float = Field(ge=0, le=1)
    latency_mean_ms: float = Field(ge=0)
    settled_cost_usd: float = Field(ge=0)
    output_audit_status: Literal["not_run", "pass", "fail"]
    evidence_disposition: NonEmpty
    frontier_role: NonEmpty
    finalist_eligible: bool

    @model_validator(mode="after")
    def validate_finalist_gate(self) -> Self:
        if self.finalist_eligible and (
            self.hard_gate_pass_rate != 1 or self.output_audit_status == "fail"
        ):
            raise ValueError("finalist eligibility requires all hard gates and no failed audit")
        return self


class SearchState(StrictModel):
    local_directional_leader: NonEmpty
    external_score_ceiling: NonEmpty
    finalist_ready_count: int = Field(ge=0)
    plateau_status: Literal[
        "not_satisfied_leader_fails_hard_gates_and_high_value_hypotheses_remain",
        "not_satisfied_leader_fails_hard_gates_and_safe_affordable_hypotheses_exhausted",
        "satisfied",
    ]
    decision: NonEmpty


class ArchitectureFrontier(StrictModel):
    version: Literal[1, 2, 3]
    frontier_id: Literal[
        "goodprose-b1-common-architecture-frontier-v1",
        "goodprose-b1-common-architecture-frontier-v2",
        "goodprose-b1-common-architecture-frontier-v3",
    ]
    generated_at: NonEmpty
    benchmark_id: Literal["goodprose-b1-v1"]
    evaluation_id: Literal["goodprose-b1-v1.1"]
    scorer_version: Literal["goodprose-deterministic-v1.1"]
    source_artifacts: tuple[SourceArtifact, ...] = Field(min_length=1)
    candidates: tuple[FrontierCandidate, ...] = Field(min_length=1)
    excluded_evidence: tuple[NonEmpty, ...]
    search_state: SearchState

    @model_validator(mode="after")
    def validate_frontier(self) -> Self:
        expected_id = f"goodprose-b1-common-architecture-frontier-v{self.version}"
        if self.frontier_id != expected_id:
            raise ValueError("frontier version and ID drifted")
        source_paths = [artifact.path for artifact in self.source_artifacts]
        candidate_ids = [candidate.candidate_id for candidate in self.candidates]
        if len(source_paths) != len(set(source_paths)):
            raise ValueError("frontier source paths must be unique")
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("frontier candidate IDs must be unique")
        if not all(candidate.source_artifact in source_paths for candidate in self.candidates):
            raise ValueError("every frontier candidate must bind a declared source artifact")
        eligible_count = sum(candidate.finalist_eligible for candidate in self.candidates)
        if self.search_state.finalist_ready_count != eligible_count:
            raise ValueError("frontier finalist-ready count does not match candidate rows")
        if self.search_state.local_directional_leader not in candidate_ids:
            raise ValueError("local directional leader is absent from candidate rows")
        if self.search_state.external_score_ceiling not in candidate_ids:
            raise ValueError("external score ceiling is absent from candidate rows")
        return self


class HypothesisEntry(StrictModel):
    hypothesis_id: NonEmpty
    category: NonEmpty
    status: Literal[
        "completed_supported",
        "completed_rejected",
        "completed_partial",
        "planned_high_value",
        "planned_contingent",
        "blocked_external",
        "not_justified",
    ]
    major_factor: NonEmpty
    evidence: NonEmpty
    next_action: NonEmpty


class HypothesisRegistry(StrictModel):
    version: Literal[1]
    registry_id: Literal["executive-writing-hypotheses-v1"]
    updated_at: NonEmpty
    source_frontier_sha256: Sha256
    hypotheses: tuple[HypothesisEntry, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_hypotheses(self) -> Self:
        hypothesis_ids = [item.hypothesis_id for item in self.hypotheses]
        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            raise ValueError("hypothesis IDs must be unique")
        has_planned = any(item.status == "planned_high_value" for item in self.hypotheses)
        has_external_blocker = any(item.status == "blocked_external" for item in self.hypotheses)
        if not has_planned and not has_external_blocker:
            raise ValueError(
                "a search without a planned hypothesis must retain an external blocker"
            )
        return self


def publish_h11_frontier(
    *,
    previous_frontier_path: Path,
    analysis_path: Path,
    audit_path: Path,
    output_path: Path,
    repo_root: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Append the frozen h11 result and close the safe automated search frontier."""

    previous = ArchitectureFrontier.model_validate_json(
        previous_frontier_path.read_text(encoding="utf-8")
    )
    if previous.version != 2:
        raise ValueError("h11 frontier publication requires the frozen v2 frontier")
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    candidate = analysis.get("candidate", {})
    candidate_id = "qwen2.5-7b-retrieval-ledger-draft-h11-v1"
    if (
        analysis.get("status") != "completed_reject"
        or candidate.get("candidate_id") != candidate_id
    ):
        raise ValueError("h11 analysis must contain the completed rejected candidate")
    if audit.get("candidate_id") != candidate_id:
        raise ValueError("h11 audit candidate does not match the analysis")
    if audit.get("outputs_sha256") != candidate.get("source_artifact_hashes", {}).get(
        "outputs_jsonl"
    ):
        raise ValueError("h11 audit and analysis do not bind the same outputs")
    if audit.get("decision", {}).get("candidate_disposition") != (
        "reject_for_artifact_contamination_or_source_grounding_risk"
    ):
        raise ValueError("h11 audit must record the frozen rejection")

    def source_artifact(path: Path) -> dict[str, str]:
        return {
            "path": path.resolve().relative_to(repo_root.resolve()).as_posix(),
            "sha256": sha256_file(path),
        }

    payload = previous.model_dump(mode="json")
    payload["version"] = 3
    payload["frontier_id"] = "goodprose-b1-common-architecture-frontier-v3"
    payload["generated_at"] = generated_at
    payload["source_artifacts"].extend(
        [source_artifact(analysis_path), source_artifact(audit_path)]
    )
    payload["candidates"].append(
        {
            "candidate_id": candidate_id,
            "source_artifact": source_artifact(analysis_path)["path"],
            "architecture_family": "retrieval_compact_ledger_draft_larger_local_base",
            "model_runtime": "ollama-qwen2.5-7b-instruct-q4_k_m",
            "trained": False,
            "external_provider": False,
            "case_count": 24,
            "mean_development_score": candidate["mean_development_score"],
            "hard_gate_pass_rate": candidate["hard_gate_pass_rate"],
            "latency_mean_ms": candidate["latency_ms"]["mean"],
            "settled_cost_usd": candidate["settled_cost_usd"],
            "output_audit_status": "fail",
            "evidence_disposition": "rejected_for_hard_gate_and_source_grounding_failures",
            "frontier_role": "larger_local_model_negative_evidence",
            "finalist_eligible": False,
        }
    )
    payload["search_state"] = {
        "local_directional_leader": previous.search_state.local_directional_leader,
        "external_score_ceiling": previous.search_state.external_score_ceiling,
        "finalist_ready_count": 0,
        "plateau_status": (
            "not_satisfied_leader_fails_hard_gates_and_safe_affordable_hypotheses_exhausted"
        ),
        "decision": (
            "No candidate is finalist-ready. The frozen h11 larger-local-model probe "
            "improved mean score but regressed hard gates and failed the full-output audit. "
            "All currently identified safe, affordable, high-value automated hypotheses are "
            "exhausted; do not fabricate finalists or call the plateau successful."
        ),
    }
    validated = ArchitectureFrontier.model_validate(payload)
    atomic_write_json(output_path, validated.model_dump(mode="json"))
    return validated.model_dump(mode="json")


def validate_architecture_frontier(
    *, frontier_path: Path, hypotheses_path: Path, repo_root: Path
) -> dict[str, int | str]:
    """Validate schemas, source hashes, cross-links, and finalist accounting."""

    frontier = ArchitectureFrontier.model_validate_json(frontier_path.read_text(encoding="utf-8"))
    hypotheses = HypothesisRegistry.model_validate_json(hypotheses_path.read_text(encoding="utf-8"))
    for artifact in frontier.source_artifacts:
        if sha256_file(repo_root / artifact.path) != artifact.sha256:
            raise ValueError(f"frontier source artifact hash mismatch: {artifact.path}")
    if hypotheses.source_frontier_sha256 != sha256_file(frontier_path):
        raise ValueError("hypothesis registry does not bind the architecture frontier")
    return {
        "frontier_id": frontier.frontier_id,
        "candidate_count": len(frontier.candidates),
        "finalist_ready_count": frontier.search_state.finalist_ready_count,
        "hypothesis_count": len(hypotheses.hypotheses),
        "planned_high_value_count": sum(
            item.status == "planned_high_value" for item in hypotheses.hypotheses
        ),
    }
