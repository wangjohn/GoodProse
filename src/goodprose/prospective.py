"""Prospective test cases: real drafts frozen before the author polishes them.

The frozen whole-post cases were reconstructed after the fact, so two of four inputs are near-
final drafts. The truest evaluation is a draft captured the moment writing starts, evaluated
against the post the author eventually publishes. ``capture-draft`` freezes such a draft with a
hash and timestamp under ``data/private/``; ``promote-prospective`` turns captured drafts into
ordinary evaluation cases once their posts exist in the canonical post file. Captured drafts
never enter training.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import Field

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import BlogPost, EvalCase, InputMethod, NonEmptyString, StrictModel
from goodprose.pairs import reuses_title_as_heading
from goodprose.roles import load_training_roles, venue_line_for_post


class ProspectiveError(ValueError):
    """A prospective draft cannot be captured or promoted safely."""


class ProspectiveDraft(StrictModel):
    version: Literal[1] = 1
    id: NonEmptyString
    captured_at: NonEmptyString
    input: NonEmptyString
    input_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    input_method: InputMethod = InputMethod.ORIGINAL_DRAFT
    intended_venue: NonEmptyString = "johnjwang.com"
    post_id: NonEmptyString | None = None
    notes: NonEmptyString | None = None


def capture_draft(
    draft_path: Path,
    drafts_file: Path,
    *,
    draft_id: str,
    input_method: InputMethod = InputMethod.ORIGINAL_DRAFT,
    intended_venue: str = "johnjwang.com",
    notes: str | None = None,
) -> ProspectiveDraft:
    """Freeze one draft file as a prospective case input; refuses to overwrite an existing id."""
    text = draft_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ProspectiveError(f"draft file is empty: {draft_path}")
    if input_method is InputMethod.DERIVED_BRIEF:
        raise ProspectiveError("a prospective draft must be authentic, not a derived brief")
    existing = load_jsonl(drafts_file, ProspectiveDraft) if drafts_file.is_file() else []
    if any(draft.id == draft_id for draft in existing):
        raise ProspectiveError(
            f"prospective draft {draft_id!r} already exists; captured drafts are frozen"
        )
    draft = ProspectiveDraft(
        id=draft_id,
        captured_at=datetime.now(UTC).isoformat(timespec="seconds"),
        input=text,
        input_sha256=hashlib.sha256(text.encode()).hexdigest(),
        input_method=input_method,
        intended_venue=intended_venue,
        notes=notes,
    )
    atomic_write(drafts_file, serialize_jsonl([*existing, draft]))
    return draft


def promote_prospective_cases(
    drafts_file: Path,
    posts_path: Path,
    output_path: Path,
    *,
    roles_path: Path | None = None,
    venue_lines: bool = True,
) -> dict[str, int]:
    """Write evaluation cases for captured drafts whose post is now in the canonical file.

    A draft is matched to its post by ``post_id`` (set it on the draft once the post exists).
    The reference is the published post rendered as the pair builder renders it, with the
    title as a level-one heading. Drafts without a post yet are counted and skipped.
    """
    drafts = load_jsonl(drafts_file, ProspectiveDraft)
    if not drafts:
        raise ProspectiveError("no prospective drafts captured")
    posts = {post.id: post for post in load_jsonl(posts_path, BlogPost)}
    roles = load_training_roles(roles_path)
    cases: list[EvalCase] = []
    pending = 0
    for draft in drafts:
        if hashlib.sha256(draft.input.encode()).hexdigest() != draft.input_sha256:
            raise ProspectiveError(f"prospective draft {draft.id!r} was edited after capture")
        if draft.post_id is None:
            pending += 1
            continue
        post = posts.get(draft.post_id)
        if post is None:
            raise ProspectiveError(
                f"prospective draft {draft.id!r} names post {draft.post_id!r}, which is not in "
                "the canonical post file"
            )
        body = post.body_markdown.strip("\n")
        reference = (
            body if reuses_title_as_heading(body, post.title) else f"# {post.title}\n\n{body}"
        )
        venue = venue_line_for_post(post, roles) if venue_lines else ""
        cases.append(
            EvalCase(
                id=f"prospective-{draft.id}",
                lineage_id=post.lineage_id,
                input=f"{venue}\n\n{draft.input}" if venue else draft.input,
                input_method=draft.input_method,
                reference_output=reference,
                target_sha256=hashlib.sha256(reference.encode()).hexdigest(),
                source_url=post.source_url,
            )
        )
    if not cases:
        raise ProspectiveError("no captured draft has a published post yet; set post_id first")
    atomic_write(output_path, serialize_jsonl(cases))
    return {"cases": len(cases), "pending": pending}
