"""Command-line entry point for the executive-writing research program."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
    raise AssertionError("unhandled command")


def main() -> int:
    try:
        return _run(build_parser().parse_args())
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
