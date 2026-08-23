from __future__ import annotations

from goodprose.executive_writing.analysis import (
    RescoredRun,
    evaluate_iteration_gates,
    paired_comparison,
)
from goodprose.executive_writing.benchmark import CaseScore


def _run(candidate_id: str, values: list[float], gates: list[bool]) -> RescoredRun:
    scores = [
        CaseScore(
            scorer_version="goodprose-deterministic-v1.1",
            case_id=f"case-{index}",
            candidate_id=candidate_id,
            output_sha256="0" * 64,
            word_count=10,
            source_change_ratio=None,
            dimensions={},
            development_score=value,
            passes_hard_gates=gate,
            checks=(),
            errors=(),
        )
        for index, (value, gate) in enumerate(zip(values, gates, strict=True))
    ]
    return RescoredRun(
        candidate_id=candidate_id,
        scores=scores,
        generations=[],
        summary={},
        artifact_hashes={},
        source_artifact_hashes={},
    )


def test_paired_comparison_is_deterministic_and_paired() -> None:
    baseline = _run("baseline", [10, 20, 30, 40], [True, False, True, False])
    candidate = _run("candidate", [13, 20, 29, 44], [True, True, True, False])

    first = paired_comparison(baseline, candidate, iterations=500, seed=17)
    second = paired_comparison(baseline, candidate, iterations=500, seed=17)

    assert first == second
    assert first["paired_mean_difference"] == 1.5
    assert first["paired_median_difference"] == 1.5
    assert first["win_tie_loss"] == {"wins": 2, "ties": 1, "losses": 1}
    assert first["hard_gate_pass_rate_difference"] == 0.25
    assert not first["meets_advancement_gate"]


def test_paired_comparison_requires_no_hard_gate_regression() -> None:
    baseline = _run("baseline", [10, 10], [True, True])
    candidate = _run("candidate", [15, 15], [True, False])

    result = paired_comparison(baseline, candidate, iterations=100, seed=19)

    assert result["paired_mean_difference"] == 5
    assert not result["meets_advancement_gate"]


def test_iteration_gates_enforce_quality_hard_gate_and_efficiency() -> None:
    result = evaluate_iteration_gates(
        comparison={"paired_mean_difference": 3.0},
        baseline_summary={"hard_gate_pass_rate": 0.375},
        candidate_summary={
            "hard_gate_pass_rate": 0.375,
            "error_counts": {"omission": 13, "fabrication": 1, "placeholder_loss": 1},
            "latency_ms": {"mean": 6800.0},
            "output_tokens": 16_800,
            "settled_cost_usd": 0,
        },
    )

    assert result["primary_advancement_pass"]
    assert result["all_guardrails_pass"]


def test_iteration_gates_reject_latency_and_token_overruns() -> None:
    result = evaluate_iteration_gates(
        comparison={"paired_mean_difference": 3.0},
        baseline_summary={"hard_gate_pass_rate": 0.375},
        candidate_summary={
            "hard_gate_pass_rate": 0.375,
            "error_counts": {"omission": 13},
            "latency_ms": {"mean": 6812.087},
            "output_tokens": 16_801,
            "settled_cost_usd": 0,
        },
    )

    assert result["primary_advancement_pass"]
    assert not result["all_guardrails_pass"]


def test_case_score_accepts_omitted_optional_change_ratio() -> None:
    score = _run("candidate", [10], [True]).scores[0]
    payload = score.model_dump(mode="json", exclude_none=True)

    restored = CaseScore.model_validate(payload)

    assert restored.source_change_ratio is None
