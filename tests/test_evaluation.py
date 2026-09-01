from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from goodprose.evaluation import EvaluationError, prepare_review, summarize_review
from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl, sha256_file
from goodprose.models import (
    DecodingSettings,
    EvalCase,
    GenerationRunManifest,
    InputMethod,
    ModelOutput,
    ReviewChoice,
    ReviewKey,
    ReviewRow,
    SystemLabel,
)


def _case(identifier: str, lineage_id: str) -> EvalCase:
    reference = f"Published {identifier}"
    return EvalCase(
        id=identifier,
        lineage_id=lineage_id,
        input=f"Outline {identifier}",
        input_method=InputMethod.ORIGINAL_OUTLINE,
        reference_output=reference,
        target_sha256=hashlib.sha256(reference.encode()).hexdigest(),
    )


def test_prepares_and_summarizes_blind_review(tmp_path: Path) -> None:
    cases_path = tmp_path / "cases.jsonl"
    baseline_path = tmp_path / "baseline.jsonl"
    candidate_path = tmp_path / "candidate.jsonl"
    packet_path = tmp_path / "review.jsonl"
    key_path = tmp_path / "key.json"
    summary_path = tmp_path / "summary.json"
    guide_path = tmp_path / "REVIEW.md"
    cases = [_case("one", "lineage-one"), _case("two", "lineage-two")]
    atomic_write(cases_path, serialize_jsonl(cases))
    atomic_write(
        baseline_path,
        serialize_jsonl([ModelOutput(id=case.id, output=f"Base {case.id}") for case in cases]),
    )
    atomic_write(
        candidate_path,
        serialize_jsonl([ModelOutput(id=case.id, output=f"SFT {case.id}") for case in cases]),
    )

    assert (
        prepare_review(
            cases_path,
            baseline_path,
            candidate_path,
            packet_path,
            key_path,
            seed=42,
            guide_path=guide_path,
        )
        == 2
    )
    assert "Published one" not in packet_path.read_text()
    assert "Unsupported facts are a hard failure" in guide_path.read_text()
    key = ReviewKey.model_validate(json.loads(key_path.read_text()))
    assignments = {assignment.id: assignment for assignment in key.assignments}
    completed: list[ReviewRow] = []
    for row in load_jsonl(packet_path, ReviewRow):
        assignment = assignments[row.id]
        candidate_is_a = assignment.a == SystemLabel.CANDIDATE
        completed.append(
            row.model_copy(
                update={
                    "factuality_a_pass": True,
                    "factuality_b_pass": True,
                    "instruction_following_a_pass": True,
                    "instruction_following_b_pass": True,
                    "voice_preference": ReviewChoice.A if candidate_is_a else ReviewChoice.B,
                    "overall_preference": ReviewChoice.A if candidate_is_a else ReviewChoice.B,
                    "edit_burden_a": 1 if candidate_is_a else 3,
                    "edit_burden_b": 3 if candidate_is_a else 1,
                }
            )
        )
    atomic_write(packet_path, serialize_jsonl(completed))

    summary = summarize_review(packet_path, key_path, summary_path)

    assert summary["preferences"] == {"baseline": 0, "candidate": 2, "tie": 0}
    assert summary["voice_preferences"] == {"baseline": 0, "candidate": 2, "tie": 0}
    assert summary["mean_edit_burden"] == {"baseline": 3, "candidate": 1}
    assert summary["candidate_passes_factuality_gate"] is True
    assert summary["lineage_preferences"] == {"baseline": 0, "candidate": 2, "tie": 0}
    assert summary["unsupported_claim_count"] == {"baseline": 0, "candidate": 0}
    assert summary["per_input_method"] == [
        {
            "input_method": "original_outline",
            "case_preferences": {"baseline": 0, "candidate": 2, "tie": 0},
        }
    ]
    assert summary["failed_decision_checks"] == []
    assert summary["candidate_recommended"] is True


def test_prepare_review_validates_run_manifests(tmp_path: Path) -> None:
    cases_path = tmp_path / "cases.jsonl"
    baseline_path = tmp_path / "baseline.jsonl"
    candidate_path = tmp_path / "candidate.jsonl"
    case = _case("one", "lineage")
    atomic_write(cases_path, serialize_jsonl([case]))
    atomic_write(baseline_path, serialize_jsonl([ModelOutput(id="one", output="Base")]))
    atomic_write(candidate_path, serialize_jsonl([ModelOutput(id="one", output="Candidate")]))
    decoding = DecodingSettings(max_new_tokens=512, seed=7)
    common = {
        "model_id": "example/model",
        "base_model_id": "example/model",
        "base_model_revision": "abc123",
        "tokenizer_revision": "abc123",
        "prompt_strategy": "matched-system-prompt",
        "chat_template_sha256": "1" * 64,
        "system_prompt_sha256": "2" * 64,
        "cases_sha256": sha256_file(cases_path),
        "dataset_manifest_sha256": "3" * 64,
        "decoding": decoding,
    }
    baseline_manifest = GenerationRunManifest(
        run_id="base-run",
        role=SystemLabel.BASELINE,
        **common,
    )
    candidate_manifest = GenerationRunManifest(
        run_id="adapter-run",
        role=SystemLabel.CANDIDATE,
        adapter_id="adapter/path",
        **common,
    )
    baseline_manifest_path = tmp_path / "base-run.json"
    candidate_manifest_path = tmp_path / "adapter-run.json"
    baseline_manifest_path.write_text(baseline_manifest.model_dump_json())
    candidate_manifest_path.write_text(candidate_manifest.model_dump_json())

    prepare_review(
        cases_path,
        baseline_path,
        candidate_path,
        tmp_path / "review.jsonl",
        tmp_path / "key.json",
        baseline_manifest_path=baseline_manifest_path,
        candidate_manifest_path=candidate_manifest_path,
    )

    bad_manifest = candidate_manifest.model_copy(
        update={"decoding": DecodingSettings(max_new_tokens=256, seed=7)}
    )
    candidate_manifest_path.write_text(bad_manifest.model_dump_json())
    with pytest.raises(EvaluationError, match="identical decoding settings"):
        prepare_review(
            cases_path,
            baseline_path,
            candidate_path,
            tmp_path / "review.jsonl",
            tmp_path / "key.json",
            baseline_manifest_path=baseline_manifest_path,
            candidate_manifest_path=candidate_manifest_path,
        )
