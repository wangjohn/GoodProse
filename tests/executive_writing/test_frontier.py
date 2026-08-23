from __future__ import annotations

import json
from pathlib import Path

import pytest

from goodprose.executive_writing.frontier import validate_architecture_frontier
from goodprose.jsonl import atomic_write_json, sha256_file


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    source_path = tmp_path / "source.json"
    atomic_write_json(source_path, {"candidate_id": "candidate-a", "score": 80})
    frontier_path = tmp_path / "frontier.json"
    atomic_write_json(
        frontier_path,
        {
            "version": 1,
            "frontier_id": "goodprose-b1-common-architecture-frontier-v1",
            "generated_at": "2026-08-23T21:20:00Z",
            "benchmark_id": "goodprose-b1-v1",
            "evaluation_id": "goodprose-b1-v1.1",
            "scorer_version": "goodprose-deterministic-v1.1",
            "source_artifacts": [{"path": "source.json", "sha256": sha256_file(source_path)}],
            "candidates": [
                {
                    "candidate_id": "candidate-a",
                    "source_artifact": "source.json",
                    "architecture_family": "synthetic",
                    "model_runtime": "synthetic-runtime",
                    "trained": False,
                    "external_provider": False,
                    "case_count": 24,
                    "mean_development_score": 80,
                    "hard_gate_pass_rate": 0.5,
                    "latency_mean_ms": 10,
                    "settled_cost_usd": 0,
                    "output_audit_status": "not_run",
                    "evidence_disposition": "synthetic baseline",
                    "frontier_role": "local leader",
                    "finalist_eligible": False,
                }
            ],
            "excluded_evidence": ["synthetic exclusion"],
            "search_state": {
                "local_directional_leader": "candidate-a",
                "external_score_ceiling": "candidate-a",
                "finalist_ready_count": 0,
                "plateau_status": (
                    "not_satisfied_leader_fails_hard_gates_and_high_value_hypotheses_remain"
                ),
                "decision": "continue one high-value hypothesis",
            },
        },
    )
    hypotheses_path = tmp_path / "hypotheses.json"
    atomic_write_json(
        hypotheses_path,
        {
            "version": 1,
            "registry_id": "executive-writing-hypotheses-v1",
            "updated_at": "2026-08-23T21:20:00Z",
            "source_frontier_sha256": sha256_file(frontier_path),
            "hypotheses": [
                {
                    "hypothesis_id": "h01",
                    "category": "synthetic",
                    "status": "planned_high_value",
                    "major_factor": "synthetic factor",
                    "evidence": "synthetic evidence",
                    "next_action": "run synthetic hypothesis",
                }
            ],
        },
    )
    return frontier_path, hypotheses_path, source_path


def test_frontier_validator_checks_sources_cross_links_and_counts(tmp_path: Path) -> None:
    frontier_path, hypotheses_path, _ = _fixture(tmp_path)

    result = validate_architecture_frontier(
        frontier_path=frontier_path,
        hypotheses_path=hypotheses_path,
        repo_root=tmp_path,
    )

    assert result == {
        "frontier_id": "goodprose-b1-common-architecture-frontier-v1",
        "candidate_count": 1,
        "finalist_ready_count": 0,
        "hypothesis_count": 1,
        "planned_high_value_count": 1,
    }


def test_frontier_validator_rejects_source_drift(tmp_path: Path) -> None:
    frontier_path, hypotheses_path, source_path = _fixture(tmp_path)
    source_path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="frontier source artifact hash mismatch"):
        validate_architecture_frontier(
            frontier_path=frontier_path,
            hypotheses_path=hypotheses_path,
            repo_root=tmp_path,
        )


def test_frontier_validator_rejects_version_id_drift(tmp_path: Path) -> None:
    frontier_path, hypotheses_path, _ = _fixture(tmp_path)
    frontier = json.loads(frontier_path.read_text())
    frontier["version"] = 2
    atomic_write_json(frontier_path, frontier)

    with pytest.raises(ValueError, match="frontier version and ID drifted"):
        validate_architecture_frontier(
            frontier_path=frontier_path,
            hypotheses_path=hypotheses_path,
            repo_root=tmp_path,
        )
