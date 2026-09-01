from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from goodprose.chunks import ChunkBuildError, build_chunks, semantic_chunks
from goodprose.jsonl import load_jsonl, serialize_jsonl
from goodprose.models import BlogPost, SemanticChunk, Split, SplitAssignment


def _post(post_id: str, body: str, *, lineage_id: str | None = None) -> BlogPost:
    return BlogPost(
        id=post_id,
        lineage_id=lineage_id or post_id,
        title=post_id,
        body_markdown=body,
        source_path=f"{post_id}.md",
    )


def test_semantic_chunks_are_exact_non_overlapping_post_spans() -> None:
    body = (
        "Opening paragraph with a compact introduction.\n\n"
        "# First idea\n\n"
        + "A first section sentence. " * 35
        + "\n\n# Second idea\n\n"
        + "A second section sentence. " * 35
    )

    chunks = semantic_chunks(_post("post", body), Split.TRAIN, min_tokens=30, max_tokens=90)

    assert len(chunks) >= 2
    cursor = 0
    for ordinal, chunk in enumerate(chunks, start=1):
        assert chunk.ordinal == ordinal
        assert chunk.target == body[chunk.source_start : chunk.source_end]
        assert body[cursor : chunk.source_start].strip() == ""
        assert chunk.source_start >= cursor
        cursor = chunk.source_end
    assert body[cursor:].strip() == ""
    assert [heading for chunk in chunks for heading in chunk.headings] == [
        "First idea",
        "Second idea",
    ]


def test_build_chunks_requires_one_assignment_per_lineage(tmp_path: Path) -> None:
    posts_path = tmp_path / "posts.jsonl"
    posts_path.write_bytes(
        serialize_jsonl([_post("one", "First post."), _post("two", "Second post.")])
    )
    splits_path = tmp_path / "splits.jsonl"
    splits_path.write_bytes(
        serialize_jsonl(
            [
                SplitAssignment(
                    lineage_id="one",
                    split=Split.TRAIN,
                    frozen_at=date(2026, 9, 1),
                    rationale="Training lineage.",
                )
            ]
        )
    )

    with pytest.raises(ChunkBuildError, match="missing split assignment"):
        build_chunks(
            posts_path,
            splits_path,
            tmp_path / "chunks.jsonl",
            tmp_path / "review.md",
        )


def test_build_chunks_writes_candidates_and_review(tmp_path: Path) -> None:
    posts = [
        _post("train", "Training post."),
        _post("dev", "Development post."),
        _post("test", "Test post."),
    ]
    assignments = [
        SplitAssignment(
            lineage_id=post.id,
            split=split,
            frozen_at=date(2026, 9, 1),
            rationale=f"Frozen {split.value} lineage.",
        )
        for post, split in zip(posts, (Split.TRAIN, Split.DEV, Split.TEST), strict=True)
    ]
    posts_path = tmp_path / "posts.jsonl"
    posts_path.write_bytes(serialize_jsonl(posts))
    splits_path = tmp_path / "splits.jsonl"
    splits_path.write_bytes(serialize_jsonl(assignments))
    output_path = tmp_path / "chunks.jsonl"
    review_path = tmp_path / "review.md"

    counts = build_chunks(posts_path, splits_path, output_path, review_path)

    assert counts == {"dev": 1, "test": 1, "train": 1}
    chunks = load_jsonl(output_path, SemanticChunk)
    assert all(chunk.target in posts[index].body_markdown for index, chunk in enumerate(chunks))
    assert "Every target is an exact contiguous span" in review_path.read_text()
