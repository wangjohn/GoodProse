from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from goodprose.dataset import DatasetValidationError, create_snapshot, validate_training_records
from goodprose.jsonl import canonical_json
from goodprose.models import EvalCase, TrainingExample
from goodprose.privacy import scan_jsonl

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text("".join(canonical_json(record) + "\n" for record in records), encoding="utf-8")


def test_validation_rejects_lineage_leakage(
    training_record: dict[str, Any], second_training_record: dict[str, Any]
) -> None:
    second_training_record["provenance"]["lineage_group"] = training_record["provenance"][
        "lineage_group"
    ]
    records = [
        TrainingExample.model_validate(training_record),
        TrainingExample.model_validate(second_training_record),
    ]

    errors = validate_training_records(records, repo_root=REPO_ROOT)

    assert any("crosses training and validation splits" in error for error in errors)


def test_validation_rejects_empty_dataset() -> None:
    errors = validate_training_records([], repo_root=REPO_ROOT)

    assert errors == ["training dataset is empty"]


def test_validation_rejects_eval_lineage_overlap(training_record: dict[str, Any]) -> None:
    record = TrainingExample.model_validate(training_record)
    eval_case = EvalCase.model_validate(
        {
            "version": 1,
            "id": "eval-overlap",
            "split": "dev",
            "input": {
                "source_material": "A held-out source.",
                "channel": "internal_memo",
                "audience": "Executive staff",
                "objective": "Explain a held-out decision.",
                "voice_profile_id": "executive-house-v1",
            },
            "expected": {"required_facts": [], "forbidden_claims": []},
            "provenance": {
                "lineage_group": record.provenance.lineage_group,
                "target_document_ids": [],
                "input_origin": "real_source_material",
            },
        }
    )

    errors = validate_training_records([record], repo_root=REPO_ROOT, eval_cases=[eval_case])

    assert any("appears in training and eval case" in error for error in errors)


def test_snapshot_is_content_addressed_and_reproducible(
    tmp_path: Path,
    training_record: dict[str, Any],
    second_training_record: dict[str, Any],
) -> None:
    source = tmp_path / "training.jsonl"
    _write_jsonl(source, [second_training_record, training_record])
    privacy_report = tmp_path / "privacy.json"
    report = scan_jsonl(source, report_path=privacy_report)
    assert report.is_clean

    first = create_snapshot(
        source,
        tmp_path / "snapshots",
        repo_root=REPO_ROOT,
        privacy_report_path=privacy_report,
        eval_paths=[],
        max_tokens=4096,
    )
    second = create_snapshot(
        source,
        tmp_path / "snapshots",
        repo_root=REPO_ROOT,
        privacy_report_path=privacy_report,
        eval_paths=[],
        max_tokens=4096,
    )

    assert first == second
    manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["record_count"] == 2
    assert manifest["split_counts"] == {"train": 1, "validation": 1}
    lines = (first / "training.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0])["id"] == "example-001"


def test_snapshot_requires_matching_clean_privacy_report(
    tmp_path: Path, training_record: dict[str, Any]
) -> None:
    source = tmp_path / "training.jsonl"
    _write_jsonl(source, [training_record])
    other = tmp_path / "other.jsonl"
    other.write_text('{"id":"other"}\n', encoding="utf-8")
    report_path = tmp_path / "privacy.json"
    scan_jsonl(other, report_path=report_path)

    with pytest.raises(DatasetValidationError, match="does not match"):
        create_snapshot(
            source,
            tmp_path / "snapshots",
            repo_root=REPO_ROOT,
            privacy_report_path=report_path,
            eval_paths=[],
        )
