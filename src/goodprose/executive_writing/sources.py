"""Named-source manifests, profile specifications, and repository-layout validation.

This module implements the machine-readable contract for the executive-writing
named-source program: source audit routes, data-availability reports against
the frozen standalone threshold, provisional rights assessments, abstract
non-identity profile specifications, content-controlled evaluation subsets,
and source-specific run configurations.

Nothing here approves material for training. Only the user or qualified
counsel may promote a source to ``training_approved``; every validator in this
module rejects that classification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)

MANIFEST_ID = "named-sources-v1"
EVALUATION_MANIFEST_ID = "source-profiles-v1"
ASSIGNMENT_ID = "ox-source-artifacts-implementation-v1"
MODEL_IDENTIFIER = "stealth/ox-alpha"
PROVIDER = "OpenRouter through Ori/OpenCode"
PROVENANCE_RECORD = (
    "programs/executive-writing/experiments/ox-source-artifacts-implementation-v1.json"
)

REQUESTED_PEOPLE: tuple[str, ...] = (
    "Patrick Collison",
    "Paul Graham",
    "Sam Altman",
    "Joel Spolsky",
    "Fred Wilson",
    "David Heinemeier Hansson",
    "Jason Fried",
    "Simon Willison",
    "Cory Doctorow",
    "Jeff Bezos",
    "Andy Jassy",
)

COMMON_EVALUATION_CASE_IDS: tuple[str, ...] = (
    "b1-001-migration-email",
    "b1-004-hiring-memo",
    "b1-007-launch-decision-memo",
    "b1-011-concise-onboarding-revision",
    "b1-015-europe-strategy-update",
    "b1-020-cache-blog",
)

THRESHOLD_MIN_EFFECTIVE_TOKENS = 50_000
THRESHOLD_MIN_INDEPENDENT_EXAMPLES = 100
THRESHOLD_MIN_RELEVANT_GENRES = 3
THRESHOLD_MIN_HELD_OUT_CASES = 30

PROFILE_CARD_RETRIEVAL_COVERAGE_ARCHITECTURE = "profile_card_retrieval_coverage"

RightsClassification = Literal[
    "training_approved",
    "private_research_only",
    "evaluation_only",
    "permission_required",
    "excluded",
]

SourceRouteType = Literal[
    "official_personal",
    "official_company",
    "court",
    "government",
    "secondary_lead",
]

AvailabilityOutlook = Literal["plausibly_reachable", "clearly_unreachable", "unknown"]

ThresholdComponentName = Literal[
    "effective_clean_tokens",
    "independent_examples",
    "genre_coverage",
    "held_out_cases",
]

ProtocolName = Literal["topic_swap", "leave_topic_out", "leave_time_out"]

MAX_METADATA_FIELD_CHARS = 800


def _require_https(value: object) -> object:
    if not str(value).startswith("https://"):
        raise ValueError("source evidence URLs must be HTTPS")
    return value


HttpsCanonicalUrl = Annotated[HttpUrl, BeforeValidator(_require_https)]


class SourceValidationError(ValueError):
    """Raised when a manifest, config, or repository layout violates the contract."""


def _check_metadata_text(value: object) -> None:
    """Reject quoted passages and oversized text in metadata fields."""

    if isinstance(value, str):
        if '"' in value:
            raise SourceValidationError(
                "metadata fields must not contain quoted passages or distinctive phrases"
            )
        if len(value) > MAX_METADATA_FIELD_CHARS:
            raise SourceValidationError(
                f"metadata field exceeds {MAX_METADATA_FIELD_CHARS} characters; "
                "it may contain copied source bodies"
            )
    elif isinstance(value, (list, tuple)):
        for item in value:
            _check_metadata_text(item)


class StrictMetadataModel(BaseModel):
    """Base model that forbids extras and screens free-text metadata fields."""

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def _screen_metadata_text(self) -> StrictMetadataModel:
        for name in type(self).model_fields:
            _check_metadata_text(getattr(self, name))
        return self


class DefaultThreshold(StrictMetadataModel):
    effective_clean_tokens: int
    independent_examples: int
    relevant_genres: int
    held_out_cases: int

    @model_validator(mode="after")
    def _frozen_defaults(self) -> DefaultThreshold:
        expected = (
            THRESHOLD_MIN_EFFECTIVE_TOKENS,
            THRESHOLD_MIN_INDEPENDENT_EXAMPLES,
            THRESHOLD_MIN_RELEVANT_GENRES,
            THRESHOLD_MIN_HELD_OUT_CASES,
        )
        actual = (
            self.effective_clean_tokens,
            self.independent_examples,
            self.relevant_genres,
            self.held_out_cases,
        )
        if actual != expected:
            raise SourceValidationError(f"default threshold must stay frozen at {expected}")
        return self


class SourceRoute(StrictMetadataModel):
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    title: str
    canonical_url: HttpsCanonicalUrl
    controller: str
    source_type: SourceRouteType
    genres: list[str] = Field(min_length=1)
    availability_proxy: str
    rights_or_terms_url: HttpUrl | None = None
    evidence_fact: str
    primary: bool


class PublicEmailFinding(StrictMetadataModel):
    verified_collection_found: bool
    strongest_lead_url: HttpUrl | None = None
    finding: str

    @model_validator(mode="after")
    def _no_verified_email_collection(self) -> PublicEmailFinding:
        if self.verified_collection_found:
            raise SourceValidationError(
                "no verified authored public-email collection may be asserted "
                "without Codex-verified evidence"
            )
        return self


class ThresholdComponentAssessment(StrictMetadataModel):
    component: ThresholdComponentName
    status: Literal["unverified", "met", "unmet"]
    note: str


class DataAvailabilityReport(StrictMetadataModel):
    default_threshold: DefaultThreshold
    outlook: AvailabilityOutlook
    component_assessments: list[ThresholdComponentAssessment] = Field(min_length=4)
    notes: list[str]

    @model_validator(mode="after")
    def _cover_every_component(self) -> DataAvailabilityReport:
        names = [entry.component for entry in self.component_assessments]
        if len(names) != 4 or set(names) != {
            "effective_clean_tokens",
            "independent_examples",
            "genre_coverage",
            "held_out_cases",
        }:
            raise SourceValidationError("threshold components must appear exactly once each")
        return self

    def all_components_met(self) -> bool:
        return all(entry.status == "met" for entry in self.component_assessments)


class RightsAssessment(StrictMetadataModel):
    classification: RightsClassification
    approved_uses: list[str] = Field(min_length=1)
    evidence_url: HttpsCanonicalUrl
    reviewer_role: str = Field(min_length=3)
    review_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    unresolved_questions: list[str]
    promotion_authority: str = Field(min_length=3)

    @model_validator(mode="after")
    def _never_training_approved(self) -> RightsAssessment:
        if self.classification == "training_approved":
            raise SourceValidationError(
                "only the user or qualified counsel may promote a source to "
                "training_approved; agents must not record it"
            )
        return self


class ProfileTrait(StrictMetadataModel):
    trait: str
    supporting_source_ids: list[str] = Field(min_length=1)


class ProtocolDeclaration(StrictMetadataModel):
    protocol: ProtocolName
    status: Literal["declared", "current_limitation"]
    detail: str


class ProfileSpecification(StrictMetadataModel):
    profile_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    production_name: str
    description: str
    traits: list[ProfileTrait] = Field(min_length=2, max_length=5)
    anti_impersonation_limits: list[str] = Field(min_length=2)


class EvaluationSubset(StrictMetadataModel):
    slice_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    case_ids: list[str]
    protocols: list[ProtocolDeclaration] = Field(min_length=3)

    @model_validator(mode="after")
    def _content_controlled_six(self) -> EvaluationSubset:
        if len(self.case_ids) != 6 or len(set(self.case_ids)) != 6:
            raise SourceValidationError(
                "evaluation subset must contain exactly six unique case IDs"
            )
        if set(self.case_ids) != set(COMMON_EVALUATION_CASE_IDS):
            raise SourceValidationError(
                "evaluation subset must use the common content-controlled B1 case set"
            )
        declared = {entry.protocol for entry in self.protocols}
        required = {"topic_swap", "leave_topic_out", "leave_time_out"}
        missing = sorted(required - declared)
        extra = sorted(declared - required)
        if len(self.protocols) != 3 or missing or extra:
            raise SourceValidationError(
                f"protocol coverage mismatch; missing={missing} unknown={extra}"
            )
        return self


class RunConfigReference(StrictMetadataModel):
    config_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    config_path: str
    architecture: Literal[
        "profile_card_retrieval_coverage",
        "standalone_adapter",
    ]
    standalone_eligible: bool
    blocker: str
    third_party_training_text_allowed: bool
    evaluation_slice_id: str
    exploratory_label: str

    @model_validator(mode="after")
    def _coverage_architecture_no_third_party_text(self) -> RunConfigReference:
        if self.architecture == "standalone_adapter":
            raise SourceValidationError(
                "source-specific run configs must select the profile-card/retrieval "
                "coverage architecture"
            )
        if self.third_party_training_text_allowed:
            raise SourceValidationError("third-party training text is not allowed in these runs")
        return self


class SourceProfile(StrictMetadataModel):
    person: str
    source_routes: list[SourceRoute] = Field(min_length=1)
    public_email: PublicEmailFinding
    availability: DataAvailabilityReport
    rights: RightsAssessment
    profile: ProfileSpecification
    evaluation_subset: EvaluationSubset
    run_configuration: RunConfigReference

    @model_validator(mode="after")
    def _internal_consistency(self) -> SourceProfile:
        route_ids = {route.source_id for route in self.source_routes}
        for trait in self.profile.traits:
            unknown = set(trait.supporting_source_ids) - route_ids
            if unknown:
                raise SourceValidationError(
                    f"profile traits reference unknown source IDs {sorted(unknown)}"
                )
        lowered = self.person.lower()
        for token in lowered.split():
            if len(token) >= 4 and token in self.profile.production_name.lower():
                raise SourceValidationError(
                    "production-facing profile name must be descriptive, not the person identity"
                )
        if self.run_configuration.evaluation_slice_id != self.evaluation_subset.slice_id:
            raise SourceValidationError("run configuration references a different evaluation slice")
        check_standalone_eligibility(
            self.run_configuration,
            self.availability,
            self.rights,
        )
        return self


class NamedSourceManifest(StrictMetadataModel):
    version: int
    manifest_id: str
    assignment_id: str
    generated_by_model: str
    provider: str
    provenance_record: str
    people: list[SourceProfile]

    @model_validator(mode="after")
    def _complete_and_unique(self) -> NamedSourceManifest:
        if (
            self.version != 1
            or self.manifest_id != MANIFEST_ID
            or self.assignment_id != ASSIGNMENT_ID
            or self.generated_by_model != MODEL_IDENTIFIER
            or self.provider != PROVIDER
            or self.provenance_record != PROVENANCE_RECORD
        ):
            raise SourceValidationError("named-source manifest provenance header is not frozen")
        persons = [entry.person for entry in self.people]
        if sorted(persons) != sorted(REQUESTED_PEOPLE):
            raise SourceValidationError("manifest must contain every requested person exactly once")
        seen_sources: list[str] = []
        seen_profiles: list[str] = []
        seen_slices: list[str] = []
        seen_configs: list[str] = []
        for entry in self.people:
            seen_sources.extend(route.source_id for route in entry.source_routes)
            seen_profiles.append(entry.profile.profile_id)
            seen_slices.append(entry.evaluation_subset.slice_id)
            seen_configs.append(entry.run_configuration.config_id)
        for label, values in (
            ("source ID", seen_sources),
            ("profile ID", seen_profiles),
            ("evaluation-slice ID", seen_slices),
            ("run-config ID", seen_configs),
        ):
            duplicates = sorted({value for value in values if values.count(value) > 1})
            if duplicates:
                raise SourceValidationError(f"duplicate {label}s: {duplicates}")
        return self


class EvalSlice(StrictMetadataModel):
    slice_id: str
    profile_id: str
    case_ids: list[str]
    protocols: list[ProtocolDeclaration]

    @model_validator(mode="after")
    def _content_controlled_six(self) -> EvalSlice:
        if len(self.case_ids) != 6 or len(set(self.case_ids)) != 6:
            raise SourceValidationError("eval slice must contain exactly six unique case IDs")
        if set(self.case_ids) != set(COMMON_EVALUATION_CASE_IDS):
            raise SourceValidationError("eval slice must use the common B1 case set")
        protocols = [entry.protocol for entry in self.protocols]
        if len(protocols) != 3 or set(protocols) != {
            "topic_swap",
            "leave_topic_out",
            "leave_time_out",
        }:
            raise SourceValidationError("eval slice must declare each control protocol once")
        return self


class SourceProfilesEvalManifest(StrictMetadataModel):
    version: int
    eval_id: str
    tier: str
    benchmark_id: str
    shared_case_ids: list[str]
    content_control_note: str
    provenance_record: str
    slices: list[EvalSlice]

    @model_validator(mode="after")
    def _consistent_slices(self) -> SourceProfilesEvalManifest:
        if (
            self.version != 1
            or self.eval_id != EVALUATION_MANIFEST_ID
            or self.benchmark_id != "goodprose-b1-v1"
            or self.provenance_record != PROVENANCE_RECORD
        ):
            raise SourceValidationError("source-profile evaluation header is not frozen")
        if len(self.slices) != len(REQUESTED_PEOPLE):
            raise SourceValidationError("evaluation manifest must contain exactly eleven slices")
        if self.shared_case_ids != list(COMMON_EVALUATION_CASE_IDS):
            raise SourceValidationError(
                "shared case IDs must equal the frozen common B1 evaluation set"
            )
        slice_ids = [entry.slice_id for entry in self.slices]
        profile_ids = [entry.profile_id for entry in self.slices]
        for label, values in (("slice ID", slice_ids), ("profile ID", profile_ids)):
            duplicates = sorted({value for value in values if values.count(value) > 1})
            if duplicates:
                raise SourceValidationError(
                    f"duplicate {label}s in evaluation manifest: {duplicates}"
                )
        for entry in self.slices:
            if sorted(entry.case_ids) != sorted(COMMON_EVALUATION_CASE_IDS):
                raise SourceValidationError(
                    f"slice {entry.slice_id} does not use the shared six-case set"
                )
        return self


class RunConfigDocument(StrictMetadataModel):
    config_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    label: str
    person: str
    profile_id: str
    architecture: Literal["profile_card_retrieval_coverage"]
    standalone_eligible: bool
    blocker: str
    third_party_training_text: bool
    purpose: Literal["exploratory_research_not_impersonation_or_endorsement"]
    source_manifest_id: str
    source_manifest_version: int
    evaluation_benchmark_id: str
    evaluation_slice_id: str
    provenance_record: str

    @model_validator(mode="after")
    def _no_third_party_training_text(self) -> RunConfigDocument:
        if self.third_party_training_text:
            raise SourceValidationError("these runs must use no third-party text for training")
        if self.provenance_record != PROVENANCE_RECORD:
            raise SourceValidationError("run config does not reference frozen Ox provenance")
        return self


class ValidatedLayout(BaseModel):
    manifest: NamedSourceManifest
    eval_manifest: SourceProfilesEvalManifest
    configs: dict[str, RunConfigDocument]


def check_standalone_eligibility(
    config: RunConfigDocument | RunConfigReference,
    availability: DataAvailabilityReport,
    rights: RightsAssessment,
) -> None:
    """Reject standalone eligibility unless thresholds and rights both allow it."""

    if not getattr(config, "standalone_eligible", False):
        return
    blockers: list[str] = []
    if rights.classification != "training_approved":
        blockers.append(f"rights classification is {rights.classification}")
    for component in availability.component_assessments:
        if component.status != "met":
            blockers.append(f"threshold component {component.component} is {component.status}")
    if blockers:
        raise SourceValidationError(
            "standalone eligibility requires training-approved rights and every "
            f"threshold component met; blocked by: {'; '.join(blockers)}"
        )


def load_named_source_manifest(path: Path) -> NamedSourceManifest:
    """Load and validate the committed named-source manifest."""

    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        return NamedSourceManifest.model_validate(data)
    except SourceValidationError:
        raise
    except ValueError as exc:
        raise SourceValidationError(str(exc)) from exc


def load_evaluation_manifest(path: Path) -> SourceProfilesEvalManifest:
    """Load and validate the source-profiles evaluation manifest."""

    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        return SourceProfilesEvalManifest.model_validate(data)
    except SourceValidationError:
        raise
    except ValueError as exc:
        raise SourceValidationError(str(exc)) from exc


def load_run_config(path: Path) -> RunConfigDocument:
    """Load and validate one source-specific run configuration file."""

    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        return RunConfigDocument.model_validate(data)
    except SourceValidationError:
        raise
    except ValueError as exc:
        raise SourceValidationError(str(exc)) from exc


def validate_repository_layout(
    manifest_path: Path,
    eval_manifest_path: Path,
    configs_dir: Path,
) -> ValidatedLayout:
    """Validate manifest, evaluation manifest, and all eleven run configs together."""

    manifest = load_named_source_manifest(manifest_path)
    eval_manifest = load_evaluation_manifest(eval_manifest_path)
    slices_by_profile = {slice_.profile_id: slice_ for slice_ in eval_manifest.slices}
    expected_profile_ids = {entry.profile.profile_id for entry in manifest.people}
    if set(slices_by_profile) != expected_profile_ids:
        raise SourceValidationError(
            "evaluation manifest profile IDs do not exactly match the source manifest"
        )

    configs: dict[str, RunConfigDocument] = {}
    for profile_entry in manifest.people:
        profile_id = profile_entry.profile.profile_id
        config_path = configs_dir / f"{profile_id}.json"
        expected_config_ref = (
            f"programs/executive-writing/configs/source-profiles/{profile_id}.json"
        )
        if profile_entry.run_configuration.config_path != expected_config_ref:
            raise SourceValidationError(
                f"profile {profile_id} has an unexpected config path reference"
            )
        if not config_path.is_file():
            raise SourceValidationError(
                f"missing run config for profile {profile_id}: {config_path}"
            )
        config = load_run_config(config_path)
        if config.profile_id != profile_id:
            raise SourceValidationError(
                f"config {config.config_id} references unknown profile {config.profile_id}"
            )
        reference = profile_entry.run_configuration
        if (
            config.config_id != reference.config_id
            or config.architecture != reference.architecture
            or config.standalone_eligible != reference.standalone_eligible
            or config.blocker != reference.blocker
            or config.third_party_training_text != reference.third_party_training_text_allowed
        ):
            raise SourceValidationError(
                f"config {config.config_id} disagrees with its manifest reference"
            )
        if config.person != profile_entry.person:
            raise SourceValidationError(
                f"config {config.config_id} targets {config.person}, not {profile_entry.person}"
            )
        if config.profile_id not in slices_by_profile:
            raise SourceValidationError(
                f"config {config.config_id} references profile with no evaluation slice"
            )
        if config.evaluation_slice_id != slices_by_profile[profile_id].slice_id:
            raise SourceValidationError(
                f"config {config.config_id} references an unknown evaluation slice"
            )
        if config.source_manifest_id != manifest.manifest_id:
            raise SourceValidationError(
                f"config {config.config_id} references unknown manifest {config.source_manifest_id}"
            )
        if config.source_manifest_version != manifest.version:
            raise SourceValidationError(
                f"config {config.config_id} pins manifest version {config.source_manifest_version}"
            )
        if config.evaluation_benchmark_id != eval_manifest.benchmark_id:
            raise SourceValidationError(
                f"config {config.config_id} references unknown benchmark "
                f"{config.evaluation_benchmark_id}"
            )
        check_standalone_eligibility(config, profile_entry.availability, profile_entry.rights)
        if config.config_id in configs:
            raise SourceValidationError(f"duplicate run-config ID {config.config_id}")
        configs[config.config_id] = config

    expected = expected_profile_ids
    found = {path.stem for path in configs_dir.glob("*.json")}
    unexpected = sorted(found - expected)
    if unexpected:
        raise SourceValidationError(f"unexpected run configs present: {unexpected}")

    return ValidatedLayout(manifest=manifest, eval_manifest=eval_manifest, configs=configs)
