from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from goodprose.chunks import ChunkBuildError, build_chunks, semantic_chunks
from goodprose.jsonl import load_jsonl, serialize_jsonl
from goodprose.models import (
    BlogPost,
    ChunkExclusionSpec,
    ReviewStatus,
    SemanticChunk,
    Split,
    SplitAssignment,
    SupplementalChunkSpec,
)


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


def test_build_chunks_adds_reviewed_exact_supplemental_training_spans(tmp_path: Path) -> None:
    posts = [
        _post("train", "Opening sentence. Second exact sentence."),
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
    splits_path = tmp_path / "splits.jsonl"
    supplemental_path = tmp_path / "supplemental.jsonl"
    exclusions_path = tmp_path / "exclusions.jsonl"
    output_path = tmp_path / "chunks.jsonl"
    atomic_spec = SupplementalChunkSpec(
        id="train--sentence-001",
        post_id="train",
        target="Second exact sentence.",
        review_status=ReviewStatus.APPROVED,
    )
    posts_path.write_bytes(serialize_jsonl(posts))
    splits_path.write_bytes(serialize_jsonl(assignments))
    supplemental_path.write_bytes(serialize_jsonl([atomic_spec]))
    exclusions_path.write_bytes(
        serialize_jsonl(
            [
                ChunkExclusionSpec(
                    chunk_id="train--001",
                    reason="Replace the default span with the sentence target.",
                )
            ]
        )
    )

    counts = build_chunks(
        posts_path,
        splits_path,
        output_path,
        tmp_path / "review.md",
        supplemental_targets_path=supplemental_path,
        exclusions_path=exclusions_path,
    )

    assert counts == {"dev": 1, "test": 1, "train": 1}
    supplemental = next(
        chunk for chunk in load_jsonl(output_path, SemanticChunk) if chunk.id == atomic_spec.id
    )
    assert supplemental.target == atomic_spec.target
    assert supplemental.review_status is ReviewStatus.APPROVED
    assert (
        posts[0].body_markdown[supplemental.source_start : supplemental.source_end]
        == atomic_spec.target
    )


def test_build_chunks_rejects_supplemental_heldout_target(tmp_path: Path) -> None:
    posts = [
        _post("train", "Training post."),
        _post("dev", "Development post."),
        _post("test", "Frozen sentence."),
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
    splits_path = tmp_path / "splits.jsonl"
    supplemental_path = tmp_path / "supplemental.jsonl"
    posts_path.write_bytes(serialize_jsonl(posts))
    splits_path.write_bytes(serialize_jsonl(assignments))
    supplemental_path.write_bytes(
        serialize_jsonl(
            [
                SupplementalChunkSpec(
                    id="test--sentence-001",
                    post_id="test",
                    target="Frozen sentence.",
                )
            ]
        )
    )

    with pytest.raises(ChunkBuildError, match="must belong to a training lineage"):
        build_chunks(
            posts_path,
            splits_path,
            tmp_path / "chunks.jsonl",
            tmp_path / "review.md",
            supplemental_targets_path=supplemental_path,
        )
