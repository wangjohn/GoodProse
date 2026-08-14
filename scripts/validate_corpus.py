#!/usr/bin/env python3
"""Validate provenance, checksums, and train/eval separation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "sources.json"
DEFAULT_TARGETS = REPO_ROOT / "evals" / "targets.json"
DEFAULT_RAW = REPO_ROOT / "data" / "raw"
ALLOWED_SPLITS = {"train_reference", "dev_eval", "test_eval", "candidate"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Validate metadata without requiring default-fetched files on disk.",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_safe_path(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(path.parts) and not path.is_absolute() and ".." not in path.parts


def validate(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    targets = json.loads(args.targets.read_text(encoding="utf-8"))
    source_ids: set[str] = set()
    document_ids: set[str] = set()
    hashes_by_split: dict[str, set[str]] = {split: set() for split in ALLOWED_SPLITS}
    documents_by_id: dict[str, dict[str, str]] = {}

    for source in manifest.get("sources", []):
        source_id = source.get("id", "")
        if source_id in source_ids:
            errors.append(f"duplicate source id: {source_id}")
        source_ids.add(source_id)

        if source.get("fetch_policy") not in {"default", "manual_review"}:
            errors.append(f"{source_id}: invalid fetch_policy")
        if source.get("holdout_policy") == "source_family":
            source_splits = {document.get("split") for document in source.get("documents", [])}
            if source_splits != {"test_eval"}:
                errors.append(
                    f"{source_id}: source_family holdout must contain only test_eval documents"
                )

        for entry_kind in ("licenses", "documents"):
            for entry in source.get(entry_kind, []):
                entry_path = entry.get("path", "")
                if not is_safe_path(entry_path):
                    errors.append(f"{source_id}: unsafe path: {entry_path!r}")
                    continue
                expected_sha = entry.get("sha256", "")
                if len(expected_sha) != 64:
                    errors.append(f"{source_id}/{entry_path}: invalid SHA-256")

                should_exist = source.get("fetch_policy") == "default"
                local_path = args.raw / source_id / Path(*PurePosixPath(entry_path).parts)
                if should_exist and not local_path.exists() and not args.allow_missing:
                    errors.append(f"missing default corpus file: {local_path.relative_to(REPO_ROOT)}")
                elif local_path.exists() and sha256_file(local_path) != expected_sha:
                    errors.append(f"checksum mismatch: {local_path.relative_to(REPO_ROOT)}")

        for document in source.get("documents", []):
            document_id = document.get("id", "")
            split = document.get("split", "")
            if document_id in document_ids:
                errors.append(f"duplicate document id: {document_id}")
            document_ids.add(document_id)
            if split not in ALLOWED_SPLITS:
                errors.append(f"{document_id}: invalid split {split!r}")
                continue
            if source.get("fetch_policy") == "manual_review" and split != "candidate":
                errors.append(f"{document_id}: manual-review sources must remain candidates")
            document_sha = document.get("sha256", "")
            hashes_by_split[split].add(document_sha)
            documents_by_id[document_id] = {"split": split, "source_id": source_id}

    protected_splits = ("train_reference", "dev_eval", "test_eval")
    for index, left in enumerate(protected_splits):
        for right in protected_splits[index + 1 :]:
            overlap = hashes_by_split[left] & hashes_by_split[right]
            if overlap:
                errors.append(f"identical content appears in both {left} and {right}")

    target_ids: set[str] = set()
    for target in targets.get("targets", []):
        target_id = target.get("document_id", "")
        expected_split = target.get("split", "")
        if target_id in target_ids:
            errors.append(f"duplicate eval target: {target_id}")
        target_ids.add(target_id)
        document = documents_by_id.get(target_id)
        if document is None:
            errors.append(f"unknown eval target: {target_id}")
        elif document["split"] != expected_split:
            errors.append(
                f"{target_id}: target split {expected_split!r} does not match "
                f"manifest split {document['split']!r}"
            )

    expected_targets = {
        document_id
        for document_id, document in documents_by_id.items()
        if document["split"] in {"dev_eval", "test_eval"}
    }
    if target_ids != expected_targets:
        missing = expected_targets - target_ids
        extra = target_ids - expected_targets
        if missing:
            errors.append(f"eval targets missing from registry: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"non-eval documents in target registry: {', '.join(sorted(extra))}")

    return errors


def main() -> int:
    args = parse_args()
    try:
        errors = validate(args)
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("corpus is valid: provenance, checksums, and split boundaries passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
