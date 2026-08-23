"""Versioned first-evidence benchmark models, builders, and deterministic scoring."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.jsonl import atomic_write, serialize_jsonl, sha256_bytes, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

SCORECARD_WEIGHTS = {
    "fidelity": 0.35,
    "clarity_coherence": 0.20,
    "concision": 0.15,
    "organization_actionability": 0.15,
    "audience_format": 0.10,
    "profile_control": 0.05,
}
SCORER_VERSION = "goodprose-deterministic-v1"
IDENTITY_SIGNAL_PATTERN = (
    r"(?i)\b(as|like)\s+(patrick collison|paul graham|sam altman|joel spolsky|"
    r"fred wilson|david heinemeier hansson|jason fried|simon willison|"
    r"cory doctorow|jeff bezos|andy jassy)\b"
)


class StrictModel(BaseModel):
    """Immutable program boundary that rejects undeclared fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class TaskFamily(StrEnum):
    ROUGH_NOTES_TO_EXECUTIVE_EMAIL = "rough_notes_to_executive_email"
    ROUGH_NOTES_TO_INTERNAL_MEMO = "rough_notes_to_internal_memo"
    MEETING_TRANSCRIPT_TO_DECISION_MEMO = "meeting_transcript_to_decision_memo"
    TECHNICAL_SOURCE_TO_ENGINEERING_DOCUMENT = "technical_source_to_engineering_document"
    LONG_DRAFT_TO_CONCISE_REVISION = "long_draft_to_concise_revision"
    DISORGANIZED_DRAFT_TO_COHERENT_REVISION = "disorganized_draft_to_coherent_revision"
    SOURCE_DOCUMENTS_TO_STRATEGY_UPDATE = "source_documents_to_strategy_update"
    ANNOUNCEMENT_OR_LAUNCH_MEMO = "announcement_or_launch_memo"
    SENSITIVE_INTERNAL_COMMUNICATION = "sensitive_internal_communication"
    SHORT_FORM_POST_OR_THREAD = "short_form_post_or_thread"
    BLOG_POST_OR_EXPLANATORY_ESSAY = "blog_post_or_explanatory_essay"
    AUDIENCE_ADAPTATION = "audience_adaptation"
    MINIMAL_EDIT_REVISION = "minimal_edit_revision"
    CONTENT_CONTROLLED_PROFILE_RENDERING = "content_controlled_profile_rendering"


class OutputFormat(StrEnum):
    EMAIL = "email"
    MEMO = "memo"
    DOCUMENT = "document"
    BLOG_POST = "blog_post"
    SHORT_POST = "short_post"


class BenchmarkInput(StrictModel):
    task_family: TaskFamily
    output_format: OutputFormat
    source_material: NonEmpty
    audience: NonEmpty
    objective: NonEmpty
    profile_id: NonEmpty
    constraints: tuple[str, ...] = ()

    @model_validator(mode="after")
    def unique_constraints(self) -> Self:
        _require_unique("constraints", self.constraints)
        return self


class TextExpectation(StrictModel):
    id: NonEmpty
    description: NonEmpty
    any_of: tuple[NonEmpty, ...] = Field(min_length=1)
    critical: bool = True

    @model_validator(mode="after")
    def unique_aliases(self) -> Self:
        _require_unique("any_of", self.any_of)
        return self


class BenchmarkExpected(StrictModel):
    required_facts: tuple[TextExpectation, ...] = ()
    forbidden_claims: tuple[TextExpectation, ...] = ()
    required_placeholders: tuple[NonEmpty, ...] = ()
    required_call_to_action: tuple[NonEmpty, ...] = ()
    opening_any_of: tuple[NonEmpty, ...] = ()
    must_preserve_spans: tuple[NonEmpty, ...] = ()
    min_words: int = Field(default=1, ge=1)
    max_words: int = Field(ge=1)
    max_source_change_ratio: float | None = Field(default=None, ge=0, le=1)
    subject_required: bool = False
    headings_required: bool = False
    headings_prohibited: bool = False

    @model_validator(mode="after")
    def valid_expectations(self) -> Self:
        if self.min_words > self.max_words:
            raise ValueError("min_words cannot exceed max_words")
        if self.headings_required and self.headings_prohibited:
            raise ValueError("headings cannot be both required and prohibited")
        for field_name in (
            "required_placeholders",
            "required_call_to_action",
            "opening_any_of",
            "must_preserve_spans",
        ):
            _require_unique(field_name, getattr(self, field_name))
        _require_unique("required fact IDs", tuple(item.id for item in self.required_facts))
        _require_unique("forbidden claim IDs", tuple(item.id for item in self.forbidden_claims))
        return self


