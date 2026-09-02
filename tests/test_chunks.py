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


def _three_posts(tmp_path: Path, train_body: str) -> tuple[Path, Path]:
    posts = [
        _post("train", train_body),
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
    posts_path.write_bytes(serialize_jsonl(posts))
    splits_path.write_bytes(serialize_jsonl(assignments))
    return posts_path, splits_path


def test_full_post_chunk_is_prefix_up_to_last_kept_section(tmp_path: Path) -> None:
    body = (
        "Opening paragraph. " * 20
        + "\n\n# Idea\n\n"
        + "Idea sentence. " * 40
        + "\n\n# Hiring\n\nWe're hiring, come join us."
    )
    posts_path, splits_path = _three_posts(tmp_path, body)
    output_path = tmp_path / "chunks.jsonl"
    chunks = build_chunks(
        posts_path, splits_path, output_path, tmp_path / "review.md", min_tokens=30, max_tokens=90
    )
    assert chunks["train"] >= 3
    default = [
        chunk for chunk in load_jsonl(output_path, SemanticChunk) if chunk.post_id == "train"
    ]
    footer = default[-1]
    assert "hiring" in footer.target
    exclusions_path = tmp_path / "exclusions.jsonl"
    exclusions_path.write_bytes(
        serialize_jsonl([ChunkExclusionSpec(chunk_id=footer.id, reason="Hiring footer.")])
    )

    build_chunks(
        posts_path,
        splits_path,
        output_path,
        tmp_path / "review.md",
        min_tokens=30,
        max_tokens=90,
        exclusions_path=exclusions_path,
        full_posts=True,
    )

    chunks = load_jsonl(output_path, SemanticChunk)
    full = next(chunk for chunk in chunks if chunk.id == "train--full")
    assert full.split is Split.TRAIN
    assert full.source_start == 0
    assert full.target == body[: full.source_end]
    assert "hiring" not in full.target
    assert full.target.rstrip().endswith("Idea sentence.")
    assert full.headings == ("Idea",)
    assert full.exceeds_target_size is True
    assert not any(
        chunk.id.endswith("--full") for chunk in chunks if chunk.split is not Split.TRAIN
    )
    assert "`--full` chunks" in (tmp_path / "review.md").read_text()


def test_rebuild_preserves_approval_when_target_is_unchanged(tmp_path: Path) -> None:
    posts_path, splits_path = _three_posts(tmp_path, "Training post that stays the same.")
    output_path = tmp_path / "chunks.jsonl"
    build_chunks(posts_path, splits_path, output_path, tmp_path / "review.md")
    chunks = load_jsonl(output_path, SemanticChunk)
    approved = [
        chunk.model_copy(update={"review_status": ReviewStatus.APPROVED})
        if chunk.post_id == "train"
        else chunk
        for chunk in chunks
    ]
    output_path.write_bytes(serialize_jsonl(approved))

    build_chunks(posts_path, splits_path, output_path, tmp_path / "review.md", full_posts=True)
    rebuilt = {chunk.id: chunk for chunk in load_jsonl(output_path, SemanticChunk)}
    assert rebuilt["train--001"].review_status is ReviewStatus.APPROVED
    assert rebuilt["train--full"].review_status is ReviewStatus.CANDIDATE
    assert rebuilt["dev--001"].review_status is ReviewStatus.CANDIDATE

    build_chunks(
        posts_path, splits_path, output_path, tmp_path / "review.md", preserve_status=False
    )
    assert all(
        chunk.review_status is ReviewStatus.CANDIDATE
        for chunk in load_jsonl(output_path, SemanticChunk)
    )


def test_intro_ending_with_colon_stays_with_its_list() -> None:
    body = (
        "Opening paragraph that runs long enough to be its own group. " * 6
        + "\n\nWe learned three things:\n\n- first\n- second\n- third\n\n"
        + "# Next\n\n"
        + "Another section. " * 30
    )

    chunks = semantic_chunks(_post("post", body), Split.TRAIN, min_tokens=20, max_tokens=60)

    for chunk in chunks:
        assert not chunk.target.rstrip().endswith(":"), chunk.target
    intro = next(chunk for chunk in chunks if "three things:" in chunk.target)
    assert "- third" in intro.target


def test_rebuild_keeps_approval_when_only_normalization_changed(tmp_path: Path) -> None:
    curly = "It\u2019s a \u201cquoted\u201d training post with _italics_."
    straight = 'It\'s a "quoted" training post with *italics*.'
    posts_path, splits_path = _three_posts(tmp_path, curly)
    output_path = tmp_path / "chunks.jsonl"
    build_chunks(posts_path, splits_path, output_path, tmp_path / "review.md")
    approved = [
        chunk.model_copy(update={"review_status": ReviewStatus.APPROVED})
        if chunk.post_id == "train"
        else chunk
        for chunk in load_jsonl(output_path, SemanticChunk)
    ]
    output_path.write_bytes(serialize_jsonl(approved))
    # The posts file is normalized (as normalize-posts would do) and chunks are rebuilt.
    posts_path, splits_path = _three_posts(tmp_path, straight)
    config_path = tmp_path / "normalization.json"
    config_path.write_text('{"version": 1}')

    build_chunks(
        posts_path,
        splits_path,
        output_path,
        tmp_path / "review.md",
        normalization_path=config_path,
    )

    rebuilt = {chunk.id: chunk for chunk in load_jsonl(output_path, SemanticChunk)}
    assert rebuilt["train--001"].target == straight
    assert rebuilt["train--001"].review_status is ReviewStatus.APPROVED

    # Without the normalization config the changed hash drops the approval.
    output_path.write_bytes(serialize_jsonl(approved))
    build_chunks(posts_path, splits_path, output_path, tmp_path / "review.md")
    assert {chunk.id: chunk for chunk in load_jsonl(output_path, SemanticChunk)}[
        "train--001"
    ].review_status is ReviewStatus.CANDIDATE
