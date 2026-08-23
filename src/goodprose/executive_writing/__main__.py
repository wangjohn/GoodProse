"""Command-line entry point for the executive-writing research program."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from goodprose.executive_writing.analysis import analyze_baselines, analyze_iteration
from goodprose.executive_writing.baseline import run_baseline
from goodprose.executive_writing.benchmark import build_benchmark, load_cases
from goodprose.executive_writing.external_evals import (
    YAP_BOOTSTRAP_SEED,
    cli_adapt,
    cli_emit_candidates,
    cli_score_yapbench,
    cli_validate_predictions_file,
    cli_validate_registry,
)
from goodprose.executive_writing.failure_audit import audit_mlx_b1_failures
from goodprose.executive_writing.frontier import validate_architecture_frontier
from goodprose.executive_writing.holdout import (
    PROTOCOL_ID,
    AggregateUsage,
    HiddenCaseScores,
    complete_tier_c,
    load_b2_request,
    load_finalist_freeze,
    load_hidden_scores,
    load_receipt_document,
    load_registration,
    load_signer_key,
    open_tier_c,
    retire,
    submit_b2_query,
    validate_finalist_freeze,
    validate_tier_c_completion_state,
    verify_receipt_chain,
    verify_receipt_document,
)
from goodprose.executive_writing.mlx_evaluation import (
    publish_mlx_b1_results,
    run_mlx_b1_evaluation,
)
from goodprose.executive_writing.ox_ceiling import (
    publish_ox_b1_ceiling_results,
    run_ox_b1_ceiling,
    run_ox_b1_source_reviser,
)
from goodprose.executive_writing.ox_output_audit import audit_ox_b1_outputs
from goodprose.executive_writing.profile_coverage import (
    load_coverage_inputs,
    publish_coverage_results,
    run_coverage,
)
from goodprose.executive_writing.smoke_data import compile_smoke_dataset
from goodprose.executive_writing.training import run_mlx_training, run_smoke_training
from goodprose.executive_writing.unified_data import compile_unified_dataset


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m goodprose.executive_writing")
    commands = parser.add_subparsers(dest="command", required=True)
    benchmark = commands.add_parser("benchmark", help="Build or validate benchmark artifacts")
    benchmark_commands = benchmark.add_subparsers(dest="benchmark_command", required=True)

    build = benchmark_commands.add_parser("build")
    build.add_argument("--source", required=True)
    build.add_argument("--cases", required=True)
    build.add_argument("--manifest", required=True)
    build.add_argument("--schema", required=True)

    validate = benchmark_commands.add_parser("validate")
    validate.add_argument("--cases", required=True)

    baseline = commands.add_parser("baseline", help="Run a local baseline candidate")
    baseline_commands = baseline.add_subparsers(dest="baseline_command", required=True)
    run = baseline_commands.add_parser("run")
    run.add_argument("--config", required=True)
    run.add_argument("--cases", required=True)
    run.add_argument("--benchmark-manifest", required=True)
    run.add_argument("--output-root", required=True)
    run.add_argument("--code-revision", required=True)

    analyze = baseline_commands.add_parser("analyze")
    analyze.add_argument("--source-run", action="append", required=True)
    analyze.add_argument("--cases", required=True)
    analyze.add_argument("--benchmark-manifest", required=True)
    analyze.add_argument("--correction-record", required=True)
    analyze.add_argument("--corrected-output-root", required=True)
    analyze.add_argument("--results", required=True)
    analyze.add_argument("--case-results", required=True)
    analyze.add_argument("--timestamp", required=True)

    iteration = baseline_commands.add_parser("analyze-iteration")
    iteration.add_argument("--source-run", required=True)
    iteration.add_argument("--baseline-corrected", required=True)
    iteration.add_argument("--cases", required=True)
    iteration.add_argument("--benchmark-manifest", required=True)
    iteration.add_argument("--correction-record", required=True)
    iteration.add_argument("--corrected-output-root", required=True)
    iteration.add_argument("--results", required=True)
    iteration.add_argument("--case-results", required=True)
    iteration.add_argument("--timestamp", required=True)
    iteration.add_argument("--analysis-id", default="goodprose-structured-retrieval-v1-analysis")
    iteration.add_argument("--max-omission-cases", type=int, default=13)
    iteration.add_argument("--max-fabrication-cases", type=int, default=1)
    iteration.add_argument("--max-placeholder-loss-cases", type=int, default=1)
    iteration.add_argument("--max-mean-latency-ms", type=float, default=6812.086)
    iteration.add_argument("--max-output-tokens", type=int, default=16800)

    smoke_data = commands.add_parser("smoke-data", help="Build smoke-training data")
    smoke_data_commands = smoke_data.add_subparsers(dest="smoke_data_command", required=True)
    smoke_build = smoke_data_commands.add_parser("build")
    smoke_build.add_argument("--output-dir", required=True)
    smoke_build.add_argument("--manifest", required=True)
    smoke_build.add_argument("--b1-cases", required=True)

    smoke_train = commands.add_parser("smoke-train", help="Run the MLX smoke fine-tune")
    smoke_train_commands = smoke_train.add_subparsers(dest="smoke_train_command", required=True)
    smoke_train_run = smoke_train_commands.add_parser("run")
    smoke_train_run.add_argument("--config", required=True)
    smoke_train_run.add_argument("--data-dir", required=True)
    smoke_train_run.add_argument("--output-root", required=True)
    smoke_train_run.add_argument("--repo-root", required=True)
    smoke_train_run.add_argument("--code-revision", required=True)
    smoke_train_run.add_argument("--started-at", required=True)

    mlx_train = commands.add_parser(
        "mlx-train", help="Run a validated MLX LoRA training config (smoke or unified pilot)"
    )
    mlx_train_commands = mlx_train.add_subparsers(dest="mlx_train_command", required=True)
    mlx_train_run = mlx_train_commands.add_parser("run")
    mlx_train_run.add_argument("--config", required=True)
    mlx_train_run.add_argument("--data-dir", required=True)
    mlx_train_run.add_argument("--output-root", required=True)
    mlx_train_run.add_argument("--repo-root", required=True)
    mlx_train_run.add_argument("--code-revision", required=True)
    mlx_train_run.add_argument("--started-at", required=True)

    unified_data = commands.add_parser(
        "unified-data", help="Build the unified three-corpus pilot dataset"
    )
    unified_data_commands = unified_data.add_subparsers(dest="unified_data_command", required=True)
    unified_build = unified_data_commands.add_parser("build")
    unified_build.add_argument("--source", required=True)
    unified_build.add_argument("--output-dir", required=True)
    unified_build.add_argument("--manifest", required=True)
    unified_build.add_argument("--b1-cases", required=True)

    mlx_eval = commands.add_parser("mlx-eval", help="Run matched MLX B1 evaluation")
    mlx_eval_commands = mlx_eval.add_subparsers(dest="mlx_eval_command", required=True)
    mlx_eval_run = mlx_eval_commands.add_parser("run")
    mlx_eval_run.add_argument("--config", required=True)
    mlx_eval_run.add_argument("--cases", required=True)
    mlx_eval_run.add_argument("--adapter-path", required=True)
    mlx_eval_run.add_argument("--model-path", required=True)
    mlx_eval_run.add_argument("--output-root", required=True)
    mlx_eval_run.add_argument("--repo-root", required=True)
    mlx_eval_run.add_argument("--code-revision", required=True)
    mlx_eval_run.add_argument("--started-at", required=True)
    mlx_eval_publish = mlx_eval_commands.add_parser("publish")
    mlx_eval_publish.add_argument("--run-dir", required=True)
    mlx_eval_publish.add_argument("--cases", required=True)
    mlx_eval_publish.add_argument("--training-record", required=True)
    mlx_eval_publish.add_argument("--results", required=True)
    mlx_eval_publish.add_argument("--case-results", required=True)
    mlx_eval_publish.add_argument("--generated-at", required=True)
    mlx_eval_audit = mlx_eval_commands.add_parser(
        "audit-failures", help="Publish a post-run exact-label and repetition diagnostic"
    )
    mlx_eval_audit.add_argument("--config", required=True)
    mlx_eval_audit.add_argument("--run-dir", required=True)
    mlx_eval_audit.add_argument("--cases", required=True)
    mlx_eval_audit.add_argument("--output", required=True)
    mlx_eval_audit.add_argument("--generated-at", required=True)

    coverage = commands.add_parser(
        "profile-coverage", help="Run or publish descriptive profile-card coverage"
    )
    coverage_commands = coverage.add_subparsers(dest="coverage_command", required=True)
    coverage_run = coverage_commands.add_parser("run")
    coverage_run.add_argument("--config", required=True)
    coverage_run.add_argument("--output-root", required=True)
    coverage_run.add_argument("--code-revision", required=True)
    coverage_publish = coverage_commands.add_parser("publish")
    coverage_publish.add_argument("--config", required=True)
    coverage_publish.add_argument("--run-dir", required=True)
    coverage_publish.add_argument("--results", required=True)
    coverage_publish.add_argument("--case-results", required=True)
    coverage_publish.add_argument("--generated-at", required=True)

    ox_ceiling = commands.add_parser("ox-ceiling", help="Run or publish the Ox B1 ceiling")
    ox_ceiling_commands = ox_ceiling.add_subparsers(dest="ox_ceiling_command", required=True)
    ox_ceiling_run = ox_ceiling_commands.add_parser("run")
    ox_ceiling_run.add_argument("--config", required=True)
    ox_ceiling_run.add_argument("--cases", required=True)
    ox_ceiling_run.add_argument("--output-root", required=True)
    ox_ceiling_run.add_argument("--repo-root", required=True)
    ox_ceiling_run.add_argument("--code-revision", required=True)
    ox_ceiling_run.add_argument("--started-at", required=True)
    ox_source_reviser_run = ox_ceiling_commands.add_parser("run-reviser")
    ox_source_reviser_run.add_argument("--config", required=True)
    ox_source_reviser_run.add_argument("--cases", required=True)
    ox_source_reviser_run.add_argument("--output-root", required=True)
    ox_source_reviser_run.add_argument("--repo-root", required=True)
    ox_source_reviser_run.add_argument("--code-revision", required=True)
    ox_source_reviser_run.add_argument("--started-at", required=True)
    ox_ceiling_publish = ox_ceiling_commands.add_parser("publish")
    ox_ceiling_publish.add_argument("--config", required=True)
    ox_ceiling_publish.add_argument("--run-dir", required=True)
    ox_ceiling_publish.add_argument("--cases", required=True)
    ox_ceiling_publish.add_argument("--repo-root", required=True)
    ox_ceiling_publish.add_argument("--results", required=True)
    ox_ceiling_publish.add_argument("--case-results", required=True)
    ox_ceiling_publish.add_argument("--generated-at", required=True)
    ox_ceiling_publish.add_argument("--baseline-correction")
    ox_ceiling_publish.add_argument("--run-metadata-correction")
    ox_ceiling_audit = ox_ceiling_commands.add_parser("audit")
    ox_ceiling_audit.add_argument("--config", required=True)
    ox_ceiling_audit.add_argument("--run-dir", required=True)
    ox_ceiling_audit.add_argument("--cases", required=True)
    ox_ceiling_audit.add_argument("--source-analysis", required=True)
    ox_ceiling_audit.add_argument("--source-case-results", required=True)
    ox_ceiling_audit.add_argument("--output", required=True)
    ox_ceiling_audit.add_argument("--generated-at", required=True)

    frontier_validate = commands.add_parser(
        "frontier-validate", help="Validate the common architecture frontier"
    )
    frontier_validate.add_argument("--frontier", required=True)
    frontier_validate.add_argument("--hypotheses", required=True)
    frontier_validate.add_argument("--repo-root", required=True)

    external = commands.add_parser(
        "external-evals",
        help="External evaluation adapters (local files only; no downloads or model calls)",
    )
    external_commands = external.add_subparsers(dest="external_command", required=True)
    external_commands.add_parser(
        "validate-registry", help="Validate the frozen public source registry"
    )
    adapt = external_commands.add_parser(
        "adapt", help="Adapt a locally acquired source into an ignored output directory"
    )
    adapt.add_argument("--benchmark-id", required=True)
    adapt.add_argument("--source", required=True)
    adapt.add_argument("--output-dir", required=True)
    adapt.add_argument(
        "--upstream-source",
        help="Pinned upstream artifact required when --source is a normalized derivative",
    )
    candidates = external_commands.add_parser(
        "emit-candidates", help="Emit a candidate-only payload from adapted cases"
    )
    candidates.add_argument("--cases", required=True)
    candidates.add_argument("--output", required=True)
    candidates.add_argument("--suite", choices=("development", "full"), required=True)
    predictions_validate = external_commands.add_parser(
        "validate-predictions", help="Validate one nonempty prediction per adapted case"
    )
    predictions_validate.add_argument("--cases", required=True)
    predictions_validate.add_argument("--predictions", required=True)
    predictions_validate.add_argument("--suite", choices=("development", "full"), required=True)
    yap_score = external_commands.add_parser("score-yapbench", help="Score YapBench predictions")
    yap_score.add_argument("--cases", required=True)
    yap_score.add_argument("--predictions", required=True)
    yap_score.add_argument("--result", required=True)
    yap_score.add_argument("--seed", type=int, default=None)

    holdout = commands.add_parser(
        "holdout",
        help=f"Aggregate-only holdout lifecycle protocol {PROTOCOL_ID}",
    )
    holdout_commands = holdout.add_subparsers(dest="holdout_command", required=True)
    registration_validate = holdout_commands.add_parser(
        "validate-registration",
        help="Validate a public holdout registration document",
    )
    registration_validate.add_argument("--registration", required=True)
    registration_validate.add_argument(
        "--expect-sha256",
        help="Expected canonical document hash of the registration",
    )

    freeze_validate = holdout_commands.add_parser(
        "validate-freeze",
        help="Validate a finalist freeze against its registration",
    )
    freeze_validate.add_argument("--freeze", required=True)
    freeze_validate.add_argument("--registration", required=True)
    freeze_validate.add_argument("--expect-registration-sha256")
    freeze_validate.add_argument("--expect-freeze-sha256")

    receipt_verify = holdout_commands.add_parser(
        "verify-receipt",
        help="Repository-side verification of an aggregate-only receipt",
    )
    receipt_verify.add_argument("--receipt", required=True)
    receipt_verify.add_argument("--registration", required=True)
    receipt_verify.add_argument("--expect-registration-sha256")
    receipt_verify.add_argument("--freeze")
    receipt_verify.add_argument("--expect-freeze-sha256")
    receipt_verify.add_argument(
        "--key-file",
        help="HMAC key held by the external evaluator; omit to skip authentication",
    )

    chain_verify = holdout_commands.add_parser(
        "verify-chain",
        help="Verify the append-only Tier B2 receipt chain",
    )
    chain_verify.add_argument("--state-dir", required=True)
    chain_verify.add_argument("--registration", required=True)
    chain_verify.add_argument("--expect-registration-sha256")
    chain_verify.add_argument("--key-file")

    b2_query = holdout_commands.add_parser(
        "b2-query",
        help="External Tier B2 broker path (evaluator-controlled environment only)",
    )
    b2_query.add_argument("--registration", required=True)
    b2_query.add_argument("--expect-registration-sha256")
    b2_query.add_argument("--request", required=True)
    b2_query.add_argument("--expect-request-sha256", required=True)
    b2_query.add_argument("--state-dir", required=True)
    b2_query.add_argument("--requests", type=int, default=0)
    b2_query.add_argument("--input-tokens", type=int, default=0)
    b2_query.add_argument("--output-tokens", type=int, default=0)
    b2_query.add_argument("--usd-cost", type=float, default=0.0)
    b2_query.add_argument("--executed-at", required=True)
    b2_query.add_argument("--code-revision", required=True)
    b2_query.add_argument("--signing-key-file")

    tier_c_open_cmd = holdout_commands.add_parser(
        "tier-c-open",
        help="Exclusive burn-before-read open of the Tier C one-shot benchmark",
    )
    tier_c_open_cmd.add_argument("--registration", required=True)
    tier_c_open_cmd.add_argument("--expect-registration-sha256")
    tier_c_open_cmd.add_argument("--freeze", required=True)
    tier_c_open_cmd.add_argument("--expect-freeze-sha256")
    tier_c_open_cmd.add_argument("--state-dir", required=True)
    tier_c_open_cmd.add_argument("--opened-at", required=True)

    tier_c_complete_cmd = holdout_commands.add_parser(
        "tier-c-complete",
        help="Complete the Tier C one-shot run and emit the single receipt",
    )
    tier_c_complete_cmd.add_argument("--registration", required=True)
    tier_c_complete_cmd.add_argument("--expect-registration-sha256")
    tier_c_complete_cmd.add_argument("--freeze", required=True)
    tier_c_complete_cmd.add_argument("--expect-freeze-sha256")
    tier_c_complete_cmd.add_argument("--state-dir", required=True)
    tier_c_complete_cmd.add_argument(
        "--scores",
        action="append",
        required=True,
        metavar="CANDIDATE_ID=SHA256=PATH",
        help="Hash-pinned hidden score JSON list per finalist candidate",
    )
    tier_c_complete_cmd.add_argument("--requests", type=int, default=0)
    tier_c_complete_cmd.add_argument("--input-tokens", type=int, default=0)
    tier_c_complete_cmd.add_argument("--output-tokens", type=int, default=0)
    tier_c_complete_cmd.add_argument("--usd-cost", type=float, default=0.0)
    tier_c_complete_cmd.add_argument("--completed-at", required=True)
    tier_c_complete_cmd.add_argument("--code-revision", required=True)
    tier_c_complete_cmd.add_argument("--signing-key-file")

    retire_cmd = holdout_commands.add_parser(
        "retire",
        help="Retire the benchmark for authorized item-level inspection",
    )
    retire_cmd.add_argument("--registration", required=True)
    retire_cmd.add_argument("--expect-registration-sha256")
    retire_cmd.add_argument("--state-dir", required=True)
    retire_cmd.add_argument("--authorized-by", required=True)
    retire_cmd.add_argument(
        "--reason",
        required=True,
        choices=["authorized_item_inspection", "superseded_by_new_version", "integrity_incident"],
    )
    retire_cmd.add_argument("--retired-at", required=True)
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "benchmark" and args.benchmark_command == "build":
        manifest = build_benchmark(
            _path(args.source),
            _path(args.cases),
            _path(args.manifest),
            _path(args.schema),
        )
        print(f"built {manifest.benchmark_id}: {manifest.case_count} cases")
        return 0
    if args.command == "benchmark" and args.benchmark_command == "validate":
        cases = load_cases(_path(args.cases))
        print(f"valid benchmark cases: {len(cases)}")
        return 0
    if args.command == "baseline" and args.baseline_command == "run":
        run_dir = run_baseline(
            config_path=_path(args.config),
            cases_path=_path(args.cases),
            benchmark_manifest_path=_path(args.benchmark_manifest),
            output_root=_path(args.output_root),
            code_revision=args.code_revision,
        )
        print(f"baseline run complete: {run_dir}")
        return 0
    if args.command == "baseline" and args.baseline_command == "analyze":
        result = analyze_baselines(
            source_run_dirs=[_path(value) for value in args.source_run],
            cases_path=_path(args.cases),
            benchmark_manifest_path=_path(args.benchmark_manifest),
            correction_record_path=_path(args.correction_record),
            corrected_output_root=_path(args.corrected_output_root),
            results_path=_path(args.results),
            case_results_path=_path(args.case_results),
            timestamp=args.timestamp,
        )
        print(
            f"baseline analysis complete: {result['analysis_id']} "
            f"({len(result['candidates'])} candidates)"
        )
        return 0
    if args.command == "baseline" and args.baseline_command == "analyze-iteration":
        result = analyze_iteration(
            source_run_dir=_path(args.source_run),
            baseline_corrected_dir=_path(args.baseline_corrected),
            cases_path=_path(args.cases),
            benchmark_manifest_path=_path(args.benchmark_manifest),
            correction_record_path=_path(args.correction_record),
            corrected_output_root=_path(args.corrected_output_root),
            results_path=_path(args.results),
            case_results_path=_path(args.case_results),
            timestamp=args.timestamp,
            analysis_id=args.analysis_id,
            max_omission_cases=args.max_omission_cases,
            max_fabrication_cases=args.max_fabrication_cases,
            max_placeholder_loss_cases=args.max_placeholder_loss_cases,
            max_mean_latency_ms=args.max_mean_latency_ms,
            max_output_tokens=args.max_output_tokens,
        )
        print(f"iteration analysis complete: {result['analysis_id']} ({result['status']})")
        return 0
    if args.command == "smoke-data" and args.smoke_data_command == "build":
        manifest = compile_smoke_dataset(
            output_dir=_path(args.output_dir),
            manifest_path=_path(args.manifest),
            b1_cases_path=_path(args.b1_cases),
        )
        print(f"built {manifest['dataset_id']}: {manifest['record_count']} records")
        return 0
    if args.command == "smoke-train" and args.smoke_train_command == "run":
        run_dir = run_smoke_training(
            config_path=_path(args.config),
            data_dir=_path(args.data_dir),
            output_root=_path(args.output_root),
            repo_root=_path(args.repo_root),
            code_revision=args.code_revision,
            started_at=args.started_at,
        )
        print(f"smoke training complete: {run_dir}")
        return 0
    if args.command == "mlx-train" and args.mlx_train_command == "run":
        run_dir = run_mlx_training(
            config_path=_path(args.config),
            data_dir=_path(args.data_dir),
            output_root=_path(args.output_root),
            repo_root=_path(args.repo_root),
            code_revision=args.code_revision,
            started_at=args.started_at,
        )
        print(f"MLX training complete: {run_dir}")
        return 0
    if args.command == "unified-data" and args.unified_data_command == "build":
        manifest = compile_unified_dataset(
            source_path=_path(args.source),
            output_dir=_path(args.output_dir),
            manifest_path=_path(args.manifest),
            b1_cases_path=_path(args.b1_cases),
        )
        print(f"built {manifest['dataset_id']}: {manifest['record_count']} records")
        return 0
    if args.command == "mlx-eval" and args.mlx_eval_command == "run":
        run_dir = run_mlx_b1_evaluation(
            config_path=_path(args.config),
            cases_path=_path(args.cases),
            adapter_path=_path(args.adapter_path),
            model_path=_path(args.model_path),
            output_root=_path(args.output_root),
            repo_root=_path(args.repo_root),
            code_revision=args.code_revision,
            started_at=args.started_at,
        )
        print(f"MLX B1 evaluation complete: {run_dir}")
        return 0
    if args.command == "mlx-eval" and args.mlx_eval_command == "publish":
        analysis = publish_mlx_b1_results(
            run_dir=_path(args.run_dir),
            cases_path=_path(args.cases),
            training_record_path=_path(args.training_record),
            results_path=_path(args.results),
            case_results_path=_path(args.case_results),
            generated_at=args.generated_at,
        )
        print(f"MLX B1 analysis complete: {analysis['status']}")
        return 0
    if args.command == "mlx-eval" and args.mlx_eval_command == "audit-failures":
        audit = audit_mlx_b1_failures(
            config_path=_path(args.config),
            run_dir=_path(args.run_dir),
            cases_path=_path(args.cases),
            output_path=_path(args.output),
            generated_at=args.generated_at,
        )
        print(f"MLX B1 failure audit complete: {audit['decision']['adapter_disposition']}")
        return 0
    if args.command == "profile-coverage" and args.coverage_command == "run":
        inputs = load_coverage_inputs(_path(args.config))
        run_dir = run_coverage(
            inputs=inputs,
            output_root=_path(args.output_root),
            code_revision=args.code_revision,
        )
        print(f"profile-coverage run complete: {run_dir}")
        return 0
    if args.command == "profile-coverage" and args.coverage_command == "publish":
        results = publish_coverage_results(
            config_path=_path(args.config),
            run_dir=_path(args.run_dir),
            results_path=_path(args.results),
            case_results_path=_path(args.case_results),
            generated_at=args.generated_at,
        )
        print(f"profile-coverage published: {results['status']}")
        return 0
    if args.command == "ox-ceiling" and args.ox_ceiling_command == "run":
        run_dir = run_ox_b1_ceiling(
            config_path=_path(args.config),
            cases_path=_path(args.cases),
            output_root=_path(args.output_root),
            repo_root=_path(args.repo_root),
            code_revision=args.code_revision,
            started_at=args.started_at,
        )
        print(f"Ox B1 ceiling run complete: {run_dir}")
        return 0
    if args.command == "ox-ceiling" and args.ox_ceiling_command == "run-reviser":
        run_dir = run_ox_b1_source_reviser(
            config_path=_path(args.config),
            cases_path=_path(args.cases),
            output_root=_path(args.output_root),
            repo_root=_path(args.repo_root),
            code_revision=args.code_revision,
            started_at=args.started_at,
        )
        print(f"Ox B1 source-reviser run complete: {run_dir}")
        return 0
    if args.command == "ox-ceiling" and args.ox_ceiling_command == "publish":
        analysis = publish_ox_b1_ceiling_results(
            config_path=_path(args.config),
            run_dir=_path(args.run_dir),
            cases_path=_path(args.cases),
            repo_root=_path(args.repo_root),
            results_path=_path(args.results),
            case_results_path=_path(args.case_results),
            generated_at=args.generated_at,
            baseline_correction_path=(
                _path(args.baseline_correction) if args.baseline_correction else None
            ),
            run_metadata_correction_path=(
                _path(args.run_metadata_correction) if args.run_metadata_correction else None
            ),
        )
        print(f"Ox B1 ceiling analysis complete: {analysis['status']}")
        return 0
    if args.command == "ox-ceiling" and args.ox_ceiling_command == "audit":
        audit = audit_ox_b1_outputs(
            config_path=_path(args.config),
            run_dir=_path(args.run_dir),
            cases_path=_path(args.cases),
            source_analysis_path=_path(args.source_analysis),
            source_case_results_path=_path(args.source_case_results),
            output_path=_path(args.output),
            generated_at=args.generated_at,
        )
        print(f"Ox B1 output audit complete: {audit['decision']['raw_candidate_disposition']}")
        return 0
    if args.command == "frontier-validate":
        summary = validate_architecture_frontier(
            frontier_path=_path(args.frontier),
            hypotheses_path=_path(args.hypotheses),
            repo_root=_path(args.repo_root),
        )
        print(
            "Architecture frontier valid: "
            f"{summary['candidate_count']} candidates, "
            f"{summary['finalist_ready_count']} finalist-ready"
        )
        return 0
    if args.command == "external-evals":
        return _run_external(args)
    if args.command == "holdout":
        return _run_holdout(args)
    raise AssertionError("unhandled command")


def _run_external(args: argparse.Namespace) -> int:
    if args.external_command == "validate-registry":
        registry = cli_validate_registry()
        for entry in registry.entries:
            print(
                f"{entry.benchmark_id.value}: {entry.execution_status.value} "
                f"(rights={entry.rights_status.value})"
            )
        print(f"registry valid: {len(registry.entries)} benchmarks")
        return 0
    if args.external_command == "adapt":
        manifest = cli_adapt(
            args.benchmark_id,
            _path(args.source),
            _path(args.output_dir),
            upstream_source=_path(args.upstream_source) if args.upstream_source else None,
        )
        print(
            f"adapted {manifest.benchmark_id.value}: {manifest.case_count} cases "
            f"({manifest.execution_status.value}; not a benchmark result)"
        )
        return 0
    if args.external_command == "emit-candidates":
        count = cli_emit_candidates(_path(args.cases), _path(args.output), suite=args.suite)
        print(f"candidate payload written: {count} cases (references and criteria excluded)")
        return 0
    if args.external_command == "validate-predictions":
        validated = cli_validate_predictions_file(
            _path(args.cases), _path(args.predictions), suite=args.suite
        )
        print(f"valid predictions: {validated.prediction_count}/{validated.case_count} cases")
        return 0
    if args.external_command == "score-yapbench":
        result = cli_score_yapbench(
            _path(args.cases),
            _path(args.predictions),
            _path(args.result),
            seed=args.seed if args.seed is not None else YAP_BOOTSTRAP_SEED,
        )
        print(
            f"yapbench scored: index={result.yap_index} "
            f"interval=[{result.yap_index_interval_low}, {result.yap_index_interval_high}] "
            f"({result.metric_version}; compatibility metric, not a quality score)"
        )
        return 0
    raise AssertionError("unhandled external-evals command")


def _optional_key(args: argparse.Namespace) -> bytes | None:
    key_file = getattr(args, "key_file", None) or getattr(args, "signing_key_file", None)
    return load_signer_key(_path(key_file)) if key_file else None


def _run_holdout(args: argparse.Namespace) -> int:
    if args.holdout_command == "validate-registration":
        registration = load_registration(
            _path(args.registration), expected_sha256=args.expect_sha256
        )
        print(
            f"valid {registration.tier} registration {registration.holdout_id} "
            f"({registration.access_posture}, case_count={registration.case_count})"
        )
        return 0
    if args.holdout_command == "validate-freeze":
        registration = load_registration(
            _path(args.registration), expected_sha256=args.expect_registration_sha256
        )
        freeze = load_finalist_freeze(_path(args.freeze), expected_sha256=args.expect_freeze_sha256)
        validate_finalist_freeze(freeze, registration)
        print(f"valid finalist freeze: {len(freeze.finalists)} finalists")
        return 0
    if args.holdout_command == "verify-receipt":
        key = _optional_key(args)
        registration = load_registration(
            _path(args.registration), expected_sha256=args.expect_registration_sha256
        )
        freeze = (
            load_finalist_freeze(_path(args.freeze), expected_sha256=args.expect_freeze_sha256)
            if args.freeze
            else None
        )
        verification = verify_receipt_document(
            load_receipt_document(_path(args.receipt)),
            key=key,
            registration=registration,
            freeze=freeze,
        )
        print(verification.model_dump_json(indent=2, exclude_none=True))
        if not verification.valid:
            print("receipt verification failed", file=sys.stderr)
            return 1
        if verification.authenticator_status == "unverified_no_key":
            print(
                "note: schema and hash-chain integrity verified; "
                "authentication unverified (no key supplied)"
            )
        return 0
    if args.holdout_command == "verify-chain":
        key = _optional_key(args)
        registration = load_registration(
            _path(args.registration), expected_sha256=args.expect_registration_sha256
        )
        chain = verify_receipt_chain(
            _path(args.state_dir) / "receipts",
            key=key,
            registration=registration,
        )
        print(
            f"chain receipts={chain.receipt_count} intact={chain.chain_intact} "
            f"authenticator={'checked' if key else 'unverified_no_key'}"
        )
        for verification in chain.verifications:
            for problem in verification.errors:
                print(f"error: {problem}", file=sys.stderr)
        return 0 if chain.chain_intact else 1
    if args.holdout_command == "b2-query":
        registration = load_registration(
            _path(args.registration), expected_sha256=args.expect_registration_sha256
        )
        request = load_b2_request(_path(args.request), expected_sha256=args.expect_request_sha256)
        receipt = submit_b2_query(
            registration,
            request,
            state_dir=_path(args.state_dir),
            usage=AggregateUsage(
                requests=args.requests,
                input_tokens=args.input_tokens,
                output_tokens=args.output_tokens,
                usd_cost=args.usd_cost,
            ),
            executed_at=args.executed_at,
            code_revision=args.code_revision,
            signer_key=_optional_key(args),
        )
        print(
            f"b2 query {receipt.query_index} recorded for {receipt.candidate_id}: {receipt.outcome}"
        )
        return 0
    if args.holdout_command == "tier-c-open":
        registration = load_registration(
            _path(args.registration), expected_sha256=args.expect_registration_sha256
        )
        freeze = load_finalist_freeze(_path(args.freeze), expected_sha256=args.expect_freeze_sha256)
        state = open_tier_c(
            registration,
            freeze,
            state_dir=_path(args.state_dir),
            opened_at=args.opened_at,
        )
        print(f"tier C benchmark opened at {state.opened_at.isoformat()}; it is now consumed")
        return 0
    if args.holdout_command == "tier-c-complete":
        registration = load_registration(
            _path(args.registration), expected_sha256=args.expect_registration_sha256
        )
        freeze = load_finalist_freeze(_path(args.freeze), expected_sha256=args.expect_freeze_sha256)
        state_dir = _path(args.state_dir)
        key = _optional_key(args)
        if registration.access_posture == "sealed" and key is None:
            raise ValueError("sealed Tier C execution requires an external signing key")
        validate_tier_c_completion_state(registration, freeze, state_dir=state_dir)
        scores_by_candidate: dict[str, list[HiddenCaseScores]] = {}
        for binding in args.scores:
            parts = binding.split("=", 2)
            if len(parts) != 3:
                raise ValueError("--scores expects CANDIDATE_ID=SHA256=PATH")
            candidate_id, score_sha256, score_path = parts
            if candidate_id in scores_by_candidate:
                raise ValueError("duplicate --scores candidate binding")
            scores_by_candidate[candidate_id] = load_hidden_scores(
                _path(score_path), expected_sha256=score_sha256
            )
        receipt = complete_tier_c(
            registration,
            freeze,
            scores_by_candidate,
            state_dir=state_dir,
            usage=AggregateUsage(
                requests=args.requests,
                input_tokens=args.input_tokens,
                output_tokens=args.output_tokens,
                usd_cost=args.usd_cost,
            ),
            completed_at=args.completed_at,
            code_revision=args.code_revision,
            signer_key=key,
        )
        posture_note = (
            "procedural evidence only; this is NOT sealed evidence"
            if receipt.envelope.access_posture == "procedurally_held_out"
            else "sealed per external access-separation attestation"
        )
        selection = receipt.selected_candidate_id or "none (no finalist passed hard gates)"
        print(f"tier C run completed: selected {selection} ({posture_note})")
        return 0
    if args.holdout_command == "retire":
        registration = load_registration(
            _path(args.registration), expected_sha256=args.expect_registration_sha256
        )
        record = retire(
            state_dir=_path(args.state_dir),
            registration=registration,
            authorized_by=args.authorized_by,
            reason=args.reason,
            retired_at=args.retired_at,
        )
        print(f"benchmark retired ({record.reason}); aggregate receipts remain verifiable")
        return 0
    raise AssertionError("unhandled holdout command")


def main(argv: list[str] | None = None) -> int:
    try:
        return _run(build_parser().parse_args(argv))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
