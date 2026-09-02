from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from goodprose.chunks import build_chunks
from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import (
    BlogPost,
    EvalCase,
    InputMethod,
    ReviewStatus,
    Split,
    SplitAssignment,
)
from goodprose.shortcases import (
    ShortCaseCandidate,
    ShortCaseError,
    align_window,
    build_short_case_candidates,
    promote_short_cases,
)

INTRO = "We wanted a faster way to review pull requests. " * 12
IDEA = "The trick is to let the reviewer see the diff first and the discussion second. " * 10
CLOSE = "So we shipped it, and review time dropped by half. " * 10
POST = f"{INTRO.strip()}\n\n# The idea\n\n{IDEA.strip()}\n\n# What happened\n\n{CLOSE.strip()}"
DRAFT = (
    "blog post about the review tool\n\n"
    + "we wanted a faster way to review pull requests, mostly because waiting was painful. " * 6
    + "\n\n"
    + "trick: let the reviewer see the diff first and the discussion second. " * 6
    + "\n\nrandom unrelated paragraph about lunch.\n\n"
    + "shipped it, review time dropped by half. " * 6
)


def test_align_window_finds_the_matching_paragraphs() -> None:
    paragraphs = [part for part in DRAFT.split("\n\n") if part.strip()]

    start, end, recall, precision = align_window(paragraphs, IDEA, max_paragraphs=3)

    assert (start, end) == (2, 3)
    assert recall > 0.6
    assert precision > 0.6


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    posts = [
        BlogPost(
            id="test",
            lineage_id="test",
            title="Review tool",
            body_markdown=POST,
            source_path="t.md",
        ),
        BlogPost(
            id="train",
            lineage_id="train",
            title="Train",
            body_markdown="Train post.",
            source_path="a.md",
        ),
        BlogPost(
            id="dev", lineage_id="dev", title="Dev", body_markdown="Dev post.", source_path="d.md"
        ),
    ]
    splits = [
        SplitAssignment(
            lineage_id="test", split=Split.TEST, frozen_at=date(2026, 9, 1), rationale="t"
        ),
        SplitAssignment(
            lineage_id="train", split=Split.TRAIN, frozen_at=date(2026, 9, 1), rationale="a"
        ),
        SplitAssignment(
            lineage_id="dev", split=Split.DEV, frozen_at=date(2026, 9, 1), rationale="d"
        ),
    ]
    posts_path = tmp_path / "posts.jsonl"
    splits_path = tmp_path / "splits.jsonl"
    chunks_path = tmp_path / "chunks.jsonl"
    atomic_write(posts_path, serialize_jsonl(posts))
    atomic_write(splits_path, serialize_jsonl(splits))
    build_chunks(
        posts_path, splits_path, chunks_path, tmp_path / "r.md", min_tokens=40, max_tokens=200
    )
    reference = f"# Review tool\n\n{POST}"
    cases_path = tmp_path / "cases.jsonl"
    atomic_write(
        cases_path,
        serialize_jsonl(
            [
                EvalCase(
                    id="test",
                    lineage_id="test",
                    input=DRAFT,
                    input_method=InputMethod.ORIGINAL_DRAFT,
                    reference_output=reference,
                    target_sha256=hashlib.sha256(reference.encode()).hexdigest(),
                )
            ]
        ),
    )
    return cases_path, chunks_path, posts_path


def test_build_and_promote_short_cases(tmp_path: Path) -> None:
    cases_path, chunks_path, posts_path = _fixture(tmp_path)
    output_path = tmp_path / "short.candidates.jsonl"
    review_path = tmp_path / "SHORT.md"

    counts = build_short_case_candidates(
        cases_path, chunks_path, posts_path, output_path, review_path, min_words=20, max_words=400
    )

    assert counts["candidates"] >= 2
    candidates = load_jsonl(output_path, ShortCaseCandidate)
    idea = next(c for c in candidates if "The idea" in c.reference_output)
    assert "diff first" in idea.input
    assert "lunch" not in idea.input
    assert idea.input.startswith("Turn these notes into one section")
    assert "Blog post: Review tool" in idea.input
    assert idea.alignment_recall > 0.6
    assert "Short review case candidates" in review_path.read_text()

    with pytest.raises(ShortCaseError, match="no short case candidates are approved"):
        promote_short_cases(output_path, tmp_path / "short.jsonl")

    edited = [
        c.model_copy(
            update={"review_status": ReviewStatus.APPROVED, "input": c.input + "\n\nkeep it tight"}
        )
        if c.id == idea.id
        else c
        for c in candidates
    ]
    atomic_write(output_path, serialize_jsonl(edited))

    # A rebuild keeps the author's edit and decision for an unchanged section.
    build_short_case_candidates(
        cases_path, chunks_path, posts_path, output_path, review_path, min_words=20, max_words=400
    )
    kept = next(c for c in load_jsonl(output_path, ShortCaseCandidate) if c.id == idea.id)
    assert kept.review_status is ReviewStatus.APPROVED
    assert kept.input.endswith("keep it tight")

    promoted = promote_short_cases(output_path, tmp_path / "short.jsonl")
    assert promoted == 1
    [case] = load_jsonl(tmp_path / "short.jsonl", EvalCase)
    assert case.id == idea.id
    assert case.lineage_id == "test"
    assert case.reference_output == idea.reference_output
    assert json.loads((tmp_path / "short.jsonl").read_text())["input_method"] == "original_draft"


def test_promote_rejects_input_that_contains_the_reference(tmp_path: Path) -> None:
    cases_path, chunks_path, posts_path = _fixture(tmp_path)
    output_path = tmp_path / "short.candidates.jsonl"
    build_short_case_candidates(
        cases_path,
        chunks_path,
        posts_path,
        output_path,
        tmp_path / "r.md",
        min_words=20,
        max_words=400,
    )
    candidates = load_jsonl(output_path, ShortCaseCandidate)
    leaked = [
        c.model_copy(update={"review_status": ReviewStatus.APPROVED, "input": c.reference_output})
        for c in candidates[:1]
    ]
    atomic_write(output_path, serialize_jsonl(leaked))

    with pytest.raises(ShortCaseError, match="contains the reference section verbatim"):
        promote_short_cases(output_path, tmp_path / "short.jsonl")
