"""Prepare and summarize a blind comparison of base and fine-tuned outputs."""

from __future__ import annotations

import json
import random
from collections.abc import Sequence
from pathlib import Path
from statistics import mean
from typing import Any

from goodprose.jsonl import atomic_write, atomic_write_json, load_jsonl, serialize_jsonl
from goodprose.models import (
    EvalCase,
    ModelOutput,
    ReviewAssignment,
    ReviewChoice,
    ReviewKey,
    ReviewRow,
    SystemLabel,
)


class EvaluationError(ValueError):
    """Evaluation files are incomplete or inconsistent."""


def _indexed[RecordT: (EvalCase, ModelOutput, ReviewRow, ReviewAssignment)](
    records: Sequence[RecordT], *, kind: str
) -> dict[str, RecordT]:
    indexed: dict[str, RecordT] = {}
    for record in records:
        if record.id in indexed:
            raise EvaluationError(f"duplicate {kind} ID {record.id!r}")
        indexed[record.id] = record
    return indexed


def _require_same_ids(expected: set[str], actual: set[str], *, label: str) -> None:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing {missing}")
        if extra:
            details.append(f"unexpected {extra}")
        raise EvaluationError(f"{label} IDs do not match cases: {', '.join(details)}")


def prepare_review(
    cases_path: Path,
    baseline_path: Path,
    candidate_path: Path,
    packet_path: Path,
    key_path: Path,
    *,
    seed: int = 20260831,
) -> int:
    cases = _indexed(load_jsonl(cases_path, EvalCase), kind="case")
    if not cases:
        raise EvaluationError("evaluation case file is empty")
    baseline = _indexed(load_jsonl(baseline_path, ModelOutput), kind="baseline output")
    candidate = _indexed(load_jsonl(candidate_path, ModelOutput), kind="candidate output")
    expected_ids = set(cases)
    _require_same_ids(expected_ids, set(baseline), label="baseline")
    _require_same_ids(expected_ids, set(candidate), label="candidate")

    randomizer = random.Random(seed)
    rows: list[ReviewRow] = []
    assignments: list[ReviewAssignment] = []
    for case_id in sorted(cases):
        case = cases[case_id]
        if randomizer.getrandbits(1):
            response_a = candidate[case_id].output
            response_b = baseline[case_id].output
            a_label = SystemLabel.CANDIDATE
            b_label = SystemLabel.BASELINE
        else:
            response_a = baseline[case_id].output
            response_b = candidate[case_id].output
            a_label = SystemLabel.BASELINE
            b_label = SystemLabel.CANDIDATE
        rows.append(
            ReviewRow(
                id=case.id,
                input=case.input,
                reference_output=case.reference_output,
                response_a=response_a,
                response_b=response_b,
            )
        )
        assignments.append(ReviewAssignment(id=case.id, a=a_label, b=b_label))

    atomic_write(packet_path, serialize_jsonl(rows))
    key = ReviewKey(seed=seed, assignments=tuple(assignments))
    atomic_write_json(key_path, key.model_dump(mode="json"))
    return len(rows)


def _load_key(path: Path) -> ReviewKey:
    return ReviewKey.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _completed(row: ReviewRow) -> bool:
    return all(
        value is not None
        for value in (
            row.factuality_a_pass,
            row.factuality_b_pass,
            row.preference,
            row.edit_burden_a,
            row.edit_burden_b,
        )
    )


def _system_value[T](assignment: ReviewAssignment, a_value: T, b_value: T) -> dict[str, T]:
    return {assignment.a.value: a_value, assignment.b.value: b_value}


def summarize_review(packet_path: Path, key_path: Path, output_path: Path) -> dict[str, Any]:
    rows = _indexed(load_jsonl(packet_path, ReviewRow), kind="review")
    assignments = _indexed(list(_load_key(key_path).assignments), kind="assignment")
    _require_same_ids(set(assignments), set(rows), label="review")
    incomplete = sorted(row.id for row in rows.values() if not _completed(row))
    if incomplete:
        raise EvaluationError(f"review fields are incomplete for {incomplete}")

    preferences = {SystemLabel.BASELINE.value: 0, SystemLabel.CANDIDATE.value: 0, "tie": 0}
    factuality: dict[str, list[bool]] = {
        SystemLabel.BASELINE.value: [],
        SystemLabel.CANDIDATE.value: [],
    }
    edit_burden: dict[str, list[int]] = {
        SystemLabel.BASELINE.value: [],
        SystemLabel.CANDIDATE.value: [],
    }
    per_case: list[dict[str, Any]] = []
    for case_id in sorted(rows):
        row = rows[case_id]
        assignment = assignments[case_id]
        assert row.factuality_a_pass is not None
        assert row.factuality_b_pass is not None
        assert row.preference is not None
        assert row.edit_burden_a is not None
        assert row.edit_burden_b is not None
        case_factuality = _system_value(assignment, row.factuality_a_pass, row.factuality_b_pass)
        case_edit = _system_value(assignment, row.edit_burden_a, row.edit_burden_b)
        for label in (SystemLabel.BASELINE.value, SystemLabel.CANDIDATE.value):
            factuality[label].append(case_factuality[label])
            edit_burden[label].append(case_edit[label])

        if row.preference == ReviewChoice.TIE:
            winner = "tie"
        elif row.preference == ReviewChoice.A:
            winner = assignment.a.value
        else:
            winner = assignment.b.value
        preferences[winner] += 1
        per_case.append(
            {
                "id": case_id,
                "winner": winner,
                "baseline_factuality_pass": case_factuality[SystemLabel.BASELINE.value],
                "candidate_factuality_pass": case_factuality[SystemLabel.CANDIDATE.value],
                "baseline_edit_burden": case_edit[SystemLabel.BASELINE.value],
                "candidate_edit_burden": case_edit[SystemLabel.CANDIDATE.value],
                "notes": row.notes,
            }
        )

    factuality_rate = {label: sum(values) / len(values) for label, values in factuality.items()}
    summary: dict[str, Any] = {
        "version": 1,
        "case_count": len(rows),
        "preferences": preferences,
        "factuality_pass_rate": factuality_rate,
        "mean_edit_burden": {label: mean(values) for label, values in edit_burden.items()},
        "candidate_passes_factuality_gate": (
            factuality_rate[SystemLabel.CANDIDATE.value]
            >= factuality_rate[SystemLabel.BASELINE.value]
        ),
        "per_case": per_case,
    }
    atomic_write_json(output_path, summary)
    return summary
