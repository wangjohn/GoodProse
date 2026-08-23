"""Integrity checks for the common architecture frontier and hypothesis registry."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.jsonl import sha256_file

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
        "satisfied",
    ]
    decision: NonEmpty


class ArchitectureFrontier(StrictModel):
    version: Literal[1, 2]
    frontier_id: Literal[
        "goodprose-b1-common-architecture-frontier-v1",
        "goodprose-b1-common-architecture-frontier-v2",
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
        if not any(item.status == "planned_high_value" for item in self.hypotheses):
            raise ValueError("an unsaturated search must retain a planned high-value hypothesis")
        return self


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
