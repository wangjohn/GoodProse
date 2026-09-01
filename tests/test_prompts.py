from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import pytest
from pydantic import AnyUrl

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import (
    BlogPost,
    InputMethod,
    PromptForm,
    ReviewStatus,
    SemanticChunk,
    Split,
    SyntheticPromptCandidate,
    SyntheticPromptDraft,
    WritingPair,
)
from goodprose.prompts import (
    PromptReviewError,
    approve_prompt_candidates,
    build_prompt_candidates,
    build_prompt_pairs,
    render_prompt_review,
)


def _chunk(*, split: Split = Split.TRAIN) -> SemanticChunk:
    target = "# Finished section\n\nThis is the author's exact finished prose."
    return SemanticChunk(
        id="post--001",
        post_id="post",
        lineage_id="post",
        split=split,
        ordinal=1,
        headings=("Finished section",),
        target=target,
        source_start=0,
        source_end=len(target),
        word_count=9,
        approx_token_count=16,
        target_sha256=hashlib.sha256(target.encode()).hexdigest(),
    )


def _candidate(chunk: SemanticChunk) -> SyntheticPromptCandidate:
    return SyntheticPromptCandidate(
        id="post--001--synthetic",
        chunk_id=chunk.id,
        post_id=chunk.post_id,
        lineage_id=chunk.lineage_id,
        split=chunk.split,
        prompt_form=PromptForm.BULLET_NOTES,
        input="Turn these notes into a section:\n- exact prose matters\n- keep it concise",
        target_sha256=chunk.target_sha256,
    )


def test_render_prompt_review_pairs_candidate_with_exact_completion() -> None:
    chunk = _chunk()

    review = render_prompt_review([_candidate(chunk)], [chunk]).decode()

    assert "No development or test target" in review
    assert "bullet_notes=1" in review
    assert chunk.target in review


def test_prompt_review_rejects_held_out_targets() -> None:
    chunk = _chunk(split=Split.TEST)

    with pytest.raises(PromptReviewError, match="must reference a training chunk"):
        render_prompt_review([_candidate(chunk)], [chunk])


def test_prompt_review_rejects_stale_target_hash() -> None:
    chunk = _chunk()
    candidate = _candidate(chunk).model_copy(update={"target_sha256": "0" * 64})

    with pytest.raises(PromptReviewError, match="does not match chunk metadata"):
        render_prompt_review([candidate], [chunk])


def test_prompt_review_excludes_required_source_urls_from_leakage_measure() -> None:
    chunk = _chunk().model_copy(
        update={
            "target": "Read [this](https://example.com/a/long/source/path) before writing.",
        }
    )
    candidate = _candidate(chunk).model_copy(
        update={"input": "Source: https://example.com/a/long/source/path"}
    )

    review = render_prompt_review([candidate], [chunk]).decode()

    assert "Longest exact shared word run (URLs excluded): 0" in review


def test_prompt_review_requires_target_source_urls_in_input() -> None:
    chunk = _chunk().model_copy(
        update={"target": "Read [this](https://example.com/source) before writing."}
    )

    with pytest.raises(PromptReviewError, match="missing target source URL"):
        render_prompt_review([_candidate(chunk)], [chunk])


def test_prompt_review_normalizes_markdown_and_sentence_url_punctuation() -> None:
    chunk = _chunk().model_copy(
        update={"target": "Read [this](https://example.com/source) before writing."}
    )
    candidate = _candidate(chunk).model_copy(
        update={"input": "Use this source: https://example.com/source."}
    )

    render_prompt_review([candidate], [chunk])


def test_build_prompt_candidates_attaches_frozen_chunk_metadata(tmp_path: Path) -> None:
    chunk = _chunk()
    chunks_path = tmp_path / "chunks.jsonl"
    drafts_path = tmp_path / "drafts.jsonl"
    output_path = tmp_path / "prompts.jsonl"
    atomic_write(chunks_path, serialize_jsonl([chunk]))
    atomic_write(
        drafts_path,
        serialize_jsonl(
            [
                SyntheticPromptDraft(
                    chunk_id=chunk.id,
                    prompt_form=PromptForm.ROUGH_SENTENCES,
                    input="Please turn this rough thought into a finished section.",
                )
            ]
        ),
    )

    assert build_prompt_candidates(drafts_path, chunks_path, output_path) == 1
    candidate = load_jsonl(output_path, SyntheticPromptCandidate)[0]
    assert candidate.post_id == chunk.post_id
    assert candidate.target_sha256 == chunk.target_sha256
    assert candidate.prompt_form is PromptForm.ROUGH_SENTENCES


