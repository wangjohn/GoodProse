"""Command-line entry point for the executive-writing research program."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from goodprose.executive_writing.analysis import analyze_baselines, analyze_iteration
from goodprose.executive_writing.baseline import run_baseline
from goodprose.executive_writing.benchmark import build_benchmark, load_cases
from goodprose.executive_writing.mlx_evaluation import run_mlx_b1_evaluation
from goodprose.executive_writing.smoke_data import compile_smoke_dataset
from goodprose.executive_writing.training import run_smoke_training


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
    raise AssertionError("unhandled command")


def main() -> int:
    try:
        return _run(build_parser().parse_args())
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
