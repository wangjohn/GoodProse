from __future__ import annotations

import json
from pathlib import Path

from goodprose.evaluation import prepare_review, summarize_review
from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import (
    EvalCase,
    ModelOutput,
    ReviewChoice,
    ReviewKey,
    ReviewRow,
    SystemLabel,
)


def test_prepares_and_summarizes_blind_review(tmp_path: Path) -> None:
    cases_path = tmp_path / "cases.jsonl"
    baseline_path = tmp_path / "baseline.jsonl"
    candidate_path = tmp_path / "candidate.jsonl"
    packet_path = tmp_path / "review.jsonl"
    key_path = tmp_path / "key.json"
    summary_path = tmp_path / "summary.json"
    cases = [
        EvalCase(id="one", input="Outline one", reference_output="Published one"),
        EvalCase(id="two", input="Outline two", reference_output="Published two"),
    ]
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
        prepare_review(cases_path, baseline_path, candidate_path, packet_path, key_path, seed=42)
        == 2
    )
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
                    "preference": ReviewChoice.A if candidate_is_a else ReviewChoice.B,
                    "edit_burden_a": 1 if candidate_is_a else 3,
                    "edit_burden_b": 3 if candidate_is_a else 1,
                }
            )
        )
    atomic_write(packet_path, serialize_jsonl(completed))

    summary = summarize_review(packet_path, key_path, summary_path)

    assert summary["preferences"] == {"baseline": 0, "candidate": 2, "tie": 0}
    assert summary["mean_edit_burden"] == {"baseline": 3, "candidate": 1}
    assert summary["candidate_passes_factuality_gate"] is True
