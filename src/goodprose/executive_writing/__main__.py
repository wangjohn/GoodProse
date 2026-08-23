"""Command-line entry point for the executive-writing research program."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from goodprose.executive_writing.analysis import analyze_baselines
from goodprose.executive_writing.baseline import run_baseline
from goodprose.executive_writing.benchmark import build_benchmark, load_cases


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
    raise AssertionError("unhandled command")


def main() -> int:
    try:
        return _run(build_parser().parse_args())
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
