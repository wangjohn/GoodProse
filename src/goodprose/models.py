"""Typed models at GoodProse's data and evaluation boundaries."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import AnyUrl, BaseModel, ConfigDict, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class StrictModel(BaseModel):
    """Base model that rejects undeclared fields at system boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Split(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"


class EvalSplit(StrEnum):
    DEV = "dev"
    TEST = "test"
    PRIVATE_TEST = "private_test"


class Channel(StrEnum):
    EMAIL = "email"
    BLOG_POST = "blog_post"
    INTERNAL_MEMO = "internal_memo"


class ContextKind(StrEnum):
    NOTES = "notes"
    REFERENCE = "reference"
    POLICY = "policy"
    CONSTRAINT = "constraint"
    OTHER = "other"


class CreationMethod(StrEnum):
    HUMAN_REVISION = "human_revision"
    PAIRED_HISTORY = "paired_history"
    SYNTHETIC_DEGRADATION = "synthetic_degradation"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class InputOrigin(StrEnum):
    REAL_SOURCE_MATERIAL = "real_source_material"
    PAIRED_HISTORY = "paired_history"
    SYNTHETIC_DEGRADATION = "synthetic_degradation"


class InputContext(StrictModel):
    kind: ContextKind
    label: str | None = None
    content: str


class ExampleInput(StrictModel):
    source_material: NonEmptyString
    channel: Channel
    audience: NonEmptyString
    objective: NonEmptyString
    voice_profile_id: NonEmptyString
    constraints: tuple[str, ...] = ()
    context: tuple[InputContext, ...] = ()

    @model_validator(mode="after")
    def validate_unique_constraints(self) -> Self:
        _require_unique("constraints", self.constraints)
        return self


def _require_unique(name: str, values: tuple[str, ...]) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must contain unique values")


class Provenance(StrictModel):
    creation_method: CreationMethod
    lineage_group: NonEmptyString
    source_document_ids: tuple[str, ...]
    style_reference_ids: tuple[str, ...]
    license_ids: tuple[str, ...]
    source_url: AnyUrl | None = None
    source_revision: str | None = None

    @model_validator(mode="after")
    def validate_unique_identifiers(self) -> Self:
        for field_name in (
            "source_document_ids",
            "style_reference_ids",
            "license_ids",
        ):
            _require_unique(field_name, getattr(self, field_name))
        return self


class ExampleOutput(StrictModel):
    title: str | None = None
    body_markdown: NonEmptyString


class Review(StrictModel):
    privacy: ReviewStatus
    factuality: ReviewStatus
    objective_fulfillment: ReviewStatus
    audience_fit: ReviewStatus
    channel_fit: ReviewStatus
    house_style: ReviewStatus
    overall_quality: ReviewStatus
    reviewer: str | None = None
    notes: str | None = None

    def is_fully_approved(self) -> bool:
        statuses = (
            self.privacy,
            self.factuality,
            self.objective_fulfillment,
            self.audience_fit,
            self.channel_fit,
            self.house_style,
            self.overall_quality,
        )
        return all(status == ReviewStatus.PASSED for status in statuses)


class AnnotationSeed(StrictModel):
    """A pre-gold record that can be sent to an annotation workflow."""

    version: Literal[1]
    id: NonEmptyString
    split: Split
    input: ExampleInput
    provenance: Provenance

    @model_validator(mode="after")
    def validate_version(self) -> Self:
        if self.version != 1:
            raise ValueError("version must be 1")
        return self


class TrainingExample(StrictModel):
    version: Literal[1]
    id: NonEmptyString
    split: Split
    input: ExampleInput
    output: ExampleOutput
    provenance: Provenance
    review: Review

    @model_validator(mode="after")
    def validate_version(self) -> Self:
        if self.version != 1:
            raise ValueError("version must be 1")
        return self


class EvalExpected(StrictModel):
    gold_output_path: str | None = None
    required_facts: tuple[str, ...]
    optional_facts: tuple[str, ...] = ()
    forbidden_claims: tuple[str, ...]
    required_call_to_action: str | None = None
    acceptable_variations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_unique_facts(self) -> Self:
        for field_name in (
            "required_facts",
            "optional_facts",
            "forbidden_claims",
            "acceptable_variations",
        ):
            _require_unique(field_name, getattr(self, field_name))
        return self


class EvalProvenance(StrictModel):
    lineage_group: NonEmptyString
    target_document_ids: tuple[str, ...]
    input_origin: InputOrigin
    reviewers: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_unique_identifiers(self) -> Self:
        _require_unique("target_document_ids", self.target_document_ids)
        _require_unique("reviewers", self.reviewers)
        return self


class EvalCase(StrictModel):
    version: Literal[1]
    id: NonEmptyString
    split: EvalSplit
    input: ExampleInput
    expected: EvalExpected
    provenance: EvalProvenance

    @model_validator(mode="after")
    def validate_version(self) -> Self:
        if self.version != 1:
            raise ValueError("version must be 1")
        return self
