"""Build reviewable semantic chunks without changing published target text."""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import (
    BlogPost,
    ChunkExclusionSpec,
    ReviewStatus,
    SemanticChunk,
    Split,
    SplitAssignment,
    SupplementalChunkSpec,
)

_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_WORD = re.compile(r"[\w]+(?:[\'\N{RIGHT SINGLE QUOTATION MARK}-][\w]+)*", re.UNICODE)
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


class ChunkBuildError(ValueError):
    """Posts and their frozen split manifest cannot produce valid chunks."""


@dataclass(frozen=True)
class _Block:
    start: int
    end: int
    heading: str | None


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _approx_tokens(value: str) -> int:
    return max(1, math.ceil(len(value) / 4))


def _word_count(value: str) -> int:
    return len(_WORD.findall(value))


def _heading(value: str) -> str | None:
    first_line = value.splitlines()[0] if value.splitlines() else ""
    match = _HEADING.fullmatch(first_line)
    return match.group(2).strip() if match else None


def _blocks(body: str) -> list[_Block]:
    blocks: list[_Block] = []
    block_start: int | None = None
    fence_marker: str | None = None
    offset = 0

    for line in body.splitlines(keepends=True):
        fence_match = _FENCE.match(line)
        is_blank_separator = not line.strip() and fence_marker is None
        if is_blank_separator:
            if block_start is not None:
                block_end = offset
                while block_end > block_start and body[block_end - 1] in "\r\n":
                    block_end -= 1
                text = body[block_start:block_end]
                blocks.append(_Block(block_start, block_end, _heading(text)))
                block_start = None
            offset += len(line)
            continue

        if block_start is None:
            block_start = offset
        if fence_match:
            marker = fence_match.group(1)
            if fence_marker is None:
                fence_marker = marker[0]
            elif marker[0] == fence_marker:
                fence_marker = None
        offset += len(line)

    if block_start is not None:
        block_end = len(body)
        while block_end > block_start and body[block_end - 1] in "\r\n":
            block_end -= 1
        text = body[block_start:block_end]
        blocks.append(_Block(block_start, block_end, _heading(text)))
    return _glue_list_introductions(body, blocks)


_LIST_START = re.compile(r"^[ \t]*(?:(?:[-*+]|\d+[.)])[ \t]+|\|)")


def _glue_list_introductions(body: str, blocks: list[_Block]) -> list[_Block]:
    """Keep a paragraph that ends with a colon together with the list or table it introduces.

    A target that ends "...the following:" with its list cut into the next chunk is a bad
    completion, so the intro and its list (or table) become one unsplittable block. A colon
    before a heading is left alone; the author is introducing the sections that follow.
    """
    glued: list[_Block] = []
    for block in blocks:
        if glued:
            previous = glued[-1]
            if body[previous.start : previous.end].rstrip().endswith(":") and _LIST_START.match(
                body[block.start : block.end]
            ):
                glued[-1] = _Block(previous.start, block.end, previous.heading)
                continue
        glued.append(block)
    return glued


def _section_groups(blocks: list[_Block]) -> list[list[_Block]]:
    sections: list[list[_Block]] = []
    current: list[_Block] = []
    for block in blocks:
        if block.heading is not None and current:
            sections.append(current)
            current = []
        current.append(block)
    if current:
        sections.append(current)
    return sections


def _span_text(body: str, blocks: list[_Block]) -> str:
    return body[blocks[0].start : blocks[-1].end]


def _split_large_sections(
    body: str, sections: list[list[_Block]], max_tokens: int
) -> list[list[_Block]]:
    groups: list[list[_Block]] = []
    for section in sections:
        current: list[_Block] = []
        for block in section:
            proposed = [*current, block]
            if current and _approx_tokens(_span_text(body, proposed)) > max_tokens:
                groups.append(current)
                current = [block]
            else:
                current = proposed
        if current:
            groups.append(current)
    return groups


def _merge_small_groups(
    body: str, groups: list[list[_Block]], min_tokens: int, max_tokens: int
) -> list[list[_Block]]:
    merged: list[list[_Block]] = []
    index = 0
    while index < len(groups):
        current = list(groups[index])
        index += 1
        while index < len(groups) and _approx_tokens(_span_text(body, current)) < min_tokens:
            proposed = [*current, *groups[index]]
            if _approx_tokens(_span_text(body, proposed)) > max_tokens:
                break
            current = proposed
            index += 1
        if (
            merged
            and _approx_tokens(_span_text(body, current)) < min_tokens
            and _approx_tokens(_span_text(body, [*merged[-1], *current])) <= max_tokens
        ):
            merged[-1].extend(current)
        else:
            merged.append(current)
    return merged


