"""Typed boundaries for the GoodProse blog-writing dataset."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
EditBurden = Annotated[int, Field(ge=1, le=5)]
UnitInterval = Annotated[float, Field(ge=0, le=1)]


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


class ReviewStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"


class PromptForm(StrEnum):
    SENTENCE_REWRITE = "sentence_rewrite"
    BULLET_NOTES = "bullet_notes"
    ROUGH_SENTENCES = "rough_sentences"
    PHRASES_AND_THOUGHTS = "phrases_and_thoughts"
    SECTION_BRIEF = "section_brief"
    POST_BRIEF = "post_brief"
    ROUGH_DRAFT = "rough_draft"
    NEAR_FINAL_DRAFT = "near_final_draft"


# Forms whose input is expected to share long verbatim runs with the target.
DRAFT_PROMPT_FORMS = frozenset({PromptForm.ROUGH_DRAFT, PromptForm.NEAR_FINAL_DRAFT})


class HistoryStatus(StrEnum):
    MATCHED = "matched"
    PARTIAL = "partial"
    NOT_FOUND = "not_found"


class ContextStatus(StrEnum):
    RECOVERED = "recovered"
    PARTIAL = "partial"
    MISSING = "missing"


class ExternalPlatform(StrEnum):
    ASSEMBLED = "assembled"
    MEDIUM = "medium"


class ExternalSourceStatus(StrEnum):
    PRIVATE_MARKDOWN_RECOVERED = "private_markdown_recovered"
    PUBLIC_PAGE_ONLY = "public_page_only"


class BlogPost(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    lineage_id: NonEmptyString
    title: NonEmptyString
    body_markdown: NonEmptyString
    source_path: NonEmptyString
    source_url: AnyUrl | None = None
    published_at: datetime | date | None = None


class SplitAssignment(StrictModel):
    version: Literal[1] = 1
    lineage_id: NonEmptyString
    split: Split
    frozen_at: date
    rationale: NonEmptyString


class SemanticChunk(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    post_id: NonEmptyString
    lineage_id: NonEmptyString
    split: Split
    ordinal: Annotated[int, Field(ge=1)]
    headings: tuple[NonEmptyString, ...] = ()
    target: NonEmptyString
    source_start: Annotated[int, Field(ge=0)]
    source_end: Annotated[int, Field(ge=1)]
    word_count: Annotated[int, Field(ge=1)]
    approx_token_count: Annotated[int, Field(ge=1)]
    target_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    exceeds_target_size: bool = False
    review_status: ReviewStatus = ReviewStatus.CANDIDATE

    @model_validator(mode="after")
    def validate_source_span(self) -> SemanticChunk:
        if self.source_end <= self.source_start:
            raise ValueError("source_end must be greater than source_start")
        return self


class SupplementalChunkSpec(StrictModel):
    """A reviewed exact post span that supplements the default semantic chunks."""

    version: Literal[1] = 1
    id: NonEmptyString
    post_id: NonEmptyString
    target: NonEmptyString
    review_status: ReviewStatus = ReviewStatus.CANDIDATE


class ChunkExclusionSpec(StrictModel):
    """A reviewed default chunk that must not enter the candidate inventory."""

    version: Literal[1] = 1
    chunk_id: NonEmptyString
    reason: NonEmptyString


class SyntheticPromptCandidate(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    chunk_id: NonEmptyString
    post_id: NonEmptyString
    lineage_id: NonEmptyString
    split: Split
    input_method: Literal["derived_brief"] = "derived_brief"
    provenance: Literal["synthetic_from_published_target"] = "synthetic_from_published_target"
    prompt_form: PromptForm
    input: NonEmptyString
    target_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    review_status: ReviewStatus = ReviewStatus.CANDIDATE
    reviewer_notes: tuple[NonEmptyString, ...] = ()
    approved_system_prompt_sha256: (
        Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None
    ) = None
    """The system prompt this record was approved against; a training example is the whole
    conversation, so changing the system prompt invalidates the approval."""


class SyntheticPromptDraft(StrictModel):
    version: Literal[1] = 1
    chunk_id: NonEmptyString
    prompt_form: PromptForm
    input: NonEmptyString


class ProvenanceInventory(StrictModel):
    version: Literal[1] = 1
    post_id: NonEmptyString
    lineage_id: NonEmptyString
    split: Split
    body_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    history_status: HistoryStatus
    context_status: ContextStatus
    source_ids: tuple[NonEmptyString, ...] = ()
    notes: NonEmptyString


class ExternalPostCatalog(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    lineage_id: NonEmptyString
    title: NonEmptyString
    platform: ExternalPlatform
    source_url: AnyUrl
    published_at: date
    author: NonEmptyString = "John Wang"
    source_status: ExternalSourceStatus
    review_status: ReviewStatus = ReviewStatus.CANDIDATE
    notes: NonEmptyString


class ExternalSourceMapping(StrictModel):
    version: Literal[1] = 1
    post_id: NonEmptyString
    source_path: NonEmptyString


class AuthenticInputMapping(StrictModel):
    version: Literal[1] = 1
    post_id: NonEmptyString
    source_path: NonEmptyString
    start_line: Annotated[int, Field(ge=1)]
    end_line: Annotated[int, Field(ge=1)] | None = None
    input_method: InputMethod

    @model_validator(mode="after")
    def validate_mapping(self) -> AuthenticInputMapping:
        if self.input_method is InputMethod.DERIVED_BRIEF:
            raise ValueError("authentic input mappings cannot use derived_brief")
        if self.end_line is not None and self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self


class ExternalPostSample(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    lineage_id: NonEmptyString
    title: NonEmptyString
    platform: ExternalPlatform
    source_url: AnyUrl
    published_at: date
    source_path: NonEmptyString
    source_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    raw_markdown: NonEmptyString
    word_count: Annotated[int, Field(ge=1)]
    review_status: ReviewStatus = ReviewStatus.CANDIDATE
    notes: NonEmptyString


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


class PairTextExclusion(StrictModel):
    """An exact reviewed span removed when assembling the canonical SFT pairs."""

    version: Literal[1] = 1
    pair_id: NonEmptyString
    field: Literal["input", "output"]
    text: NonEmptyString
    reason: NonEmptyString


class EvalCase(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    lineage_id: NonEmptyString
    input: NonEmptyString
    input_method: InputMethod
    reference_output: NonEmptyString
    target_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
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
    version: Literal[2] = 2
    id: NonEmptyString
    lineage_id: NonEmptyString
    input_method: InputMethod
    input: NonEmptyString
    response_a: NonEmptyString
    response_b: NonEmptyString
    factuality_a_pass: bool | None = None
    factuality_b_pass: bool | None = None
    unsupported_claims_a: tuple[NonEmptyString, ...] = ()
    unsupported_claims_b: tuple[NonEmptyString, ...] = ()
    instruction_following_a_pass: bool | None = None
    instruction_following_b_pass: bool | None = None
    voice_preference: ReviewChoice | None = None
    overall_preference: ReviewChoice | None = None
    edit_burden_a: EditBurden | None = None
    edit_burden_b: EditBurden | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_unsupported_claims(self) -> ReviewRow:
        for label, passed, claims in (
            ("a", self.factuality_a_pass, self.unsupported_claims_a),
            ("b", self.factuality_b_pass, self.unsupported_claims_b),
        ):
            if passed is True and claims:
                raise ValueError(
                    f"unsupported_claims_{label} must be empty after a factuality pass"
                )
            if passed is False and not claims:
                raise ValueError(
                    f"unsupported_claims_{label} must list at least one finding after a failure"
                )
        return self


class ReviewAssignment(StrictModel):
    id: NonEmptyString
    a: SystemLabel
    b: SystemLabel


class ReviewKey(StrictModel):
    version: Literal[2] = 2
    seed: int
    baseline_run_id: NonEmptyString | None = None
    candidate_run_id: NonEmptyString | None = None
    assignments: tuple[ReviewAssignment, ...]


class DecodingSettings(StrictModel):
    temperature: Annotated[float, Field(ge=0)] = 0.7
    top_p: UnitInterval = 0.9
    repetition_penalty: Annotated[float, Field(ge=1)] = 1.05
    max_new_tokens: Annotated[int, Field(ge=1)]
    seed: int

    @property
    def do_sample(self) -> bool:
        return self.temperature > 0


class PreferencePair(StrictModel):
    """A DPO record: the author's published text against the current model's attempt."""

    version: Literal[1] = 1
    id: NonEmptyString
    lineage_id: NonEmptyString
    prompt: tuple[dict[str, str], ...]
    chosen: NonEmptyString
    rejected: NonEmptyString
    rejected_run_id: NonEmptyString

    @model_validator(mode="after")
    def validate_prompt(self) -> PreferencePair:
        roles = tuple(message.get("role") for message in self.prompt)
        if roles != ("system", "user"):
            raise ValueError("preference prompt must contain exactly system and user turns")
        if self.chosen == self.rejected:
            raise ValueError("chosen and rejected completions are identical")
        return self


class GenerationRunManifest(StrictModel):
    version: Literal[1] = 1
    run_id: NonEmptyString
    role: SystemLabel
    model_id: NonEmptyString
    base_model_id: NonEmptyString
    base_model_revision: NonEmptyString
    tokenizer_revision: NonEmptyString
    adapter_id: NonEmptyString | None = None
    prompt_strategy: NonEmptyString
    chat_template_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    rendered_prompt_prefix_sha256: (
        Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None
    ) = None
    system_prompt_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    cases_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    dataset_manifest_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    decoding: DecodingSettings


class DecisionRules(StrictModel):
    version: Literal[1] = 1
    require_all_candidate_factuality_passes: bool = True
    require_all_candidate_instruction_passes: bool = True
    require_candidate_overall_case_advantage: bool = True
    require_no_lineage_losses: bool = True
    minimum_lineage_wins: Annotated[int, Field(ge=0)] = 1
    minimum_mean_edit_burden_improvement: Annotated[float, Field(ge=0)] = 0.5
