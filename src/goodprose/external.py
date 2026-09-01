"""Build private source samples for external John Wang posts."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import (
    AuthenticInputMapping,
    BlogPost,
    Brief,
    ExternalPlatform,
    ExternalPostCatalog,
    ExternalPostSample,
    ExternalSourceMapping,
    ExternalSourceStatus,
    ReviewStatus,
    Split,
    SplitAssignment,
)

_WORD = re.compile(r"[\w]+(?:[\'\N{RIGHT SINGLE QUOTATION MARK}-][\w]+)*", re.UNICODE)
_READING_TIME = re.compile(r"^\d+ min read$")
_MEDIUM_DATE = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}$")
_IMAGE_LINE = re.compile(r"^\[?!\[Image \d+(?::[^]]*)?]|^!\[Image \d+(?::[^]]*)?]")
_MARKDOWN_CONTENT = "Markdown Content:"
_PUBLIC_PAGE_UI_PREFIXES = (
    "This file contains hidden or bidirectional Unicode text",
    "[Show hidden characters]",
)
_MEDIUM_UI_LINES = {
    "## Get John Wang\N{RIGHT SINGLE QUOTATION MARK}s stories in your inbox",
    "Join Medium for free to get updates from this writer.",
    "Remember me for faster sign in",
    "Press enter or click to view image in full size",
    "--",
}


class ExternalSourceError(ValueError):
    """External catalog and private source mappings are inconsistent."""


def _unique[
    RecordT: ExternalPostCatalog | ExternalSourceMapping | AuthenticInputMapping | SplitAssignment
](records: Sequence[RecordT], *, key: str, kind: str) -> dict[str, RecordT]:
    indexed: dict[str, RecordT] = {}
    for record in records:
        value = str(getattr(record, key))
        if value in indexed:
            raise ExternalSourceError(f"duplicate {kind} {value!r}")
        indexed[value] = record
    return indexed


def _safe_source_path(source_root: Path, relative_path: str) -> Path:
    root = source_root.resolve()
    path = (root / relative_path).resolve()
    if not path.is_relative_to(root):
        raise ExternalSourceError(f"source path escapes source root: {relative_path!r}")
    if not path.is_file():
        raise ExternalSourceError(f"source file does not exist: {relative_path!r}")
    return path


def build_external_samples(
    catalog_path: Path,
    source_map_path: Path,
    source_root: Path,
    output_path: Path,
) -> dict[str, int]:
    catalog = _unique(load_jsonl(catalog_path, ExternalPostCatalog), key="id", kind="post ID")
    mappings = _unique(
        load_jsonl(source_map_path, ExternalSourceMapping),
        key="post_id",
        kind="source mapping",
    )
    unexpected = sorted(set(mappings) - set(catalog))
    if unexpected:
        raise ExternalSourceError(f"source mappings reference unknown post(s): {unexpected}")

    recoverable = {
        post_id
        for post_id, post in catalog.items()
        if post.source_status is ExternalSourceStatus.PRIVATE_MARKDOWN_RECOVERED
    }
    missing = sorted(recoverable - set(mappings))
    if missing:
        raise ExternalSourceError(f"missing source mapping(s): {missing}")
    mapped_public_only = sorted(set(mappings) - recoverable)
    if mapped_public_only:
        raise ExternalSourceError(
            f"public-page-only post(s) unexpectedly have source mappings: {mapped_public_only}"
        )

    samples: list[ExternalPostSample] = []
    for post_id in sorted(recoverable):
        post = catalog[post_id]
        mapping = mappings[post_id]
        source_path = _safe_source_path(source_root, mapping.source_path)
        raw_markdown = source_path.read_text(encoding="utf-8").strip()
        samples.append(
            ExternalPostSample(
                id=post.id,
                lineage_id=post.lineage_id,
                title=post.title,
                platform=post.platform,
                source_url=post.source_url,
                published_at=post.published_at,
                source_path=mapping.source_path,
                source_sha256=hashlib.sha256(raw_markdown.encode()).hexdigest(),
                raw_markdown=raw_markdown,
                word_count=len(_WORD.findall(raw_markdown)),
                notes=(
                    "Raw private author source. Compare it with the published page, remove export "
                    "metadata, and confirm final authorship before canonical use."
                ),
            )
        )
    atomic_write(output_path, serialize_jsonl(samples))
    return dict(sorted(Counter(sample.platform.value for sample in samples).items()))


def normalize_published_snapshot(snapshot: str, platform: ExternalPlatform) -> str:
    """Extract article Markdown from a saved public-page Markdown snapshot."""
    _, marker, content = snapshot.partition(_MARKDOWN_CONTENT)
    if not marker:
        raise ExternalSourceError("published snapshot has no Markdown Content marker")

    normalized: list[str] = []
    for raw_line in content.replace("\r\n", "\n").splitlines():
        line = raw_line.replace("\N{ZERO WIDTH JOINER}", "").rstrip()
        stripped = line.strip()
        if _IMAGE_LINE.match(stripped):
            continue
        if stripped.startswith(_PUBLIC_PAGE_UI_PREFIXES):
            continue
        if platform is ExternalPlatform.MEDIUM and (
            stripped in _MEDIUM_UI_LINES
            or _READING_TIME.fullmatch(stripped)
            or _MEDIUM_DATE.fullmatch(stripped)
        ):
            continue
        if not stripped:
            if normalized and normalized[-1] != "":
                normalized.append("")
            continue
        normalized.append(line)

    body = "\n".join(normalized).strip()
    if not body:
        raise ExternalSourceError("published snapshot has no article content")
    return body


def build_external_posts(
    catalog_path: Path,
    snapshot_root: Path,
    output_path: Path,
    *,
    base_posts_path: Path | None = None,
) -> dict[str, int]:
    """Build canonical posts from reviewed public snapshots and optionally merge base posts."""
    catalog = _unique(load_jsonl(catalog_path, ExternalPostCatalog), key="id", kind="post ID")
    unapproved = sorted(
        post.id for post in catalog.values() if post.review_status is not ReviewStatus.APPROVED
    )
    if unapproved:
        raise ExternalSourceError(f"external post(s) are not approved: {unapproved}")

    external_posts: list[BlogPost] = []
    for post_id in sorted(catalog):
        catalog_post = catalog[post_id]
        snapshot_filename = f"{post_id}.md"
        snapshot_path = _safe_source_path(snapshot_root, snapshot_filename)
        body = normalize_published_snapshot(
            snapshot_path.read_text(encoding="utf-8"), catalog_post.platform
        )
        external_posts.append(
            BlogPost(
                id=catalog_post.id,
                lineage_id=catalog_post.lineage_id,
                title=catalog_post.title,
                body_markdown=body,
                source_path=f"external/published-raw/{snapshot_filename}",
                source_url=catalog_post.source_url,
                published_at=catalog_post.published_at,
            )
        )

    base_posts = load_jsonl(base_posts_path, BlogPost) if base_posts_path is not None else []
    external_ids = set(catalog)
    merged = [post for post in base_posts if post.id not in external_ids]
    merged.extend(external_posts)
    ids = Counter(post.id for post in merged)
    duplicates = sorted(post_id for post_id, count in ids.items() if count > 1)
    if duplicates:
        raise ExternalSourceError(f"duplicate merged post ID(s): {duplicates}")
    merged.sort(key=lambda post: post.id)
    atomic_write(output_path, serialize_jsonl(merged))
    return {
        "base": len(merged) - len(external_posts),
        "external": len(external_posts),
        "total": len(merged),
    }


def build_authentic_eval_briefs(
    source_map_path: Path,
    source_root: Path,
    splits_path: Path,
    output_path: Path,
) -> dict[str, int]:
    """Extract exact author drafts/outlines for held-out development and test lineages."""
    mappings = _unique(
        load_jsonl(source_map_path, AuthenticInputMapping),
        key="post_id",
        kind="authentic input mapping",
    )
    assignments = _unique(
        load_jsonl(splits_path, SplitAssignment),
        key="lineage_id",
        kind="split assignment",
    )
    briefs: list[Brief] = []
    for post_id in sorted(mappings):
        mapping = mappings[post_id]
        assignment = assignments.get(post_id)
        if assignment is None:
            raise ExternalSourceError(f"authentic input has no split assignment: {post_id!r}")
        if assignment.split is Split.TRAIN:
            raise ExternalSourceError(
                f"authentic eval input cannot use training split: {post_id!r}"
            )
        source_path = _safe_source_path(source_root, mapping.source_path)
        lines = source_path.read_text(encoding="utf-8").splitlines()
        if mapping.start_line > len(lines):
            raise ExternalSourceError(
                f"start line {mapping.start_line} exceeds {len(lines)} lines in "
                f"{mapping.source_path!r}"
            )
        end_line = mapping.end_line or len(lines)
        if end_line > len(lines):
            raise ExternalSourceError(
                f"end line {end_line} exceeds {len(lines)} lines in {mapping.source_path!r}"
            )
        input_text = "\n".join(lines[mapping.start_line - 1 : end_line]).strip()
        briefs.append(
            Brief(
                id=post_id,
                post_id=post_id,
                split=assignment.split,
                input=input_text,
                input_method=mapping.input_method,
            )
        )
    atomic_write(output_path, serialize_jsonl(briefs))
    return dict(sorted(Counter(brief.split.value for brief in briefs).items()))
