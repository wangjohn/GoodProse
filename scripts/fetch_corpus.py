#!/usr/bin/env python3
"""Fetch pinned corpus files and verify their SHA-256 checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
import urllib.error
import urllib.request


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "sources.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "raw"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--source",
        action="append",
        dest="sources",
        help="Fetch only this source id. Repeat to select multiple sources.",
    )
    parser.add_argument(
        "--split",
        action="append",
        dest="splits",
        choices=("train_reference", "dev_eval", "test_eval", "candidate"),
        help="Fetch only this split. Repeat to select multiple splits.",
    )
    parser.add_argument(
        "--include-review",
        action="store_true",
        help="Include sources whose fetch_policy is manual_review.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace a local file whose contents do not match the manifest.",
    )
    return parser.parse_args()


def safe_relative_path(value: str) -> Path:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe manifest path: {value!r}")
    return Path(*path.parts)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "RFClear-corpus-fetcher/1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.URLError as error:
        raise RuntimeError(f"failed to download {url}: {error}") from error


def install_file(destination: Path, data: bytes, expected_sha: str, force: bool) -> str:
    actual_sha = sha256_bytes(data)
    if actual_sha != expected_sha:
        raise RuntimeError(
            f"upstream checksum mismatch for {destination}: "
            f"expected {expected_sha}, received {actual_sha}"
        )

    if destination.exists():
        local_sha = sha256_bytes(destination.read_bytes())
        if local_sha == expected_sha:
            return "verified"
        if not force:
            raise RuntimeError(
                f"local file differs from the manifest: {destination}\n"
                "Use --force only if replacing it is intentional."
            )

    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", dir=destination.parent
    )
    try:
        with os.fdopen(file_descriptor, "wb") as temporary_file:
            temporary_file.write(data)
        os.replace(temporary_name, destination)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return "fetched"


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    selected_sources = set(args.sources or [])
    selected_splits = set(args.splits or [])
    known_sources = {source["id"] for source in manifest["sources"]}
    unknown_sources = selected_sources - known_sources
    if unknown_sources:
        raise ValueError(f"unknown source ids: {', '.join(sorted(unknown_sources))}")

    fetched_count = 0
    verified_count = 0
    skipped_sources: list[str] = []

    for source in manifest["sources"]:
        source_id = source["id"]
        if selected_sources and source_id not in selected_sources:
            continue
        if source["fetch_policy"] == "manual_review" and not args.include_review:
            skipped_sources.append(source_id)
            continue

        documents = [
            document
            for document in source["documents"]
            if not selected_splits or document["split"] in selected_splits
        ]
        if not documents:
            continue

        entries = [("license", entry) for entry in source["licenses"]]
        entries.extend(("document", entry) for entry in documents)
        for entry_kind, entry in entries:
            relative_path = safe_relative_path(entry["path"])
            destination = args.output / source_id / relative_path
            url = f"{source['raw_base_url'].rstrip('/')}/{entry['path']}"
            if destination.exists() and sha256_bytes(destination.read_bytes()) == entry["sha256"]:
                result = "verified"
            else:
                result = install_file(
                    destination, download(url), entry["sha256"], args.force
                )
            if result == "fetched":
                fetched_count += 1
            else:
                verified_count += 1
            print(f"{result:8} {entry_kind:8} {destination.relative_to(REPO_ROOT)}")

    if skipped_sources:
        print(
            "skipped sources requiring manual review: "
            + ", ".join(sorted(skipped_sources)),
            file=sys.stderr,
        )
    print(f"done: {fetched_count} fetched, {verified_count} already verified")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