def semantic_chunks(
    post: BlogPost,
    split: Split,
    *,
    min_tokens: int = 250,
    max_tokens: int = 700,
) -> list[SemanticChunk]:
    """Split a post at headings and paragraph boundaries into exact target spans."""
    if min_tokens < 1 or max_tokens < min_tokens:
        raise ChunkBuildError("chunk token bounds must satisfy 1 <= min_tokens <= max_tokens")
    blocks = _blocks(post.body_markdown)
    if not blocks:
        raise ChunkBuildError(f"post {post.id!r} has no non-whitespace Markdown blocks")
    groups = _split_large_sections(post.body_markdown, _section_groups(blocks), max_tokens)
    groups = _merge_small_groups(post.body_markdown, groups, min_tokens, max_tokens)

    chunks: list[SemanticChunk] = []
    for ordinal, group in enumerate(groups, start=1):
        target = _span_text(post.body_markdown, group)
        token_count = _approx_tokens(target)
        chunks.append(
            SemanticChunk(
                id=f"{post.id}--{ordinal:03d}",
                post_id=post.id,
                lineage_id=post.lineage_id,
                split=split,
                ordinal=ordinal,
                headings=tuple(block.heading for block in group if block.heading is not None),
                target=target,
                source_start=group[0].start,
                source_end=group[-1].end,
                word_count=_word_count(target),
                approx_token_count=token_count,
                target_sha256=_sha256_text(target),
                exceeds_target_size=token_count > max_tokens,
            )
        )
    return chunks


FULL_POST_SUFFIX = "--full"


def full_post_chunks(
    posts: list[BlogPost],
    splits: dict[str, Split],
    kept_chunks: list[SemanticChunk],
    *,
    max_tokens: int,
) -> list[SemanticChunk]:
    """One post-scale target per training post: the contiguous prefix of kept sections.

    Test cases are whole posts, so training needs whole-post targets too. The span runs
    from the start of the post to the end of the last default chunk that survived the
    exclusions, which drops trailing promotional footers while keeping the target an exact
    contiguous span of the published Markdown.
    """
    last_end: dict[str, int] = {}
    for chunk in kept_chunks:
        if chunk.id.endswith(FULL_POST_SUFFIX):
            continue
        last_end[chunk.post_id] = max(last_end.get(chunk.post_id, 0), chunk.source_end)
    full: list[SemanticChunk] = []
    for post in posts:
        split = splits[post.lineage_id]
        if split is not Split.TRAIN or post.id not in last_end:
            continue
        target = post.body_markdown[: last_end[post.id]]
        blocks = _blocks(target)
        token_count = _approx_tokens(target)
        ordinal = max(chunk.ordinal for chunk in kept_chunks if chunk.post_id == post.id) + 1
        full.append(
            SemanticChunk(
                id=f"{post.id}{FULL_POST_SUFFIX}",
                post_id=post.id,
                lineage_id=post.lineage_id,
                split=split,
                ordinal=ordinal,
                headings=tuple(block.heading for block in blocks if block.heading is not None),
                target=target,
                source_start=0,
                source_end=last_end[post.id],
                word_count=_word_count(target),
                approx_token_count=token_count,
                target_sha256=_sha256_text(target),
                exceeds_target_size=token_count > max_tokens,
            )
        )
    return full


_HEADING_RUN = re.compile(r"^#{1,6}(?=[ \t])", re.MULTILINE)


def _flatten_headings(text: str) -> str:
    return _HEADING_RUN.sub("#", text)


def preserve_review_status(
    chunks: list[SemanticChunk],
    previous: list[SemanticChunk],
    *,
    equivalent: Callable[[str, str], bool] | None = None,
) -> list[SemanticChunk]:
    """Carry an existing approval forward when the target is unchanged.

    ``equivalent(earlier_target, new_target)`` may widen "unchanged" to targets that differ
    only by a configured normalization (quotes, italics, heading level), so a formatting pass
    does not throw away every approval.
    """
    previous_by_id = {chunk.id: chunk for chunk in previous}
    preserved: list[SemanticChunk] = []
    for chunk in chunks:
        earlier = previous_by_id.get(chunk.id)
        if (
            earlier is not None
            and earlier.review_status is not chunk.review_status
            and chunk.review_status is ReviewStatus.CANDIDATE
            and (
                earlier.target_sha256 == chunk.target_sha256
                or (equivalent is not None and equivalent(earlier.target, chunk.target))
            )
        ):
            chunk = chunk.model_copy(update={"review_status": earlier.review_status})
        preserved.append(chunk)
    return preserved


