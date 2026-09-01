"""Command-line entry point for the small GoodProse workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from goodprose.evaluation import EvaluationError, prepare_review, summarize_review
from goodprose.jsonl import JsonlError
from goodprose.pairs import PairBuildError, build_pairs
from goodprose.posts import PostImportError, import_posts
from goodprose.sft import build_sft


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="goodprose")
    commands = parser.add_subparsers(dest="command", required=True)

    import_command = commands.add_parser("import-posts", help="Import Markdown blog posts")
    import_command.add_argument("directory")
    import_command.add_argument("--output", required=True)
    import_command.add_argument("--url-base")

    pairs_command = commands.add_parser("build-pairs", help="Join reviewed briefs to posts")
    pairs_command.add_argument("--posts", required=True)
    pairs_command.add_argument("--briefs", required=True)
    pairs_command.add_argument("--output", required=True)

    sft_command = commands.add_parser("build-sft", help="Build chat SFT files and test cases")
    sft_command.add_argument("--pairs", required=True)
    sft_command.add_argument("--output-dir", required=True)
    sft_command.add_argument("--eval-output", required=True)

    eval_command = commands.add_parser("eval", help="Prepare or summarize blind comparisons")
    eval_commands = eval_command.add_subparsers(dest="eval_command", required=True)

    prepare = eval_commands.add_parser("prepare", help="Randomize base and candidate outputs")
    prepare.add_argument("--cases", required=True)
    prepare.add_argument("--baseline", required=True)
    prepare.add_argument("--candidate", required=True)
    prepare.add_argument("--packet", required=True)
    prepare.add_argument("--key", required=True)
    prepare.add_argument("--seed", type=int, default=20260831)

    summarize = eval_commands.add_parser("summarize", help="Unblind completed reviews")
    summarize.add_argument("--packet", required=True)
    summarize.add_argument("--key", required=True)
    summarize.add_argument("--output", required=True)
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "import-posts":
        count = import_posts(_path(args.directory), _path(args.output), url_base=args.url_base)
        print(f"imported {count} blog post(s) to {_path(args.output)}")
        return 0
    if args.command == "build-pairs":
        count = build_pairs(_path(args.posts), _path(args.briefs), _path(args.output))
        print(f"built {count} canonical pair(s) at {_path(args.output)}")
        return 0
    if args.command == "build-sft":
        counts = build_sft(_path(args.pairs), _path(args.output_dir), _path(args.eval_output))
        print("built SFT data: " + ", ".join(f"{split}={count}" for split, count in counts.items()))
        return 0
    if args.command == "eval" and args.eval_command == "prepare":
        count = prepare_review(
            _path(args.cases),
            _path(args.baseline),
            _path(args.candidate),
            _path(args.packet),
            _path(args.key),
            seed=args.seed,
        )
        print(f"prepared {count} blind review case(s) at {_path(args.packet)}")
        return 0
    if args.command == "eval" and args.eval_command == "summarize":
        summary = summarize_review(_path(args.packet), _path(args.key), _path(args.output))
        print(
            f"summarized {summary['case_count']} case(s); "
            f"candidate factuality gate={summary['candidate_passes_factuality_gate']}"
        )
        return 0
    raise AssertionError("unhandled command")


def main() -> int:
    try:
        return _run(build_parser().parse_args())
    except (EvaluationError, JsonlError, PairBuildError, PostImportError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
