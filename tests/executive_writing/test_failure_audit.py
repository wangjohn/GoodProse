from __future__ import annotations

import json
from pathlib import Path

import pytest

from goodprose.executive_writing.baseline import Generation
from goodprose.executive_writing.benchmark import load_cases
from goodprose.executive_writing.failure_audit import audit_mlx_b1_failures
from goodprose.jsonl import (
    atomic_write_json,
    serialize_jsonl,
    sha256_bytes,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
B1_CASES = REPO_ROOT / "evals/executive-writing/goodprose-b1-v1/cases.jsonl"


def _generation(case_id: str, candidate_id: str, output: str) -> Generation:
    return Generation(
        case_id=case_id,
        candidate_id=candidate_id,
        prompt_sha256=sha256_bytes(f"prompt:{case_id}".encode()),
        output=output,
        output_sha256=sha256_bytes(output.encode()),
        latency_ms=1.0,
    )


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    run_dir = tmp_path / "run"
    candidates = {
        "base-profile": {},
        "tuned-profile": {
            "b1-001-migration-email": "Northstar migration update",
            "b1-002-pricing-pilot-email": "Again\nAgain\nAgain\nAgain",
        },
        "base-ledger": {},
        "tuned-ledger": {
            "b1-003-incident-email": "Northstar incident update",
        },
    }
    cases = load_cases(B1_CASES)
    hashes = {}
    for candidate_id, overrides in candidates.items():
        output_path = run_dir / candidate_id / "outputs.jsonl"
        output_path.parent.mkdir(parents=True)
        generations = [
            _generation(case.id, candidate_id, overrides.get(case.id, "Clean output"))
            for case in cases
        ]
        output_path.write_bytes(serialize_jsonl(generations))
        hashes[candidate_id] = sha256_file(output_path)

    atomic_write_json(
        run_dir / "run-manifest.json",
        {
            "status": "completed",
            "experiment_id": "synthetic-eval",
            "run_id": "synthetic-run",
            "candidate_artifacts": {
                candidate_id: {"outputs_sha256": output_hash}
                for candidate_id, output_hash in hashes.items()
            },
        },
    )
    config_path = tmp_path / "audit-config.json"
    atomic_write_json(
        config_path,
        {
            "version": 1,
            "audit_id": "synthetic-audit",
            "classification": "post_run_exploratory_diagnostic",
            "source_experiment_id": "synthetic-eval",
            "source_run_id": "synthetic-run",
            "benchmark_cases_sha256": sha256_file(B1_CASES),
            "source_records_sha256": "0" * 64,
            "candidate_output_sha256": hashes,
            "comparisons": [
                {
                    "strategy": "profile",
                    "baseline_id": "base-profile",
                    "candidate_id": "tuned-profile",
                },
                {
                    "strategy": "ledger_draft",
                    "baseline_id": "base-ledger",
                    "candidate_id": "tuned-ledger",
                },
            ],
            "scenario_labels": ["Northstar"],
            "exact_line_repetition_threshold": 4,
            "ngram_words": 4,
            "ngram_repetition_threshold": 8,
        },
    )
    return run_dir, config_path


def test_failure_audit_detects_introduced_labels_and_repetition(tmp_path: Path) -> None:
    run_dir, config_path = _fixture(tmp_path)
    output_path = tmp_path / "audit.json"

    result = audit_mlx_b1_failures(
        config_path=config_path,
        run_dir=run_dir,
        cases_path=B1_CASES,
        output_path=output_path,
        generated_at="2026-08-23T19:30:00Z",
    )

    tuned = result["candidates"]["tuned-profile"]
    assert tuned["introduced_training_label_case_count"] == 1
    assert tuned["severe_repetition_case_count"] == 1
    assert result["comparisons"][0]["introduced_training_label_case_difference"] == 1
    assert json.loads(output_path.read_text()) == result


def test_failure_audit_rejects_output_hash_drift(tmp_path: Path) -> None:
    run_dir, config_path = _fixture(tmp_path)
    outputs_path = run_dir / "tuned-profile/outputs.jsonl"
    outputs_path.write_text(outputs_path.read_text() + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="output bytes do not match frozen hash"):
        audit_mlx_b1_failures(
            config_path=config_path,
            run_dir=run_dir,
            cases_path=B1_CASES,
            output_path=tmp_path / "audit.json",
            generated_at="2026-08-23T19:30:00Z",
        )
