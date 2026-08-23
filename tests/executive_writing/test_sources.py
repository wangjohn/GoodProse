"""Deterministic tests for the named-source artifact contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError as PydanticValidationError

from goodprose.executive_writing.sources import (
    COMMON_EVALUATION_CASE_IDS,
    REQUESTED_PEOPLE,
    DataAvailabilityReport,
    NamedSourceManifest,
    RightsAssessment,
    RunConfigDocument,
    SourceValidationError,
    check_standalone_eligibility,
    load_run_config,
    validate_repository_layout,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "data/executive-writing/sources/named-sources-v1.json"
EVAL_MANIFEST_PATH = REPO_ROOT / "evals/executive-writing/source-profiles-v1/manifest.json"
CONFIGS_DIR = REPO_ROOT / "programs/executive-writing/configs/source-profiles"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest_data() -> dict[str, Any]:
    return _load(MANIFEST_PATH)


def test_committed_artifacts_validate_together() -> None:
    layout = validate_repository_layout(MANIFEST_PATH, EVAL_MANIFEST_PATH, CONFIGS_DIR)
    assert [entry.person for entry in layout.manifest.people] == list(REQUESTED_PEOPLE)
    assert len(layout.configs) == 11
    assert layout.eval_manifest.shared_case_ids == list(COMMON_EVALUATION_CASE_IDS)
    for entry in layout.manifest.people:
        assert entry.public_email.verified_collection_found is False
        assert len(entry.evaluation_subset.case_ids) == 6
        assert entry.rights.classification != "training_approved"
        assert not entry.run_configuration.standalone_eligible


def test_every_profile_uses_common_six_case_set(manifest_data: dict[str, Any]) -> None:
    for person in manifest_data["people"]:
        subset = person["evaluation_subset"]
        assert sorted(subset["case_ids"]) == sorted(COMMON_EVALUATION_CASE_IDS)


def _write_layout(
    tmp_path: Path,
    manifest: dict[str, Any],
    eval_manifest: dict[str, Any],
) -> tuple[Path, Path, Path]:
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir(parents=True)
    for profile in manifest["people"]:
        profile_id = profile["profile"]["profile_id"]
        config = {
            "config_id": profile["run_configuration"]["config_id"],
            "label": "test run",
            "person": profile["person"],
            "profile_id": profile_id,
            "architecture": "profile_card_retrieval_coverage",
            "standalone_eligible": False,
            "blocker": profile["run_configuration"]["blocker"],
            "third_party_training_text": False,
            "purpose": "exploratory_research_not_impersonation_or_endorsement",
            "source_manifest_id": manifest["manifest_id"],
            "source_manifest_version": manifest["version"],
            "evaluation_benchmark_id": eval_manifest["benchmark_id"],
            "evaluation_slice_id": profile["evaluation_subset"]["slice_id"],
            "provenance_record": (
                "programs/executive-writing/experiments/ox-source-artifacts-implementation-v1.json"
            ),
        }
        (configs_dir / f"{profile_id}.json").write_text(json.dumps(config), encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    eval_path = tmp_path / "eval-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    eval_path.write_text(json.dumps(eval_manifest), encoding="utf-8")
    return manifest_path, eval_path, configs_dir


@pytest.fixture(scope="module")
def mutable_copies(
    manifest_data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return copy.deepcopy(manifest_data), _load(EVAL_MANIFEST_PATH)


def _expect_error(data: Any, model: type, match: str) -> None:
    # Pydantic wraps validator-raised ValueErrors, including our contract errors.
    with pytest.raises((SourceValidationError, PydanticValidationError), match=match):
        model.model_validate(data)


def test_missing_requested_person_is_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    broken["people"] = broken["people"][:-1]
    _expect_error(broken, NamedSourceManifest, "every requested person exactly once")


def test_duplicate_person_is_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    broken["people"].append(copy.deepcopy(broken["people"][0]))
    _expect_error(broken, NamedSourceManifest, "every requested person exactly once")


def test_duplicate_source_id_is_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    route = copy.deepcopy(broken["people"][0]["source_routes"][0])
    other = broken["people"][1]["source_routes"][0]
    route["source_id"] = other["source_id"]
    route["canonical_url"] = "https://example.com/other"
    broken["people"][0]["source_routes"].append(route)
    _expect_error(broken, NamedSourceManifest, "duplicate source IDs")


def test_duplicate_profile_id_is_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    broken["people"][1]["profile"]["profile_id"] = broken["people"][0]["profile"]["profile_id"]
    _expect_error(broken, NamedSourceManifest, "duplicate profile IDs")


def test_duplicate_slice_ids_are_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    first, second = broken["people"][0], broken["people"][1]
    second["evaluation_subset"]["slice_id"] = first["evaluation_subset"]["slice_id"]
    second["run_configuration"]["evaluation_slice_id"] = first["evaluation_subset"]["slice_id"]
    _expect_error(broken, NamedSourceManifest, "duplicate evaluation-slice IDs")


def test_duplicate_config_ids_are_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    broken["people"][1]["run_configuration"]["config_id"] = broken["people"][0][
        "run_configuration"
    ]["config_id"]
    _expect_error(broken, NamedSourceManifest, "duplicate run-config IDs")


def test_training_approved_classification_is_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    broken["people"][0]["rights"]["classification"] = "training_approved"
    _expect_error(broken, NamedSourceManifest, "training_approved")


def test_non_https_canonical_url_is_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    broken["people"][0]["source_routes"][0]["canonical_url"] = "http://patrickcollison.com/"
    _expect_error(broken, NamedSourceManifest, "must be HTTPS")


def test_rights_record_without_reviewer_metadata_is_rejected() -> None:
    with pytest.raises((SourceValidationError, PydanticValidationError)):
        RightsAssessment.model_validate(
            {
                "classification": "permission_required",
                "approved_uses": ["internal evaluation"],
                "evidence_url": "https://example.com/",
                "reviewer_role": "",
                "review_date": "2026-08-22",
                "unresolved_questions": ["licensing unknown"],
                "promotion_authority": "user-or-qualified-counsel",
            }
        )


def test_identity_named_profile_is_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    broken["people"][0]["profile"]["production_name"] = "Patrick Collison style brief"
    _expect_error(broken, NamedSourceManifest, "descriptive")


def test_quoted_passage_in_metadata_is_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    route = broken["people"][0]["source_routes"][0]
    quoted = f'{route["evidence_fact"]}, quoting "a distinctive phrase"'
    route["evidence_fact"] = quoted
    _expect_error(broken, NamedSourceManifest, "quoted passages")


def test_wrong_or_duplicate_evaluation_case_ids_are_rejected(mutable_copies) -> None:
    manifest, _ = mutable_copies
    short = copy.deepcopy(manifest)
    short["people"][0]["evaluation_subset"]["case_ids"] = COMMON_EVALUATION_CASE_IDS[:5]
    _expect_error(short, NamedSourceManifest, "exactly six unique case IDs")

    duplicated = copy.deepcopy(manifest)
    duplicated["people"][0]["evaluation_subset"]["case_ids"] = [
        *COMMON_EVALUATION_CASE_IDS[:5],
        COMMON_EVALUATION_CASE_IDS[0],
    ]
    _expect_error(duplicated, NamedSourceManifest, "exactly six unique case IDs")

    foreign = copy.deepcopy(manifest)
    foreign["people"][0]["evaluation_subset"]["case_ids"] = [
        *COMMON_EVALUATION_CASE_IDS[:5],
        "b1-999-unknown-case",
    ]
    _expect_error(foreign, NamedSourceManifest, "common content-controlled B1 case set")


def test_standalone_eligibility_requires_thresholds_and_rights() -> None:
    availability = DataAvailabilityReport.model_validate(
        {
            "default_threshold": {
                "effective_clean_tokens": 50000,
                "independent_examples": 100,
                "relevant_genres": 3,
                "held_out_cases": 30,
            },
            "outlook": "plausibly_reachable",
            "component_assessments": [
                {"component": name, "status": "unverified", "note": "not measured"}
                for name in (
                    "effective_clean_tokens",
                    "independent_examples",
                    "genre_coverage",
                    "held_out_cases",
                )
            ],
            "notes": [],
        }
    )
    rights = RightsAssessment.model_validate(
        {
            "classification": "permission_required",
            "approved_uses": ["internal evaluation"],
            "evidence_url": "https://example.com/",
            "reviewer_role": "codex-reviewer",
            "review_date": "2026-08-22",
            "unresolved_questions": [],
            "promotion_authority": "user-or-qualified-counsel",
        }
    )
    config = RunConfigDocument.model_validate(
        {
            "config_id": "runconfig-test-v1",
            "label": "test run",
            "person": REQUESTED_PEOPLE[0],
            "profile_id": "test-profile-v1",
            "architecture": "profile_card_retrieval_coverage",
            "standalone_eligible": True,
            "blocker": "none recorded",
            "third_party_training_text": False,
            "purpose": "exploratory_research_not_impersonation_or_endorsement",
            "source_manifest_id": "named-sources-v1",
            "source_manifest_version": 1,
            "evaluation_benchmark_id": "goodprose-b1-v1",
            "evaluation_slice_id": "slice-test-v1",
            "provenance_record": (
                "programs/executive-writing/experiments/ox-source-artifacts-implementation-v1.json"
            ),
        }
    )
    with pytest.raises(SourceValidationError, match="blocked by"):
        check_standalone_eligibility(config, availability, rights)


def test_manifest_standalone_reference_is_rejected_when_blocked(mutable_copies) -> None:
    manifest, _ = mutable_copies
    broken = copy.deepcopy(manifest)
    broken["people"][0]["run_configuration"]["standalone_eligible"] = True
    _expect_error(broken, NamedSourceManifest, "blocked by")


def test_config_referencing_unknown_profile_or_slice_is_rejected(
    mutable_copies, tmp_path: Path
) -> None:
    manifest, eval_manifest = mutable_copies
    good_paths = _write_layout(tmp_path / "good", manifest, eval_manifest)

    paths = _write_layout(tmp_path / "missing-config", manifest, eval_manifest)
    (paths[2] / f"{manifest['people'][0]['profile']['profile_id']}.json").unlink()
    with pytest.raises(SourceValidationError, match="missing run config"):
        validate_repository_layout(*paths)

    bad_slice = copy.deepcopy(manifest)
    new_slice = "slice-does-not-exist-v1"
    bad_slice["people"][0]["evaluation_subset"]["slice_id"] = new_slice
    bad_slice["people"][0]["run_configuration"]["evaluation_slice_id"] = new_slice
    paths = _write_layout(tmp_path / "bad-slice", bad_slice, eval_manifest)
    with pytest.raises(SourceValidationError, match="unknown evaluation slice"):
        validate_repository_layout(*paths)

    config_file = good_paths[2] / f"{manifest['people'][0]['profile']['profile_id']}.json"
    config_data = _load(config_file)
    config_data["source_manifest_id"] = "named-sources-v9"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")
    with pytest.raises(SourceValidationError, match="references unknown manifest"):
        validate_repository_layout(*good_paths)


def test_eval_profiles_and_embedded_config_references_must_match(
    mutable_copies, tmp_path: Path
) -> None:
    manifest, eval_manifest = mutable_copies

    unexpected_eval = copy.deepcopy(eval_manifest)
    unexpected_eval["slices"][0]["profile_id"] = "unknown-profile-v1"
    paths = _write_layout(tmp_path / "bad-eval", manifest, unexpected_eval)
    with pytest.raises(SourceValidationError, match="do not exactly match"):
        validate_repository_layout(*paths)

    bad_path_ref = copy.deepcopy(manifest)
    bad_path_ref["people"][0]["run_configuration"]["config_path"] = "wrong.json"
    paths = _write_layout(tmp_path / "bad-path-ref", bad_path_ref, eval_manifest)
    with pytest.raises(SourceValidationError, match="unexpected config path"):
        validate_repository_layout(*paths)

    paths = _write_layout(tmp_path / "drift", manifest, eval_manifest)
    config_path = paths[2] / f"{manifest['people'][0]['profile']['profile_id']}.json"
    config = _load(config_path)
    config["blocker"] = "drifted blocker"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(SourceValidationError, match="disagrees with its manifest reference"):
        validate_repository_layout(*paths)


def test_load_run_config_rejects_third_party_training_text(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "config_id": "runconfig-test-v1",
                "label": "test run",
                "person": REQUESTED_PEOPLE[0],
                "profile_id": "test-profile-v1",
                "architecture": "profile_card_retrieval_coverage",
                "standalone_eligible": False,
                "blocker": "permission_required",
                "third_party_training_text": True,
                "purpose": "exploratory_research_not_impersonation_or_endorsement",
                "source_manifest_id": "named-sources-v1",
                "source_manifest_version": 1,
                "evaluation_benchmark_id": "goodprose-b1-v1",
                "evaluation_slice_id": "slice-test-v1",
                "provenance_record": (
                    "programs/executive-writing/experiments/"
                    "ox-source-artifacts-implementation-v1.json"
                ),
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SourceValidationError, match="third-party"):
        load_run_config(path)


def test_unexpected_extra_config_in_directory_is_rejected(mutable_copies, tmp_path: Path) -> None:
    manifest, eval_manifest = mutable_copies
    paths = _write_layout(tmp_path / "extra", manifest, eval_manifest)
    extra = {
        "config_id": "runconfig-extra-v1",
        "label": "stray",
        "person": REQUESTED_PEOPLE[0],
        "profile_id": "concise-curation-brief-v1",
        "architecture": "profile_card_retrieval_coverage",
        "standalone_eligible": False,
        "blocker": "permission_required",
        "third_party_training_text": False,
        "purpose": "exploratory_research_not_impersonation_or_endorsement",
        "source_manifest_id": "named-sources-v1",
        "source_manifest_version": 1,
        "evaluation_benchmark_id": "goodprose-b1-v1",
        "evaluation_slice_id": "slice-patrick-collison-v1",
        "provenance_record": (
            "programs/executive-writing/experiments/ox-source-artifacts-implementation-v1.json"
        ),
    }
    (paths[2] / "stray-config.json").write_text(json.dumps(extra), encoding="utf-8")
    with pytest.raises(SourceValidationError, match="unexpected run configs"):
        validate_repository_layout(*paths)
