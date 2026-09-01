"""Join reviewed inputs to the author's exact published posts."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import BlogPost, Brief, Split, WritingPair


class PairBuildError(ValueError):
    """Canonical pairs violate a dataset invariant."""


def _unique_by_id[RecordT: BlogPost | Brief | WritingPair](
    records: list[RecordT], *, kind: str
) -> dict[str, RecordT]:
    indexed: dict[str, RecordT] = {}
    for record in records:
        if record.id in indexed:
            raise PairBuildError(f"duplicate {kind} ID {record.id!r}")
        indexed[record.id] = record
    return indexed


def _render_post(post: BlogPost) -> str:
    body = post.body_markdown.strip("\n")
    if reuses_title_as_heading(body, post.title):
        return body
    return f"# {post.title}\n\n{body}"


def reuses_title_as_heading(body: str, title: str) -> bool:
    first_line = body.lstrip().splitlines()[0].strip()
    return first_line == f"# {title}"


def validate_pairs(pairs: list[WritingPair]) -> None:
    if not pairs:
        raise PairBuildError("pair dataset is empty")
    _unique_by_id(pairs, kind="pair")
    post_splits: dict[str, set[Split]] = defaultdict(set)
    lineage_splits: dict[str, set[Split]] = defaultdict(set)
    for pair in pairs:
        post_splits[pair.post_id].add(pair.split)
        lineage_splits[pair.lineage_id].add(pair.split)
    for post_id, splits in post_splits.items():
        if len(splits) > 1:
            raise PairBuildError(f"post {post_id!r} crosses splits")
    for lineage_id, splits in lineage_splits.items():
        if len(splits) > 1:
            raise PairBuildError(f"lineage {lineage_id!r} crosses splits")


def load_pairs(path: Path) -> list[WritingPair]:
    pairs = load_jsonl(path, WritingPair)
    validate_pairs(pairs)
    return sorted(pairs, key=lambda pair: pair.id)


def build_pairs(posts_path: Path, briefs_path: Path, output_path: Path) -> int:
    posts = _unique_by_id(load_jsonl(posts_path, BlogPost), kind="post")
    briefs = load_jsonl(briefs_path, Brief)
    _unique_by_id(briefs, kind="brief")
    seen_posts: set[str] = set()
    pairs: list[WritingPair] = []
    for brief in briefs:
        post = posts.get(brief.post_id)
        if post is None:
            raise PairBuildError(f"{brief.id}: unknown post ID {brief.post_id!r}")
        if brief.post_id in seen_posts:
            raise PairBuildError(f"post {brief.post_id!r} has more than one brief")
        seen_posts.add(brief.post_id)
        pairs.append(
            WritingPair(
                id=brief.id,
                post_id=post.id,
                lineage_id=post.lineage_id,
                split=brief.split,
                input=brief.input,
                input_method=brief.input_method,
                title=post.title,
                output=_render_post(post),
                source_url=post.source_url,
                published_at=post.published_at,
            )
        )
    validate_pairs(pairs)
    pairs.sort(key=lambda pair: pair.id)
    atomic_write(output_path, serialize_jsonl(pairs))
    return len(pairs)
