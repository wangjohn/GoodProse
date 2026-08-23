"""Aggregate-only holdout lifecycle protocol ``holdout-lifecycle-v1``.

Implements the public protocol and local tooling for two evaluation
boundaries:

- Tier B2 shadow development: queried only at a preregistered cadence and
  reported only through aggregate candidate results.
- Tier C: opened exactly once per benchmark version after the complete
  finalist set and every behavior-affecting configuration are frozen.

Boundary rules enforced here:

- Per-example results are retained for audit *only* inside the separately
  controlled evaluator boundary. Hidden records (opaque case IDs plus numeric
  metrics) may flow only into the broker/one-shot worker, which must run in
  the access-controlled environment -- never in a candidate-development
  checkout. The committed side receives aggregate metrics, hashes,
  timestamps, lifecycle state, and an immutable receipt only.
- A local or agent-readable boundary is always ``procedurally_held_out``.
  ``sealed`` requires a positive external access-separation attestation;
  validating its structure never proves its claim.
- Receipts contain only preregistered aggregates, hashes, timestamps,
  lifecycle state, aggregate usage, and cryptographic fields. No dynamic
  field name or nested payload provides item-, case-, output-, rationale-,
  rubric-, or slice-level side channels.
- All lifecycle and receipt writes use exclusive creation and fail rather
  than overwrite. Input artifacts are hash-verified immediately before use.

Nothing in this module can make fixture or repository-local runs genuinely
sealed; synthetic examples remain procedural demonstrations only.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from collections.abc import Iterable
from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Literal, TypeVar

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)

from goodprose.jsonl import canonical_json, model_to_dict

PROTOCOL_ID = "holdout-lifecycle-v1"
SELECTION_RULE = "max_primary_among_hard_gate_passing_then_lexicographic_candidate_id"

NonEmpty = Annotated[str, StringConstraints(min_length=1, max_length=256)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
OpaqueId = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")]
FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]


class HoldoutError(ValueError):
    """A protocol violation raised by validation, the broker, or the lifecycle."""


def _require_utc(value: datetime) -> datetime:
    if value.utcoffset() != timedelta(0):
        raise ValueError("timestamps must be timezone-aware UTC")
    return value


UtcDatetime = Annotated[datetime, AfterValidator(_require_utc)]

ModelT = TypeVar("ModelT", bound=BaseModel)


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise HoldoutError("timestamps must be timezone-aware UTC")
    return parsed


def canonical_document_hash(value: BaseModel) -> str:
    """SHA-256 over the canonical UTF-8 JSON serialization of a model."""

    payload = canonical_json(model_to_dict(value)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class StrictModel(BaseModel):
    """Immutable protocol boundary that rejects undeclared fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)


AccessPostureLiteral = Literal["sealed", "procedurally_held_out"]
TierLiteral = Literal["B2", "C"]
SelectionRuleLiteral = Literal[
    "max_primary_among_hard_gate_passing_then_lexicographic_candidate_id"
]


class SplitDimension(StrEnum):
    DOCUMENT = "document"
    THREAD = "thread"
    SOURCE = "source"
    PERSON = "person"
    PUBLICATION = "publication"
    TOPIC = "topic"
    TIME_PERIOD = "time_period"


class SeparatedParty(StrEnum):
    TRAINING = "training"
    RETRIEVAL = "retrieval"
    MODEL_UNDER_DEVELOPMENT = "model_under_development"
    TEACHER_SYNTHETIC_GENERATORS = "teacher_synthetic_generators"
    CANDIDATE_DEVELOPERS = "candidate_developers"
    ORCHESTRATION_AGENTS = "orchestration_agents"


_LEAKING_KEY_PATTERN = re.compile(
    r"^(input|source|prompt|output|rationale|rubric|expected|answer|reference|"
    r"slice|example|document|topic|person|publication)(\b|$)",
    re.IGNORECASE,
)


def _reject_leaking_keys(field_name: str, keys: Iterable[str]) -> None:
    for key in keys:
        if not key.strip():
            raise ValueError(f"{field_name} keys must be non-empty")
        if _LEAKING_KEY_PATTERN.search(key):
            raise ValueError(f"{field_name} contains a prohibited item-level key")


# --------------------------------------------------------------------------
# Public registration and evidence models
# --------------------------------------------------------------------------


class AccessSeparationAttestation(StrictModel):
    """Structural attestation; validating it never proves the claim itself."""

    attesting_authority: NonEmpty
    evaluator_boundary: NonEmpty
    separated_parties: tuple[SeparatedParty, ...]
    attested_at: UtcDatetime
    statement_reference: NonEmpty

    @model_validator(mode="after")
    def all_parties_named(self) -> AccessSeparationAttestation:
        if len(self.separated_parties) != len(SeparatedParty) or set(self.separated_parties) != set(
            SeparatedParty
        ):
            raise ValueError("attestation must name every separated party exactly once")
        return self


class CandidateIdentity(StrictModel):
    """Every behavior-affecting field required by ``evals/AGENTS.md``."""

    candidate_id: OpaqueId
    model_identifier: NonEmpty
    model_version: NonEmpty
    base_model: NonEmpty
    adapter_checkpoint_sha256: Sha256
    prompt_version: NonEmpty
    system_instructions_sha256: Sha256
    decoding_config_sha256: Sha256
    inference_provider: NonEmpty
    retrieval_corpus_sha256: Sha256
    retrieval_config_sha256: Sha256
    dataset_split_id: NonEmpty
    grader_identifier: NonEmpty
    grader_version: NonEmpty
    seed: NonEmpty
    code_revision: NonEmpty
    hardware_provider: NonEmpty
    cost_token_accounting_policy: NonEmpty


class HardGate(StrictModel):
    metric: NonEmpty
    case_minimum: FiniteFloat
    minimum_pass_rate: FiniteFloat = Field(ge=0, le=1)


class B2CadencePolicy(StrictModel):
    """Frozen cadence/promotion policy inherited from Tier B1 evidence."""

    eligible_b1_evidence_fields: tuple[NonEmpty, ...] = Field(min_length=1)
    minimum_primary_improvement: FiniteFloat = Field(ge=0)
    max_queries: int = Field(ge=1)
    minimum_accepted_candidate_gap: int = Field(ge=0)
    reference_candidate_id: OpaqueId
    reference_candidate_identity_sha256: Sha256
    reference_aggregates: dict[str, FiniteFloat]
    regression_margin: FiniteFloat = Field(ge=0)
    regression_block_threshold: int = Field(ge=1)

    @model_validator(mode="after")
    def unique_evidence_fields(self) -> B2CadencePolicy:
        fields = self.eligible_b1_evidence_fields
        if len(fields) != len(set(fields)):
            raise ValueError("eligible_b1_evidence_fields must be unique")
        _reject_leaking_keys("eligible_b1_evidence_fields", fields)
        return self