def _supplemental_chunks(
    specs: list[SupplementalChunkSpec],
    posts: list[BlogPost],
    splits: dict[str, Split],
    base_chunks: list[SemanticChunk],
    *,
    max_tokens: int,
    normalize: Callable[[str], str] | None = None,
) -> list[SemanticChunk]:
    """Reviewed exact spans; ``normalize`` maps spans authored against the raw import onto the
    normalized post text so a formatting pass does not orphan them."""
    if normalize is not None:
        specs = [spec.model_copy(update={"target": normalize(spec.target)}) for spec in specs]
    spec_counts = Counter(spec.id for spec in specs)
    duplicate_specs = sorted(spec_id for spec_id, count in spec_counts.items() if count > 1)
    if duplicate_specs:
        raise ChunkBuildError(f"duplicate supplemental target ID(s): {', '.join(duplicate_specs)}")

    posts_by_id = {post.id: post for post in posts}
    if len(posts_by_id) != len(posts):
        raise ChunkBuildError("canonical post file contains duplicate post IDs")
    existing_ids = {chunk.id for chunk in base_chunks}
    collisions = sorted(existing_ids.intersection(spec_counts))
    if collisions:
        raise ChunkBuildError(
            f"supplemental target ID(s) collide with semantic chunks: {', '.join(collisions)}"
        )

    next_ordinal: dict[str, int] = {}
    for chunk in base_chunks:
        next_ordinal[chunk.post_id] = max(next_ordinal.get(chunk.post_id, 0), chunk.ordinal)

    supplemental: list[SemanticChunk] = []
    for spec in specs:
        post = posts_by_id.get(spec.post_id)
        if post is None:
            raise ChunkBuildError(
                f"supplemental target {spec.id!r} references missing post {spec.post_id!r}"
            )
        split = splits[post.lineage_id]
        if split is not Split.TRAIN:
            raise ChunkBuildError(
                f"supplemental target {spec.id!r} must belong to a training lineage"
            )
        occurrence_count = post.body_markdown.count(spec.target)
        if occurrence_count != 1:
            raise ChunkBuildError(
                f"supplemental target {spec.id!r} must occur exactly once in its post; "
                f"found {occurrence_count} occurrences"
            )
        source_start = post.body_markdown.index(spec.target)
        source_end = source_start + len(spec.target)
        ordinal = next_ordinal.get(post.id, 0) + 1
        next_ordinal[post.id] = ordinal
        target_blocks = _blocks(spec.target)
        token_count = _approx_tokens(spec.target)
        supplemental.append(
            SemanticChunk(
                id=spec.id,
                post_id=post.id,
                lineage_id=post.lineage_id,
                split=split,
                ordinal=ordinal,
                headings=tuple(
                    block.heading for block in target_blocks if block.heading is not None
                ),
                target=spec.target,
                source_start=source_start,
                source_end=source_end,
                word_count=_word_count(spec.target),
                approx_token_count=token_count,
                target_sha256=_sha256_text(spec.target),
                exceeds_target_size=token_count > max_tokens,
                review_status=spec.review_status,
            )
        )
    return supplemental


def _apply_exclusions(
    chunks: list[SemanticChunk], exclusions: list[ChunkExclusionSpec]
) -> list[SemanticChunk]:
    exclusion_counts = Counter(exclusion.chunk_id for exclusion in exclusions)
    duplicates = sorted(chunk_id for chunk_id, count in exclusion_counts.items() if count > 1)
    if duplicates:
        raise ChunkBuildError(f"duplicate chunk exclusion(s): {', '.join(duplicates)}")
    chunks_by_id = {chunk.id: chunk for chunk in chunks}
    missing = sorted(set(exclusion_counts) - set(chunks_by_id))
    if missing:
        raise ChunkBuildError(f"chunk exclusion(s) do not exist: {', '.join(missing)}")
    heldout = sorted(
        chunk_id for chunk_id in exclusion_counts if chunks_by_id[chunk_id].split is not Split.TRAIN
    )
    if heldout:
        raise ChunkBuildError(
            f"chunk exclusion(s) must belong to training lineages: {', '.join(heldout)}"
        )
    return [chunk for chunk in chunks if chunk.id not in exclusion_counts]


def _split_map(posts: list[BlogPost], assignments: list[SplitAssignment]) -> dict[str, Split]:
    counts = Counter(assignment.lineage_id for assignment in assignments)
    duplicates = sorted(lineage_id for lineage_id, count in counts.items() if count > 1)
    if duplicates:
        raise ChunkBuildError(f"duplicate split assignment(s): {', '.join(duplicates)}")

    post_lineages = {post.lineage_id for post in posts}
    assigned_lineages = set(counts)
    missing = sorted(post_lineages - assigned_lineages)
    unexpected = sorted(assigned_lineages - post_lineages)
    if missing:
        raise ChunkBuildError(f"missing split assignment(s): {', '.join(missing)}")
    if unexpected:
        raise ChunkBuildError(f"split assignment(s) without a post: {', '.join(unexpected)}")

    splits = {assignment.lineage_id: assignment.split for assignment in assignments}
    absent_splits = [split.value for split in Split if split not in set(splits.values())]
    if absent_splits:
        raise ChunkBuildError(f"frozen manifest has no {', '.join(absent_splits)} lineage")
    return splits