class SourceCase(StrictModel):
    version: Literal[1]
    id: NonEmpty
    tier: Literal["B1"]
    input: BenchmarkInput
    expected: BenchmarkExpected
    lineage_group: NonEmpty
    topic: NonEmpty
    time_bucket: NonEmpty
    adversarial_features: tuple[NonEmpty, ...] = ()
    difficulty: Literal["standard", "difficult"]
    authored_by: Literal["codex"]
    authored_at: datetime
    rights_status: Literal["evaluation_approved_project_owned"]

    @model_validator(mode="after")
    def unique_tags(self) -> Self:
        _require_unique("adversarial_features", self.adversarial_features)
        return self


class BenchmarkProvenance(StrictModel):
    creation_method: Literal["project_authored"]
    authored_by: Literal["codex"]
    authored_at: datetime
    rights_status: Literal["evaluation_approved_project_owned"]
    lineage_group: NonEmpty
    topic: NonEmpty
    time_bucket: NonEmpty
    source_material_sha256: Sha256


class BenchmarkCase(StrictModel):
    version: Literal[1]
    id: NonEmpty
    tier: Literal["B1"]
    input: BenchmarkInput
    expected: BenchmarkExpected
    provenance: BenchmarkProvenance
    adversarial_features: tuple[NonEmpty, ...] = ()
    difficulty: Literal["standard", "difficult"]

    @model_validator(mode="after")
    def validate_source_hash(self) -> Self:
        actual = content_sha256(self.input.source_material)
        if self.provenance.source_material_sha256 != actual:
            raise ValueError(f"source_material_sha256 mismatch for {self.id}")
        return self


class BenchmarkManifest(StrictModel):
    version: Literal[1]
    benchmark_id: NonEmpty
    tier: Literal["B1"]
    status: Literal["search_development"]
    case_count: int = Field(ge=1)
    case_schema_sha256: Sha256
    cases_sha256: Sha256
    source_cases_sha256: Sha256
    scorer_version: Literal["goodprose-deterministic-v1"]
    scorecard_weights: dict[str, float]
    task_family_counts: dict[str, int]
    output_format_counts: dict[str, int]
    adversarial_feature_counts: dict[str, int]
    creation_method: Literal["project_authored"]
    rights_status: Literal["evaluation_approved_project_owned"]
    limitations: tuple[NonEmpty, ...]


class CheckResult(StrictModel):
    id: NonEmpty
    passed: bool
    critical: bool
    description: NonEmpty


class CaseScore(StrictModel):
    scorer_version: Literal["goodprose-deterministic-v1"]
    case_id: NonEmpty
    candidate_id: NonEmpty
    output_sha256: Sha256
    word_count: int = Field(ge=0)
    source_change_ratio: float | None
    dimensions: dict[str, float]
    development_score: float
    passes_hard_gates: bool
    checks: tuple[CheckResult, ...]
    errors: tuple[str, ...]


def _require_unique(name: str, values: tuple[str, ...]) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must contain unique values")


def _normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def content_sha256(value: str) -> str:
    return sha256(_normalized(value).encode("utf-8")).hexdigest()


def _matches_any(output: str, aliases: tuple[str, ...]) -> bool:
    normalized = _normalized(output)
    return any(_normalized(alias) in normalized for alias in aliases)


