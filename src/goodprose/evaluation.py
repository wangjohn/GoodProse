"""Prepare and summarize a blind comparison of base and fine-tuned outputs."""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from statistics import mean
from typing import Any

from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    load_jsonl,
    serialize_jsonl,
    sha256_file,
)
from goodprose.models import (
    DecisionRules,
    EvalCase,
    GenerationRunManifest,
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
    baseline_manifest_path: Path | None = None,
    candidate_manifest_path: Path | None = None,
    guide_path: Path | None = None,
) -> int:
    cases = _indexed(load_jsonl(cases_path, EvalCase), kind="case")
    if not cases:
        raise EvaluationError("evaluation case file is empty")
    for case in cases.values():
        actual_hash = hashlib.sha256(case.reference_output.encode()).hexdigest()
        if actual_hash != case.target_sha256:
            raise EvaluationError(f"case {case.id!r} has a stale reference target hash")
    baseline = _indexed(load_jsonl(baseline_path, ModelOutput), kind="baseline output")
    candidate = _indexed(load_jsonl(candidate_path, ModelOutput), kind="candidate output")
    expected_ids = set(cases)
    _require_same_ids(expected_ids, set(baseline), label="baseline")
    _require_same_ids(expected_ids, set(candidate), label="candidate")
    baseline_run_id, candidate_run_id = _validate_run_manifests(
        cases_path,
        baseline_manifest_path,
        candidate_manifest_path,
    )

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
                lineage_id=case.lineage_id,
                input_method=case.input_method,
                input=case.input,
                response_a=response_a,
                response_b=response_b,
            )
        )
        assignments.append(ReviewAssignment(id=case.id, a=a_label, b=b_label))

    atomic_write(packet_path, serialize_jsonl(rows))
    key = ReviewKey(
        seed=seed,
        baseline_run_id=baseline_run_id,
        candidate_run_id=candidate_run_id,
        assignments=tuple(assignments),
    )
    atomic_write_json(key_path, key.model_dump(mode="json"))
    if guide_path is not None:
        atomic_write(guide_path, render_review_guide())
    return len(rows)


def _load_run_manifest(path: Path) -> GenerationRunManifest:
    return GenerationRunManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _validate_run_manifests(
    cases_path: Path,
    baseline_manifest_path: Path | None,
    candidate_manifest_path: Path | None,
) -> tuple[str | None, str | None]:
    if (baseline_manifest_path is None) != (candidate_manifest_path is None):
        raise EvaluationError("provide both run manifests or neither")
    if baseline_manifest_path is None or candidate_manifest_path is None:
        return None, None

    baseline = _load_run_manifest(baseline_manifest_path)
    candidate = _load_run_manifest(candidate_manifest_path)
    if baseline.role is not SystemLabel.BASELINE:
        raise EvaluationError("baseline run manifest must use the baseline role")
    if candidate.role is not SystemLabel.CANDIDATE:
        raise EvaluationError("candidate run manifest must use the candidate role")
    if baseline.adapter_id is not None:
        raise EvaluationError("baseline run manifest must not identify an adapter")
    if candidate.adapter_id is None:
        raise EvaluationError("candidate run manifest must identify its adapter checkpoint")
    cases_hash = sha256_file(cases_path)
    for manifest in (baseline, candidate):
        if manifest.cases_sha256 != cases_hash:
            raise EvaluationError(f"run {manifest.run_id!r} does not match the frozen case file")
    for attribute in (
        "base_model_id",
        "model_id",
        "base_model_revision",
        "tokenizer_revision",
        "prompt_strategy",
        "chat_template_sha256",
        "system_prompt_sha256",
        "dataset_manifest_sha256",
    ):
        if getattr(baseline, attribute) != getattr(candidate, attribute):
            raise EvaluationError(f"run manifests differ on {attribute}")
    if baseline.decoding != candidate.decoding:
        raise EvaluationError("run manifests must use identical decoding settings")
    return baseline.run_id, candidate.run_id


def render_review_guide() -> bytes:
    return b"""# Blind writing evaluation

Do not open the published reference or the unblinding key until this packet is complete.
Evaluate both responses only against the supplied input and any sources it contains.

For each response:

1. Set factuality to `false` if it adds any unsupported factual claim, and list every finding in
   `unsupported_claims_a` or `unsupported_claims_b`. Unsupported facts are a hard failure.
2. Mark whether it follows the requested deliverable, scope, and constraints.
3. Choose which response sounds more like the author in `voice_preference`.
4. Choose which response you would rather edit and publish in `overall_preference`.
5. Score edit burden:
   - 1: publishable as written
   - 2: light wording or transition edits
   - 3: substantial paragraph or structural edits
   - 4: rewrite most of it, though some material is reusable
   - 5: unusable or complete rewrite

Use `a`, `b`, or `tie` for both preference fields. Keep concrete reasons in `notes`.
"""


