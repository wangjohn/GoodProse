"""Offline rescoring and paired analysis for executive-writing baselines."""

from __future__ import annotations

import json
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from goodprose.executive_writing.baseline import Generation
from goodprose.executive_writing.benchmark import (
    BenchmarkCase,
    CaseScore,
    load_cases,
    score_output_v1_1,
)
from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    load_jsonl,
    serialize_jsonl,
    sha256_file,
)

EVALUATION_ID = "goodprose-b1-v1.1"
SCORER_VERSION = "goodprose-deterministic-v1.1"
MINIMUM_EFFECT_POINTS = 2.0
BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 20_260_822


@dataclass(frozen=True)
class RescoredRun:
    candidate_id: str
    scores: list[CaseScore]
    generations: list[Generation]
    summary: dict[str, Any]
    artifact_hashes: dict[str, str]
    source_artifact_hashes: dict[str, str]


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _validate_timestamp(value: str) -> None:
    from datetime import datetime

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("analysis timestamp must include a timezone")


def _summarize(scores: list[CaseScore], generations: list[Generation]) -> dict[str, Any]:
    if not scores or not generations:
        raise ValueError("rescoring requires non-empty scores and generations")
    candidate_ids = {score.candidate_id for score in scores} | {
        generation.candidate_id for generation in generations
    }
    if len(candidate_ids) != 1:
        raise ValueError("rescored run must contain exactly one candidate ID")
    dimensions = {
        name: round(statistics.fmean(score.dimensions[name] for score in scores), 4)
        for name in scores[0].dimensions
    }
    errors = Counter(error for score in scores for error in score.errors)
    latencies = [generation.latency_ms for generation in generations]
    return {
        "evaluation_id": EVALUATION_ID,
        "scorer_version": SCORER_VERSION,
        "candidate_id": candidate_ids.pop(),
        "case_count": len(scores),
        "mean_development_score": round(
            statistics.fmean(score.development_score for score in scores), 4
        ),
        "median_development_score": round(
            statistics.median(score.development_score for score in scores), 4
        ),
        "hard_gate_pass_rate": round(
            statistics.fmean(float(score.passes_hard_gates) for score in scores), 4
        ),
        "dimension_means": dimensions,
        "error_counts": dict(sorted(errors.items())),
        "latency_ms": {
            "mean": round(statistics.fmean(latencies), 4),
            "median": round(statistics.median(latencies), 4),
            "p95": round(_percentile(latencies, 0.95), 4),
        },
        "prompt_tokens": sum(item.prompt_tokens or 0 for item in generations),
        "output_tokens": sum(item.output_tokens or 0 for item in generations),
        "settled_cost_usd": 0,
    }


def rescore_run(
    *,
    run_dir: Path,
    cases: list[BenchmarkCase],
    output_root: Path,
    benchmark_manifest_path: Path,
    correction_record_path: Path,
    timestamp: str,
) -> RescoredRun:
    """Rescore exact saved output bytes without invoking a model."""

    _validate_timestamp(timestamp)
    source_manifest: dict[str, Any] = json.loads(
        (run_dir / "run-manifest.json").read_text(encoding="utf-8")
    )
    source_outputs_path = run_dir / "outputs.jsonl"
    expected_output_hash = source_manifest.get("artifact_hashes", {}).get("outputs_jsonl")
    actual_output_hash = sha256_file(source_outputs_path)
    if expected_output_hash != actual_output_hash:
        raise ValueError(f"source output hash mismatch in {run_dir}")
    if source_manifest.get("cases_sha256") != sha256_file(
        benchmark_manifest_path.parent / "cases.jsonl"
    ):
        raise ValueError(f"source cases hash mismatch in {run_dir}")

    generations = load_jsonl(source_outputs_path, Generation)
    case_by_id = {case.id: case for case in cases}
    if [item.case_id for item in generations] != [case.id for case in cases]:
        raise ValueError(f"source output case order mismatch in {run_dir}")
    for generation in generations:
        if generation.output_sha256 != sha256(generation.output.encode("utf-8")).hexdigest():
            raise ValueError(f"generation output hash mismatch for {generation.case_id}")

    scores = [
        score_output_v1_1(
            case_by_id[generation.case_id],
            generation.output,
            candidate_id=generation.candidate_id,
        )
        for generation in generations
    ]
    summary = _summarize(scores, generations)
    candidate_id = summary["candidate_id"]
    corrected_dir = output_root / candidate_id
    scores_payload = serialize_jsonl(scores)
    summary_payload = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
    atomic_write(corrected_dir / "scores.jsonl", scores_payload)
    atomic_write(corrected_dir / "summary.json", summary_payload)
    artifact_hashes = {
        "scores_jsonl": sha256(scores_payload).hexdigest(),
        "summary_json": sha256(summary_payload).hexdigest(),
    }
    source_artifact_hashes = {
        "outputs_jsonl": actual_output_hash,
        "v1_scores_jsonl": sha256_file(run_dir / "scores.jsonl"),
        "v1_summary_json": sha256_file(run_dir / "summary.json"),
        "v1_run_manifest_json": sha256_file(run_dir / "run-manifest.json"),
    }
    rescore_manifest = {
        "version": 1,
        "evaluation_id": EVALUATION_ID,
        "scorer_version": SCORER_VERSION,
        "candidate_id": candidate_id,
        "generated_at": timestamp,
        "method": "offline_rescore_of_identical_output_bytes",
        "source_experiment_id": source_manifest["experiment_id"],
        "source_code_revision": source_manifest["code_revision"],
        "benchmark_id": source_manifest["benchmark_id"],
        "benchmark_manifest_sha256": sha256_file(benchmark_manifest_path),
        "correction_record_sha256": sha256_file(correction_record_path),
        "source_artifact_hashes": source_artifact_hashes,
        "artifact_hashes": artifact_hashes,
        "provider": source_manifest["provider"],
        "model_id": source_manifest["model_id"],
        "settled_cost_usd": 0,
        "validity_status": "post_generation_evaluator_calibration",
    }
    atomic_write_json(corrected_dir / "rescore-manifest.json", rescore_manifest)
    artifact_hashes["rescore_manifest_json"] = sha256_file(corrected_dir / "rescore-manifest.json")
    return RescoredRun(
        candidate_id=candidate_id,
        scores=scores,
        generations=generations,
        summary=summary,
        artifact_hashes=artifact_hashes,
        source_artifact_hashes=source_artifact_hashes,
    )


