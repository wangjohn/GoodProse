"""Deterministic tests for the unified three-corpus pilot compiler.

All fixtures are unmistakably synthetic token soup; none is a real pilot
dataset. Smaller count expectations are only ever injected into these pure
compiler test functions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pydantic
import pytest

from goodprose.executive_writing.__main__ import main
from goodprose.executive_writing.benchmark import load_cases
from goodprose.executive_writing.smoke_data import contamination_matches
from goodprose.executive_writing.unified_data import (
    AUTHORING_SYSTEM,
    CREATION_METHOD,
    DATASET_ID,
    FROZEN_V1_EXPECTATIONS,
    GENRES,
    INTENDED_USE,
    PROFILES,
    RIGHTS_STATUS,
    CompilationExpectations,
    SourceRecord,
    UnifiedChatRecord,
    compile_unified_dataset,
    normalized_sha256,
    source_record_schema,
)
from goodprose.jsonl import canonical_json, sha256_bytes

REPO_ROOT = Path(__file__).resolve().parents[2]
B1_CASES = REPO_ROOT / "evals" / "executive-writing" / "goodprose-b1-v1" / "cases.jsonl"


def _layout(slot: int) -> tuple[str, str]:
    split = "train" if slot < 60 else "valid" if slot < 75 else "test"
    if slot < 14:
        corpus = "preference_pair"
    elif slot < 28 or 60 <= slot < 64 or 75 <= slot < 79:
        corpus = "style_target"
    else:
        corpus = "task_pair"
    return split, corpus


def _refresh_commitments(record: dict[str, Any]) -> dict[str, Any]:
    record["system_sha256"] = normalized_sha256(record["system_prompt"])
    record["user_sha256"] = normalized_sha256(record["user_prompt"])
    if record.get("preference") is not None:
        record["target_sha256"] = normalized_sha256(record["preference"]["chosen"])
        record["rejected_sha256"] = normalized_sha256(record["preference"]["rejected"])
    else:
        record["target_sha256"] = normalized_sha256(record["assistant_target"])
        record["rejected_sha256"] = None
    return record


def synthetic_record(slot: int) -> dict[str, Any]:
    split, corpus = _layout(slot)
    record: dict[str, Any] = {
        "version": 1,
        "example_id": f"synthetic-unified-{slot:03d}",
        "lineage_group": f"synthetic-lineage-{slot // 3:02d}",
        "split": split,
        "corpus": corpus,
        "profile_id": PROFILES[slot % 3],
        "genre": GENRES[slot % 7],
        "creation_method": CREATION_METHOD,
        "authoring_system": AUTHORING_SYSTEM,
        "rights_status": RIGHTS_STATUS,
        "intended_use": INTENDED_USE,
        "system_prompt": f"zzqx synthetic system prompt slot {slot:03d} kxs{slot:03d}",
        "user_prompt": f"zzqx synthetic user request slot {slot:03d} kxu{slot:03d}",
        "system_sha256": "",
        "user_sha256": "",
        "target_sha256": "",
        "rejected_sha256": None,
        "source_provenance": {
            "ownership": "project_owned",
            "named_source": None,
            "external_source_used": False,
            "personal_private_data": False,
            "transformation_history": [
                f"codex authored synthetic architecture-pilot record {slot:03d}"
            ],
        },
    }
    if corpus == "preference_pair":
        record["preference"] = {
            "chosen": f"zzqx synthetic chosen response slot {slot:03d} qtc{slot:03d}",
            "rejected": f"zzqx synthetic rejected response slot {slot:03d} qtr{slot:03d}",
            "rejection_reasons": ["verbosity"] if slot % 2 == 0 else ["caveat_loss"],
        }
    else:
        record["assistant_target"] = f"zzqx synthetic target response slot {slot:03d} qtt{slot:03d}"
    return _refresh_commitments(record)


def synthetic_source_lines() -> list[dict[str, Any]]:
    return [synthetic_record(slot) for slot in range(90)]


def write_source(path: Path, records: list[dict[str, Any]]) -> Path:
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
    return path


def small_record(
    *,
    example_id: str,
    split: str,
    corpus: str,
    profile: str,
    genre: str,
    lineage: str,
    marker: str,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "version": 1,
        "example_id": example_id,
        "lineage_group": lineage,
        "split": split,
        "corpus": corpus,
        "profile_id": profile,
        "genre": genre,
        "creation_method": CREATION_METHOD,
        "authoring_system": AUTHORING_SYSTEM,
        "rights_status": RIGHTS_STATUS,
        "intended_use": INTENDED_USE,
        "system_prompt": f"zzqx small system {marker}",
        "user_prompt": f"zzqx small user {marker}",
        "system_sha256": "",
        "user_sha256": "",
        "target_sha256": "",
        "rejected_sha256": None,
        "source_provenance": {
            "ownership": "project_owned",
            "transformation_history": [f"codex authored small synthetic {marker}"],
        },
    }
    if corpus == "preference_pair":
        record["preference"] = {
            "chosen": f"zzqx small chosen {marker}",
            "rejected": f"zzqx small rejected {marker}",
            "rejection_reasons": ["verbosity"],
        }
    else:
        record["assistant_target"] = f"zzqx small target {marker}"
    return _refresh_commitments(record)


def compile_synthetic(
    tmp_path: Path, records: list[dict[str, Any]], name: str = "main"
) -> tuple[Path, Path, dict[str, Any]]:
    output_dir = tmp_path / f"{name}-data"
    manifest_path = tmp_path / f"{name}-manifest.json"
    manifest = compile_unified_dataset(
        source_path=write_source(tmp_path / f"{name}-source.jsonl", records),
        output_dir=output_dir,
        manifest_path=manifest_path,
        b1_cases_path=B1_CASES,
    )
    return output_dir, manifest_path, manifest


def test_frozen_boundary_strings_are_exact() -> None:
    assert DATASET_ID == "goodprose-project-authored-unified-pilot-v1"
    assert RIGHTS_STATUS == "training_permitted_project_owned_architecture_pilot"
    assert INTENDED_USE == "unified_profile_conditioning_architecture_pilot_only"
    assert CREATION_METHOD == "codex_project_authored_v1"
    assert AUTHORING_SYSTEM == "goodprose-unified-pilot-content-v1"


def test_full_synthetic_compile_meets_frozen_counts_and_ratios(tmp_path: Path) -> None:
    output_dir, _, manifest = compile_synthetic(tmp_path, synthetic_source_lines())

    assert manifest["record_count"] == 90
    assert manifest["lineage_group_count"] == 30
    assert manifest["split_counts"] == {"train": 60, "valid": 15, "test": 15}
    assert manifest["corpus_counts"] == {
        "task_pair": 54,
        "style_target": 22,
        "preference_pair": 14,
    }
    assert manifest["corpus_ratios"] == {
        "task_pair": 54 / 90,
        "style_target": 22 / 90,
        "preference_pair": 14 / 90,
    }
    assert manifest["corpus_ratio_fractions"] == {
        "task_pair": {"numerator": 54, "denominator": 90},
        "style_target": {"numerator": 22, "denominator": 90},
        "preference_pair": {"numerator": 14, "denominator": 90},
    }
    assert manifest["rights_status"] == RIGHTS_STATUS
    assert manifest["intended_use"] == INTENDED_USE
    assert manifest["contamination_check"]["status"] == "pass"  # type: ignore[index]
    assert manifest["limitations"]
    assert "unified-data build" in manifest["build_command"]  # type: ignore[operator]
    preference_rows = (output_dir / "preferences.jsonl").read_text(encoding="utf-8")
    assert len([line for line in preference_rows.splitlines() if line]) == 14


def test_committed_schema_matches_model_and_manifest_commitment(tmp_path: Path) -> None:
    public_schema_path = (
        REPO_ROOT / "data" / "executive-writing" / "unified-pilot-v1" / "record-schema.json"
    )
    public_schema = json.loads(public_schema_path.read_text(encoding="utf-8"))
    assert canonical_json(public_schema) == canonical_json(source_record_schema())

    _, _, manifest = compile_synthetic(tmp_path, synthetic_source_lines())
    canonical_schema_bytes = (canonical_json(public_schema) + "\n").encode()
    assert manifest["record_schema_sha256"] == sha256_bytes(canonical_schema_bytes)


def test_compile_is_reproducible_and_preserves_source_order(tmp_path: Path) -> None:
    first_dir, _, first_manifest = compile_synthetic(tmp_path, synthetic_source_lines())
    second_dir, _, second_manifest = compile_synthetic(
        tmp_path, synthetic_source_lines(), name="second"
    )

    assert first_manifest == second_manifest
    for split in ("train", "valid", "test", "preferences"):
        assert (first_dir / f"{split}.jsonl").read_bytes() == (
            second_dir / f"{split}.jsonl"
        ).read_bytes()

    reversed_dir, _, reversed_manifest = compile_synthetic(
        tmp_path, list(reversed(synthetic_source_lines())), name="reversed"
    )
    assert reversed_manifest["record_count"] == 90  # type: ignore[index]
    assert (reversed_dir / "train.jsonl").read_bytes() != (first_dir / "train.jsonl").read_bytes()
    first_train_row = json.loads(
        (first_dir / "train.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert first_train_row["metadata"]["example_id"].endswith("-000")


def test_chat_rows_preserve_preference_information(tmp_path: Path) -> None:
    output_dir, _, _ = compile_synthetic(tmp_path, synthetic_source_lines())

    preference_line = (output_dir / "preferences.jsonl").read_text(encoding="utf-8").splitlines()[0]
    row = UnifiedChatRecord.model_validate_json(preference_line)
    source = synthetic_record(0)
    assert source["corpus"] == "preference_pair"
    assert [message.role for message in row.messages] == ["system", "user", "assistant"]
    assert row.messages[2].content == source["preference"]["chosen"]
    assert row.metadata.rejected_response == source["preference"]["rejected"]
    assert row.metadata.rejection_reasons == ("verbosity",)
    assert row.metadata.rejected_sha256 == normalized_sha256(source["preference"]["rejected"])
    assert (
        list(row.metadata.transformation_history)
        == source["source_provenance"]["transformation_history"]
    )
    assert row.metadata.source_provenance.model_dump(mode="json") == source["source_provenance"]
    assert row.metadata.dataset_id == DATASET_ID

    task_line = (output_dir / "train.jsonl").read_text(encoding="utf-8").splitlines()[28]
    task_row = UnifiedChatRecord.model_validate_json(task_line)
    assert task_row.metadata.corpus == "task_pair"
    assert task_row.metadata.rejected_response is None
    assert task_row.metadata.rejection_reasons == ()


def test_source_schema_rejects_invalid_variants() -> None:
    base = synthetic_record(40)

    def variant(mutate: Any) -> dict[str, Any]:
        record = json.loads(json.dumps(base))
        mutate(record)
        return record

    invalid = [
        variant(lambda r: r.update(version=2)),
        variant(lambda r: r.update(example_id="")),
        variant(lambda r: r.update(split="holdout")),
        variant(lambda r: r.update(corpus="chat_pairs")),
        variant(lambda r: r.update(profile_id="executive-house-v1")),
        variant(lambda r: r.update(genre="newsletter")),
        variant(lambda r: r.update(creation_method="template")),
        variant(lambda r: r.update(authoring_system="other-v9")),
        variant(lambda r: r.update(rights_status="training_permitted_project_owned_smoke")),
        variant(lambda r: r.update(intended_use="pipeline_smoke_test_only")),
        variant(lambda r: r.update(system_prompt="")),
        variant(lambda r: r.pop("assistant_target")),
        variant(lambda r: r.update(target_sha256="0" * 64)),
        variant(lambda r: r.update(unexpected_field=True)),
        variant(lambda r: r["source_provenance"].update(ownership="scraped")),
        variant(lambda r: r["source_provenance"].update(named_source="someone@example.com")),
        variant(lambda r: r["source_provenance"].update(external_source_used=True)),
        variant(lambda r: r["source_provenance"].update(personal_private_data=True)),
        variant(lambda r: r["source_provenance"].update(transformation_history=[])),
        variant(
            lambda r: r.update(
                preference={
                    "chosen": "a",
                    "rejected": "b",
                    "rejection_reasons": ["verbosity"],
                }
            )
        ),
        variant(
            lambda r: r.update(
                preference={
                    "chosen": r.pop("assistant_target"),
                    "rejected": "zzqx different rejected response",
                    "rejection_reasons": ["verbosity"],
                }
            )
        ),
    ]
    for record in invalid:
        with pytest.raises(pydantic.ValidationError):
            SourceRecord.model_validate(record)

    good_task = SourceRecord.model_validate(base)
    assert good_task.example_id == "synthetic-unified-040"


def test_preference_schema_rejects_bad_reasons_and_equal_responses() -> None:
    preference = synthetic_record(0)["preference"]

    with pytest.raises(pydantic.ValidationError):
        SourceRecord.model_validate(
            {
                **synthetic_record(0),
                "preference": {**preference, "rejection_reasons": ["made_up_reason"]},
            }
        )
    with pytest.raises(pydantic.ValidationError):
        SourceRecord.model_validate(
            {**synthetic_record(0), "preference": {**preference, "rejection_reasons": []}}
        )
    with pytest.raises(pydantic.ValidationError):
        SourceRecord.model_validate(
            {
                **synthetic_record(0),
                "preference": {**preference, "rejected": preference["chosen"]},
            }
        )


def test_compiler_rejects_wrong_counts(tmp_path: Path) -> None:
    truncated = synthetic_source_lines()[:-1]
    with pytest.raises(ValueError, match="expected exactly 90"):
        compile_synthetic(tmp_path, truncated)

    with pytest.raises(ValueError, match="expected exactly"):
        compile_unified_dataset(
            source_path=write_source(tmp_path / "count-source.jsonl", synthetic_source_lines()),
            output_dir=tmp_path / "count-data",
            manifest_path=tmp_path / "count-manifest.json",
            b1_cases_path=B1_CASES,
            expectations=FROZEN_V1_EXPECTATIONS.model_copy(update={"record_count": 91}),
        )


def test_compiler_rejects_genre_minimum_violation(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="below minimum"):
        compile_unified_dataset(
            source_path=write_source(tmp_path / "genre-source.jsonl", synthetic_source_lines()),
            output_dir=tmp_path / "genre-data",
            manifest_path=tmp_path / "genre-manifest.json",
            b1_cases_path=B1_CASES,
            expectations=FROZEN_V1_EXPECTATIONS.model_copy(update={"min_genre_count": 13}),
        )


def small_expectations(records: list[dict[str, Any]]) -> CompilationExpectations:
    corpora: dict[str, int] = {}
    for record in records:
        corpora[record["corpus"]] = corpora.get(record["corpus"], 0) + 1
    return CompilationExpectations(
        record_count=len(records),
        lineage_group_count=len({record["lineage_group"] for record in records}),
        split_counts={
            "train": sum(1 for record in records if record["split"] == "train"),
            "valid": sum(1 for record in records if record["split"] == "valid"),
            "test": sum(1 for record in records if record["split"] == "test"),
        },
        corpus_counts=corpora,  # type: ignore[arg-type]
        min_genre_count=1,
    )


def compile_small(tmp_path: Path, records: list[dict[str, Any]], name: str) -> None:
    compile_unified_dataset(
        source_path=write_source(tmp_path / f"{name}-source.jsonl", records),
        output_dir=tmp_path / f"{name}-data",
        manifest_path=tmp_path / f"{name}-manifest.json",
        b1_cases_path=B1_CASES,
        expectations=small_expectations(records),
    )


def test_small_valid_dataset_compiles(tmp_path: Path) -> None:
    records = []
    corpora_cycle = ["task_pair", "style_target", "preference_pair", "task_pair"]
    for index in range(7):
        records.append(
            small_record(
                example_id=f"small-{index:02d}",
                split="train",
                corpus=corpora_cycle[index % 4],
                profile=PROFILES[index % 3],
                genre=GENRES[index],
                lineage="small-lineage-a" if index < 4 else "small-lineage-b",
                marker=f"m{index:02d}",
            )
        )
    compile_small(tmp_path, records, "ok")


def test_compiler_rejects_profile_imbalance_missing_genre_and_duplicate_cells(
    tmp_path: Path,
) -> None:
    imbalanced = [
        small_record(
            example_id=f"imb-{index:02d}",
            split="train",
            corpus=["task_pair", "style_target", "preference_pair", "task_pair"][index % 4],
            profile=PROFILES[0] if index < 5 else PROFILES[index - 4],
            genre=GENRES[index],
            lineage=f"imb-lineage-{index % 2}",
            marker=f"i{index:02d}",
        )
        for index in range(7)
    ]
    with pytest.raises(ValueError, match="imbalance"):
        compile_small(tmp_path, imbalanced, "imbalanced")

    missing_genre = [
        small_record(
            example_id=f"mg-{index:02d}",
            split="train",
            corpus=["task_pair", "style_target", "preference_pair", "task_pair"][index % 4],
            profile=PROFILES[index % 3],
            genre=GENRES[index] if index < 6 else GENRES[1],
            lineage=f"mg-lineage-{index % 2}",
            marker=f"g{index:02d}",
        )
        for index in range(7)
    ]
    with pytest.raises(ValueError, match="coverage incomplete"):
        compile_small(tmp_path, missing_genre, "missing-genre")

    duplicate_corpora = [
        "task_pair",
        "task_pair",
        "style_target",
        "preference_pair",
        "task_pair",
        "task_pair",
        "task_pair",
    ]
    duplicate_profiles = [
        PROFILES[0],
        PROFILES[0],
        PROFILES[1],
        PROFILES[2],
        PROFILES[1],
        PROFILES[2],
        PROFILES[0],
    ]
    duplicate_genres = [
        "email",
        "email",
        "memo",
        "revision",
        "short_post",
        "blog_post",
        "engineering_document",
    ]
    duplicate_cell = [
        small_record(
            example_id=f"dc-{index}",
            split="train",
            corpus=duplicate_corpora[index],
            profile=duplicate_profiles[index],
            genre=duplicate_genres[index],
            lineage="dc-lineage",
            marker=f"d{index}",
        )
        for index in range(7)
    ]
    with pytest.raises(ValueError, match="duplicate"):
        compile_small(tmp_path, duplicate_cell, "duplicate-cell")


def test_compiler_rejects_duplicate_ids_and_prompts(tmp_path: Path) -> None:
    duplicated_id = synthetic_source_lines()
    duplicated_id[1]["example_id"] = duplicated_id[0]["example_id"]
    with pytest.raises(ValueError, match="duplicate example IDs"):
        compile_synthetic(tmp_path, duplicated_id, name="dup-id")

    records = synthetic_source_lines()
    clone = json.loads(json.dumps(records[1]))
    clone["user_prompt"] = records[0]["user_prompt"]
    _refresh_commitments(clone)
    records[1] = clone
    with pytest.raises(ValueError, match="duplicate normalized user prompts"):
        compile_synthetic(tmp_path, records, name="dup-prompt")


def test_compiler_rejects_lineage_crossing_splits(tmp_path: Path) -> None:
    records = synthetic_source_lines()
    records[60]["lineage_group"] = "synthetic-lineage-00"
    records[3]["lineage_group"] = "synthetic-lineage-20"
    with pytest.raises(ValueError, match="cross splits"):
        compile_synthetic(tmp_path, records)


def test_compiler_rejects_b1_contamination(tmp_path: Path) -> None:
    source_material = load_cases(B1_CASES)[0].input.source_material
    words = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?%?", source_material.casefold())
    span = " ".join(words[:12])

    records = synthetic_source_lines()
    records[80]["user_prompt"] = f"zzqx prefix {span} zzqx suffix"
    _refresh_commitments(records[80])
    with pytest.raises(ValueError, match="12-grams"):
        compile_synthetic(tmp_path, records)


def test_contamination_matcher_detects_shared_span() -> None:
    shared = "one two three four five six seven eight nine ten eleven twelve"
    matches = contamination_matches([f"zzqx {shared} zzqx"], [f"b1 {shared} b1"], ngram_words=12)
    assert tuple(shared.split()) in matches


def test_compiler_refuses_existing_outputs_and_partial_writes(tmp_path: Path) -> None:
    blocked_output = tmp_path / "blocked-data"
    blocked_output.mkdir()
    (blocked_output / "train.jsonl").write_bytes(b"existing\n")
    with pytest.raises(ValueError, match="refusing to overwrite"):
        compile_unified_dataset(
            source_path=write_source(tmp_path / "blocked-source.jsonl", synthetic_source_lines()),
            output_dir=blocked_output,
            manifest_path=tmp_path / "blocked-manifest.json",
            b1_cases_path=B1_CASES,
        )
    assert not (tmp_path / "blocked-manifest.json").exists()

    invalid_records = synthetic_source_lines()
    invalid_records[10]["split"] = "valid"
    invalid_records[11]["split"] = "test"
    with pytest.raises(ValueError):
        compile_unified_dataset(
            source_path=write_source(tmp_path / "invalid-source.jsonl", invalid_records),
            output_dir=tmp_path / "fresh-data",
            manifest_path=tmp_path / "fresh-manifest.json",
            b1_cases_path=B1_CASES,
        )
    fresh_data = tmp_path / "fresh-data"
    assert not fresh_data.exists() or not any(fresh_data.iterdir())
    assert not (tmp_path / "fresh-manifest.json").exists()


def test_cli_build_matches_direct_compile(tmp_path: Path) -> None:
    source = write_source(tmp_path / "cli-source.jsonl", synthetic_source_lines())
    output_dir = tmp_path / "cli-data"
    manifest_path = tmp_path / "cli-manifest.json"
    exit_code = main(
        [
            "unified-data",
            "build",
            "--source",
            str(source),
            "--output-dir",
            str(output_dir),
            "--manifest",
            str(manifest_path),
            "--b1-cases",
            str(B1_CASES),
        ]
    )

    assert exit_code == 0
    direct_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _, _, expected_manifest = compile_synthetic(tmp_path, synthetic_source_lines())
    assert direct_manifest == expected_manifest


def test_frozen_v1_expectations_are_immutable() -> None:
    with pytest.raises(pydantic.ValidationError):
        FROZEN_V1_EXPECTATIONS.record_count = 10  # type: ignore[misc]