def _load_key(path: Path) -> ReviewKey:
    return ReviewKey.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _completed(row: ReviewRow) -> bool:
    return all(
        value is not None
        for value in (
            row.factuality_a_pass,
            row.factuality_b_pass,
            row.instruction_following_a_pass,
            row.instruction_following_b_pass,
            row.voice_preference,
            row.overall_preference,
            row.edit_burden_a,
            row.edit_burden_b,
        )
    )


def _system_value[T](assignment: ReviewAssignment, a_value: T, b_value: T) -> dict[str, T]:
    return {assignment.a.value: a_value, assignment.b.value: b_value}


def _winner(assignment: ReviewAssignment, preference: ReviewChoice) -> str:
    if preference == ReviewChoice.TIE:
        return "tie"
    if preference == ReviewChoice.A:
        return assignment.a.value
    return assignment.b.value


def _load_rules(path: Path | None) -> DecisionRules:
    if path is None:
        return DecisionRules()
    return DecisionRules.model_validate(json.loads(path.read_text(encoding="utf-8")))


def summarize_review(
    packet_path: Path,
    key_path: Path,
    output_path: Path,
    *,
    decision_rules_path: Path | None = None,
) -> dict[str, Any]:
    rows = _indexed(load_jsonl(packet_path, ReviewRow), kind="review")
    if not rows:
        raise EvaluationError("review packet is empty")
    key = _load_key(key_path)
    assignments = _indexed(list(key.assignments), kind="assignment")
    _require_same_ids(set(assignments), set(rows), label="review")
    incomplete = sorted(row.id for row in rows.values() if not _completed(row))
    if incomplete:
        raise EvaluationError(f"review fields are incomplete for {incomplete}")

    voice_preferences = {SystemLabel.BASELINE.value: 0, SystemLabel.CANDIDATE.value: 0, "tie": 0}
    overall_preferences = {
        SystemLabel.BASELINE.value: 0,
        SystemLabel.CANDIDATE.value: 0,
        "tie": 0,
    }
    factuality: dict[str, list[bool]] = {
        SystemLabel.BASELINE.value: [],
        SystemLabel.CANDIDATE.value: [],
    }
    edit_burden: dict[str, list[int]] = {
        SystemLabel.BASELINE.value: [],
        SystemLabel.CANDIDATE.value: [],
    }
    instruction_following: dict[str, list[bool]] = {
        SystemLabel.BASELINE.value: [],
        SystemLabel.CANDIDATE.value: [],
    }
    lineage_case_winners: dict[str, Counter[str]] = {}
    input_method_case_winners: dict[str, Counter[str]] = {}
    unsupported_claim_counts = {
        SystemLabel.BASELINE.value: 0,
        SystemLabel.CANDIDATE.value: 0,
    }
    per_case: list[dict[str, Any]] = []
    for case_id in sorted(rows):
        row = rows[case_id]
        assignment = assignments[case_id]
        assert row.factuality_a_pass is not None
        assert row.factuality_b_pass is not None
        assert row.instruction_following_a_pass is not None
        assert row.instruction_following_b_pass is not None
        assert row.voice_preference is not None
        assert row.overall_preference is not None
        assert row.edit_burden_a is not None
        assert row.edit_burden_b is not None
        case_factuality = _system_value(assignment, row.factuality_a_pass, row.factuality_b_pass)
        case_instruction = _system_value(
            assignment,
            row.instruction_following_a_pass,
            row.instruction_following_b_pass,
        )
        case_edit = _system_value(assignment, row.edit_burden_a, row.edit_burden_b)
        for label in (SystemLabel.BASELINE.value, SystemLabel.CANDIDATE.value):
            factuality[label].append(case_factuality[label])
            instruction_following[label].append(case_instruction[label])
            edit_burden[label].append(case_edit[label])

        voice_winner = _winner(assignment, row.voice_preference)
        overall_winner = _winner(assignment, row.overall_preference)
        voice_preferences[voice_winner] += 1
        overall_preferences[overall_winner] += 1
        lineage_case_winners.setdefault(row.lineage_id, Counter())[overall_winner] += 1
        input_method_case_winners.setdefault(row.input_method.value, Counter())[overall_winner] += 1
        unsupported = _system_value(
            assignment,
            list(row.unsupported_claims_a),
            list(row.unsupported_claims_b),
        )
        for label in (SystemLabel.BASELINE.value, SystemLabel.CANDIDATE.value):
            unsupported_claim_counts[label] += len(unsupported[label])
        per_case.append(
            {
                "id": case_id,
                "lineage_id": row.lineage_id,
                "input_method": row.input_method.value,
                "voice_winner": voice_winner,
                "overall_winner": overall_winner,
                "baseline_factuality_pass": case_factuality[SystemLabel.BASELINE.value],
                "candidate_factuality_pass": case_factuality[SystemLabel.CANDIDATE.value],
                "baseline_unsupported_claims": unsupported[SystemLabel.BASELINE.value],
                "candidate_unsupported_claims": unsupported[SystemLabel.CANDIDATE.value],
                "baseline_instruction_following_pass": case_instruction[SystemLabel.BASELINE.value],
                "candidate_instruction_following_pass": case_instruction[
                    SystemLabel.CANDIDATE.value
                ],
                "baseline_edit_burden": case_edit[SystemLabel.BASELINE.value],
                "candidate_edit_burden": case_edit[SystemLabel.CANDIDATE.value],
                "notes": row.notes,
            }
        )

    per_input_method = [
        {
            "input_method": input_method,
            "case_preferences": {
                SystemLabel.BASELINE.value: counts[SystemLabel.BASELINE.value],
                SystemLabel.CANDIDATE.value: counts[SystemLabel.CANDIDATE.value],
                "tie": counts["tie"],
            },
        }
        for input_method, counts in sorted(input_method_case_winners.items())
    ]

    factuality_rate = {label: sum(values) / len(values) for label, values in factuality.items()}
    instruction_rate = {
        label: sum(values) / len(values) for label, values in instruction_following.items()
    }
    mean_edit = {label: mean(values) for label, values in edit_burden.items()}
    per_lineage: list[dict[str, Any]] = []
    lineage_wins = {SystemLabel.BASELINE.value: 0, SystemLabel.CANDIDATE.value: 0, "tie": 0}
    for lineage_id in sorted(lineage_case_winners):
        counts = lineage_case_winners[lineage_id]
        if counts[SystemLabel.CANDIDATE.value] > counts[SystemLabel.BASELINE.value]:
            winner = SystemLabel.CANDIDATE.value
        elif counts[SystemLabel.BASELINE.value] > counts[SystemLabel.CANDIDATE.value]:
            winner = SystemLabel.BASELINE.value
        else:
            winner = "tie"
        lineage_wins[winner] += 1
        per_lineage.append(
            {
                "lineage_id": lineage_id,
                "winner": winner,
                "case_preferences": {
                    SystemLabel.BASELINE.value: counts[SystemLabel.BASELINE.value],
                    SystemLabel.CANDIDATE.value: counts[SystemLabel.CANDIDATE.value],
                    "tie": counts["tie"],
                },
            }
        )

    rules = _load_rules(decision_rules_path)
    edit_improvement = (
        mean_edit[SystemLabel.BASELINE.value] - mean_edit[SystemLabel.CANDIDATE.value]
    )
    decision_checks = {
        "candidate_factuality": (
            not rules.require_all_candidate_factuality_passes
            or all(factuality[SystemLabel.CANDIDATE.value])
        ),
        "candidate_instruction_following": (
            not rules.require_all_candidate_instruction_passes
            or all(instruction_following[SystemLabel.CANDIDATE.value])
        ),
        "overall_case_advantage": (
            not rules.require_candidate_overall_case_advantage
            or overall_preferences[SystemLabel.CANDIDATE.value]
            > overall_preferences[SystemLabel.BASELINE.value]
        ),
        "no_lineage_losses": (
            not rules.require_no_lineage_losses or lineage_wins[SystemLabel.BASELINE.value] == 0
        ),
        "minimum_lineage_wins": (
            lineage_wins[SystemLabel.CANDIDATE.value] >= rules.minimum_lineage_wins
        ),
        "mean_edit_burden_improvement": (
            edit_improvement >= rules.minimum_mean_edit_burden_improvement
        ),
    }
    failed_checks = [name for name, passed in decision_checks.items() if not passed]
    summary: dict[str, Any] = {
        "version": 2,
        "runs": {
            "baseline": key.baseline_run_id,
            "candidate": key.candidate_run_id,
        },
        "case_count": len(rows),
        "lineage_count": len(per_lineage),
        "preferences": overall_preferences,
        "overall_preferences": overall_preferences,
        "voice_preferences": voice_preferences,
        "factuality_pass_rate": factuality_rate,
        "unsupported_claim_count": unsupported_claim_counts,
        "instruction_following_pass_rate": instruction_rate,
        "mean_edit_burden": mean_edit,
        "mean_edit_burden_improvement": edit_improvement,
        "candidate_passes_factuality_gate": (all(factuality[SystemLabel.CANDIDATE.value])),
        "lineage_preferences": lineage_wins,
        "decision_rules": rules.model_dump(mode="json"),
        "decision_checks": decision_checks,
        "failed_decision_checks": failed_checks,
        "candidate_recommended": all(decision_checks.values()),
        "per_case": per_case,
        "per_lineage": per_lineage,
        "per_input_method": per_input_method,
    }
    atomic_write_json(output_path, summary)
    return summary
