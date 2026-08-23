"""Typed validation for the requirement-by-requirement completion audit."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.jsonl import sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
AuditStatus = Literal[
    "satisfied",
    "partial",
    "conditional_not_triggered",
    "failed_gate",
    "blocked_external",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AuditItem(StrictModel):
    id: NonEmpty
    requirement: NonEmpty
    status: AuditStatus
    evidence: tuple[NonEmpty, ...] = Field(min_length=1)
    note: NonEmpty


class ContractCompletionAudit(StrictModel):
    version: Literal[1]
    audit_id: Literal["executive-writing-contract-completion-audit-v1"]
    generated_at: NonEmpty
    contract_path: Literal["docs/goals/executive-writing-model.md"]
    goal_complete: Literal[False]
    status: Literal["safe_repository_work_complete_external_and_candidate_gates_remain"]
    deliverables: tuple[AuditItem, ...] = Field(min_length=1)
    stopping_conditions: tuple[AuditItem, ...] = Field(min_length=1)
    evidence_hashes: dict[NonEmpty, Sha256]
    unmet_completion_conditions: tuple[NonEmpty, ...] = Field(min_length=1)
    next_external_trigger: NonEmpty
    safe_autonomous_work_remaining: tuple[NonEmpty, ...]
    settled_cost_usd: Literal[0]
    remaining_budget_usd: Literal[100]

    @model_validator(mode="after")
    def unique_complete_matrix(self) -> ContractCompletionAudit:
        for label, items in (
            ("deliverable", self.deliverables),
            ("stopping condition", self.stopping_conditions),
        ):
            ids = [item.id for item in items]
            if len(ids) != len(set(ids)):
                raise ValueError(f"{label} IDs must be unique")
        if len(self.deliverables) != 28:
            raise ValueError("completion audit must enumerate all 28 deliverables")
        if len(self.stopping_conditions) != 18:
            raise ValueError("completion audit must enumerate all 18 stopping conditions")
        if all(item.status == "satisfied" for item in self.stopping_conditions):
            raise ValueError("an incomplete goal must retain at least one unmet stopping condition")
        return self


def load_and_validate_contract_audit(
    audit_path: Path, *, repo_root: Path
) -> ContractCompletionAudit:
    """Validate schema, evidence existence, and every declared evidence hash."""

    audit = ContractCompletionAudit.model_validate_json(audit_path.read_text(encoding="utf-8"))
    contract_path = repo_root / audit.contract_path
    if not contract_path.is_file():
        raise ValueError(f"contract path does not exist: {audit.contract_path}")
    for item in (*audit.deliverables, *audit.stopping_conditions):
        for evidence in item.evidence:
            path = repo_root / evidence
            if not path.exists():
                raise ValueError(f"audit evidence path does not exist: {evidence}")
    for relative_path, expected_hash in audit.evidence_hashes.items():
        path = repo_root / relative_path
        if not path.is_file():
            raise ValueError(f"hashed audit evidence is not a file: {relative_path}")
        if sha256_file(path) != expected_hash:
            raise ValueError(f"audit evidence hash drifted: {relative_path}")
    return audit
