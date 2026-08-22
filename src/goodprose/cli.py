"""Command-line interface for GoodProse dataset operations."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from goodprose.annotation import (
    AUTHORING_DATASET,
    REVIEW_DATASET,
    AnnotationError,
    backup_dataset,
    connect,
    ensure_workflows,
    export_reviewed,
    import_authoring_seeds,
    initialize_env,
    prepare_review_records,
)
from goodprose.dataset import DatasetValidationError, create_snapshot, validate_jsonl
from goodprose.jsonl import JsonlError
from goodprose.privacy import PrivacyScanError, scan_jsonl

REPO_ROOT = Path(__file__).resolve().parents[2]


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _argilla_connection(args: argparse.Namespace) -> tuple[object, str]:
    api_url = args.api_url or os.environ.get("ARGILLA_API_URL", "http://localhost:6900")
    api_key = os.environ.get("ARGILLA_API_KEY")
    if not api_key:
        raise AnnotationError("ARGILLA_API_KEY must be set in the environment")
    workspace = args.workspace or os.environ.get("ARGILLA_WORKSPACE", "goodprose")
    return connect(api_url, api_key), workspace


def _eval_paths(values: list[str] | None) -> list[Path]:
    if values:
        return [_path(value) for value in values]
    return [REPO_ROOT / "evals" / "cases", REPO_ROOT / "evals" / "private"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="goodprose")
    commands = parser.add_subparsers(dest="command", required=True)

    privacy = commands.add_parser("privacy", help="Scan JSONL for secrets and PII")
    privacy_commands = privacy.add_subparsers(dest="privacy_command", required=True)
    scan = privacy_commands.add_parser("scan")
    scan.add_argument("input")
    scan.add_argument("--report", required=True)
    scan.add_argument("--redacted-output")
    scan.add_argument("--presidio", action="store_true")
    scan.add_argument("--language", default="en")

    dataset = commands.add_parser("dataset", help="Validate and snapshot training datasets")
    dataset_commands = dataset.add_subparsers(dest="dataset_command", required=True)
    validate = dataset_commands.add_parser("validate")
    validate.add_argument("input")
    validate.add_argument("--eval-path", action="append")
    snapshot = dataset_commands.add_parser("snapshot")
    snapshot.add_argument("input")
    snapshot.add_argument("--privacy-report", required=True)
    snapshot.add_argument(
        "--output-root",
        default=str(REPO_ROOT / "data" / "derived" / "snapshots"),
    )
    snapshot.add_argument("--eval-path", action="append")
    snapshot.add_argument("--tokenizer")
    snapshot.add_argument("--tokenizer-revision")
    snapshot.add_argument("--max-tokens", type=int, default=32768)
    snapshot.add_argument("--allow-over-limit", action="store_true")

    annotation = commands.add_parser("annotation", help="Operate GoodProse's Argilla workflows")
    annotation_commands = annotation.add_subparsers(dest="annotation_command", required=True)
    init_env = annotation_commands.add_parser("init-env")
    init_env.add_argument(
        "--output",
        default=str(REPO_ROOT / "infra" / "argilla" / ".env"),
    )
    for name in ("setup", "import-authoring", "prepare-review", "export-reviewed", "backup"):
        command = annotation_commands.add_parser(name)
        command.add_argument("--api-url")
        command.add_argument("--workspace")
        if name == "import-authoring":
            command.add_argument("input")
            command.add_argument("--privacy-report", required=True)
        elif name == "export-reviewed":
            command.add_argument("--output", required=True)
        elif name == "backup":
            command.add_argument(
                "--dataset", choices=(AUTHORING_DATASET, REVIEW_DATASET), required=True
            )
            command.add_argument("--output", required=True)
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "privacy":
        report = scan_jsonl(
            _path(args.input),
            report_path=_path(args.report),
            redacted_output=_path(args.redacted_output) if args.redacted_output else None,
            use_presidio=args.presidio,
            language=args.language,
        )
        print(
            f"privacy scan complete: {report.record_count} records, {len(report.findings)} findings"
        )
        return 0 if report.is_clean else 1

    if args.command == "dataset" and args.dataset_command == "validate":
        errors = validate_jsonl(
            _path(args.input),
            repo_root=REPO_ROOT,
            eval_paths=_eval_paths(args.eval_path),
        )
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        print("training dataset is valid")
        return 0

    if args.command == "dataset" and args.dataset_command == "snapshot":
        snapshot_dir = create_snapshot(
            _path(args.input),
            _path(args.output_root),
            repo_root=REPO_ROOT,
            privacy_report_path=_path(args.privacy_report),
            eval_paths=_eval_paths(args.eval_path),
            tokenizer_name=args.tokenizer,
            tokenizer_revision=args.tokenizer_revision,
            max_tokens=args.max_tokens,
            allow_over_limit=args.allow_over_limit,
        )
        print(f"immutable snapshot ready: {snapshot_dir}")
        return 0

    if args.command == "annotation" and args.annotation_command == "init-env":
        path = initialize_env(_path(args.output))
        print(f"created private Argilla environment file: {path}")
        return 0

    if args.command == "annotation":
        client, workspace = _argilla_connection(args)
        if args.annotation_command == "setup":
            ensure_workflows(client, workspace)
            print(f"Argilla workflows are ready in workspace {workspace!r}")
        elif args.annotation_command == "import-authoring":
            added, skipped = import_authoring_seeds(
                client,
                workspace,
                _path(args.input),
                _path(args.privacy_report),
            )
            print(f"authoring import complete: {added} added, {skipped} already present")
        elif args.annotation_command == "prepare-review":
            added, skipped = prepare_review_records(client, workspace)
            print(f"review preparation complete: {added} added, {skipped} already present")
        elif args.annotation_command == "export-reviewed":
            count = export_reviewed(client, workspace, _path(args.output))
            print(f"exported {count} reviewed examples to {_path(args.output)}")
        elif args.annotation_command == "backup":
            path = backup_dataset(client, workspace, args.dataset, _path(args.output))
            print(f"Argilla backup written to {path}")
        return 0
    raise AssertionError("unhandled command")


def main() -> int:
    try:
        return _run(build_parser().parse_args())
    except (
        AnnotationError,
        DatasetValidationError,
        JsonlError,
        PrivacyScanError,
        OSError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
