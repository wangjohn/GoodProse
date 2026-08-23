from __future__ import annotations

from pathlib import Path

import pytest

from goodprose.executive_writing.human_evaluation import (
    HumanRating,
    HumanStudyRegistration,
    aggregate_human_ratings,
)
from goodprose.jsonl import atomic_write_json, serialize_jsonl


def _registration(tmp_path: Path) -> Path:
    path = tmp_path / "registration.json"
    atomic_write_json(
        path,
        HumanStudyRegistration(
            version=1,
            protocol_id="goodprose-intended-audience-human-v1",
            study_id="synthetic-human-study-v1",
            status="preregistered_unopened",
            benchmark_version="synthetic-v1",
            finalist_freeze_sha256="a" * 64,
            case_manifest_sha256="b" * 64,
            assignment_manifest_sha256="c" * 64,
            case_count=50,
            packet_candidate_count=2,
            ratings_per_assignment=3,
            required_cohorts=(
                "founder_or_executive",
                "technical_leader",
                "business_editor",
            ),
            position_balanced=True,
            candidate_identity_blinded=True,
            source_visible_to_raters=True,
            primary_endpoint="publish_ready_acceptance_rate",
            critical_factual_error_is_veto=True,
            secondary_endpoint="blinded_pairwise_preference",
            generated_at="2026-08-23T22:30:00Z",
        ).model_dump(mode="json"),
    )
    return path


def _ratings() -> list[HumanRating]:
    rows = []
    cohorts = ("founder_or_executive", "technical_leader", "business_editor")
    labels = ("publishable", "minor_edits", "substantive_edits")
    for index, (cohort, label) in enumerate(zip(cohorts, labels, strict=True), start=1):
        rows.append(
            HumanRating(
                version=1,
                protocol_id="goodprose-intended-audience-human-v1",
                study_id="synthetic-human-study-v1",
                assignment_id="assignment-1",
                case_id="case-1",
                artifact_label="artifact-A",
                rater_id=f"rater-{index}",
                rater_cohort=cohort,
                operational_label=label,
                critical_factual_error=False,
                editing_minutes=float(index - 1),
                error_labels=() if label == "publishable" else ("other",),
                submitted_at=f"2026-08-23T22:3{index}:00Z",
            )
        )
    return rows


def test_human_rating_enforces_critical_error_veto() -> None:
    with pytest.raises(ValueError, match="critical factual error veto"):
        HumanRating(
            version=1,
            protocol_id="goodprose-intended-audience-human-v1",
            study_id="synthetic-human-study-v1",
            assignment_id="assignment-1",
            case_id="case-1",
            artifact_label="artifact-A",
            rater_id="rater-1",
            rater_cohort="business_editor",
            operational_label="minor_edits",
            critical_factual_error=True,
            editing_minutes=1,
            error_labels=("fabrication",),
            submitted_at="2026-08-23T22:31:00Z",
        )


def test_aggregate_human_ratings_reports_primary_endpoint(tmp_path: Path) -> None:
    registration_path = _registration(tmp_path)
    ratings_path = tmp_path / "ratings.jsonl"
    ratings_path.write_bytes(serialize_jsonl(_ratings()))
    output_path = tmp_path / "aggregate.json"

    result = aggregate_human_ratings(
        registration_path=registration_path,
        ratings_path=ratings_path,
        output_path=output_path,
        generated_at="2026-08-23T22:40:00Z",
    )

    assert result["overall"]["rating_count"] == 3
    assert result["overall"]["publish_ready_acceptance_rate"] == 0.6667
    assert result["overall"]["editing_minutes_median"] == 1
    assert result["candidate_identity_status"] == "opaque_labels_only_not_resolved"


def test_aggregate_rejects_under_rated_assignment(tmp_path: Path) -> None:
    registration_path = _registration(tmp_path)
    ratings_path = tmp_path / "ratings.jsonl"
    ratings_path.write_bytes(serialize_jsonl(_ratings()[:2]))

    with pytest.raises(ValueError, match="fewer ratings"):
        aggregate_human_ratings(
            registration_path=registration_path,
            ratings_path=ratings_path,
            output_path=tmp_path / "aggregate.json",
            generated_at="2026-08-23T22:40:00Z",
        )