class HoldoutRegistration(StrictModel):
    """Public registration. Contains no item-level material of any kind."""

    version: Literal[1]
    protocol_id: Literal["holdout-lifecycle-v1"]
    tier: TierLiteral
    holdout_id: NonEmpty
    created_at: UtcDatetime
    case_count: int = Field(ge=1)
    content_commitment_sha256: Sha256
    canary_commitment_sha256: Sha256
    split_dimensions: tuple[SplitDimension, ...] = Field(min_length=1)
    aggregate_metrics: tuple[NonEmpty, ...] = Field(min_length=1)
    primary_metric: NonEmpty
    hard_gates: tuple[HardGate, ...] = ()
    scorer_sha256: Sha256
    judge_sha256: Sha256 | None = None
    contamination_scan_sha256: Sha256
    protocol_sha256: Sha256
    code_sha256: Sha256
    access_posture: AccessPostureLiteral
    retention_location_id: NonEmpty
    responsible_authority: NonEmpty
    attestation: AccessSeparationAttestation | None = None
    cadence_policy: B2CadencePolicy | None = None

    @model_validator(mode="after")
    def coherent_registration(self) -> HoldoutRegistration:
        if len(self.split_dimensions) != len(SplitDimension) or set(self.split_dimensions) != set(
            SplitDimension
        ):
            raise ValueError("split_dimensions must contain every required grouping exactly once")
        if len(self.aggregate_metrics) != len(set(self.aggregate_metrics)):
            raise ValueError("aggregate_metrics must be unique")
        _reject_leaking_keys("aggregate_metrics", self.aggregate_metrics)
        if self.primary_metric not in self.aggregate_metrics:
            raise ValueError("primary_metric must be a registered aggregate metric")
        gate_metrics = [gate.metric for gate in self.hard_gates]
        if len(gate_metrics) != len(set(gate_metrics)):
            raise ValueError("hard gate metrics must be unique")
        for gate in self.hard_gates:
            if gate.metric not in self.aggregate_metrics:
                raise ValueError(f"hard gate references unregistered metric {gate.metric!r}")
        if self.access_posture == "sealed":
            if self.attestation is None:
                raise ValueError("sealed registration requires an access-separation attestation")
            if self.attestation.attested_at > self.created_at:
                raise ValueError("access separation must be attested before registration")
        elif self.attestation is not None:
            raise ValueError(
                "procedurally_held_out registration must not carry a sealed-style attestation"
            )
        if (self.tier == "B2") != (self.cadence_policy is not None):
            raise ValueError("cadence policy is required for tier B2 and forbidden for tier C")
        if self.cadence_policy is not None and set(self.cadence_policy.reference_aggregates) != set(
            self.aggregate_metrics
        ):
            raise ValueError("reference_aggregates must cover exactly the registered metrics")
        return self


class HiddenAudit(StrictModel):
    recorded_at: UtcDatetime
    evaluator_run_id: OpaqueId


class HiddenCaseScores(StrictModel):
    """Hidden-boundary record: opaque IDs, registered numbers, nothing else."""

    case_id: OpaqueId
    candidate_id: OpaqueId
    metrics: dict[str, FiniteFloat]
    gate_passes: dict[str, bool]
    audit: HiddenAudit

    @field_validator("metrics", "gate_passes")
    @classmethod
    def no_leaking_keys(cls, value: dict[str, Any], info: ValidationInfo) -> dict[str, Any]:
        _reject_leaking_keys(str(info.field_name), value)
        return value


class B1PromotionClaim(StrictModel):
    evidence: dict[str, FiniteFloat]
    primary_improvement: FiniteFloat
    accepted_candidate_ordinal: int = Field(ge=1)
    evidence_artifact_sha256: Sha256
    milestone: bool = False

    @field_validator("evidence")
    @classmethod
    def no_leaking_keys(cls, value: dict[str, float]) -> dict[str, float]:
        _reject_leaking_keys("evidence", value)
        return value


class AggregateUsage(StrictModel):
    requests: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    usd_cost: FiniteFloat = Field(ge=0)


class B2QueryRequest(StrictModel):
    candidate_id: OpaqueId
    candidate_identity: CandidateIdentity
    b1_promotion_claim: B1PromotionClaim
    hidden_case_scores: tuple[HiddenCaseScores, ...]


class ContaminationAttestation(StrictModel):
    attesting_authority: NonEmpty
    registration_sha256: Sha256
    content_commitment_sha256: Sha256
    canary_commitment_sha256: Sha256
    finalist_configuration_set_sha256: Sha256
    scan_report_sha256: Sha256
    exact_match_passed: bool
    ngram_scan_passed: bool
    embedding_scan_passed: bool
    canary_scan_passed: bool
    exact_match_scanner_sha256: Sha256
    ngram_scanner_sha256: Sha256
    embedding_model_sha256: Sha256
    canary_suite_sha256: Sha256
    scanned_at: UtcDatetime

    @model_validator(mode="after")
    def all_scans_passing(self) -> ContaminationAttestation:
        failing = sorted(
            name
            for name, passed in (
                ("exact_match_passed", self.exact_match_passed),
                ("ngram_scan_passed", self.ngram_scan_passed),
                ("embedding_scan_passed", self.embedding_scan_passed),
                ("canary_scan_passed", self.canary_scan_passed),
            )
            if not passed
        )
        if failing:
            raise ValueError(f"contamination scans must pass: {', '.join(failing)}")
        return self


class FinalistFreeze(StrictModel):
    """Immutable pre-read freeze of three to five finalist configurations."""

    version: Literal[1]
    registration_sha256: Sha256
    frozen_at: UtcDatetime
    finalists: tuple[CandidateIdentity, ...] = Field(min_length=3, max_length=5)
    selection_rule: SelectionRuleLiteral = SELECTION_RULE
    selection_procedure_sha256: Sha256
    declared_metric_names: tuple[NonEmpty, ...] = Field(min_length=1)
    contamination: ContaminationAttestation


def identity_commitment_sha256(identity: CandidateIdentity) -> str:
    """Commit to the configuration only; the candidate ID is tracked apart."""

    data = model_to_dict(identity)
    data.pop("candidate_id", None)
    payload = canonical_json(data).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def finalist_configuration_set_sha256(finalists: tuple[CandidateIdentity, ...]) -> str:
    commitments = sorted(identity_commitment_sha256(finalist) for finalist in finalists)
    return hashlib.sha256(canonical_json(commitments).encode("utf-8")).hexdigest()


def registration_commitment(registration: HoldoutRegistration) -> str:
    return canonical_document_hash(registration)


def finalist_freeze_commitment(freeze: FinalistFreeze) -> str:
    return canonical_document_hash(freeze)


def b1_claim_commitment_sha256(claim: B1PromotionClaim) -> str:
    return canonical_document_hash(claim)


