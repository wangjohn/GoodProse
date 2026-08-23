from __future__ import annotations

import json
from pathlib import Path

from goodprose.executive_writing.smoke_data import (
    DATASET_ID,
    SmokeRecord,
    SmokeSplit,
    build_smoke_records,
    compile_smoke_dataset,
    contamination_matches,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
B1_CASES = REPO_ROOT / "evals" / "executive-writing" / "goodprose-b1-v1" / "cases.jsonl"


def test_smoke_records_have_isolated_lineage_splits_and_rights() -> None:
    records = build_smoke_records()

    assert {split: len(values) for split, values in records.items()} == {
        SmokeSplit.TRAIN: 32,
        SmokeSplit.VALID: 8,
        SmokeSplit.TEST: 8,
    }
    lineage_splits: dict[str, set[SmokeSplit]] = {}
    for split, values in records.items():
        for record in values:
            assert record.metadata.dataset_id == DATASET_ID
            assert record.metadata.rights_status == "training_permitted_project_owned_smoke"
            assert record.metadata.intended_use == "pipeline_smoke_test_only"
            lineage_splits.setdefault(record.metadata.lineage_group, set()).add(split)
    assert len(lineage_splits) == 12
    assert all(len(splits) == 1 for splits in lineage_splits.values())


def test_compile_smoke_dataset_is_reproducible_and_b1_disjoint(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_manifest = tmp_path / "first-manifest.json"
    second_manifest = tmp_path / "second-manifest.json"

    first = compile_smoke_dataset(
        output_dir=first_dir, manifest_path=first_manifest, b1_cases_path=B1_CASES
    )
    second = compile_smoke_dataset(
        output_dir=second_dir, manifest_path=second_manifest, b1_cases_path=B1_CASES
    )

    assert first == second
    assert first_manifest.read_bytes() == second_manifest.read_bytes()
    assert first["record_count"] == 48
    assert first["contamination_check"]["status"] == "pass"  # type: ignore[index]
    for split in SmokeSplit:
        assert (first_dir / f"{split.value}.jsonl").read_bytes() == (
            second_dir / f"{split.value}.jsonl"
        ).read_bytes()


def test_compiled_jsonl_matches_mlx_chat_shape(tmp_path: Path) -> None:
    compile_smoke_dataset(
        output_dir=tmp_path / "data",
        manifest_path=tmp_path / "manifest.json",
        b1_cases_path=B1_CASES,
    )

    line = (tmp_path / "data" / "train.jsonl").read_text(encoding="utf-8").splitlines()[0]
    value = json.loads(line)
    record = SmokeRecord.model_validate(value)

    assert [message.role for message in record.messages] == ["system", "user", "assistant"]
    assert value["messages"][-1]["content"]
    assert value["metadata"]["corpus"] == "task_pairs"


def test_contamination_matcher_detects_long_shared_span() -> None:
    shared = "one two three four five six seven eight nine ten eleven twelve"

    matches = contamination_matches(
        [f"candidate prefix {shared} candidate suffix"],
        [f"reference prefix {shared} reference suffix"],
        ngram_words=12,
    )

    assert tuple(shared.split()) in matches
