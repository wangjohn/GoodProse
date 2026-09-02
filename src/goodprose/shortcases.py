"""Section-scale review cases cut from the whole-post held-out cases.

Reading two 1,500-word responses per case makes the blind review slow. Each held-out post is
already split into verbatim sections (the test and dev chunks), and each has an authentic
draft. This module aligns every section to the window of draft paragraphs that produced it,
so the reviewer compares two 250-word responses against a 250-word section instead of two
posts. The author approves or rewrites each candidate; approved ones become ordinary
evaluation cases and run through `eval generate`, `eval prepare`, and `eval summarize`
unchanged. The whole-post cases remain the shipping gate.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal

from pydantic import AnyUrl, Field

from goodprose.chunks import _markdown_fence
from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import (
    BlogPost,
    EvalCase,
    InputMethod,
    NonEmptyString,
    ReviewStatus,
    SemanticChunk,
    Split,
    StrictModel,
)
from goodprose.prompts import _PROMOTIONAL_CTA
from goodprose.text import words

DEFAULT_SCOPE_LINE = "Turn these notes into one section of a blog post; return only that section."
_PARAGRAPH = re.compile(r"\n\s*\n")


class ShortCaseError(ValueError):
    """Short review cases cannot be derived safely."""


class ShortCaseCandidate(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    lineage_id: NonEmptyString
    source_case_id: NonEmptyString
    chunk_id: NonEmptyString
    input: NonEmptyString
    draft_window: NonEmptyString
    reference_output: NonEmptyString
    target_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    input_method: InputMethod = InputMethod.ORIGINAL_DRAFT
    alignment_recall: float = Field(ge=0, le=1)
    alignment_precision: float = Field(ge=0, le=1)
    window_paragraphs: tuple[int, int]
    reference_words: int = Field(ge=1)
    window_words: int = Field(ge=0)
    review_status: ReviewStatus = ReviewStatus.CANDIDATE
    notes: str | None = None
    source_url: str | None = None


def _paragraphs(text: str) -> list[str]:
    return [part.strip() for part in _PARAGRAPH.split(text) if part.strip()]


def _matched_words(left: Sequence[str], right: Sequence[str]) -> int:
    matcher = SequenceMatcher(None, list(left), list(right), autojunk=False)
    return sum(block.size for block in matcher.get_matching_blocks())


def align_window(
    draft_paragraphs: list[str],
    target: str,
    *,
    max_paragraphs: int,
) -> tuple[int, int, float, float]:
    """Best contiguous paragraph window for a target: (start, end, recall, precision).

    Recall is the share of target words found, in order, inside the window; precision is
    the share of window words that matched. The window with the best F1 wins, ties going to
    the shorter window.
    """
    target_words = words(target)
    if not target_words or not draft_paragraphs:
        return 0, 0, 0.0, 0.0
    paragraph_words = [words(paragraph) for paragraph in draft_paragraphs]
    best = (0, 1, 0.0, 0.0, -1.0)
    for start in range(len(draft_paragraphs)):
        window: list[str] = []
        for end in range(start + 1, min(start + max_paragraphs, len(draft_paragraphs)) + 1):
            window = window + paragraph_words[end - 1]
            if not window:
                continue
            matched = _matched_words(window, target_words)
            recall = matched / len(target_words)
            precision = matched / len(window)
            f1 = 2 * recall * precision / (recall + precision) if matched else 0.0
            if f1 > best[4] + 1e-9:
                best = (start, end, recall, precision, f1)
    start, end, recall, precision, _ = best
    return start, end, recall, precision


def _held_out_chunks(chunks: list[SemanticChunk], case: EvalCase) -> list[SemanticChunk]:
    return sorted(
        (
            chunk
            for chunk in chunks
            if chunk.lineage_id == case.lineage_id
            and chunk.split in (Split.TEST, Split.DEV)
            and not chunk.id.endswith("--full")
        ),
        key=lambda chunk: chunk.ordinal,
    )


def build_short_case_candidates(
    cases_path: Path,
    chunks_path: Path,
    posts_path: Path,
    output_path: Path,
    review_output_path: Path,
    *,
    min_words: int = 60,
    max_words: int = 450,
    max_paragraphs: int = 8,
    min_recall: float = 0.35,
    scope_line: str = DEFAULT_SCOPE_LINE,
) -> dict[str, int]:
    """Propose one section-scale case per held-out section, with alignment scores."""
    if min_words < 1 or max_words < min_words:
        raise ShortCaseError("word bounds must satisfy 1 <= min_words <= max_words")
    if max_paragraphs < 1:
        raise ShortCaseError("max_paragraphs must be at least 1")
    cases = load_jsonl(cases_path, EvalCase)
    if not cases:
        raise ShortCaseError("case file is empty")
    chunks = load_jsonl(chunks_path, SemanticChunk)
    posts = {post.id: post for post in load_jsonl(posts_path, BlogPost)}
    previous = (
        {candidate.id: candidate for candidate in load_jsonl(output_path, ShortCaseCandidate)}
        if output_path.is_file()
        else {}
    )

    candidates: list[ShortCaseCandidate] = []
    skipped = {"size": 0, "promotional": 0, "not_in_reference": 0}
    for case in cases:
        draft_paragraphs = _paragraphs(case.input)
        for chunk in _held_out_chunks(chunks, case):
            if not (min_words <= chunk.word_count <= max_words):
                skipped["size"] += 1
                continue
            if _PROMOTIONAL_CTA.search(chunk.target):
                skipped["promotional"] += 1
                continue
            if chunk.target not in case.reference_output:
                skipped["not_in_reference"] += 1
                continue
            start, end, recall, precision = align_window(
                draft_paragraphs, chunk.target, max_paragraphs=max_paragraphs
            )
            window = "\n\n".join(draft_paragraphs[start:end])
            notes = None
            if recall < min_recall:
                notes = (
                    f"weak alignment (recall {recall:.2f}); rewrite the input by hand from the "
                    "draft or reject"
                )
            elif recall >= 0.95 and precision >= 0.95:
                notes = (
                    "near-verbatim draft; this is a polish case that tests leaving good prose "
                    "alone, not voice"
                )
            title = posts[chunk.post_id].title if chunk.post_id in posts else case.lineage_id
            candidate = ShortCaseCandidate(
                id=f"{chunk.id}--short",
                lineage_id=case.lineage_id,
                source_case_id=case.id,
                chunk_id=chunk.id,
                input=f"{scope_line}\n\nBlog post: {title}\n\n{window}" if window else scope_line,
                draft_window=window or "(no aligned draft text)",
                reference_output=chunk.target,
                target_sha256=chunk.target_sha256,
                alignment_recall=recall,
                alignment_precision=precision,
                window_paragraphs=(start, end),
                reference_words=chunk.word_count,
                window_words=len(words(window)),
                notes=notes,
                source_url=str(case.source_url) if case.source_url else None,
            )
            earlier = previous.get(candidate.id)
            if earlier is not None and earlier.target_sha256 == candidate.target_sha256:
                # Keep the author's edits and decision when the section is unchanged.
                candidate = earlier
            candidates.append(candidate)
    if not candidates:
        raise ShortCaseError("no held-out sections satisfied the size and reference checks")
    atomic_write(output_path, serialize_jsonl(candidates))
    atomic_write(review_output_path, render_short_case_review(candidates))
    return {
        "candidates": len(candidates),
        "weak_alignment": sum(candidate.alignment_recall < min_recall for candidate in candidates),
        "near_verbatim": sum(
            candidate.alignment_recall >= 0.95 and candidate.alignment_precision >= 0.95
            for candidate in candidates
        ),
        "approved": sum(
            candidate.review_status is ReviewStatus.APPROVED for candidate in candidates
        ),
        **{f"skipped_{key}": value for key, value in skipped.items()},
    }


def render_short_case_review(candidates: list[ShortCaseCandidate]) -> bytes:
    lines = [
        "# Short review case candidates",
        "",
        "Each candidate pairs a window of your authentic draft with the exact published section",
        "it became. Approve the ones whose input is a fair brief for the section (set",
        '`"review_status": "approved"` in the JSONL, editing `input` if needed), reject the rest,',
        "then run `promote-short-cases`. Recall is the share of the section's words found in the",
        "draft window; precision is the share of the window that matched. Low recall means you",
        "wrote most of the section fresh, so the window is a weak brief unless you edit it.",
        "",
        f"Candidates: {len(candidates)}",
        "",
    ]
    for candidate in candidates:
        input_fence = _markdown_fence(candidate.input)
        target_fence = _markdown_fence(candidate.reference_output)
        status = candidate.review_status.value
        note = f"  \nNote: {candidate.notes}" if candidate.notes else ""
        lines.extend(
            [
                f"## {candidate.id}",
                "",
                f"`{status}` - recall {candidate.alignment_recall:.2f} - precision "
                f"{candidate.alignment_precision:.2f} - window {candidate.window_words} words -> "
                f"section {candidate.reference_words} words - draft paragraphs "
                f"{candidate.window_paragraphs[0]}..{candidate.window_paragraphs[1]}{note}",
                "",
                "### Input",
                "",
                f"{input_fence}text",
                candidate.input,
                input_fence,
                "",
                "### Reference section",
                "",
                f"{target_fence}markdown",
                candidate.reference_output,
                target_fence,
                "",
            ]
        )
    return ("\n".join(lines).rstrip() + "\n").encode()


def promote_short_cases(candidates_path: Path, output_path: Path) -> int:
    """Write approved candidates as evaluation cases."""
    candidates = load_jsonl(candidates_path, ShortCaseCandidate)
    approved = [c for c in candidates if c.review_status is ReviewStatus.APPROVED]
    if not approved:
        raise ShortCaseError("no short case candidates are approved")
    cases: list[EvalCase] = []
    seen: set[str] = set()
    for candidate in approved:
        if candidate.id in seen:
            raise ShortCaseError(f"duplicate short case id {candidate.id!r}")
        seen.add(candidate.id)
        digest = hashlib.sha256(candidate.reference_output.encode()).hexdigest()
        if digest != candidate.target_sha256:
            raise ShortCaseError(f"short case {candidate.id!r} has a stale reference hash")
        if candidate.reference_output.strip() in candidate.input:
            raise ShortCaseError(
                f"short case {candidate.id!r} input contains the reference section verbatim"
            )
        cases.append(
            EvalCase(
                id=candidate.id,
                lineage_id=candidate.lineage_id,
                input=candidate.input,
                input_method=candidate.input_method,
                reference_output=candidate.reference_output,
                target_sha256=candidate.target_sha256,
                source_url=AnyUrl(candidate.source_url) if candidate.source_url else None,
            )
        )
    atomic_write(output_path, serialize_jsonl(cases))
    return len(cases)