# --------------------------------------------------------------------------
# Pure validation and aggregation
# --------------------------------------------------------------------------


def validate_finalist_freeze(freeze: FinalistFreeze, registration: HoldoutRegistration) -> None:
    if registration.tier != "C":
        raise HoldoutError("finalist freeze requires a Tier C registration")
    if freeze.registration_sha256 != registration_commitment(registration):
        raise HoldoutError("finalist freeze commits to a different registration commitment")
    if freeze.frozen_at < registration.created_at:
        raise HoldoutError("finalist freeze predates the holdout registration")
    if freeze.declared_metric_names != registration.aggregate_metrics:
        raise HoldoutError(
            "finalist freeze metric declarations must equal the registered metrics exactly"
        )
    finalist_ids = [finalist.candidate_id for finalist in freeze.finalists]
    if len(finalist_ids) != len(set(finalist_ids)):
        raise HoldoutError("finalist candidate IDs must be unique")
    identity_hashes = [identity_commitment_sha256(item) for item in freeze.finalists]
    if len(identity_hashes) != len(set(identity_hashes)):
        raise HoldoutError("finalist configurations must be unique")
    attestation = freeze.contamination
    if attestation.scanned_at < freeze.frozen_at:
        raise HoldoutError("contamination attestation predates the finalist freeze")
    if attestation.attesting_authority != registration.responsible_authority:
        raise HoldoutError("contamination attestation authority does not match the registration")
    if (
        attestation.registration_sha256 != registration_commitment(registration)
        or attestation.content_commitment_sha256 != registration.content_commitment_sha256
        or attestation.canary_commitment_sha256 != registration.canary_commitment_sha256
        or attestation.finalist_configuration_set_sha256
        != finalist_configuration_set_sha256(freeze.finalists)
    ):
        raise HoldoutError("contamination attestation does not cover this registration and freeze")


def _validate_hidden_coverage(
    scores: list[HiddenCaseScores],
    registration: HoldoutRegistration,
    *,
    expected_candidate_id: str | None,
) -> None:
    if len(scores) != registration.case_count:
        raise HoldoutError(
            f"expected {registration.case_count} hidden case records, received {len(scores)}"
        )
    case_ids = [record.case_id for record in scores]
    if len(case_ids) != len(set(case_ids)):
        raise HoldoutError("hidden case records contain duplicate case IDs")
    if expected_candidate_id is not None and any(
        record.candidate_id != expected_candidate_id for record in scores
    ):
        raise HoldoutError("hidden records carry an unexpected candidate ID")
    registered_metrics = set(registration.aggregate_metrics)
    registered_gates = {gate.metric: gate for gate in registration.hard_gates}
    for record in scores:
        if set(record.metrics) != registered_metrics:
            raise HoldoutError("a hidden record does not contain exactly the registered metrics")
        if set(record.gate_passes) != set(registered_gates):
            raise HoldoutError("a hidden record does not contain exactly the registered hard gates")
        for gate_name, gate in registered_gates.items():
            expected_pass = record.metrics[gate.metric] >= gate.case_minimum
            if record.gate_passes[gate_name] != expected_pass:
                raise HoldoutError("a hidden hard-gate value is inconsistent with its metric")


def aggregate_hidden_scores(
    scores: list[HiddenCaseScores], registration: HoldoutRegistration
) -> dict[str, float]:
    _validate_hidden_coverage(scores, registration, expected_candidate_id=None)
    totals = dict.fromkeys(registration.aggregate_metrics, 0.0)
    for record in scores:
        for metric in registration.aggregate_metrics:
            totals[metric] += record.metrics[metric]
    count = len(scores)
    return {metric: round(value / count, 6) for metric, value in totals.items()}


def hard_gate_pass_rates(
    scores: list[HiddenCaseScores], registration: HoldoutRegistration
) -> dict[str, float]:
    rates: dict[str, float] = {}
    for gate in registration.hard_gates:
        passing = sum(1 for record in scores if record.gate_passes[gate.metric])
        rates[gate.metric] = round(passing / len(scores), 6)
    return rates


def hard_gate_pass_counts(
    scores: list[HiddenCaseScores], registration: HoldoutRegistration
) -> dict[str, int]:
    return {
        gate.metric: sum(1 for record in scores if record.gate_passes[gate.metric])
        for gate in registration.hard_gates
    }


def gates_met(rates: dict[str, float], registration: HoldoutRegistration) -> bool:
    return all(
        rates.get(gate.metric, 0.0) >= gate.minimum_pass_rate for gate in registration.hard_gates
    )


# --------------------------------------------------------------------------
# Receipt cryptography
# --------------------------------------------------------------------------


class ReceiptEnvelope(StrictModel):
    protocol_id: Literal["holdout-lifecycle-v1"]
    protocol_sha256: Sha256
    code_revision: NonEmpty
    registration_sha256: Sha256
    access_posture: AccessPostureLiteral
    executed_at: UtcDatetime
    prior_receipt_sha256: Sha256 | None = None
    usage: AggregateUsage
    receipt_sha256: Sha256 | None = None
    authenticator: Sha256 | None = None


class CandidateAggregate(StrictModel):
    candidate_id: OpaqueId
    candidate_identity_sha256: Sha256
    aggregate_metrics: dict[str, FiniteFloat]
    evaluated_case_count: int = Field(ge=1)
    hard_gate_pass_counts: dict[str, int]
    hard_gate_pass_rates: dict[str, FiniteFloat]
    gates_met: bool

    @field_validator("aggregate_metrics", "hard_gate_pass_counts", "hard_gate_pass_rates")
    @classmethod
    def no_leaking_keys(cls, value: dict[str, Any], info: ValidationInfo) -> dict[str, Any]:
        _reject_leaking_keys(str(info.field_name), value)
        return value

    @model_validator(mode="after")
    def coherent_counts_and_rates(self) -> CandidateAggregate:
        if set(self.hard_gate_pass_counts) != set(self.hard_gate_pass_rates):
            raise ValueError("hard-gate count and rate names must match")
        for name, count in self.hard_gate_pass_counts.items():
            if count < 0 or count > self.evaluated_case_count:
                raise ValueError("hard-gate counts must be within the evaluated case count")
            expected_rate = round(count / self.evaluated_case_count, 6)
            if self.hard_gate_pass_rates[name] != expected_rate:
                raise ValueError("hard-gate rates must equal count divided by case count")
        return self


