"""Command-line entry point for the small GoodProse workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from goodprose.chat import ChatTemplateError
from goodprose.chunks import ChunkBuildError, build_chunks
from goodprose.dpo import DpoError, run_dpo
from goodprose.evaluation import EvaluationError, prepare_review, summarize_review
from goodprose.external import (
    ExternalSourceError,
    build_authentic_eval_briefs,
    build_external_posts,
    build_external_samples,
)
from goodprose.generation import GenerationError, generate_eval_outputs
from goodprose.jsonl import JsonlError
from goodprose.judge import build_judge_packet, summarize_judge_verdicts
from goodprose.models import SystemLabel
from goodprose.pairs import PairBuildError, build_pairs
from goodprose.posts import PostImportError, import_posts
from goodprose.preference import PreferenceBuildError, build_preference_pairs
from goodprose.prompts import (
    PromptReviewError,
    approve_prompt_candidates,
    build_prompt_candidates,
    build_prompt_pairs,
    build_prompt_review,
)
from goodprose.proxy import ProxyError, proxy_report
from goodprose.scoring import ScoringError, score_completions
from goodprose.sft import build_sft
from goodprose.shortcases import (
    DEFAULT_SCOPE_LINE,
    ShortCaseError,
    approve_short_cases,
    build_short_case_candidates,
    promote_short_cases,
)
from goodprose.training import TrainingError, run_lora_plus


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _labelled_path(value: str) -> tuple[str, Path]:
    label, separator, path = value.partition("=")
    if not separator or not label.strip() or not path.strip():
        raise argparse.ArgumentTypeError("expected LABEL=PATH")
    return label.strip(), _path(path.strip())


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
    chunks_command.add_argument(
        "--full-posts",
        action="store_true",
        help="Also emit one post-scale target per training post (prefix of kept sections)",
    )
    chunks_command.add_argument(
        "--no-preserve-status",
        action="store_true",
        help="Do not carry existing approvals forward from the current output file",
    )

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
    prompt_pairs_command.add_argument(
        "--text-exclusions",
        help="Reviewed exact input/target spans to remove from the assembled pairs",
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
    sft_command.add_argument(
        "--raw-completions",
        action="store_true",
        help="Append title-conditioned completions of every distinct training target",
    )
    sft_command.add_argument(
        "--train-cases-output",
        help="Also write the training inputs as cases for on-policy rejected sampling",
    )
    sft_command.add_argument(
        "--dev-cases-output",
        help="Also write the development pairs as cases for proxy calibration",
    )

    short_cases_command = commands.add_parser(
        "build-short-cases",
        help="Cut held-out whole-post cases into section-scale review candidates",
    )
    short_cases_command.add_argument("--cases", required=True)
    short_cases_command.add_argument("--chunks", required=True)
    short_cases_command.add_argument("--posts", required=True)
    short_cases_command.add_argument("--output", required=True)
    short_cases_command.add_argument("--review-output", required=True)
    short_cases_command.add_argument("--min-words", type=int, default=60)
    short_cases_command.add_argument("--max-words", type=int, default=450)
    short_cases_command.add_argument("--max-paragraphs", type=int, default=8)
    short_cases_command.add_argument("--min-recall", type=float, default=0.35)
    short_cases_command.add_argument(
        "--max-near-verbatim",
        type=int,
        default=2,
        help="Keep at most this many near-verbatim polish cases; auto-reject the rest",
    )
    short_cases_command.add_argument("--scope-line", default=DEFAULT_SCOPE_LINE)

    approve_short_command = commands.add_parser(
        "approve-short-cases",
        help="Stamp the reviewed system prompt onto short cases marked approved",
    )
    approve_short_command.add_argument("--candidates", required=True)
    approve_short_command.add_argument("--reviewer-note", required=True)

    promote_short_command = commands.add_parser(
        "promote-short-cases", help="Write approved short candidates as evaluation cases"
    )
    promote_short_command.add_argument("--candidates", required=True)
    promote_short_command.add_argument("--output", required=True)

    preference_command = commands.add_parser(
        "build-preference",
        help="Join training pairs to sampled model outputs as DPO chosen/rejected records",
    )
    preference_command.add_argument("--pairs", required=True)
    preference_command.add_argument("--rejected", required=True)
    preference_command.add_argument("--rejected-manifest")
    preference_command.add_argument("--rejected-run-id")
    preference_command.add_argument("--output", required=True)

    train_command = commands.add_parser(
        "train-lora-plus",
        help="Validate or run a PEFT/TRL LoRA or LoRA+ supervised fine-tune",
    )
    train_command.add_argument("--config", required=True)
    train_command.add_argument("--validate-only", action="store_true")
    train_command.add_argument("--resume-from-checkpoint")

    dpo_command = commands.add_parser(
        "train-dpo", help="Validate or run a DPO pass on top of a finished SFT adapter"
    )
    dpo_command.add_argument("--config", required=True)
    dpo_command.add_argument("--validate-only", action="store_true")

    eval_command = commands.add_parser("eval", help="Generate, score, and compare outputs")
    eval_commands = eval_command.add_subparsers(dest="eval_command", required=True)

    generate = eval_commands.add_parser(
        "generate",
        help="Generate matched base-model or LoRA-checkpoint outputs",
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
    generate.add_argument(
        "--temperature", type=float, default=0.7, help="0 selects greedy decoding"
    )
    generate.add_argument("--top-p", type=float, default=0.9)
    generate.add_argument("--repetition-penalty", type=float, default=1.05)

    nll = eval_commands.add_parser(
        "nll", help="Score held-out completions' negative log-likelihood under a checkpoint"
    )
    nll.add_argument("--config", required=True)
    nll.add_argument("--records", required=True, help="Chat JSONL such as data/sft/dev.jsonl")
    nll.add_argument("--adapter")
    nll.add_argument("--run-id", required=True)
    nll.add_argument("--output", required=True)

    proxy = eval_commands.add_parser(
        "proxy", help="Stylometric, repetition, and memorization proxies for output files"
    )
    proxy.add_argument("--cases", required=True)
    proxy.add_argument(
        "--outputs",
        action="append",
        type=_labelled_path,
        default=[],
        required=True,
        help="LABEL=PATH of a model output file; repeat to rank several systems",
    )
    proxy.add_argument("--posts", required=True)
    proxy.add_argument("--splits", required=True)
    proxy.add_argument("--output", required=True)
    proxy.add_argument("--memorization-run-threshold", type=int, default=30)

    judge_packet = eval_commands.add_parser(
        "judge-packet", help="Render blinded pairwise voice prompts for a frontier judge"
    )
    judge_packet.add_argument("--cases", required=True)
    judge_packet.add_argument("--baseline", required=True)
    judge_packet.add_argument("--candidate", required=True)
    judge_packet.add_argument("--posts", required=True)
    judge_packet.add_argument("--splits", required=True)
    judge_packet.add_argument("--packet", required=True)
    judge_packet.add_argument("--key", required=True)
    judge_packet.add_argument("--seed", type=int, default=20260902)
    judge_packet.add_argument("--sample-count", type=int, default=3)
    judge_packet.add_argument("--sample-words", type=int, default=400)

    judge_summary = eval_commands.add_parser(
        "judge-summarize", help="Unblind judge verdicts against the packet key"
    )
    judge_summary.add_argument("--verdicts", required=True)
    judge_summary.add_argument("--key", required=True)
    judge_summary.add_argument("--output", required=True)

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


def _format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items())


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
            full_posts=args.full_posts,
            preserve_status=not args.no_preserve_status,
        )
        print(f"built semantic chunks: {_format_counts(counts)}")
        return 0
    if args.command == "review-prompts":
        count = build_prompt_review(_path(args.prompts), _path(args.chunks), _path(args.output))
        print(f"rendered {count} synthetic prompt candidate(s) at {_path(args.output)}")
        return 0
    if args.command == "approve-prompts":
        counts = approve_prompt_candidates(
            _path(args.prompts),
            _path(args.chunks),
            reviewer_note=args.reviewer_note,
        )
        print(f"approved training data: {_format_counts(counts)}")
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
            text_exclusions_path=(_path(args.text_exclusions) if args.text_exclusions else None),
        )
        print(f"built canonical prompt pairs: {_format_counts(counts)}")
        return 0
    if args.command == "build-external-samples":
        counts = build_external_samples(
            _path(args.catalog),
            _path(args.source_map),
            _path(args.source_root),
            _path(args.output),
        )
        print(f"built external source samples: {_format_counts(counts)}")
        return 0
    if args.command == "build-external-posts":
        counts = build_external_posts(
            _path(args.catalog),
            _path(args.snapshot_root),
            _path(args.output),
            base_posts_path=_path(args.base_posts) if args.base_posts else None,
        )
        print(f"built canonical post file: {_format_counts(counts)}")
        return 0
    if args.command == "build-authentic-eval-briefs":
        counts = build_authentic_eval_briefs(
            _path(args.source_map),
            _path(args.source_root),
            _path(args.splits),
            _path(args.output),
        )
        print(f"built authentic eval briefs: {_format_counts(counts)}")
        return 0
    if args.command == "build-sft":
        counts = build_sft(
            _path(args.pairs),
            _path(args.output_dir),
            _path(args.eval_output),
            raw_completions=args.raw_completions,
            train_cases_output=(
                _path(args.train_cases_output) if args.train_cases_output else None
            ),
            dev_cases_output=_path(args.dev_cases_output) if args.dev_cases_output else None,
        )
        print(f"built SFT data: {_format_counts(counts)}")
        return 0
    if args.command == "build-short-cases":
        counts = build_short_case_candidates(
            _path(args.cases),
            _path(args.chunks),
            _path(args.posts),
            _path(args.output),
            _path(args.review_output),
            min_words=args.min_words,
            max_words=args.max_words,
            max_paragraphs=args.max_paragraphs,
            min_recall=args.min_recall,
            max_near_verbatim=args.max_near_verbatim,
            scope_line=args.scope_line,
        )
        print(f"built short case candidates: {_format_counts(counts)}")
        return 0
    if args.command == "approve-short-cases":
        counts = approve_short_cases(_path(args.candidates), reviewer_note=args.reviewer_note)
        print(f"approved short review cases: {_format_counts(counts)}")
        return 0
    if args.command == "promote-short-cases":
        count = promote_short_cases(_path(args.candidates), _path(args.output))
        print(f"promoted {count} short review case(s) to {_path(args.output)}")
        return 0
    if args.command == "build-preference":
        counts = build_preference_pairs(
            _path(args.pairs),
            _path(args.rejected),
            _path(args.output),
            rejected_manifest_path=(
                _path(args.rejected_manifest) if args.rejected_manifest else None
            ),
            rejected_run_id=args.rejected_run_id,
        )
        print(f"built preference pairs: {_format_counts(counts)}")
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
                "validated fine-tune run: "
                f"train={result['train_examples']}, eval={result['eval_examples']}, "
                f"lr_A={result['learning_rate_a']}, lr_B={result['learning_rate_b']}, "
                f"optimizer_steps={result['optimizer_steps']}"
            )
        else:
            print(f"completed fine-tune run at {result['config']['output_dir']}")
        return 0
    if args.command == "train-dpo":
        result = run_dpo(_path(args.config), validate_only=args.validate_only)
        if args.validate_only:
            print(
                "validated DPO run: "
                f"pairs={result['preference_pairs']}, beta={result['beta']}, "
                f"optimizer_steps={result['optimizer_steps']}"
            )
        else:
            print(f"completed DPO run at {result['config']['output_dir']}")
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
            temperature=args.temperature,
            top_p=args.top_p,
            repetition_penalty=args.repetition_penalty,
        )
        print(f"generated {count} output(s) at {_path(args.output)}")
        return 0
    if args.command == "eval" and args.eval_command == "nll":
        report = score_completions(
            _path(args.config),
            _path(args.records),
            _path(args.output),
            run_id=args.run_id,
            adapter_path=_path(args.adapter) if args.adapter else None,
        )
        print(f"scored {report['records']} record(s): mean completion NLL {report['mean_nll']:.4f}")
        return 0
    if args.command == "eval" and args.eval_command == "proxy":
        report = proxy_report(
            _path(args.cases),
            args.outputs,
            _path(args.posts),
            _path(args.splits),
            _path(args.output),
            memorization_run_threshold=args.memorization_run_threshold,
        )
        print("proxy ranking (closest to author first): " + ", ".join(report["ranking"]))
        return 0
    if args.command == "eval" and args.eval_command == "judge-packet":
        count = build_judge_packet(
            _path(args.cases),
            _path(args.baseline),
            _path(args.candidate),
            _path(args.posts),
            _path(args.splits),
            _path(args.packet),
            _path(args.key),
            seed=args.seed,
            sample_count=args.sample_count,
            sample_words=args.sample_words,
        )
        print(f"rendered {count} blinded judge prompt(s) at {_path(args.packet)}")
        return 0
    if args.command == "eval" and args.eval_command == "judge-summarize":
        summary = summarize_judge_verdicts(
            _path(args.verdicts), _path(args.key), _path(args.output)
        )
        print(
            f"judge voice wins: {_format_counts(summary['voice_wins'])} "
            f"(candidate win rate {summary['candidate_win_rate']:.2f})"
        )
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
        ChatTemplateError,
        ChunkBuildError,
        DpoError,
        EvaluationError,
        ExternalSourceError,
        GenerationError,
        JsonlError,
        PairBuildError,
        PostImportError,
        PreferenceBuildError,
        PromptReviewError,
        ProxyError,
        ScoringError,
        ShortCaseError,
        TrainingError,
        OSError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
