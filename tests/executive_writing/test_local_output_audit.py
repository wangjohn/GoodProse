from __future__ import annotations

import json
from pathlib import Path

import pytest

from goodprose.executive_writing.baseline import Generation
from goodprose.executive_writing.benchmark import load_cases
from goodprose.executive_writing.local_output_audit import audit_local_b1_outputs
from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    serialize_jsonl,
    sha256_bytes,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
B1_CASES = REPO_ROOT / "evals/executive-writing/goodprose-b1-v1/cases.jsonl"


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path]:
    cases = load_cases(B1_CASES)
    candidate_id = "synthetic-local-candidate"
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outputs = []
    for index, case in enumerate(cases):
        output = "Source-backed finished artifact."
        if index == 0:
            output = "Finished artifact. The compact ledger is a checklist."
        elif index == 1:
            output = "Finished artifact with [New Owner]."
        outputs.append(
            Generation(
                case_id=case.id,
                candidate_id=candidate_id,
                prompt_sha256="0" * 64,
                output=output,
                output_sha256=sha256_bytes(output.encode()),
                latency_ms=1,
            )
        )
    outputs_path = run_dir / "outputs.jsonl"
    atomic_write(outputs_path, serialize_jsonl(outputs))
    manifest_path = run_dir / "run-manifest.json"
    atomic_write_json(
        manifest_path,
        {
            "candidate_id": candidate_id,
            "artifact_hashes": {"outputs_jsonl": sha256_file(outputs_path)},
        },
    )
    case_results_path = tmp_path / "case-results.jsonl"
    case_results_path.write_text('{"case_id":"synthetic"}\n', encoding="utf-8")
    analysis_path = tmp_path / "analysis.json"
    atomic_write_json(
        analysis_path,
        {
            "status": "completed_reject",
            "case_results_sha256": sha256_file(case_results_path),
            "candidate": {
                "candidate_id": candidate_id,
                "source_artifact_hashes": {"outputs_jsonl": sha256_file(outputs_path)},
            },
            "preregistered_gate_result": {"all_guardrails_pass": False},
        },
    )
    config_path = tmp_path / "audit-config.json"
    atomic_write_json(
        config_path,
        {
            "version": 1,
            "audit_id": "synthetic-local-output-audit",
            "classification": "post_run_full_output_source_grounding_audit",
            "candidate_id": candidate_id,
            "source_run_manifest_sha256": sha256_file(manifest_path),
            "outputs_sha256": sha256_file(outputs_path),
            "benchmark_cases_sha256": sha256_file(B1_CASES),
            "source_analysis_sha256": sha256_file(analysis_path),
            "source_case_results_sha256": sha256_file(case_results_path),
            "artifact_substrings": ["The compact ledger is a checklist"],
            "manual_findings": [
                {
                    "case_id": cases[2].id,
                    "category": "material_source_expansion_risk",
                    "rationale": "Synthetic unsupported follow-up.",
                }
            ],
        },
    )
    return run_dir, analysis_path, case_results_path, config_path, outputs_path


def test_local_output_audit_binds_and_records_compact_findings(tmp_path: Path) -> None:
    run_dir, analysis_path, case_results_path, config_path, _ = _fixture(tmp_path)
    output_path = tmp_path / "audit.json"

    result = audit_local_b1_outputs(
        config_path=config_path,
        run_dir=run_dir,
        cases_path=B1_CASES,
        source_analysis_path=analysis_path,
        source_case_results_path=case_results_path,
        output_path=output_path,
        generated_at="2026-08-23T22:20:00Z",
    )

    assert result["summary"]["model_prompt_instruction_or_process_commentary_case_count"] == 1
    assert result["summary"]["introduced_non_source_placeholder_case_count"] == 1
    assert result["summary"]["material_source_expansion_risk_case_count"] == 1
    assert result["summary"]["no_audit_flag_case_count"] == 21
    assert all("output" not in finding for finding in result["case_findings"])
    assert json.loads(output_path.read_text()) == result


def test_local_output_audit_rejects_output_drift(tmp_path: Path) -> None:
    run_dir, analysis_path, case_results_path, config_path, outputs_path = _fixture(tmp_path)
    outputs_path.write_text(outputs_path.read_text() + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="local outputs hash"):
        audit_local_b1_outputs(
            config_path=config_path,
            run_dir=run_dir,
            cases_path=B1_CASES,
            source_analysis_path=analysis_path,
            source_case_results_path=case_results_path,
            output_path=tmp_path / "audit.json",
            generated_at="2026-08-23T22:20:00Z",
        )