def _markdown_fence(target: str) -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", target)), default=0)
    return "`" * max(3, longest + 1)


def render_review(posts: list[BlogPost], chunks: list[SemanticChunk]) -> bytes:
    chunks_by_post: dict[str, list[SemanticChunk]] = {}
    for chunk in chunks:
        chunks_by_post.setdefault(chunk.post_id, []).append(chunk)

    split_counts = Counter(chunk.split.value for chunk in chunks)
    lines = [
        "# Semantic chunk review",
        "",
        "Every target is an exact contiguous span of the imported published post. Default chunks",
        "begin as candidates; reviewed supplemental spans retain their checked-in status, and",
        "approvals of unchanged targets are preserved across rebuilds. `--full` chunks are the",
        "post-scale prefix of each training post up to its last kept section. A target becomes an",
        "SFT example only after both its chunk and a matching prompt are approved.",
        "",
        f"- Posts: {len(posts)}",
        f"- Chunks: {len(chunks)}",
        "- Splits: " + ", ".join(f"{key}={split_counts[key]}" for key in sorted(split_counts)),
        "",
    ]
    for post in posts:
        post_chunks = chunks_by_post.get(post.id, [])
        lines.extend([f"## {post.title}", ""])
        for chunk in post_chunks:
            headings = " / ".join(chunk.headings) if chunk.headings else "(intro or continuation)"
            size_note = " - exceeds target size" if chunk.exceeds_target_size else ""
            fence = _markdown_fence(chunk.target)
            lines.extend(
                [
                    f"### {chunk.id}",
                    "",
                    f"`{chunk.split.value}` - `{chunk.review_status.value}` - "
                    f"{chunk.approx_token_count} approximate tokens - "
                    f"{chunk.word_count} words{size_note}",
                    "",
                    f"Headings: {headings}",
                    "",
                    f"{fence}markdown",
                    chunk.target,
                    fence,
                    "",
                ]
            )
    return ("\n".join(lines).rstrip() + "\n").encode()


def build_chunks(
    posts_path: Path,
    splits_path: Path,
    output_path: Path,
    review_output_path: Path,
    *,
    min_tokens: int = 250,
    max_tokens: int = 700,
    supplemental_targets_path: Path | None = None,
    exclusions_path: Path | None = None,
    full_posts: bool = False,
    preserve_status: bool = True,
    normalization_path: Path | None = None,
) -> dict[str, int]:
    posts = load_jsonl(posts_path, BlogPost)
    assignments = load_jsonl(splits_path, SplitAssignment)
    splits = _split_map(posts, assignments)
    previous = (
        load_jsonl(output_path, SemanticChunk) if preserve_status and output_path.is_file() else []
    )
    equivalent: Callable[[str, str], bool] | None = None
    normalize_span: Callable[[str], str] | None = None
    if normalization_path is not None:
        from goodprose.normalize import load_normalization_config, normalize_markdown

        config = load_normalization_config(normalization_path)

        def _normalize_span(text: str) -> str:
            return normalize_markdown(text, config, strict_substitutions=False)[0]

        def _normalized_equivalent(earlier: str, current: str) -> bool:
            # Heading levels are compared loosely: the post-level shift that produced the new
            # target is not recoverable from a single chunk, and a changed level is exactly the
            # kind of difference a formatting pass is allowed to introduce.
            return _flatten_headings(_normalize_span(earlier)) == _flatten_headings(current)

        equivalent = _normalized_equivalent
        normalize_span = _normalize_span

    chunks = [
        chunk
        for post in posts
        for chunk in semantic_chunks(
            post,
            splits[post.lineage_id],
            min_tokens=min_tokens,
            max_tokens=max_tokens,
        )
    ]
    if exclusions_path is not None:
        chunks = _apply_exclusions(
            chunks,
            load_jsonl(exclusions_path, ChunkExclusionSpec),
        )
    if full_posts:
        chunks.extend(full_post_chunks(posts, splits, chunks, max_tokens=max_tokens))
    if supplemental_targets_path is not None:
        specs = load_jsonl(supplemental_targets_path, SupplementalChunkSpec)
        chunks.extend(
            _supplemental_chunks(
                specs,
                posts,
                splits,
                chunks,
                max_tokens=max_tokens,
                normalize=normalize_span,
            )
        )
    chunks = preserve_review_status(chunks, previous, equivalent=equivalent)
    atomic_write(output_path, serialize_jsonl(chunks))
    atomic_write(review_output_path, render_review(posts, chunks))
    return dict(sorted(Counter(chunk.split.value for chunk in chunks).items()))
