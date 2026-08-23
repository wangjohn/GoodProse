from __future__ import annotations

from goodprose.executive_writing.analysis import RescoredRun, paired_comparison
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