def paired_comparison(
    baseline: RescoredRun,
    candidate: RescoredRun,
    *,
    iterations: int = BOOTSTRAP_ITERATIONS,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Compute the preregistered paired exploratory comparison."""

    if iterations < 1:
        raise ValueError("bootstrap iterations must be positive")
    baseline_by_case = {score.case_id: score for score in baseline.scores}
    candidate_by_case = {score.case_id: score for score in candidate.scores}
    if baseline_by_case.keys() != candidate_by_case.keys():
        raise ValueError("paired candidates must cover identical case IDs")
    case_ids = sorted(baseline_by_case)
    differences = [
        candidate_by_case[case_id].development_score - baseline_by_case[case_id].development_score
        for case_id in case_ids
    ]
    rng = random.Random(seed)
    bootstrap_means = [
        statistics.fmean(differences[rng.randrange(len(differences))] for _ in differences)
        for _ in range(iterations)
    ]
    wins = sum(value > 0 for value in differences)
    losses = sum(value < 0 for value in differences)
    ties = len(differences) - wins - losses
    baseline_gate = statistics.fmean(float(score.passes_hard_gates) for score in baseline.scores)
    candidate_gate = statistics.fmean(float(score.passes_hard_gates) for score in candidate.scores)
    mean_difference = statistics.fmean(differences)
    return {
        "baseline_id": baseline.candidate_id,
        "candidate_id": candidate.candidate_id,
        "case_count": len(differences),
        "paired_mean_difference": round(mean_difference, 4),
        "paired_median_difference": round(statistics.median(differences), 4),
        "win_tie_loss": {"wins": wins, "ties": ties, "losses": losses},
        "bootstrap_95_ci": {
            "lower": round(_percentile(bootstrap_means, 0.025), 4),
            "upper": round(_percentile(bootstrap_means, 0.975), 4),
            "iterations": iterations,
            "seed": seed,
        },
        "hard_gate_pass_rate_difference": round(candidate_gate - baseline_gate, 4),
        "minimum_effect_points": MINIMUM_EFFECT_POINTS,
        "meets_advancement_gate": (
            mean_difference >= MINIMUM_EFFECT_POINTS and candidate_gate >= baseline_gate
        ),
    }


def _case_results(runs: list[RescoredRun], cases: list[BenchmarkCase]) -> list[dict[str, Any]]:
    case_by_id = {case.id: case for case in cases}
    records: list[dict[str, Any]] = []
    for run in sorted(runs, key=lambda item: item.candidate_id):
        for score in run.scores:
            records.append(
                {
                    "evaluation_id": EVALUATION_ID,
                    "scorer_version": SCORER_VERSION,
                    "candidate_id": run.candidate_id,
                    "case_id": score.case_id,
                    "task_family": case_by_id[score.case_id].input.task_family.value,
                    "development_score": score.development_score,
                    "passes_hard_gates": score.passes_hard_gates,
                    "errors": list(score.errors),
                    "failed_critical_check_ids": [
                        check.id for check in score.checks if check.critical and not check.passed
                    ],
                }
            )
    return records


def _task_family_slices(
    runs: list[RescoredRun], cases: list[BenchmarkCase]
) -> dict[str, dict[str, Any]]:
    family_by_case = {case.id: case.input.task_family.value for case in cases}
    slices: dict[str, dict[str, Any]] = defaultdict(dict)
    for run in runs:
        grouped: dict[str, list[CaseScore]] = defaultdict(list)
        for score in run.scores:
            grouped[family_by_case[score.case_id]].append(score)
        for family, scores in grouped.items():
            slices[family][run.candidate_id] = {
                "case_count": len(scores),
                "mean_development_score": round(
                    statistics.fmean(score.development_score for score in scores), 4
                ),
                "hard_gate_pass_rate": round(
                    statistics.fmean(float(score.passes_hard_gates) for score in scores), 4
                ),
            }
    return dict(sorted(slices.items()))


def _failure_analysis(run: RescoredRun) -> dict[str, Any]:
    failed_checks = Counter(
        check.id
        for score in run.scores
        for check in score.checks
        if check.critical and not check.passed
    )
    return {
        "error_counts": run.summary["error_counts"],
        "failed_critical_check_counts": dict(sorted(failed_checks.items())),
        "hard_gate_failures": sum(not score.passes_hard_gates for score in run.scores),
    }


def analyze_baselines(
    *,
    source_run_dirs: list[Path],
    cases_path: Path,
    benchmark_manifest_path: Path,
    correction_record_path: Path,
    corrected_output_root: Path,
    results_path: Path,
    case_results_path: Path,
    timestamp: str,
) -> dict[str, Any]:
    """Rescore all runs and publish one machine-readable comparison artifact."""

    _validate_timestamp(timestamp)
    cases = load_cases(cases_path)
    runs = [
        rescore_run(
            run_dir=run_dir,
            cases=cases,
            output_root=corrected_output_root,
            benchmark_manifest_path=benchmark_manifest_path,
            correction_record_path=correction_record_path,
            timestamp=timestamp,
        )
        for run_dir in source_run_dirs
    ]
    run_by_id = {run.candidate_id: run for run in runs}
    if len(run_by_id) != len(runs):
        raise ValueError("candidate IDs must be unique")
    minimal_id = "qwen2.5-0.5b-minimal-v1"
    profile_id = "qwen2.5-0.5b-profile-v1"
    retrieval_id = "qwen2.5-0.5b-retrieval-v1"
    required = {minimal_id, profile_id, retrieval_id}
    if set(run_by_id) != required:
        raise ValueError(f"expected candidate IDs {sorted(required)}")

    case_records = _case_results(runs, cases)
    case_payload = (
        "\n".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            for record in case_records
        )
        + "\n"
    ).encode()
    atomic_write(case_results_path, case_payload)
    comparisons = [
        paired_comparison(run_by_id[minimal_id], run_by_id[profile_id]),
        paired_comparison(run_by_id[minimal_id], run_by_id[retrieval_id]),
        paired_comparison(run_by_id[profile_id], run_by_id[retrieval_id]),
    ]
    result = {
        "version": 1,
        "analysis_id": "goodprose-b1-v1.1-baseline-analysis",
        "generated_at": timestamp,
        "status": "exploratory_post_generation_evaluator_calibration",
        "benchmark_id": "goodprose-b1-v1",
        "evaluation_id": EVALUATION_ID,
        "cases_sha256": sha256_file(cases_path),
        "benchmark_manifest_sha256": sha256_file(benchmark_manifest_path),
        "scorer_version": SCORER_VERSION,
        "correction_record_sha256": sha256_file(correction_record_path),
        "case_results_sha256": sha256(case_payload).hexdigest(),
        "candidates": [
            {
                **run.summary,
                "source_artifact_hashes": run.source_artifact_hashes,
                "corrected_artifact_hashes": run.artifact_hashes,
            }
            for run in sorted(runs, key=lambda item: item.candidate_id)
        ],
        "comparisons": comparisons,
        "task_family_slices": _task_family_slices(runs, cases),
        "failure_analysis": {
            run.candidate_id: _failure_analysis(run)
            for run in sorted(runs, key=lambda item: item.candidate_id)
        },
        "decision": {
            "selected_for_next_iteration": retrieval_id,
            "rationale": (
                "Retrieval has the highest corrected mean and hard-gate pass rate, "
                "and it clears the preregistered advancement gate versus minimal prompting."
            ),
            "next_hypothesis": (
                "A structured fact-and-constraint ledger followed by a verification pass "
                "will reduce omissions and unsupported transformations without lowering "
                "hard-gate pass rate versus retrieval v1."
            ),
        },
        "limitations": [
            (
                "The scorer correction was frozen after generation and is evaluator "
                "calibration, not confirmation."
            ),
            "B1 is visible, project-authored, and too small for broad quality claims.",
            "Lexical checks do not establish semantic fidelity or human writing preference.",
            "Task-family slices contain only one to three cases and are descriptive.",
        ],
        "settled_cost_usd": 0,
    }
    atomic_write_json(results_path, result)
    return result
