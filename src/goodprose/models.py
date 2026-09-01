"""Typed boundaries for the GoodProse blog-writing dataset."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, StringConstraints

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
EditBurden = Annotated[int, Field(ge=1, le=5)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Split(StrEnum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"


class InputMethod(StrEnum):
    ORIGINAL_OUTLINE = "original_outline"
    ORIGINAL_DRAFT = "original_draft"
    DERIVED_BRIEF = "derived_brief"


class BlogPost(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    lineage_id: NonEmptyString
    title: NonEmptyString
    body_markdown: NonEmptyString
    source_path: NonEmptyString
    source_url: AnyUrl | None = None
    published_at: datetime | date | None = None


class Brief(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    post_id: NonEmptyString
    split: Split
    input: NonEmptyString
    input_method: InputMethod


class WritingPair(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    post_id: NonEmptyString
    lineage_id: NonEmptyString
    split: Split
    input: NonEmptyString
    input_method: InputMethod
    title: NonEmptyString
    output: NonEmptyString
    source_url: AnyUrl | None = None
    published_at: datetime | date | None = None


class EvalCase(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    input: NonEmptyString
    reference_output: NonEmptyString
    source_url: AnyUrl | None = None


class ModelOutput(StrictModel):
    id: NonEmptyString
    output: NonEmptyString


class ReviewChoice(StrEnum):
    A = "a"
    B = "b"
    TIE = "tie"


class SystemLabel(StrEnum):
    BASELINE = "baseline"
    CANDIDATE = "candidate"


class ReviewRow(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    input: NonEmptyString
    reference_output: NonEmptyString
    response_a: NonEmptyString
    response_b: NonEmptyString
    factuality_a_pass: bool | None = None
    factuality_b_pass: bool | None = None
    preference: ReviewChoice | None = None
    edit_burden_a: EditBurden | None = None
    edit_burden_b: EditBurden | None = None
    notes: str | None = None


class ReviewAssignment(StrictModel):
    id: NonEmptyString
    a: SystemLabel
    b: SystemLabel


class ReviewKey(StrictModel):
    version: Literal[1] = 1
    seed: int
    assignments: tuple[ReviewAssignment, ...]