class TierB2Receipt(StrictModel):
    kind: Literal["tier_b2"]
    envelope: ReceiptEnvelope
    query_index: int = Field(ge=1)
    candidate_id: OpaqueId
    candidate_identity_sha256: Sha256
    b1_claim_sha256: Sha256
    b1_accepted_candidate_ordinal: int = Field(ge=1)
    content_commitment_sha256: Sha256
    canary_commitment_sha256: Sha256
    aggregate_metrics: dict[str, FiniteFloat]
    evaluated_case_count: int = Field(ge=1)
    hard_gate_pass_counts: dict[str, int]
    hard_gate_pass_rates: dict[str, FiniteFloat]
    gates_met: bool
    primary_metric: NonEmpty
    primary_value: FiniteFloat
    reference_value: FiniteFloat
    regressed: bool
    cumulative_regressions: int = Field(ge=0)
    outcome: Literal["accepted", "not_accepted", "advancement_blocked"]

    @field_validator("aggregate_metrics", "hard_gate_pass_counts", "hard_gate_pass_rates")
    @classmethod
    def no_leaking_keys(cls, value: dict[str, Any], info: ValidationInfo) -> dict[str, Any]:
        _reject_leaking_keys(str(info.field_name), value)
        return value

    @model_validator(mode="after")
    def coherent_aggregate(self) -> TierB2Receipt:
        if self.primary_metric not in self.aggregate_metrics:
            raise ValueError("primary metric must be present in aggregate metrics")
        if self.primary_value != self.aggregate_metrics[self.primary_metric]:
            raise ValueError("primary value must equal the reported aggregate metric")
        CandidateAggregate(
            candidate_id=self.candidate_id,
            candidate_identity_sha256=self.candidate_identity_sha256,
            aggregate_metrics=self.aggregate_metrics,
            evaluated_case_count=self.evaluated_case_count,
            hard_gate_pass_counts=self.hard_gate_pass_counts,
            hard_gate_pass_rates=self.hard_gate_pass_rates,
            gates_met=self.gates_met,
        )
        return self


