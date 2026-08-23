from __future__ import annotations

import json
from pathlib import Path

import pytest

from goodprose.executive_writing.contract_audit import (
    ContractCompletionAudit,
    load_and_validate_contract_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = (
    REPO_ROOT
    / "programs"
    / "executive-writing"
    / "experiments"
    / "contract-completion-audit-v1.json"
)


def test_committed_contract_audit_validates_all_evidence_and_hashes() -> None:
    audit = load_and_validate_contract_audit(AUDIT_PATH, repo_root=REPO_ROOT)

    assert audit.goal_complete is False
    assert len(audit.deliverables) == 28
    assert len(audit.stopping_conditions) == 18
    assert audit.safe_autonomous_work_remaining == ()
    assert {item.status for item in audit.stopping_conditions} >= {
        "satisfied",
        "failed_gate",
        "blocked_external",
        "partial",
    }


def test_contract_audit_rejects_duplicate_or_missing_requirements() -> None:
    payload = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    payload["deliverables"][1]["id"] = payload["deliverables"][0]["id"]

    with pytest.raises(ValueError, match="IDs must be unique"):
        ContractCompletionAudit.model_validate(payload)


def test_contract_audit_detects_evidence_hash_drift(tmp_path: Path) -> None:
    payload = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    payload["evidence_hashes"] = {"evidence.txt": "0" * 64}
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "docs/goals").mkdir(parents=True)
    (tmp_path / "docs/goals/executive-writing-model.md").write_text("contract", encoding="utf-8")
    for item in (*payload["deliverables"], *payload["stopping_conditions"]):
        item["evidence"] = ["evidence.txt"]
    audit_path.write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "evidence.txt").write_text("not zero hash", encoding="utf-8")

    with pytest.raises(ValueError, match="hash drifted"):
        load_and_validate_contract_audit(audit_path, repo_root=tmp_path)


def test_latest_results_v3_binds_the_contract_audit() -> None:
    latest_path = (
        REPO_ROOT / "programs" / "executive-writing" / "experiments" / "latest-results-v3.json"
    )
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    audit = load_and_validate_contract_audit(AUDIT_PATH, repo_root=REPO_ROOT)

    assert latest["version"] == 3
    assert latest["production_recommendation"] == "no_deployment"
    assert latest["contract_audit"]["deliverables_satisfied"] == sum(
        item.status == "satisfied" for item in audit.deliverables
    )
    assert latest["contract_audit"]["stopping_conditions_satisfied"] == sum(
        item.status == "satisfied" for item in audit.stopping_conditions
    )
    assert latest["contract_audit"]["safe_autonomous_work_remaining_count"] == 0
