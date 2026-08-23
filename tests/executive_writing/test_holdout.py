"""Deterministic, fully synthetic tests for the holdout lifecycle protocol.

Every fixture here is project-authored and unmistakably synthetic. No true
hidden evaluation content exists in this repository and none is created;
nothing in these tests demonstrates a genuinely sealed boundary.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from goodprose.executive_writing.holdout import (
    PROTOCOL_ID,
    SELECTION_RULE,
    AccessSeparationAttestation,
    AggregateUsage,
    B1PromotionClaim,
    B2CadencePolicy,
    B2QueryRequest,
    CandidateIdentity,
    ContaminationAttestation,
    FinalistFreeze,
    HiddenAudit,
    HiddenCaseScores,
    HoldoutError,
    HoldoutRegistration,
    SeparatedParty,
    SplitDimension,
    canonical_document_hash,
    complete_tier_c,
    evaluate_b2_query,
    finalist_configuration_set_sha256,
    finalize_receipt,
    identity_commitment_sha256,
    load_b2_request,
    load_hidden_scores,
    load_registration,
    open_tier_c,
    retire,
    submit_b2_query,
    validate_finalist_freeze,
    verify_receipt_chain,
    verify_receipt_document,
)

TEST_KEY = b"ox-alpha-synthetic-test-key-NOT-PRODUCTION"
NOW = datetime(2026, 8, 23, 12, 0, 0, tzinfo=UTC)
HEX = "ab" * 32
METRICS = ("quality", "fidelity")
GATES = (("fidelity", 50.0, 0.75),)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _identity(candidate_id: str) -> CandidateIdentity:
    return CandidateIdentity(
        candidate_id=candidate_id,
        model_identifier="synthetic-model",
        model_version="v0",
        base_model="synthetic-base",
        adapter_checkpoint_sha256=_sha(f"adapter:{candidate_id}"),
        prompt_version="synthetic-prompt-v1",
        system_instructions_sha256=_sha("system"),
        decoding_config_sha256=_sha("decoding"),
        inference_provider="synthetic-provider",
        retrieval_corpus_sha256=_sha("corpus"),
        retrieval_config_sha256=_sha("retrieval-config"),
        dataset_split_id="synthetic-split",
        grader_identifier="synthetic-grader",
        grader_version="synthetic-grader-v1",
        seed="0",
        code_revision="0000000000000000000000000000000000000000",
        hardware_provider="synthetic-hardware",
        cost_token_accounting_policy="synthetic-zero-cost-policy",
    )


def _attestation() -> AccessSeparationAttestation:
    return AccessSeparationAttestation(
        attesting_authority="synthetic external authority",
        evaluator_boundary="synthetic independently controlled evaluator",
        separated_parties=tuple(SeparatedParty),
        attested_at=NOW,
        statement_reference="synthetic-statement-0001",
    )


def _cadence_policy(**overrides: Any) -> B2CadencePolicy:
    values: dict[str, Any] = {
        "eligible_b1_evidence_fields": ("b1_mean_quality", "b1_hard_gate_rate"),
        "minimum_primary_improvement": 1.0,
        "max_queries": 5,
        "minimum_accepted_candidate_gap": 0,
        "reference_candidate_id": "reference-candidate",
        "reference_candidate_identity_sha256": identity_commitment_sha256(
            _identity("reference-candidate")
        ),
        "reference_aggregates": {"quality": 70.0, "fidelity": 90.0},
        "regression_margin": 0.0,
        "regression_block_threshold": 2,
    }
    values.update(overrides)
    return B2CadencePolicy.model_validate(values)


def _registration(**overrides: Any) -> HoldoutRegistration:
    values: dict[str, Any] = {
        "version": 1,
        "protocol_id": PROTOCOL_ID,
        "tier": "B2",
        "holdout_id": "synthetic-b2-shadow-v1",
        "created_at": NOW,
        "case_count": 4,
        "content_commitment_sha256": _sha("content"),
        "canary_commitment_sha256": _sha("canary"),
        "split_dimensions": tuple(SplitDimension),
        "aggregate_metrics": METRICS,
        "primary_metric": "quality",
        "hard_gates": tuple(
            {"metric": metric, "case_minimum": minimum, "minimum_pass_rate": rate}
            for metric, minimum, rate in GATES
        ),
        "scorer_sha256": HEX,
        "contamination_scan_sha256": HEX,
        "protocol_sha256": HEX,
        "code_sha256": HEX,
        "access_posture": "procedurally_held_out",
        "retention_location_id": "synthetic-controlled-evaluator",
        "responsible_authority": "synthetic external authority",
        "cadence_policy": _cadence_policy(),
    }
    values.update(overrides)
    return HoldoutRegistration.model_validate(values)


def _hidden_scores(
    candidate_id: str, qualities: list[float], fidelties: list[float] | None = None
) -> list[HiddenCaseScores]:
    fidelties = fidelties if fidelties is not None else [95.0] * len(qualities)
    return [
        HiddenCaseScores(
            case_id=f"opaque-case-{index:04d}",
            candidate_id=candidate_id,
            metrics={"quality": quality, "fidelity": fidelity},
            gate_passes={"fidelity": fidelity >= 50.0},
            audit=HiddenAudit(recorded_at=NOW, evaluator_run_id="synthetic-run-0001"),
        )
        for index, (quality, fidelity) in enumerate(zip(qualities, fidelties, strict=True), 1)
    ]


def _request(
    candidate_id: str,
    *,
    qualities: list[float] | None = None,
    claim_improvement: float = 5.0,
    accepted_candidate_ordinal: int = 1,
    milestone: bool = False,
) -> B2QueryRequest:
    return B2QueryRequest(
        candidate_id=candidate_id,
        candidate_identity=_identity(candidate_id),
        b1_promotion_claim=B1PromotionClaim(
            evidence={"b1_mean_quality": 72.0, "b1_hard_gate_rate": 1.0},
            primary_improvement=claim_improvement,
            accepted_candidate_ordinal=accepted_candidate_ordinal,
            evidence_artifact_sha256=_sha(f"b1-evidence:{candidate_id}"),
            milestone=milestone,
        ),
        hidden_case_scores=tuple(
            _hidden_scores(candidate_id, qualities or [80.0, 82.0, 78.0, 84.0])
        ),
    )


def _usage() -> AggregateUsage:
    return AggregateUsage(requests=4, input_tokens=1000, output_tokens=500, usd_cost=0.0)


def _freeze(registration: HoldoutRegistration, finalist_ids: list[str]) -> FinalistFreeze:
    finalists = tuple(_identity(candidate) for candidate in finalist_ids)
    return FinalistFreeze(
        version=1,
        registration_sha256=canonical_document_hash(registration),
        frozen_at=NOW,
        finalists=finalists,
        selection_rule=SELECTION_RULE,
        selection_procedure_sha256=_sha("synthetic-selection-procedure"),
        declared_metric_names=registration.aggregate_metrics,
        contamination=ContaminationAttestation(
            attesting_authority="synthetic external authority",
            registration_sha256=canonical_document_hash(registration),
            content_commitment_sha256=registration.content_commitment_sha256,
            canary_commitment_sha256=registration.canary_commitment_sha256,
            finalist_configuration_set_sha256=finalist_configuration_set_sha256(finalists),
            scan_report_sha256=_sha("synthetic-contamination-report"),
            exact_match_passed=True,
            ngram_scan_passed=True,
            embedding_scan_passed=True,
            canary_scan_passed=True,
            exact_match_scanner_sha256=HEX,
            ngram_scanner_sha256=HEX,
            embedding_model_sha256=HEX,
            canary_suite_sha256=HEX,
            scanned_at=NOW,
        ),
    )


# ---------------------------------------------------------------------------
# Registration and evidence rules
# ---------------------------------------------------------------------------


def test_registration_round_trip_and_commitments_are_stable() -> None:
    registration = _registration()
    assert canonical_document_hash(registration) == canonical_document_hash(_registration())
    assert registration.cadence_policy is not None


def test_sealed_registration_requires_attestation() -> None:
    with pytest.raises(ValueError, match="requires an access-separation attestation"):
        _registration(access_posture="sealed")


def test_procedural_registration_rejects_attestation() -> None:
    with pytest.raises(ValueError, match="must not carry"):
        _registration(attestation=_attestation())


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _registration(created_at=datetime(2026, 8, 23, 12, 0, 0))


def test_non_utc_offset_and_incomplete_split_grouping_are_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware UTC"):
        _registration(created_at="2026-08-23T12:00:00-07:00")
    with pytest.raises(ValueError, match="every required grouping"):
        _registration(split_dimensions=(SplitDimension.TOPIC, SplitDimension.TIME_PERIOD))


def test_non_finite_metric_is_rejected() -> None:
    payload = _request("candidate-a").model_dump(mode="json")
    payload["hidden_case_scores"][0]["metrics"]["quality"] = float("inf")
    with pytest.raises(ValueError, match="Input should be a finite number"):
        B2QueryRequest.model_validate(payload)


def test_leaking_hidden_key_is_rejected() -> None:
    payload = _hidden_scores("candidate-a", [80.0])[0].model_dump(mode="json")
    payload["metrics"]["source"] = 1.0
    with pytest.raises(ValueError, match="prohibited item-level key"):
        HiddenCaseScores.model_validate(payload)


def test_compound_metric_names_are_permitted() -> None:
    payload = _hidden_scores("candidate-a", [80.0])[0].model_dump(mode="json")
    payload["metrics"]["topic_adherence"] = 90.0
    parsed = HiddenCaseScores.model_validate(payload)
    assert parsed.metrics["topic_adherence"] == 90.0


def test_b2_without_cadence_policy_and_c_with_policy_are_rejected() -> None:
    with pytest.raises(ValueError, match="cadence policy"):
        _registration(cadence_policy=None)
    with pytest.raises(ValueError, match="cadence policy"):
        _registration(tier="C")


def test_reference_aggregates_must_cover_registered_metrics() -> None:
    policy = _cadence_policy(reference_aggregates={"quality": 70.0})
    with pytest.raises(ValueError, match="exactly the registered metrics"):
        _registration(cadence_policy=policy)


def test_load_registration_verifies_expected_hash(tmp_path: Path) -> None:
    path = tmp_path / "registration.json"
    path.write_text(_registration().model_dump_json(indent=2), encoding="utf-8")
    loaded = load_registration(path)
    assert load_registration(path, expected_sha256=canonical_document_hash(loaded)) == loaded
    with pytest.raises(HoldoutError, match="failed verification"):
        load_registration(path, expected_sha256="0" * 64)


# ---------------------------------------------------------------------------
# Tier B2 aggregate-only broker
# ---------------------------------------------------------------------------


def test_permitted_b2_query_emits_verified_acceptance_receipt(tmp_path: Path) -> None:
    registration = _registration()
    receipt = submit_b2_query(
        registration,
        _request("candidate-a"),
        state_dir=tmp_path,
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
        signer_key=TEST_KEY,
    )
    assert receipt.outcome == "accepted"
    assert receipt.query_index == 1
    assert receipt.aggregate_metrics["quality"] == 81.0
    assert receipt.envelope.prior_receipt_sha256 is None
    document = json.loads(
        (tmp_path / "receipts" / "b2-receipt-0001.json").read_text(encoding="utf-8")
    )
    verification = verify_receipt_document(document, key=TEST_KEY, registration=registration)
    assert verification.valid
    assert verification.authenticator_status == "verified"
    without_key = verify_receipt_document(document, key=None, registration=registration)
    assert without_key.valid
    assert without_key.authenticator_status == "unverified_no_key"


def test_keyed_verification_rejects_missing_authenticator() -> None:
    receipt = evaluate_b2_query(
        _registration(),
        [],
        _request("candidate-a"),
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    verification = verify_receipt_document(
        json.loads(receipt.model_dump_json()),
        key=TEST_KEY,
        registration=_registration(),
    )
    assert verification.authenticator_status == "invalid"
    assert not verification.valid


def test_sealed_b2_requires_external_signing_key(tmp_path: Path) -> None:
    registration = _registration(access_posture="sealed", attestation=_attestation())
    with pytest.raises(HoldoutError, match="requires an external signing key"):
        submit_b2_query(
            registration,
            _request("candidate-a"),
            state_dir=tmp_path,
            usage=_usage(),
            executed_at="2026-08-23T13:00:00Z",
            code_revision="0" * 40,
        )


def test_duplicate_candidate_and_configuration_queries_fail(tmp_path: Path) -> None:
    registration = _registration()
    submit_b2_query(
        registration,
        _request("candidate-a"),
        state_dir=tmp_path,
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    with pytest.raises(HoldoutError, match="duplicate candidate or configuration"):
        submit_b2_query(
            registration,
            _request("candidate-a"),
            state_dir=tmp_path,
            usage=_usage(),
            executed_at="2026-08-23T14:00:00Z",
            code_revision="0" * 40,
        )
    clone = _request("candidate-b").model_copy(
        update={
            "candidate_identity": _identity("candidate-a").model_copy(
                update={"candidate_id": "candidate-b"}
            )
        }
    )
    with pytest.raises(HoldoutError, match="duplicate candidate or configuration"):
        submit_b2_query(
            registration,
            clone,
            state_dir=tmp_path,
            usage=_usage(),
            executed_at="2026-08-23T14:00:00Z",
            code_revision="0" * 40,
        )


def test_cadence_gap_violation_fails_closed(tmp_path: Path) -> None:
    registration = _registration(cadence_policy=_cadence_policy(minimum_accepted_candidate_gap=1))
    submit_b2_query(
        registration,
        _request("candidate-a"),
        state_dir=tmp_path,
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    with pytest.raises(HoldoutError, match="cadence gap"):
        submit_b2_query(
            registration,
            _request("candidate-b", accepted_candidate_ordinal=1),
            state_dir=tmp_path,
            usage=_usage(),
            executed_at="2026-08-23T14:00:00Z",
            code_revision="0" * 40,
        )


def test_maximum_query_count_blocks_further_queries(tmp_path: Path) -> None:
    registration = _registration(cadence_policy=_cadence_policy(max_queries=1))
    submit_b2_query(
        registration,
        _request("candidate-a"),
        state_dir=tmp_path,
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    with pytest.raises(HoldoutError, match="maximum preregistered query count"):
        submit_b2_query(
            registration,
            _request("candidate-b"),
            state_dir=tmp_path,
            usage=_usage(),
            executed_at="2026-08-23T14:00:00Z",
            code_revision="0" * 40,
        )


def test_b1_promotion_policy_must_be_satisfied(tmp_path: Path) -> None:
    registration = _registration()
    weak_claim = _request("candidate-a", claim_improvement=0.5)
    with pytest.raises(HoldoutError, match="does not satisfy the registered policy"):
        evaluate_b2_query(
            registration,
            [],
            weak_claim,
            usage=_usage(),
            executed_at="2026-08-23T13:00:00Z",
            code_revision="0" * 40,
        )
    ineligible_field = _request("candidate-a").b1_promotion_claim.model_copy(
        update={"evidence": {"topic_gain": 10.0}}
    )
    ineligible_request = _request("candidate-a").model_copy(
        update={"b1_promotion_claim": ineligible_field}
    )
    with pytest.raises(HoldoutError, match="exactly the preregistered evidence fields"):
        evaluate_b2_query(
            registration,
            [],
            ineligible_request,
            usage=_usage(),
            executed_at="2026-08-23T13:00:00Z",
            code_revision="0" * 40,
        )


def test_repeated_regressions_block_advancement_without_item_detail(tmp_path: Path) -> None:
    registration = _registration()
    first = evaluate_b2_query(
        registration,
        [],
        _request("regressor-1", qualities=[60.0, 62.0, 58.0, 64.0]),
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    assert first.outcome == "not_accepted"
    assert first.regressed
    second = evaluate_b2_query(
        registration,
        [first],
        _request(
            "regressor-2",
            qualities=[61.0, 63.0, 59.0, 65.0],
            accepted_candidate_ordinal=2,
        ),
        usage=_usage(),
        executed_at="2026-08-23T14:00:00Z",
        code_revision="0" * 40,
    )
    assert second.outcome == "advancement_blocked"
    assert second.cumulative_regressions == 2
    serialized = second.model_dump_json()
    for banned in ("opaque-case", "rationale", "rubric"):
        assert banned not in serialized.lower()
    with pytest.raises(HoldoutError, match="already blocked"):
        evaluate_b2_query(
            registration,
            [first, second],
            _request("candidate-after-block", accepted_candidate_ordinal=3),
            usage=_usage(),
            executed_at="2026-08-23T15:00:00Z",
            code_revision="0" * 40,
        )


def test_incomplete_hidden_coverage_is_rejected() -> None:
    registration = _registration()
    request = _request("candidate-a").model_copy(
        update={"hidden_case_scores": tuple(_hidden_scores("candidate-a", [80.0]))}
    )
    with pytest.raises(HoldoutError, match="expected 4 hidden case records"):
        evaluate_b2_query(
            registration,
            [],
            request,
            usage=_usage(),
            executed_at="2026-08-23T13:00:00Z",
            code_revision="0" * 40,
        )


def test_hidden_records_require_exact_metrics_gates_and_matching_identity() -> None:
    registration = _registration()
    identity_mismatch = _request("candidate-a").model_copy(
        update={"candidate_identity": _identity("candidate-b")}
    )
    with pytest.raises(HoldoutError, match="identity does not match"):
        evaluate_b2_query(
            registration,
            [],
            identity_mismatch,
            usage=_usage(),
            executed_at="2026-08-23T13:00:00Z",
            code_revision="0" * 40,
        )

    missing_gates = tuple(
        record.model_copy(update={"gate_passes": {}})
        for record in _hidden_scores("candidate-a", [80.0, 81.0, 82.0, 83.0])
    )
    request = _request("candidate-a").model_copy(update={"hidden_case_scores": missing_gates})
    with pytest.raises(HoldoutError, match="registered hard gates"):
        evaluate_b2_query(
            registration,
            [],
            request,
            usage=_usage(),
            executed_at="2026-08-23T13:00:00Z",
            code_revision="0" * 40,
        )


def test_chain_verification_detects_tampering(tmp_path: Path) -> None:
    registration = _registration()
    submit_b2_query(
        registration,
        _request("candidate-a"),
        state_dir=tmp_path,
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    receipt_path = tmp_path / "receipts" / "b2-receipt-0001.json"
    document = json.loads(receipt_path.read_text(encoding="utf-8"))
    document["primary_value"] = 99.9
    receipt_path.write_text(json.dumps(document), encoding="utf-8")
    chain = verify_receipt_chain(tmp_path / "receipts", key=None, registration=registration)
    assert not chain.chain_intact
    assert not chain.verifications[0].hash_intact
    with pytest.raises(HoldoutError, match="failed integrity verification"):
        submit_b2_query(
            registration,
            _request("candidate-b", accepted_candidate_ordinal=2),
            state_dir=tmp_path,
            usage=_usage(),
            executed_at="2026-08-23T14:00:00Z",
            code_revision="0" * 40,
        )


def test_chain_verification_recomputes_cumulative_regressions(tmp_path: Path) -> None:
    registration = _registration()
    first = evaluate_b2_query(
        registration,
        [],
        _request("candidate-a"),
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    second = evaluate_b2_query(
        registration,
        [first],
        _request("candidate-b", accepted_candidate_ordinal=2),
        usage=_usage(),
        executed_at="2026-08-23T14:00:00Z",
        code_revision="0" * 40,
    )
    forged = finalize_receipt(
        second.model_copy(update={"cumulative_regressions": 1}), signer_key=None
    )
    receipt_dir = tmp_path / "receipts"
    receipt_dir.mkdir()
    (receipt_dir / "b2-receipt-0001.json").write_text(first.model_dump_json(), encoding="utf-8")
    (receipt_dir / "b2-receipt-0002.json").write_text(forged.model_dump_json(), encoding="utf-8")

    verification = verify_receipt_chain(receipt_dir, key=None, registration=registration)
    assert not verification.chain_intact
    assert verification.verifications[1].hash_intact
    assert any(
        "inconsistent cumulative regression count" in error
        for error in verification.verifications[1].errors
    )


# ---------------------------------------------------------------------------
# Tier C burn-before-read one-shot lifecycle
# ---------------------------------------------------------------------------


def _tier_c_setup(tmp_path: Path) -> tuple[Any, Any, dict[str, list[HiddenCaseScores]]]:
    registration = _registration(tier="C", holdout_id="synthetic-tier-c-v1", cadence_policy=None)
    freeze = _freeze(registration, ["finalist-a", "finalist-b", "finalist-c"])
    scores = {
        "finalist-a": _hidden_scores("finalist-a", [85.0, 87.0, 83.0, 86.0]),
        "finalist-b": _hidden_scores("finalist-b", [70.0, 72.0, 68.0, 71.0]),
        "finalist-c": _hidden_scores("finalist-c", [77.0, 79.0, 75.0, 78.0]),
    }
    return registration, freeze, scores


def test_successful_procedural_tier_c_run(tmp_path: Path) -> None:
    registration, freeze, scores = _tier_c_setup(tmp_path)
    open_tier_c(
        registration,
        freeze,
        state_dir=tmp_path,
        opened_at="2026-08-23T13:00:00Z",
    )
    assert (tmp_path / "opened.json").exists()
    receipt = complete_tier_c(
        registration,
        freeze,
        scores,
        state_dir=tmp_path,
        usage=_usage(),
        completed_at="2026-08-23T14:00:00Z",
        code_revision="0" * 40,
        signer_key=TEST_KEY,
    )
    assert receipt.selected_candidate_id == "finalist-a"
    assert receipt.outcome == "completed"
    assert receipt.envelope.access_posture == "procedurally_held_out"
    assert (tmp_path / "receipts" / "tier-c-receipt.json").exists()
    assert (tmp_path / "completed.json").exists()
    document = json.loads(
        (tmp_path / "receipts" / "tier-c-receipt.json").read_text(encoding="utf-8")
    )
    assert verify_receipt_document(
        document,
        key=TEST_KEY,
        registration=registration,
        freeze=freeze,
    ).valid


def test_tier_c_verifier_recomputes_frozen_selection(tmp_path: Path) -> None:
    registration, freeze, scores = _tier_c_setup(tmp_path)
    open_tier_c(
        registration,
        freeze,
        state_dir=tmp_path,
        opened_at="2026-08-23T13:00:00Z",
    )
    receipt = complete_tier_c(
        registration,
        freeze,
        scores,
        state_dir=tmp_path,
        usage=_usage(),
        completed_at="2026-08-23T14:00:00Z",
        code_revision="0" * 40,
        signer_key=TEST_KEY,
    )
    forged = finalize_receipt(
        receipt.model_copy(update={"selected_candidate_id": "finalist-b"}),
        signer_key=TEST_KEY,
    )

    verification = verify_receipt_document(
        json.loads(forged.model_dump_json()),
        key=TEST_KEY,
        registration=registration,
        freeze=freeze,
    )
    assert verification.hash_intact
    assert verification.authenticator_status == "verified"
    assert not verification.valid
    assert "receipt selection is inconsistent with the frozen rule" in verification.errors


def test_sealed_tier_c_completion_requires_signing_key(tmp_path: Path) -> None:
    registration = _registration(
        tier="C",
        holdout_id="synthetic-sealed-tier-c-v1",
        cadence_policy=None,
        access_posture="sealed",
        attestation=_attestation(),
    )
    freeze = _freeze(registration, ["finalist-a", "finalist-b", "finalist-c"])
    scores = {
        candidate_id: _hidden_scores(candidate_id, [80.0, 81.0, 82.0, 83.0])
        for candidate_id in ("finalist-a", "finalist-b", "finalist-c")
    }
    open_tier_c(
        registration,
        freeze,
        state_dir=tmp_path,
        opened_at="2026-08-23T13:00:00Z",
    )
    with pytest.raises(HoldoutError, match="requires an external signing key"):
        complete_tier_c(
            registration,
            freeze,
            scores,
            state_dir=tmp_path,
            usage=_usage(),
            completed_at="2026-08-23T14:00:00Z",
            code_revision="0" * 40,
        )


def test_second_tier_c_run_fails_after_open(tmp_path: Path) -> None:
    registration, freeze, scores = _tier_c_setup(tmp_path)
    open_tier_c(registration, freeze, state_dir=tmp_path, opened_at="2026-08-23T13:00:00Z")
    with pytest.raises(OSError):
        open_tier_c(registration, freeze, state_dir=tmp_path, opened_at="2026-08-23T13:30:00Z")
    complete_tier_c(
        registration,
        freeze,
        scores,
        state_dir=tmp_path,
        usage=_usage(),
        completed_at="2026-08-23T14:00:00Z",
        code_revision="0" * 40,
    )
    with pytest.raises(OSError):
        open_tier_c(registration, freeze, state_dir=tmp_path, opened_at="2026-08-23T15:00:00Z")
    with pytest.raises(HoldoutError, match="already consumed"):
        complete_tier_c(
            registration,
            freeze,
            scores,
            state_dir=tmp_path,
            usage=_usage(),
            completed_at="2026-08-23T15:00:00Z",
            code_revision="0" * 40,
        )


def test_completion_requires_prior_open(tmp_path: Path) -> None:
    registration, freeze, scores = _tier_c_setup(tmp_path)
    with pytest.raises(HoldoutError, match="before the exclusive opened state"):
        complete_tier_c(
            registration,
            freeze,
            scores,
            state_dir=tmp_path,
            usage=_usage(),
            completed_at="2026-08-23T14:00:00Z",
            code_revision="0" * 40,
        )


def test_tier_c_rejects_b2_registration_and_selects_no_gate_failure(tmp_path: Path) -> None:
    b2_registration = _registration()
    tier_c_registration, freeze, scores = _tier_c_setup(tmp_path)
    with pytest.raises(HoldoutError, match="requires a Tier C registration"):
        open_tier_c(
            b2_registration,
            freeze.model_copy(
                update={"registration_sha256": canonical_document_hash(b2_registration)}
            ),
            state_dir=tmp_path / "wrong-tier",
            opened_at="2026-08-23T13:00:00Z",
        )

    failing_scores = {
        candidate_id: _hidden_scores(
            candidate_id,
            [90.0, 91.0, 92.0, 93.0],
            fidelties=[10.0, 20.0, 30.0, 40.0],
        )
        for candidate_id in scores
    }
    open_tier_c(
        tier_c_registration,
        freeze,
        state_dir=tmp_path / "no-pass",
        opened_at="2026-08-23T13:00:00Z",
    )
    receipt = complete_tier_c(
        tier_c_registration,
        freeze,
        failing_scores,
        state_dir=tmp_path / "no-pass",
        usage=_usage(),
        completed_at="2026-08-23T14:00:00Z",
        code_revision="0" * 40,
    )
    assert receipt.selected_candidate_id is None
    assert receipt.outcome == "no_hard_gate_passing_finalist"


def test_freeze_validation_rules(tmp_path: Path) -> None:
    registration = _registration(tier="C", holdout_id="synthetic-tier-c-v1", cadence_policy=None)
    with pytest.raises(ValueError):
        _freeze(registration, ["only-one", "only-two"])
    base_freeze = _freeze(registration, ["finalist-a", "finalist-b", "finalist-c"])
    config_clone = CandidateIdentity.model_validate(
        {**_identity("finalist-a").model_dump(), "candidate_id": "finalist-b"}
    )
    duplicated = base_freeze.model_copy(
        update={
            "finalists": (
                _identity("finalist-a"),
                config_clone,
                _identity("finalist-c"),
            )
        }
    )
    with pytest.raises(HoldoutError, match="configurations must be unique"):
        validate_finalist_freeze(duplicated, registration)
    same_ids = base_freeze.model_copy(
        update={
            "finalists": (
                _identity("finalist-a"),
                _identity("finalist-a"),
                _identity("finalist-c"),
            )
        }
    )
    with pytest.raises(HoldoutError, match="candidate IDs must be unique"):
        validate_finalist_freeze(same_ids, registration)
    wrong_metrics = _freeze(registration, ["a", "b", "c"]).model_copy(
        update={"declared_metric_names": ("quality",)}
    )
    with pytest.raises(HoldoutError, match="equal the registered metrics exactly"):
        validate_finalist_freeze(wrong_metrics, registration)
    wrong_registration_link = _freeze(registration, ["a", "b", "c"]).model_copy(
        update={"registration_sha256": "0" * 64}
    )
    with pytest.raises(HoldoutError, match="different registration commitment"):
        validate_finalist_freeze(wrong_registration_link, registration)
    failing_contamination = base_freeze.contamination.model_dump(mode="json")
    failing_contamination["ngram_scan_passed"] = False
    with pytest.raises(ValueError, match="contamination scans must pass"):
        ContaminationAttestation.model_validate(failing_contamination)
    other = _registration(tier="C", holdout_id="synthetic-tier-c-v2", cadence_policy=None)
    freeze = _freeze(registration, ["a", "b", "c"])
    open_state_dir = tmp_path
    open_tier_c(registration, freeze, state_dir=open_state_dir, opened_at="2026-08-23T13:00:00Z")
    with pytest.raises(HoldoutError, match="does not commit to this registration and freeze"):
        complete_tier_c(
            other,
            _freeze(other, ["a", "b", "c"]),
            {},
            state_dir=open_state_dir,
            usage=_usage(),
            completed_at="2026-08-23T14:00:00Z",
            code_revision="0" * 40,
        )


# ---------------------------------------------------------------------------
# Receipt cryptography
# ---------------------------------------------------------------------------


def test_tampered_receipt_fails_verification(tmp_path: Path) -> None:
    registration = _registration()
    receipt = evaluate_b2_query(
        registration,
        [],
        _request("candidate-a"),
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    signed = finalize_receipt(receipt, signer_key=TEST_KEY)
    tampered = signed.model_copy(deep=True)
    envelope = tampered.envelope.model_copy(update={"code_revision": "9" * 40})
    tampered = tampered.model_copy(update={"envelope": envelope})
    verification = verify_receipt_document(json.loads(tampered.model_dump_json()), key=TEST_KEY)
    assert not verification.hash_intact
    assert not verification.valid


def test_bad_authenticator_fails_closed(tmp_path: Path) -> None:
    registration = _registration()
    receipt = evaluate_b2_query(
        registration,
        [],
        _request("candidate-a"),
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    signed = finalize_receipt(receipt, signer_key=b"a-different-non-production-test-key")
    verification = verify_receipt_document(json.loads(signed.model_dump_json()), key=TEST_KEY)
    assert verification.authenticator_status == "invalid"
    assert not verification.valid


# ---------------------------------------------------------------------------
# Retirement
# ---------------------------------------------------------------------------


def test_retirement_blocks_future_use_and_preserves_receipts(tmp_path: Path) -> None:
    registration, _, _ = _tier_c_setup(tmp_path)
    b2_registration = _registration()
    submit_b2_query(
        b2_registration,
        _request("candidate-a"),
        state_dir=tmp_path,
        usage=_usage(),
        executed_at="2026-08-23T13:00:00Z",
        code_revision="0" * 40,
    )
    retire(
        state_dir=tmp_path,
        registration=registration,
        authorized_by="synthetic authority",
        reason="authorized_item_inspection",
        retired_at="2026-08-23T15:00:00Z",
    )
    assert (tmp_path / "retired.json").exists()
    with pytest.raises(OSError):
        retire(
            state_dir=tmp_path,
            registration=registration,
            authorized_by="synthetic authority",
            reason="authorized_item_inspection",
            retired_at="2026-08-23T15:30:00Z",
        )
    with pytest.raises(HoldoutError, match="retired"):
        submit_b2_query(
            b2_registration,
            _request("candidate-b"),
            state_dir=tmp_path,
            usage=_usage(),
            executed_at="2026-08-23T16:00:00Z",
            code_revision="0" * 40,
        )
    freeze = _freeze(registration, ["a", "b", "c"])
    with pytest.raises(HoldoutError, match="retired"):
        open_tier_c(registration, freeze, state_dir=tmp_path, opened_at="2026-08-23T16:00:00Z")
    assert (tmp_path / "receipts" / "b2-receipt-0001.json").exists()


# ---------------------------------------------------------------------------
# Loader wrappers and CLI
# ---------------------------------------------------------------------------


def test_hidden_score_loader_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    records = _hidden_scores("candidate-a", [80.0, 81.0])
    path.write_text(
        json.dumps([record.model_dump(mode="json") for record in records]), encoding="utf-8"
    )
    assert load_hidden_scores(path) == records


def test_hidden_score_loader_verifies_exact_raw_bytes_without_leaking(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    sentinel = "CONFIDENTIAL-SENTINEL-MUST-NOT-LEAK"
    records = _hidden_scores("candidate-a", [80.0, 81.0])
    path.write_text(
        json.dumps([record.model_dump(mode="json") for record in records]) + sentinel,
        encoding="utf-8",
    )
    with pytest.raises(HoldoutError) as captured:
        load_hidden_scores(path, expected_sha256="0" * 64)
    assert "hash verification" in str(captured.value)
    assert sentinel not in str(captured.value)


def test_b2_request_loader_rejects_unknown_fields(tmp_path: Path) -> None:
    path = tmp_path / "request.json"
    payload = _request("candidate-a").model_dump(mode="json")
    sentinel = "CONFIDENTIAL-SENTINEL-MUST-NOT-LEAK"
    payload["outputs"] = [sentinel]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(HoldoutError) as captured:
        load_b2_request(path)
    assert sentinel not in str(captured.value)


def test_cli_holdout_paths(tmp_path: Path) -> None:
    from goodprose.executive_writing.__main__ import _run, build_parser

    registration_path = tmp_path / "registration.json"
    registration_path.write_text(_registration().model_dump_json(indent=2), encoding="utf-8")
    request_path = tmp_path / "request.json"
    request_path.write_text(_request("candidate-a").model_dump_json(), encoding="utf-8")

    def invoke(*argv: str) -> int:
        try:
            return _run(build_parser().parse_args(list(argv)))
        except (OSError, ValueError, SystemExit):
            return 1

    assert (
        invoke(
            "holdout",
            "validate-registration",
            "--registration",
            str(registration_path),
        )
        == 0
    )
    assert (
        invoke(
            "holdout",
            "validate-registration",
            "--registration",
            str(registration_path),
            "--expect-sha256",
            "0" * 64,
        )
        != 0
    )
    assert (
        invoke(
            "holdout",
            "b2-query",
            "--registration",
            str(registration_path),
            "--request",
            str(request_path),
            "--expect-request-sha256",
            hashlib.sha256(request_path.read_bytes()).hexdigest(),
            "--state-dir",
            str(tmp_path / "state"),
            "--executed-at",
            "2026-08-23T13:00:00Z",
            "--code-revision",
            "0" * 40,
        )
        == 0
    )
    assert (
        invoke(
            "holdout",
            "verify-receipt",
            "--receipt",
            str(tmp_path / "state" / "receipts" / "b2-receipt-0001.json"),
            "--registration",
            str(registration_path),
        )
        == 0
    )
    assert (
        invoke(
            "holdout",
            "verify-chain",
            "--state-dir",
            str(tmp_path / "state"),
            "--registration",
            str(registration_path),
        )
        == 0
    )
    assert (
        invoke(
            "holdout",
            "retire",
            "--registration",
            str(registration_path),
            "--state-dir",
            str(tmp_path / "state"),
            "--authorized-by",
            "synthetic authority",
            "--reason",
            "authorized_item_inspection",
            "--retired-at",
            "2026-08-23T18:00:00Z",
        )
        == 0
    )
    assert (
        invoke(
            "holdout",
            "b2-query",
            "--registration",
            str(registration_path),
            "--request",
            str(request_path),
            "--expect-request-sha256",
            hashlib.sha256(request_path.read_bytes()).hexdigest(),
            "--state-dir",
            str(tmp_path / "state"),
            "--executed-at",
            "2026-08-23T19:00:00Z",
            "--code-revision",
            "0" * 40,
        )
        == 1
    )


def test_example_protocol_documents_validate(tmp_path: Path) -> None:
    """The committed synthetic protocol examples must remain schema-valid."""

    examples_dir = (
        Path(__file__).resolve().parents[2]
        / "evals"
        / "executive-writing"
        / "holdout-lifecycle-v1"
        / "examples"
    )
    if not examples_dir.exists():  # pragma: no cover - guards partial checkouts
        pytest.skip("protocol examples not present")
    for path in sorted(examples_dir.glob("*.json")):
        document: Any = json.loads(path.read_text(encoding="utf-8"))
        if "registration" in path.name:
            HoldoutRegistration.model_validate(document)
        elif "freeze" in path.name:
            FinalistFreeze.model_validate(document)
        elif "request" in path.name:
            B2QueryRequest.model_validate(document)
        elif "scores" in path.name:
            for record in document:
                HiddenCaseScores.model_validate(record)
        else:
            pytest.fail(f"unclassified example fixture: {path.name}")
