"""Command-line entry point for the small GoodProse workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from goodprose.chunks import ChunkBuildError, build_chunks
from goodprose.evaluation import EvaluationError, prepare_review, summarize_review
from goodprose.external import (
    ExternalSourceError,
    build_authentic_eval_briefs,
    build_external_posts,
    build_external_samples,
)
from goodprose.generation import GenerationError, generate_eval_outputs
from goodprose.jsonl import JsonlError
from goodprose.models import SystemLabel
from goodprose.pairs import PairBuildError, build_pairs
from goodprose.posts import PostImportError, import_posts
from goodprose.prompts import (
    PromptReviewError,
    approve_prompt_candidates,
    build_prompt_candidates,
    build_prompt_pairs,
    build_prompt_review,
)
from goodprose.sft import build_sft
from goodprose.training import TrainingError, run_lora_plus


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="goodprose")
    commands = parser.add_subparsers(dest="command", required=True)

    import_command = commands.add_parser("import-posts", help="Import Markdown blog posts")
    import_command.add_argument("directory")
    import_command.add_argument("--output", required=True)
    import_urls = import_command.add_mutually_exclusive_group()
    import_urls.add_argument("--url-base")
    import_urls.add_argument(
        "--url-template",
        help="URL template using {id}, {slug}, {year}, {month}, and {day}",
    )

    pairs_command = commands.add_parser("build-pairs", help="Join reviewed briefs to posts")
    pairs_command.add_argument("--posts", required=True)
    pairs_command.add_argument("--briefs", required=True)
    pairs_command.add_argument("--output", required=True)

    chunks_command = commands.add_parser(
        "build-chunks", help="Build verbatim semantic chunk candidates"
    )
    chunks_command.add_argument("--posts", required=True)
    chunks_command.add_argument("--splits", required=True)
    chunks_command.add_argument("--output", required=True)
    chunks_command.add_argument("--review-output", required=True)
    chunks_command.add_argument("--supplemental-targets")
    chunks_command.add_argument("--exclusions")
    chunks_command.add_argument("--min-tokens", type=int, default=250)
    chunks_command.add_argument("--max-tokens", type=int, default=700)

    prompts_command = commands.add_parser(
        "review-prompts", help="Validate and render synthetic prompt candidates"
    )
    prompts_command.add_argument("--prompts", required=True)
    prompts_command.add_argument("--chunks", required=True)
    prompts_command.add_argument("--output", required=True)

    approve_prompts_command = commands.add_parser(
        "approve-prompts",
        help="Approve reviewed training prompts and their exact completion chunks",
    )
    approve_prompts_command.add_argument("--prompts", required=True)
    approve_prompts_command.add_argument("--chunks", required=True)
    approve_prompts_command.add_argument("--reviewer-note", required=True)

    prompt_candidates_command = commands.add_parser(
        "build-prompt-candidates", help="Attach frozen chunk metadata to compact prompt drafts"
    )
    prompt_candidates_command.add_argument("--drafts", required=True)
    prompt_candidates_command.add_argument("--chunks", required=True)
    prompt_candidates_command.add_argument("--base-prompts")
    prompt_candidates_command.add_argument(
        "--replace-lineage",
        action="append",
        default=[],
        help="Drop base prompts from this lineage before merging; repeat as needed",
    )
    prompt_candidates_command.add_argument("--output", required=True)

    prompt_pairs_command = commands.add_parser(
        "build-prompt-pairs",
        help="Promote approved prompts and exact chunks into canonical pairs",
    )
    prompt_pairs_command.add_argument("--prompts", required=True)
    prompt_pairs_command.add_argument("--chunks", required=True)
    prompt_pairs_command.add_argument("--posts", required=True)
    prompt_pairs_command.add_argument(
        "--heldout-pairs",
        action="append",
        default=[],
        help="Held-out canonical pair file; repeat for multiple files",
    )
    prompt_pairs_command.add_argument("--output", required=True)

    external_command = commands.add_parser(
        "build-external-samples", help="Build private candidates from external source Markdown"
    )
    external_command.add_argument("--catalog", required=True)
    external_command.add_argument("--source-map", required=True)
    external_command.add_argument("--source-root", required=True)
    external_command.add_argument("--output", required=True)

    external_posts_command = commands.add_parser(
        "build-external-posts", help="Normalize approved public snapshots into canonical posts"
    )
    external_posts_command.add_argument("--catalog", required=True)
    external_posts_command.add_argument("--snapshot-root", required=True)
    external_posts_command.add_argument("--base-posts")
    external_posts_command.add_argument("--output", required=True)

    authentic_briefs_command = commands.add_parser(
        "build-authentic-eval-briefs",
        help="Extract private draft/outline inputs for held-out posts",
    )
    authentic_briefs_command.add_argument("--source-map", required=True)
    authentic_briefs_command.add_argument("--source-root", required=True)
    authentic_briefs_command.add_argument("--splits", required=True)
    authentic_briefs_command.add_argument("--output", required=True)

    sft_command = commands.add_parser("build-sft", help="Build chat SFT files and test cases")
    sft_command.add_argument("--pairs", required=True)
    sft_command.add_argument("--output-dir", required=True)
    sft_command.add_argument("--eval-output", required=True)

    train_command = commands.add_parser(
        "train-lora-plus",
        help="Validate or run a PEFT/TRL LoRA+ supervised fine-tune",
    )
    train_command.add_argument("--config", required=True)
    train_command.add_argument("--validate-only", action="store_true")
    train_command.add_argument("--resume-from-checkpoint")

    eval_command = commands.add_parser("eval", help="Prepare or summarize blind comparisons")
    eval_commands = eval_command.add_subparsers(dest="eval_command", required=True)

    generate = eval_commands.add_parser(
        "generate",
        help="Generate deterministic base-model or LoRA-checkpoint outputs",
    )
    generate.add_argument("--config", required=True)
    generate.add_argument("--cases", required=True)
    generate.add_argument("--role", type=SystemLabel, choices=tuple(SystemLabel), required=True)
    generate.add_argument("--adapter")
    generate.add_argument("--run-id", required=True)
    generate.add_argument("--output", required=True)
    generate.add_argument("--manifest", required=True)
    generate.add_argument("--max-new-tokens", type=int, default=8192)
    generate.add_argument("--seed", type=int, default=20260901)

    prepare = eval_commands.add_parser("prepare", help="Randomize base and candidate outputs")
    prepare.add_argument("--cases", required=True)
    prepare.add_argument("--baseline", required=True)
    prepare.add_argument("--candidate", required=True)
    prepare.add_argument("--packet", required=True)
    prepare.add_argument("--key", required=True)
    prepare.add_argument("--guide")
    prepare.add_argument("--baseline-manifest")
    prepare.add_argument("--candidate-manifest")
    prepare.add_argument("--seed", type=int, default=20260831)

    summarize = eval_commands.add_parser("summarize", help="Unblind completed reviews")
    summarize.add_argument("--packet", required=True)
    summarize.add_argument("--key", required=True)
    summarize.add_argument("--output", required=True)
    summarize.add_argument("--decision-rules")
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "import-posts":
        count = import_posts(
            _path(args.directory),
            _path(args.output),
            url_base=args.url_base,
            url_template=args.url_template,
        )
        print(f"imported {count} blog post(s) to {_path(args.output)}")
        return 0
    if args.command == "build-pairs":
        count = build_pairs(_path(args.posts), _path(args.briefs), _path(args.output))
        print(f"built {count} canonical pair(s) at {_path(args.output)}")
        return 0
    if args.command == "build-chunks":
        counts = build_chunks(
            _path(args.posts),
            _path(args.splits),
            _path(args.output),
            _path(args.review_output),
            min_tokens=args.min_tokens,
            max_tokens=args.max_tokens,
            supplemental_targets_path=(
                _path(args.supplemental_targets) if args.supplemental_targets else None
            ),
            exclusions_path=_path(args.exclusions) if args.exclusions else None,
        )
        print(
            "built semantic chunks: "
            + ", ".join(f"{split}={count}" for split, count in counts.items())
        )
        return 0
    if args.command == "review-prompts":
        count = build_prompt_review(
            _path(args.prompts),
            _path(args.chunks),
            _path(args.output),
        )
        print(f"rendered {count} synthetic prompt candidate(s) at {_path(args.output)}")
        return 0
    if args.command == "approve-prompts":
        counts = approve_prompt_candidates(
            _path(args.prompts),
            _path(args.chunks),
            reviewer_note=args.reviewer_note,
        )
        print(
            "approved training data: "
            + ", ".join(f"{kind}={count}" for kind, count in counts.items())
        )
        return 0
    if args.command == "build-prompt-candidates":
        count = build_prompt_candidates(
            _path(args.drafts),
            _path(args.chunks),
            _path(args.output),
            base_prompts_path=_path(args.base_prompts) if args.base_prompts else None,
            replace_lineages=args.replace_lineage,
        )
        print(f"built {count} synthetic prompt candidate(s) at {_path(args.output)}")
        return 0
    if args.command == "build-prompt-pairs":
        counts = build_prompt_pairs(
            _path(args.prompts),
            _path(args.chunks),
            _path(args.posts),
            _path(args.output),
            heldout_pairs_paths=[_path(path) for path in args.heldout_pairs],
        )
        print(
            "built canonical prompt pairs: "
            + ", ".join(f"{split}={count}" for split, count in counts.items())
        )
        return 0
    if args.command == "build-external-samples":
        counts = build_external_samples(
            _path(args.catalog),
            _path(args.source_map),
            _path(args.source_root),
            _path(args.output),
        )
        print(
            "built external source samples: "
            + ", ".join(f"{platform}={count}" for platform, count in counts.items())
        )
        return 0
    if args.command == "build-external-posts":
        counts = build_external_posts(
            _path(args.catalog),
            _path(args.snapshot_root),
            _path(args.output),
            base_posts_path=_path(args.base_posts) if args.base_posts else None,
        )
        print(
            "built canonical post file: "
            + ", ".join(f"{kind}={count}" for kind, count in counts.items())
        )
        return 0
    if args.command == "build-authentic-eval-briefs":
        counts = build_authentic_eval_briefs(
            _path(args.source_map),
            _path(args.source_root),
            _path(args.splits),
            _path(args.output),
        )
        print(
            "built authentic eval briefs: "
            + ", ".join(f"{split}={count}" for split, count in counts.items())
        )
        return 0
    if args.command == "build-sft":
        counts = build_sft(_path(args.pairs), _path(args.output_dir), _path(args.eval_output))
        print("built SFT data: " + ", ".join(f"{split}={count}" for split, count in counts.items()))
        return 0
    if args.command == "train-lora-plus":
        result = run_lora_plus(
            _path(args.config),
            validate_only=args.validate_only,
            resume_from_checkpoint=(
                _path(args.resume_from_checkpoint) if args.resume_from_checkpoint else None
            ),
        )
        if args.validate_only:
            print(
                "validated LoRA+ run: "
                f"train={result['train_examples']}, eval={result['eval_examples']}, "
                f"lr_A={result['learning_rate_a']}, lr_B={result['learning_rate_b']}"
            )
        else:
            print(f"completed LoRA+ run at {result['config']['output_dir']}")
        return 0
    if args.command == "eval" and args.eval_command == "generate":
        count = generate_eval_outputs(
            _path(args.config),
            _path(args.cases),
            _path(args.output),
            _path(args.manifest),
            role=args.role,
            run_id=args.run_id,
            adapter_path=_path(args.adapter) if args.adapter else None,
            max_new_tokens=args.max_new_tokens,
            seed=args.seed,
        )
        print(f"generated {count} deterministic output(s) at {_path(args.output)}")
        return 0
    if args.command == "eval" and args.eval_command == "prepare":
        count = prepare_review(
            _path(args.cases),
            _path(args.baseline),
            _path(args.candidate),
            _path(args.packet),
            _path(args.key),
            seed=args.seed,
            baseline_manifest_path=(
                _path(args.baseline_manifest) if args.baseline_manifest else None
            ),
            candidate_manifest_path=(
                _path(args.candidate_manifest) if args.candidate_manifest else None
            ),
            guide_path=_path(args.guide) if args.guide else None,
        )
        print(f"prepared {count} blind review case(s) at {_path(args.packet)}")
        return 0
    if args.command == "eval" and args.eval_command == "summarize":
        summary = summarize_review(
            _path(args.packet),
            _path(args.key),
            _path(args.output),
            decision_rules_path=(_path(args.decision_rules) if args.decision_rules else None),
        )
        print(
            f"summarized {summary['case_count']} case(s); "
            f"candidate recommended={summary['candidate_recommended']}"
        )
        return 0
    raise AssertionError("unhandled command")


def main() -> int:
    try:
        return _run(build_parser().parse_args())
    except (
        ChunkBuildError,
        EvaluationError,
        ExternalSourceError,
        GenerationError,
        JsonlError,
        PairBuildError,
        PostImportError,
        PromptReviewError,
        TrainingError,
        OSError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