class TierCReceipt(StrictModel):
    kind: Literal["tier_c"]
    envelope: ReceiptEnvelope
    finalist_freeze_sha256: Sha256
    content_commitment_sha256: Sha256
    canary_commitment_sha256: Sha256
    selection_rule: SelectionRuleLiteral
    aggregates: tuple[CandidateAggregate, ...] = Field(min_length=3, max_length=5)
    selected_candidate_id: OpaqueId | None
    outcome: Literal["completed", "no_hard_gate_passing_finalist"]

    @model_validator(mode="after")
    def coherent_selection(self) -> TierCReceipt:
        candidate_ids = [aggregate.candidate_id for aggregate in self.aggregates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("tier C aggregate candidate IDs must be unique")
        if (
            self.selected_candidate_id is not None
            and self.selected_candidate_id not in candidate_ids
        ):
            raise ValueError("selected_candidate_id must name a reported aggregate")
        if (self.selected_candidate_id is None) != (
            self.outcome == "no_hard_gate_passing_finalist"
        ):
            raise ValueError("tier C selection and outcome are inconsistent")
        return self


Receipt = TierB2Receipt | TierCReceipt


def receipt_payload_bytes(receipt: Receipt) -> bytes:
    data = receipt.model_dump(mode="json", exclude_none=True)
    envelope = data["envelope"]
    envelope.pop("receipt_sha256", None)
    envelope.pop("authenticator", None)
    return canonical_json(data).encode("utf-8")


def compute_receipt_hash(receipt: Receipt) -> str:
    return hashlib.sha256(receipt_payload_bytes(receipt)).hexdigest()


def compute_authenticator(payload: bytes, key: bytes) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def finalize_receipt(receipt: Receipt, *, signer_key: bytes | None) -> Receipt:
    payload = receipt_payload_bytes(receipt)
    envelope = receipt.envelope.model_copy(
        update={"receipt_sha256": hashlib.sha256(payload).hexdigest()}
    )
    if signer_key is not None:
        envelope = envelope.model_copy(
            update={"authenticator": compute_authenticator(payload, signer_key)}
        )
    return receipt.model_copy(update={"envelope": envelope})


AuthenticatorStatus = Literal["verified", "unverified_no_key", "absent", "invalid"]


class ReceiptVerification(StrictModel):
    receipt_kind: Literal["tier_b2", "tier_c"] | None = None
    receipt_sha256: str | None = None
    hash_intact: bool = False
    authenticator_status: AuthenticatorStatus = "absent"
    errors: tuple[NonEmpty, ...] = ()

    @property
    def valid(self) -> bool:
        schema_ok = self.receipt_kind is not None
        auth_ok = self.authenticator_status in ("verified", "unverified_no_key", "absent")
        return bool(schema_ok and self.hash_intact and auth_ok and not self.errors)


class ChainVerification(StrictModel):
    receipt_count: int
    chain_intact: bool
    verifications: tuple[ReceiptVerification, ...]


def _receipt_registration_errors(
    receipt: Receipt,
    registration: HoldoutRegistration,
    freeze: FinalistFreeze | None,
) -> list[str]:
    errors: list[str] = []
    envelope = receipt.envelope
    if envelope.registration_sha256 != registration_commitment(registration):
        errors.append("receipt commits to a different registration")
    if envelope.protocol_sha256 != registration.protocol_sha256:
        errors.append("receipt protocol hash does not match the registration")
    if envelope.access_posture != registration.access_posture:
        errors.append("receipt access posture does not match the registration")
    if registration.access_posture == "sealed" and envelope.authenticator is None:
        errors.append("sealed receipts require an external authenticator")

    metric_names = set(registration.aggregate_metrics)
    gate_names = {gate.metric for gate in registration.hard_gates}

    def check_aggregate(aggregate: CandidateAggregate) -> None:
        if set(aggregate.aggregate_metrics) != metric_names:
            errors.append("receipt aggregate metrics do not match the registration")
        if (
            set(aggregate.hard_gate_pass_counts) != gate_names
            or set(aggregate.hard_gate_pass_rates) != gate_names
        ):
            errors.append("receipt hard gates do not match the registration")
        if aggregate.evaluated_case_count != registration.case_count:
            errors.append("receipt evaluated case count does not match the registration")
        expected_gate_result = all(
            aggregate.hard_gate_pass_rates.get(gate.metric, 0.0) >= gate.minimum_pass_rate
            for gate in registration.hard_gates
        )
        if aggregate.gates_met != expected_gate_result:
            errors.append("receipt hard-gate outcome is inconsistent with the registration")

    if isinstance(receipt, TierB2Receipt):
        if registration.tier != "B2":
            errors.append("a Tier B2 receipt cannot use a Tier C registration")
        if receipt.content_commitment_sha256 != registration.content_commitment_sha256:
            errors.append("receipt content commitment does not match the registration")
        if receipt.canary_commitment_sha256 != registration.canary_commitment_sha256:
            errors.append("receipt canary commitment does not match the registration")
        check_aggregate(
            CandidateAggregate(
                candidate_id=receipt.candidate_id,
                candidate_identity_sha256=receipt.candidate_identity_sha256,
                aggregate_metrics=receipt.aggregate_metrics,
                evaluated_case_count=receipt.evaluated_case_count,
                hard_gate_pass_counts=receipt.hard_gate_pass_counts,
                hard_gate_pass_rates=receipt.hard_gate_pass_rates,
                gates_met=receipt.gates_met,
            )
        )
        if receipt.primary_metric != registration.primary_metric:
            errors.append("receipt primary metric does not match the registration")
        if (
            registration.cadence_policy is None
            or receipt.reference_value
            != registration.cadence_policy.reference_aggregates[registration.primary_metric]
        ):
            errors.append("receipt reference value does not match the B2 policy")
        if registration.cadence_policy is not None:
            policy = registration.cadence_policy
            expected_regression = (
                receipt.primary_value < receipt.reference_value - policy.regression_margin
            )
            if receipt.regressed != expected_regression:
                errors.append("receipt regression decision is inconsistent with the B2 policy")
            if receipt.cumulative_regressions < int(receipt.regressed):
                errors.append("receipt cumulative regression count is impossible")
            if receipt.cumulative_regressions > receipt.query_index:
                errors.append("receipt cumulative regression count exceeds its query index")
            expected_b2_outcome: Literal["accepted", "not_accepted", "advancement_blocked"]
            if receipt.cumulative_regressions >= policy.regression_block_threshold:
                expected_b2_outcome = "advancement_blocked"
            elif (
                receipt.gates_met
                and receipt.primary_value
                >= receipt.reference_value + policy.minimum_primary_improvement
            ):
                expected_b2_outcome = "accepted"
            else:
                expected_b2_outcome = "not_accepted"
            if receipt.outcome != expected_b2_outcome:
                errors.append("receipt outcome is inconsistent with the B2 policy")
    else:
        if registration.tier != "C":
            errors.append("a Tier C receipt cannot use a Tier B2 registration")
        if receipt.content_commitment_sha256 != registration.content_commitment_sha256:
            errors.append("receipt content commitment does not match the registration")
        if receipt.canary_commitment_sha256 != registration.canary_commitment_sha256:
            errors.append("receipt canary commitment does not match the registration")
        for aggregate in receipt.aggregates:
            check_aggregate(aggregate)
        if freeze is None:
            errors.append("Tier C receipt verification requires the finalist freeze")
        else:
            try:
                validate_finalist_freeze(freeze, registration)
            except HoldoutError:
                errors.append("finalist freeze failed registration validation")
            if receipt.finalist_freeze_sha256 != finalist_freeze_commitment(freeze):
                errors.append("receipt commits to a different finalist freeze")
            expected = {
                finalist.candidate_id: identity_commitment_sha256(finalist)
                for finalist in freeze.finalists
            }
            actual = {
                aggregate.candidate_id: aggregate.candidate_identity_sha256
                for aggregate in receipt.aggregates
            }
            if actual != expected:
                errors.append("receipt finalist configurations do not match the freeze")
            if [aggregate.candidate_id for aggregate in receipt.aggregates] != sorted(actual):
                errors.append("receipt finalist aggregates are not in canonical candidate order")
            if receipt.selection_rule != freeze.selection_rule:
                errors.append("receipt selection rule does not match the finalist freeze")
            passing = [aggregate for aggregate in receipt.aggregates if aggregate.gates_met]
            expected_selected: str | None = None
            expected_tier_c_outcome: Literal["completed", "no_hard_gate_passing_finalist"]
            if passing:
                best_value = max(
                    aggregate.aggregate_metrics[registration.primary_metric]
                    for aggregate in passing
                )
                expected_selected = min(
                    aggregate.candidate_id
                    for aggregate in passing
                    if aggregate.aggregate_metrics[registration.primary_metric] == best_value
                )
                expected_tier_c_outcome = "completed"
            else:
                expected_tier_c_outcome = "no_hard_gate_passing_finalist"
            if (
                receipt.selected_candidate_id != expected_selected
                or receipt.outcome != expected_tier_c_outcome
            ):
                errors.append("receipt selection is inconsistent with the frozen rule")
    return errors


def verify_receipt_document(
    document: dict[str, Any],
    *,
    key: bytes | None,
    registration: HoldoutRegistration | None = None,
    freeze: FinalistFreeze | None = None,
) -> ReceiptVerification:
    parsed: Receipt | None = None
    for model_type in (TierB2Receipt, TierCReceipt):
        try:
            parsed = model_type.model_validate(document)
            break
        except ValidationError:
            continue
    if parsed is None:
        return ReceiptVerification(errors=("document does not match any receipt schema",))
    errors: list[str] = []
    recomputed = compute_receipt_hash(parsed)
    hash_intact = parsed.envelope.receipt_sha256 == recomputed
    if not hash_intact:
        errors.append("receipt hash mismatch: document was modified after emission")
    status: AuthenticatorStatus = "absent"
    authenticator = parsed.envelope.authenticator
    if key is not None:
        if authenticator is None:
            status = "invalid"
            errors.append("authenticator missing: fail closed")
        else:
            expected = compute_authenticator(receipt_payload_bytes(parsed), key)
            if hmac.compare_digest(authenticator, expected):
                status = "verified"
            else:
                status = "invalid"
                errors.append("authenticator invalid: fail closed")
    elif authenticator is not None:
        status = "unverified_no_key"
    if registration is not None:
        errors.extend(_receipt_registration_errors(parsed, registration, freeze))
    return ReceiptVerification(
        receipt_kind=parsed.kind,
        receipt_sha256=recomputed,
        hash_intact=hash_intact,
        authenticator_status=status,
        errors=tuple(errors),
    )


def verify_receipt_chain(
    receipt_dir: Path,
    *,
    key: bytes | None,
    registration: HoldoutRegistration | None = None,
) -> ChainVerification:
    paths = sorted(receipt_dir.glob("b2-receipt-*.json"))
    verifications: list[ReceiptVerification] = []
    prior_hash: str | None = None
    chain_intact = True
    seen_candidate_ids: set[str] = set()
    seen_identity_hashes: set[str] = set()
    prior_ordinal: int | None = None
    cumulative_regressions = 0
    advancement_blocked = False
    for index, path in enumerate(paths, start=1):
        if path.name != f"b2-receipt-{index:04d}.json":
            chain_intact = False
            break
        try:
            document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            verifications.append(ReceiptVerification(errors=(f"unreadable receipt: {error}",)))
            chain_intact = False
            break
        verification = verify_receipt_document(
            document,
            key=key,
            registration=registration,
        )
        if not verification.valid:
            chain_intact = False
        problems: list[str] = list(verification.errors)
        if verification.receipt_kind == "tier_b2":
            receipt = TierB2Receipt.model_validate(document)
            if receipt.envelope.prior_receipt_sha256 != prior_hash:
                problems.append("receipt-chain fork detected")
                chain_intact = False
            if receipt.query_index != index:
                problems.append("query index out of sequence")
                chain_intact = False
            if registration is not None and registration.cadence_policy is not None:
                policy = registration.cadence_policy
                if index > policy.max_queries:
                    problems.append("receipt chain exceeds the registered query limit")
                    chain_intact = False
                if advancement_blocked:
                    problems.append("receipt appended after advancement was blocked")
                    chain_intact = False
                if (
                    receipt.candidate_id in seen_candidate_ids
                    or receipt.candidate_identity_sha256 in seen_identity_hashes
                ):
                    problems.append("duplicate candidate or configuration in receipt chain")
                    chain_intact = False
                if prior_ordinal is not None:
                    ordinal_gap = receipt.b1_accepted_candidate_ordinal - prior_ordinal
                    if ordinal_gap < max(1, policy.minimum_accepted_candidate_gap):
                        problems.append("receipt chain violates the accepted-candidate cadence")
                        chain_intact = False
                cumulative_regressions += int(receipt.regressed)
                if receipt.cumulative_regressions != cumulative_regressions:
                    problems.append("receipt chain has an inconsistent cumulative regression count")
                    chain_intact = False
                advancement_blocked = cumulative_regressions >= policy.regression_block_threshold
                seen_candidate_ids.add(receipt.candidate_id)
                seen_identity_hashes.add(receipt.candidate_identity_sha256)
                prior_ordinal = receipt.b1_accepted_candidate_ordinal
            prior_hash = verification.receipt_sha256
        else:
            problems.append("non-B2 receipt inside the B2 chain directory")
            chain_intact = False
        if problems != list(verification.errors):
            verification = verification.model_copy(update={"errors": tuple(problems)})
        verifications.append(verification)
    return ChainVerification(
        receipt_count=len(verifications),
        chain_intact=chain_intact and bool(paths),
        verifications=tuple(verifications),
    )


# --------------------------------------------------------------------------
# Durable lifecycle state: exclusive creation, fail rather than overwrite
# --------------------------------------------------------------------------


def _exclusive_write_json(path: Path, value: StrictModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value.model_dump(mode="json"), indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def ensure_not_retired(state_dir: Path) -> None:
    if (state_dir / "retired.json").exists():
        raise HoldoutError("benchmark is retired and ineligible for further use")


RetirementReason = Literal[
    "authorized_item_inspection",
    "superseded_by_new_version",
    "integrity_incident",
]


class RetirementRecord(StrictModel):
    protocol_id: Literal["holdout-lifecycle-v1"]
    registration_sha256: Sha256
    authorized_by: NonEmpty
    reason: RetirementReason
    retired_at: UtcDatetime


def retire(
    *,
    state_dir: Path,
    registration: HoldoutRegistration,
    authorized_by: str,
    reason: RetirementReason,
    retired_at: str,
) -> RetirementRecord:
    record = RetirementRecord(
        protocol_id=PROTOCOL_ID,
        registration_sha256=registration_commitment(registration),
        authorized_by=authorized_by,
        reason=reason,
        retired_at=_parse_utc(retired_at),
    )
    _exclusive_write_json(state_dir / "retired.json", record)
    return record


# --------------------------------------------------------------------------
# Tier B2 aggregate-only broker (external append-only receipt chain)
# --------------------------------------------------------------------------


def evaluate_b2_query(
    registration: HoldoutRegistration,
    prior_receipts: list[TierB2Receipt],
    request: B2QueryRequest,
    *,
    usage: AggregateUsage,
    executed_at: str,
    code_revision: str,
) -> TierB2Receipt:
    """Pure broker decision: validate one query and build its receipt.

    Preconditions that fail raise :class:`HoldoutError` without accepting any
    hidden score. Only fully validated queries produce receipts. Once the
    preregistered repeated-regression threshold is reached the outcome is
    ``advancement_blocked``; no cases, outputs, explanations, slices, or
    per-error examples are ever returned to explain the regression.
    """

    if registration.tier != "B2" or registration.cadence_policy is None:
        raise HoldoutError("b2 broker requires a tier-B2 registration with a cadence policy")
    policy = registration.cadence_policy
    if len(prior_receipts) >= policy.max_queries:
        raise HoldoutError("b2 maximum preregistered query count exhausted")
    if (
        prior_receipts
        and prior_receipts[-1].cumulative_regressions >= policy.regression_block_threshold
    ):
        raise HoldoutError("b2 advancement is already blocked by repeated aggregate regressions")

    prior_hash: str | None = None
    for index, prior in enumerate(prior_receipts, start=1):
        if prior.query_index != index or prior.envelope.prior_receipt_sha256 != prior_hash:
            raise HoldoutError("prior B2 receipt chain is out of sequence")
        if _receipt_registration_errors(prior, registration, None):
            raise HoldoutError("prior B2 receipt does not match the active registration")
        prior_hash = prior.envelope.receipt_sha256

    identity_hash = identity_commitment_sha256(request.candidate_identity)
    if request.candidate_identity.candidate_id != request.candidate_id:
        raise HoldoutError("candidate identity does not match the requested candidate ID")
    if any(
        receipt.candidate_id == request.candidate_id
        or receipt.candidate_identity_sha256 == identity_hash
        for receipt in prior_receipts
    ):
        raise HoldoutError("duplicate candidate or configuration query rejected")

    claim = request.b1_promotion_claim
    if set(claim.evidence) != set(policy.eligible_b1_evidence_fields):
        raise HoldoutError("B1 claim does not contain exactly the preregistered evidence fields")
    if prior_receipts:
        ordinal_gap = (
            claim.accepted_candidate_ordinal - prior_receipts[-1].b1_accepted_candidate_ordinal
        )
        if ordinal_gap < max(1, policy.minimum_accepted_candidate_gap):
            raise HoldoutError("preregistered accepted-candidate cadence gap not met")
    promoted = claim.milestone or claim.primary_improvement >= policy.minimum_primary_improvement
    if not promoted:
        raise HoldoutError("B1 promotion claim does not satisfy the registered policy")

    scores = list(request.hidden_case_scores)
    _validate_hidden_coverage(scores, registration, expected_candidate_id=request.candidate_id)
    aggregates = aggregate_hidden_scores(scores, registration)
    rates = hard_gate_pass_rates(scores, registration)
    gate_ok = gates_met(rates, registration)

    reference_value = policy.reference_aggregates[registration.primary_metric]
    primary_value = aggregates[registration.primary_metric]
    regressed = primary_value < reference_value - policy.regression_margin
    cumulative_regressions = sum(1 for receipt in prior_receipts if receipt.regressed) + int(
        regressed
    )

    outcome: Literal["accepted", "not_accepted", "advancement_blocked"]
    if cumulative_regressions >= policy.regression_block_threshold:
        outcome = "advancement_blocked"
    elif gate_ok and primary_value >= reference_value + policy.minimum_primary_improvement:
        outcome = "accepted"
    else:
        outcome = "not_accepted"

    envelope = ReceiptEnvelope(
        protocol_id=PROTOCOL_ID,
        protocol_sha256=registration.protocol_sha256,
        code_revision=code_revision,
        registration_sha256=registration_commitment(registration),
        access_posture=registration.access_posture,
        executed_at=_parse_utc(executed_at),
        prior_receipt_sha256=prior_hash,
        usage=usage,
    )
    receipt = TierB2Receipt(
        kind="tier_b2",
        envelope=envelope,
        query_index=len(prior_receipts) + 1,
        candidate_id=request.candidate_id,
        candidate_identity_sha256=identity_hash,
        b1_claim_sha256=b1_claim_commitment_sha256(claim),
        b1_accepted_candidate_ordinal=claim.accepted_candidate_ordinal,
        content_commitment_sha256=registration.content_commitment_sha256,
        canary_commitment_sha256=registration.canary_commitment_sha256,
        aggregate_metrics=aggregates,
        evaluated_case_count=registration.case_count,
        hard_gate_pass_counts=hard_gate_pass_counts(scores, registration),
        hard_gate_pass_rates=rates,
        gates_met=gate_ok,
        primary_metric=registration.primary_metric,
        primary_value=primary_value,
        reference_value=reference_value,
        regressed=regressed,
        cumulative_regressions=cumulative_regressions,
        outcome=outcome,
    )
    finalized = finalize_receipt(receipt, signer_key=None)
    if not isinstance(finalized, TierB2Receipt):  # pragma: no cover - defensive
        raise HoldoutError("broker produced a non-B2 receipt")
    return finalized


def load_b2_receipt_chain(
    state_dir: Path,
    *,
    registration: HoldoutRegistration,
    key: bytes | None,
) -> list[TierB2Receipt]:
    receipt_dir = state_dir / "receipts"
    paths = sorted(receipt_dir.glob("b2-receipt-*.json"))
    if paths:
        verification = verify_receipt_chain(
            receipt_dir,
            key=key,
            registration=registration,
        )
        if not verification.chain_intact:
            raise HoldoutError("prior B2 receipt chain failed integrity verification")
    receipts: list[TierB2Receipt] = []
    for index, path in enumerate(paths, start=1):
        if path.name != f"b2-receipt-{index:04d}.json":
            raise HoldoutError("receipt chain has a gap or fork on disk")
        try:
            receipt = TierB2Receipt.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, ValidationError) as error:
            raise HoldoutError(f"unreadable prior receipt {path.name}: {error}") from error
        receipts.append(receipt)
    return receipts


def append_b2_receipt(state_dir: Path, receipt: TierB2Receipt) -> Path:
    target = state_dir / "receipts" / f"b2-receipt-{receipt.query_index:04d}.json"
    _exclusive_write_json(target, receipt)
    return target


def submit_b2_query(
    registration: HoldoutRegistration,
    request: B2QueryRequest,
    *,
    state_dir: Path,
    usage: AggregateUsage,
    executed_at: str,
    code_revision: str,
    signer_key: bytes | None = None,
) -> TierB2Receipt:
    """External broker path: runs where hidden scores are already held."""

    ensure_not_retired(state_dir)
    if registration.access_posture == "sealed" and signer_key is None:
        raise HoldoutError("sealed B2 execution requires an external signing key")
    prior_receipts = load_b2_receipt_chain(
        state_dir,
        registration=registration,
        key=signer_key,
    )
    receipt = evaluate_b2_query(
        registration,
        prior_receipts,
        request,
        usage=usage,
        executed_at=executed_at,
        code_revision=code_revision,
    )
    if signer_key is not None:
        receipt = finalize_receipt(receipt, signer_key=signer_key)
        if not isinstance(receipt, TierB2Receipt):  # pragma: no cover - defensive
            raise HoldoutError("broker produced a non-B2 receipt")
    append_b2_receipt(state_dir, receipt)
    return receipt


# --------------------------------------------------------------------------
# Tier C burn-before-read one-shot lifecycle
# --------------------------------------------------------------------------


class OpenedState(StrictModel):
    protocol_id: Literal["holdout-lifecycle-v1"]
    registration_sha256: Sha256
    finalist_freeze_sha256: Sha256
    opened_at: UtcDatetime


class CompletedState(StrictModel):
    protocol_id: Literal["holdout-lifecycle-v1"]
    registration_sha256: Sha256
    finalist_freeze_sha256: Sha256
    receipt_sha256: Sha256
    completed_at: UtcDatetime


def open_tier_c(
    registration: HoldoutRegistration,
    freeze: FinalistFreeze,
    *,
    state_dir: Path,
    opened_at: str,
) -> OpenedState:
    """Atomically create the durable ``opened`` state before any read.

    If evaluation crashes after this point the benchmark remains consumed;
    a second run fails because the state file already exists exclusively.
    """

    ensure_not_retired(state_dir)
    if registration.tier != "C":
        raise HoldoutError("tier C open requires a Tier C registration")
    validate_finalist_freeze(freeze, registration)
    state = OpenedState(
        protocol_id=PROTOCOL_ID,
        registration_sha256=registration_commitment(registration),
        finalist_freeze_sha256=finalist_freeze_commitment(freeze),
        opened_at=_parse_utc(opened_at),
    )
    _exclusive_write_json(state_dir / "opened.json", state)
    return state


def complete_tier_c(
    registration: HoldoutRegistration,
    freeze: FinalistFreeze,
    scores_by_candidate: dict[str, list[HiddenCaseScores]],
    *,
    usage: AggregateUsage,
    state_dir: Path,
    completed_at: str,
    code_revision: str,
    signer_key: bytes | None = None,
) -> TierCReceipt:
    """Aggregate once, apply the frozen selection procedure, emit one receipt."""

    if registration.access_posture == "sealed" and signer_key is None:
        raise HoldoutError("sealed Tier C execution requires an external signing key")
    validate_tier_c_completion_state(registration, freeze, state_dir=state_dir)
    freeze_hash = finalist_freeze_commitment(freeze)

    expected_ids = {finalist.candidate_id for finalist in freeze.finalists}
    if set(scores_by_candidate) != expected_ids:
        raise HoldoutError("tier C case coverage must include every finalist exactly")
    aggregates: list[CandidateAggregate] = []
    for finalist in freeze.finalists:
        scores = scores_by_candidate[finalist.candidate_id]
        _validate_hidden_coverage(scores, registration, expected_candidate_id=finalist.candidate_id)
        candidate_rates = hard_gate_pass_rates(scores, registration)
        candidate_counts = hard_gate_pass_counts(scores, registration)
        aggregates.append(
            CandidateAggregate(
                candidate_id=finalist.candidate_id,
                candidate_identity_sha256=identity_commitment_sha256(finalist),
                aggregate_metrics=aggregate_hidden_scores(scores, registration),
                evaluated_case_count=registration.case_count,
                hard_gate_pass_counts=candidate_counts,
                hard_gate_pass_rates=candidate_rates,
                gates_met=gates_met(candidate_rates, registration),
            )
        )
    aggregates.sort(key=lambda item: item.candidate_id)
    passing = [aggregate for aggregate in aggregates if aggregate.gates_met]
    selected: str | None = None
    outcome: Literal["completed", "no_hard_gate_passing_finalist"]
    if passing:
        best_value = max(item.aggregate_metrics[registration.primary_metric] for item in passing)
        selected = min(
            item.candidate_id
            for item in passing
            if item.aggregate_metrics[registration.primary_metric] == best_value
        )
        outcome = "completed"
    else:
        outcome = "no_hard_gate_passing_finalist"

    receipt = TierCReceipt(
        kind="tier_c",
        envelope=ReceiptEnvelope(
            protocol_id=PROTOCOL_ID,
            protocol_sha256=registration.protocol_sha256,
            code_revision=code_revision,
            registration_sha256=registration_commitment(registration),
            access_posture=registration.access_posture,
            executed_at=_parse_utc(completed_at),
            prior_receipt_sha256=None,
            usage=usage,
        ),
        finalist_freeze_sha256=freeze_hash,
        content_commitment_sha256=registration.content_commitment_sha256,
        canary_commitment_sha256=registration.canary_commitment_sha256,
        selection_rule=SELECTION_RULE,
        aggregates=tuple(aggregates),
        selected_candidate_id=selected,
        outcome=outcome,
    )
    finalized = finalize_receipt(receipt, signer_key=signer_key)
    if not isinstance(finalized, TierCReceipt):  # pragma: no cover - defensive
        raise HoldoutError("one-shot lifecycle produced a non-tier-C receipt")
    receipt_hash = finalized.envelope.receipt_sha256
    if receipt_hash is None:  # pragma: no cover - defensive
        raise HoldoutError("finalized receipt lacks its hash")
    _exclusive_write_json(state_dir / "receipts" / "tier-c-receipt.json", finalized)
    _exclusive_write_json(
        state_dir / "completed.json",
        CompletedState(
            protocol_id=PROTOCOL_ID,
            registration_sha256=registration_commitment(registration),
            finalist_freeze_sha256=freeze_hash,
            receipt_sha256=receipt_hash,
            completed_at=_parse_utc(completed_at),
        ),
    )
    return finalized


def validate_tier_c_completion_state(
    registration: HoldoutRegistration,
    freeze: FinalistFreeze,
    *,
    state_dir: Path,
) -> OpenedState:
    """Fail before hidden score loading when completion is not permitted."""

    ensure_not_retired(state_dir)
    if registration.tier != "C":
        raise HoldoutError("tier C completion requires a Tier C registration")
    validate_finalist_freeze(freeze, registration)
    opened_path = state_dir / "opened.json"
    if not opened_path.exists():
        raise HoldoutError("tier C cannot run before the exclusive opened state exists")
    if (state_dir / "completed.json").exists():
        raise HoldoutError("tier C benchmark already consumed; second runs fail closed")
    if (state_dir / "receipts" / "tier-c-receipt.json").exists():
        raise HoldoutError("tier C receipt already exists; completion retry fails closed")
    try:
        opened = OpenedState.model_validate(json.loads(opened_path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        raise HoldoutError(f"unreadable opened state: {error}") from error
    freeze_hash = finalist_freeze_commitment(freeze)
    if (
        opened.registration_sha256 != registration_commitment(registration)
        or opened.finalist_freeze_sha256 != freeze_hash
    ):
        raise HoldoutError("opened state does not commit to this registration and freeze")
    return opened


# --------------------------------------------------------------------------
# File/process wrappers. Loaders hash-verify inputs immediately before use.
#
# The wrappers below that touch hidden records or durable lifecycle state
# (submit_b2_query, open_tier_c, complete_tier_c, retire, load_hidden_scores,
# load_signer_key) are intended to run inside the access-controlled evaluator
# environment, never in a candidate-development checkout. The repository-side
# verifier accepts only registration/freeze metadata and a receipt.
# --------------------------------------------------------------------------


def _load_strict_model[ModelT: BaseModel](
    path: Path, model_type: type[ModelT], expected_sha256: str | None
) -> ModelT:
    try:
        model = model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValidationError) as error:
        raise HoldoutError(f"{path}: {error}") from error
    actual = canonical_document_hash(model)
    if expected_sha256 is not None and actual != expected_sha256:
        raise HoldoutError(
            f"{path}: canonical document hash mismatch; input artifact failed verification"
        )
    return model


def load_registration(path: Path, *, expected_sha256: str | None = None) -> HoldoutRegistration:
    return _load_strict_model(path, HoldoutRegistration, expected_sha256)


def load_finalist_freeze(path: Path, *, expected_sha256: str | None = None) -> FinalistFreeze:
    return _load_strict_model(path, FinalistFreeze, expected_sha256)


def load_b2_request(path: Path, *, expected_sha256: str | None = None) -> B2QueryRequest:
    try:
        raw = path.read_bytes()
        if expected_sha256 is not None and hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise HoldoutError("B2 request failed confidential hash verification")
        document: Any = json.loads(raw.decode("utf-8"))
        return B2QueryRequest.model_validate(document)
    except HoldoutError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValidationError) as error:
        raise HoldoutError("B2 request failed confidential schema validation") from error


def load_hidden_scores(path: Path, *, expected_sha256: str | None = None) -> list[HiddenCaseScores]:
    try:
        raw = path.read_bytes()
        if expected_sha256 is not None and hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise HoldoutError("hidden score file failed confidential hash verification")
        document: Any = json.loads(raw.decode("utf-8"))
    except HoldoutError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise HoldoutError("hidden score file failed confidential decoding") from error
    if not isinstance(document, list):
        raise HoldoutError("hidden score file failed confidential container validation")
    records: list[HiddenCaseScores] = []
    for item in document:
        try:
            records.append(HiddenCaseScores.model_validate(item))
        except ValidationError as error:
            raise HoldoutError(
                "hidden score record failed confidential schema validation"
            ) from error
    return records


def load_signer_key(path: Path) -> bytes:
    key = path.read_bytes()
    if len(key) < 32:
        raise HoldoutError("signing key must contain at least 32 bytes")
    return key


def load_receipt_document(path: Path) -> dict[str, Any]:
    try:
        document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise HoldoutError(f"{path}: unreadable receipt: {error}") from error
    if not isinstance(document, dict):
        raise HoldoutError(f"{path}: receipt must be a JSON object")
    return document