def _word_count(value: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", value, flags=re.UNICODE))


def _source_change_ratio(source: str, output: str) -> float:
    from difflib import SequenceMatcher

    return 1 - SequenceMatcher(None, _normalized(source), _normalized(output)).ratio()


def _clarity_score(output: str) -> float:
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", output) if item.strip()]
    if not sentences:
        return 0.0
    lengths = [_word_count(sentence) for sentence in sentences]
    long_fraction = sum(length > 32 for length in lengths) / len(lengths)
    very_long_fraction = sum(length > 48 for length in lengths) / len(lengths)
    duplicates = len(sentences) - len({_normalized(sentence) for sentence in sentences})
    penalty = 45 * long_fraction + 35 * very_long_fraction + 10 * duplicates
    return max(0.0, 100.0 - penalty)


def _concision_score(word_count: int, minimum: int, maximum: int) -> float:
    if minimum <= word_count <= maximum:
        return 100.0
    if word_count < minimum:
        return max(0.0, 100 * word_count / minimum)
    return max(0.0, 100 * maximum / word_count)


def _subject_present(output: str) -> bool:
    first_line = output.lstrip().splitlines()[0] if output.strip() else ""
    return bool(re.match(r"(?i)^subject\s*:", first_line))


def _headings_present(output: str) -> bool:
    return bool(re.search(r"(?m)^#{1,6}\s+\S", output))


def score_output(case: BenchmarkCase, output: str, *, candidate_id: str) -> CaseScore:
    """Score inspectable properties without claiming complete semantic quality."""

    checks: list[CheckResult] = []
    errors: list[str] = []

    for fact in case.expected.required_facts:
        passed = _matches_any(output, fact.any_of)
        checks.append(
            CheckResult(
                id=fact.id,
                passed=passed,
                critical=fact.critical,
                description=fact.description,
            )
        )
        if not passed:
            errors.append("omission")

    for claim in case.expected.forbidden_claims:
        passed = not _matches_any(output, claim.any_of)
        checks.append(
            CheckResult(
                id=claim.id,
                passed=passed,
                critical=claim.critical,
                description=claim.description,
            )
        )
        if not passed:
            errors.append("fabrication")

    for placeholder in case.expected.required_placeholders:
        passed = placeholder in output
        checks.append(
            CheckResult(
                id=f"placeholder:{placeholder}",
                passed=passed,
                critical=True,
                description="preserve confidential placeholder verbatim",
            )
        )
        if not passed:
            errors.append("placeholder_loss")

    for span in case.expected.must_preserve_spans:
        passed = _normalized(span) in _normalized(output)
        checks.append(
            CheckResult(
                id=f"preserve:{content_sha256(span)[:12]}",
                passed=passed,
                critical=True,
                description="preserve already-correct source span",
            )
        )
        if not passed:
            errors.append("excessive_rewriting")

    cta_passed = not case.expected.required_call_to_action or _matches_any(
        output, case.expected.required_call_to_action
    )
    checks.append(
        CheckResult(
            id="call_to_action",
            passed=cta_passed,
            critical=False,
            description="include the requested next action",
        )
    )
    if not cta_passed:
        errors.append("poor_actionability")

    opening_passed = not case.expected.opening_any_of or _matches_any(
        " ".join(output.split()[:45]), case.expected.opening_any_of
    )
    checks.append(
        CheckResult(
            id="decision_first_opening",
            passed=opening_passed,
            critical=False,
            description="lead with the decision, thesis, or purpose",
        )
    )

    subject_passed = not case.expected.subject_required or _subject_present(output)
    headings_present = _headings_present(output)
    headings_passed = (not case.expected.headings_required or headings_present) and (
        not case.expected.headings_prohibited or not headings_present
    )
    checks.extend(
        (
            CheckResult(
                id="subject_format",
                passed=subject_passed,
                critical=False,
                description="follow the subject-line requirement",
            ),
            CheckResult(
                id="heading_format",
                passed=headings_passed,
                critical=False,
                description="follow the heading requirement",
            ),
        )
    )
    if not subject_passed or not headings_passed:
        errors.append("structural_failure")

    word_count = _word_count(output)
    change_ratio = None
    change_passed = True
    if case.expected.max_source_change_ratio is not None:
        change_ratio = _source_change_ratio(case.input.source_material, output)
        change_passed = change_ratio <= case.expected.max_source_change_ratio
        checks.append(
            CheckResult(
                id="source_change_budget",
                passed=change_passed,
                critical=False,
                description="stay within the preregistered edit budget",
            )
        )
        if not change_passed:
            errors.append("excessive_rewriting")

    non_quality_ids = {
        "call_to_action",
        "decision_first_opening",
        "subject_format",
        "heading_format",
        "source_change_budget",
    }
    required_checks = [check for check in checks if check.id not in non_quality_ids]
    fidelity = 100 * sum(check.passed for check in required_checks) / max(1, len(required_checks))
    clarity = _clarity_score(output)
    concision = _concision_score(word_count, case.expected.min_words, case.expected.max_words)
    organization_parts = [cta_passed, opening_passed]
    organization = 100 * sum(organization_parts) / len(organization_parts)
    format_parts = [subject_passed, headings_passed, change_passed]
    audience_format = 100 * sum(format_parts) / len(format_parts)
    identity_signals = re.search(IDENTITY_SIGNAL_PATTERN, output)
    profile_control = 0.0 if identity_signals else 100.0
    if identity_signals:
        errors.append("identity_signaling")

    dimensions = {
        "fidelity": fidelity,
        "clarity_coherence": clarity,
        "concision": concision,
        "organization_actionability": organization,
        "audience_format": audience_format,
        "profile_control": profile_control,
    }
    development_score = sum(dimensions[name] * weight for name, weight in SCORECARD_WEIGHTS.items())
    hard_gates = all(check.passed for check in checks if check.critical) and not identity_signals
    if word_count > math.ceil(case.expected.max_words * 1.5):
        hard_gates = False
        errors.append("unnecessary_expansion")

    return CaseScore(
        scorer_version=SCORER_VERSION,
        case_id=case.id,
        candidate_id=candidate_id,
        output_sha256=sha256(output.encode("utf-8")).hexdigest(),
        word_count=word_count,
        source_change_ratio=change_ratio,
        dimensions={name: round(value, 4) for name, value in dimensions.items()},
        development_score=round(development_score, 4),
        passes_hard_gates=hard_gates,
        checks=tuple(checks),
        errors=tuple(sorted(set(errors))),
    )


def _case_from_source(source: SourceCase) -> BenchmarkCase:
    return BenchmarkCase(
        version=source.version,
        id=source.id,
        tier=source.tier,
        input=source.input,
        expected=source.expected,
        provenance=BenchmarkProvenance(
            creation_method="project_authored",
            authored_by=source.authored_by,
            authored_at=source.authored_at,
            rights_status=source.rights_status,
            lineage_group=source.lineage_group,
            topic=source.topic,
            time_bucket=source.time_bucket,
            source_material_sha256=content_sha256(source.input.source_material),
        ),
        adversarial_features=source.adversarial_features,
        difficulty=source.difficulty,
    )


def build_benchmark(
    source_path: Path,
    cases_path: Path,
    manifest_path: Path,
    schema_path: Path,
) -> BenchmarkManifest:
    """Build content-hashed JSONL cases and a manifest from reviewed source JSON."""

    value: Any = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("benchmark source must be a JSON list")
    source_cases = [SourceCase.model_validate(item) for item in value]
    _require_unique("case IDs", tuple(case.id for case in source_cases))
    cases = sorted((_case_from_source(case) for case in source_cases), key=lambda case: case.id)
    cases_payload = serialize_jsonl(cases)
    schema_payload = (
        json.dumps(BenchmarkCase.model_json_schema(), indent=2, sort_keys=True) + "\n"
    ).encode()
    task_counts = Counter(case.input.task_family.value for case in cases)
    format_counts = Counter(case.input.output_format.value for case in cases)
    feature_counts = Counter(feature for case in cases for feature in case.adversarial_features)
    manifest = BenchmarkManifest(
        version=1,
        benchmark_id="goodprose-b1-v1",
        tier="B1",
        status="search_development",
        case_count=len(cases),
        case_schema_sha256=sha256_bytes(schema_payload),
        cases_sha256=sha256_bytes(cases_payload),
        source_cases_sha256=sha256_file(source_path),
        scorer_version=SCORER_VERSION,
        scorecard_weights=SCORECARD_WEIGHTS,
        task_family_counts=dict(sorted(task_counts.items())),
        output_format_counts=dict(sorted(format_counts.items())),
        adversarial_feature_counts=dict(sorted(feature_counts.items())),
        creation_method="project_authored",
        rights_status="evaluation_approved_project_owned",
        limitations=(
            "Twenty-four project-authored cases provide plumbing and directional "
            "search evidence only.",
            "Lexical deterministic checks do not establish semantic writing quality "
            "or detect every unsupported claim.",
            "This B1 set is visible to developers and must never be represented as "
            "sealed or confirmatory.",
        ),
    )
    atomic_write(schema_path, schema_payload)
    atomic_write(cases_path, cases_payload)
    atomic_write(
        manifest_path,
        (json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True) + "\n").encode(),
    )
    return manifest


def load_cases(path: Path) -> list[BenchmarkCase]:
    cases = [
        BenchmarkCase.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _require_unique("case IDs", tuple(case.id for case in cases))
    return cases
