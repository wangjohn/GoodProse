"""Blinded intended-audience human-evaluation protocol and aggregation."""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean, median
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.jsonl import atomic_write_json, load_jsonl, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

OperationalLabel = Literal["publishable", "minor_edits", "substantive_edits", "unacceptable"]
RaterCohort = Literal["founder_or_executive", "technical_leader", "business_editor"]
ErrorLabel = Literal[
    "fabrication",
    "numerical_mutation",
    "omission",
    "caveat_loss",
    "intent_reversal",
    "privacy_or_safety",
    "unsupported_claim",
    "poor_actionability",
    "audience_mismatch",
    "structural_failure",
    "excessive_rewriting",
    "other",
]
PairwisePreference = Literal["preferred_first", "preferred_second", "tie", "both_unacceptable"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class HumanStudyRegistration(StrictModel):
    version: Literal[1]
    protocol_id: Literal["goodprose-intended-audience-human-v1"]
    study_id: NonEmpty
    status: Literal["preregistered_unopened"]
    benchmark_version: NonEmpty
    finalist_freeze_sha256: Sha256
    case_manifest_sha256: Sha256
    assignment_manifest_sha256: Sha256
    case_count: int = Field(ge=50, le=100)
    packet_candidate_count: int = Field(ge=2, le=3)
    ratings_per_assignment: int = Field(ge=3)
    required_cohorts: tuple[RaterCohort, ...]
    position_balanced: Literal[True]
    candidate_identity_blinded: Literal[True]
    source_visible_to_raters: Literal[True]
    primary_endpoint: Literal["publish_ready_acceptance_rate"]
    critical_factual_error_is_veto: Literal[True]
    secondary_endpoint: Literal["blinded_pairwise_preference"]
    generated_at: NonEmpty

    @model_validator(mode="after")
    def validate_cohorts(self) -> Self:
        expected = {"founder_or_executive", "technical_leader", "business_editor"}
        if set(self.required_cohorts) != expected or len(self.required_cohorts) != 3:
            raise ValueError(
                "registration must require all three distinct intended-audience cohorts"
            )
        return self


class PairwiseRating(StrictModel):
    first_artifact_label: NonEmpty
    second_artifact_label: NonEmpty
    preference: PairwisePreference

    @model_validator(mode="after")
    def validate_distinct_labels(self) -> Self:
        if self.first_artifact_label == self.second_artifact_label:
            raise ValueError("pairwise artifact labels must be distinct")
        return self


class HumanRating(StrictModel):
    version: Literal[1]
    protocol_id: Literal["goodprose-intended-audience-human-v1"]
    study_id: NonEmpty
    assignment_id: NonEmpty
    case_id: NonEmpty
    artifact_label: NonEmpty
    rater_id: NonEmpty
    rater_cohort: RaterCohort
    operational_label: OperationalLabel
    critical_factual_error: bool
    editing_minutes: float = Field(ge=0, le=240)
    error_labels: tuple[ErrorLabel, ...]
    pairwise: PairwiseRating | None = None
    submitted_at: NonEmpty

    @model_validator(mode="after")
    def validate_rating(self) -> Self:
        if len(self.error_labels) != len(set(self.error_labels)):
            raise ValueError("error labels must be unique")
        if self.critical_factual_error and self.operational_label != "unacceptable":
            raise ValueError("a critical factual error veto requires an unacceptable label")
        if self.operational_label == "publishable" and self.error_labels:
            raise ValueError("a publishable rating cannot include error labels")
        if self.pairwise and self.artifact_label not in {
            self.pairwise.first_artifact_label,
            self.pairwise.second_artifact_label,
        }:
            raise ValueError("rated artifact must be one of the pairwise artifacts")
        return self


def load_registration(path: Path) -> HumanStudyRegistration:
    return HumanStudyRegistration.model_validate_json(path.read_text(encoding="utf-8"))


def _agreement_rate(ratings: list[HumanRating]) -> float:
    by_assignment: dict[tuple[str, str], list[OperationalLabel]] = defaultdict(list)
    for rating in ratings:
        by_assignment[(rating.assignment_id, rating.artifact_label)].append(
            rating.operational_label
        )
    comparisons = 0
    agreements = 0
    for labels in by_assignment.values():
        for first, second in combinations(labels, 2):
            comparisons += 1
            agreements += first == second
    return round(agreements / comparisons, 4) if comparisons else 0.0


def _operational_summary(ratings: list[HumanRating]) -> dict[str, Any]:
    counts = Counter(rating.operational_label for rating in ratings)
    total = len(ratings)
    publish_ready = counts["publishable"] + counts["minor_edits"]
    critical_count = sum(rating.critical_factual_error for rating in ratings)
    vetoed_assignments = {
        (rating.assignment_id, rating.artifact_label)
        for rating in ratings
        if rating.critical_factual_error
    }
    error_counts = Counter(label for rating in ratings for label in rating.error_labels)
    editing = [rating.editing_minutes for rating in ratings]
    return {
        "rating_count": total,
        "operational_label_counts": dict(sorted(counts.items())),
        "publish_ready_acceptance_rate": round(publish_ready / total, 4),
        "substantive_or_unacceptable_rate": round(
            (counts["substantive_edits"] + counts["unacceptable"]) / total, 4
        ),
        "critical_factual_error_rating_count": critical_count,
        "critical_factual_error_rate": round(critical_count / total, 4),
        "critical_vetoed_assignment_count": len(vetoed_assignments),
        "editing_minutes_mean": round(mean(editing), 4),
        "editing_minutes_median": round(median(editing), 4),
        "error_label_counts": dict(sorted(error_counts.items())),
        "pairwise_exact_operational_agreement_rate": _agreement_rate(ratings),
    }


def aggregate_human_ratings(
    *,
    registration_path: Path,
    ratings_path: Path,
    output_path: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Validate and aggregate blinded ratings without resolving candidate identity."""

    registration = load_registration(registration_path)
    ratings = load_jsonl(ratings_path, HumanRating)
    if not ratings:
        raise ValueError("human evaluation requires at least one rating")
    if any(rating.study_id != registration.study_id for rating in ratings):
        raise ValueError("rating study ID does not match the registration")
    duplicate_keys = [
        (rating.assignment_id, rating.artifact_label, rating.rater_id) for rating in ratings
    ]
    if len(duplicate_keys) != len(set(duplicate_keys)):
        raise ValueError("duplicate rater assignment detected")
    assignment_counts = Counter((rating.assignment_id, rating.artifact_label) for rating in ratings)
    if any(count < registration.ratings_per_assignment for count in assignment_counts.values()):
        raise ValueError("an assignment has fewer ratings than preregistered")

    by_artifact: dict[str, list[HumanRating]] = defaultdict(list)
    by_cohort: dict[str, list[HumanRating]] = defaultdict(list)
    for rating in ratings:
        by_artifact[rating.artifact_label].append(rating)
        by_cohort[rating.rater_cohort].append(rating)
    pairwise_by_assignment: dict[tuple[str, str], PairwiseRating] = {}
    for rating in ratings:
        if rating.pairwise is None:
            continue
        key = (rating.assignment_id, rating.rater_id)
        existing = pairwise_by_assignment.get(key)
        if existing is not None and existing != rating.pairwise:
            raise ValueError("conflicting pairwise ratings for one rater assignment")
        pairwise_by_assignment[key] = rating.pairwise
    pairwise_counts = Counter(item.preference for item in pairwise_by_assignment.values())
    pairwise_non_ties = pairwise_counts["preferred_first"] + pairwise_counts["preferred_second"]
    result = {
        "version": 1,
        "protocol_id": registration.protocol_id,
        "study_id": registration.study_id,
        "generated_at": generated_at,
        "registration_sha256": sha256_file(registration_path),
        "ratings_sha256": sha256_file(ratings_path),
        "candidate_identity_status": "opaque_labels_only_not_resolved",
        "overall": _operational_summary(ratings),
        "by_artifact_label": {
            label: _operational_summary(items) for label, items in sorted(by_artifact.items())
        },
        "by_rater_cohort": {
            cohort: _operational_summary(items) for cohort, items in sorted(by_cohort.items())
        },
        "pairwise": {
            "rating_count": sum(pairwise_counts.values()),
            "preference_counts": dict(sorted(pairwise_counts.items())),
            "first_preference_rate_excluding_ties_and_both_unacceptable": (
                round(pairwise_counts["preferred_first"] / pairwise_non_ties, 4)
                if pairwise_non_ties
                else None
            ),
        },
        "limitations": [
            "Opaque artifact labels must be resolved only after this aggregate is frozen.",
            "Confidence intervals and power analysis belong in the preregistered study analysis.",
            "This aggregate cannot substitute for intended-audience qualification evidence.",
        ],
    }
    atomic_write_json(output_path, result)
    return result