def test_approve_prompt_candidates_only_approves_referenced_training_chunks(
    tmp_path: Path,
) -> None:
    train_chunk = _chunk()
    test_chunk = _chunk(split=Split.TEST).model_copy(
        update={"id": "heldout--001", "post_id": "heldout", "lineage_id": "heldout"}
    )
    prompts_path = tmp_path / "prompts.jsonl"
    chunks_path = tmp_path / "chunks.jsonl"
    atomic_write(prompts_path, serialize_jsonl([_candidate(train_chunk)]))
    atomic_write(chunks_path, serialize_jsonl([train_chunk, test_chunk]))

    assert approve_prompt_candidates(
        prompts_path,
        chunks_path,
        reviewer_note="Approved by the author.",
    ) == {"prompts": 1, "chunks": 1}
    prompt = load_jsonl(prompts_path, SyntheticPromptCandidate)[0]
    chunks = {chunk.id: chunk for chunk in load_jsonl(chunks_path, SemanticChunk)}
    assert prompt.review_status is ReviewStatus.APPROVED
    assert prompt.reviewer_notes == ("Approved by the author.",)
    assert chunks[train_chunk.id].review_status is ReviewStatus.APPROVED
    assert chunks[test_chunk.id].review_status is ReviewStatus.CANDIDATE


def test_build_prompt_pairs_requires_approval_and_preserves_exact_target(
    tmp_path: Path,
) -> None:
    chunk = _chunk().model_copy(update={"review_status": ReviewStatus.APPROVED})
    candidate = _candidate(chunk).model_copy(update={"review_status": ReviewStatus.APPROVED})
    post = BlogPost(
        id="post",
        lineage_id="post",
        title="Post title",
        body_markdown="Full post body.",
        source_path="post.md",
        source_url=AnyUrl("https://example.com/post"),
        published_at=date(2025, 1, 2),
    )
    prompts_path = tmp_path / "prompts.jsonl"
    chunks_path = tmp_path / "chunks.jsonl"
    posts_path = tmp_path / "posts.jsonl"
    dev_path = tmp_path / "dev.jsonl"
    test_path = tmp_path / "test.jsonl"
    output_path = tmp_path / "pairs.jsonl"
    atomic_write(prompts_path, serialize_jsonl([candidate]))
    atomic_write(chunks_path, serialize_jsonl([chunk]))
    atomic_write(posts_path, serialize_jsonl([post]))
    atomic_write(
        dev_path,
        serialize_jsonl(
            [
                WritingPair(
                    id="heldout-dev",
                    post_id="heldout-dev",
                    lineage_id="heldout-dev",
                    split=Split.DEV,
                    input="Authentic development draft.",
                    input_method=InputMethod.ORIGINAL_DRAFT,
                    title="Development post",
                    output="Published development post.",
                )
            ]
        ),
    )
    atomic_write(
        test_path,
        serialize_jsonl(
            [
                WritingPair(
                    id="heldout-test",
                    post_id="heldout-test",
                    lineage_id="heldout-test",
                    split=Split.TEST,
                    input="Authentic test outline.",
                    input_method=InputMethod.ORIGINAL_OUTLINE,
                    title="Test post",
                    output="Published test post.",
                )
            ]
        ),
    )

    assert build_prompt_pairs(
        prompts_path,
        chunks_path,
        posts_path,
        output_path,
        heldout_pairs_paths=[dev_path, test_path],
    ) == {
        "train": 1,
        "dev": 1,
        "test": 1,
    }
    pair = next(pair for pair in load_jsonl(output_path, WritingPair) if pair.split is Split.TRAIN)
    assert pair.input == candidate.input
    assert pair.output == chunk.target
    assert str(pair.source_url) == "https://example.com/post"


def test_build_prompt_pairs_rejects_unreviewed_candidates(tmp_path: Path) -> None:
    chunk = _chunk()
    prompts_path = tmp_path / "prompts.jsonl"
    chunks_path = tmp_path / "chunks.jsonl"
    posts_path = tmp_path / "posts.jsonl"
    atomic_write(prompts_path, serialize_jsonl([_candidate(chunk)]))
    atomic_write(chunks_path, serialize_jsonl([chunk]))
    atomic_write(
        posts_path,
        serialize_jsonl(
            [
                BlogPost(
                    id="post",
                    lineage_id="post",
                    title="Post title",
                    body_markdown="Full post body.",
                    source_path="post.md",
                )
            ]
        ),
    )

    with pytest.raises(PromptReviewError, match=r"prompt candidate.*not approved"):
        build_prompt_pairs(prompts_path, chunks_path, posts_path, tmp_path / "pairs.jsonl")
