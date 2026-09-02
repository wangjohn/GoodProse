from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import AnyUrl

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import BlogPost, EvalCase, InputMethod
from goodprose.prospective import (
    ProspectiveDraft,
    ProspectiveError,
    capture_draft,
    promote_prospective_cases,
)


def test_capture_freezes_a_draft_and_refuses_duplicates(tmp_path: Path) -> None:
    draft_file = tmp_path / "draft.md"
    draft_file.write_text("rough notes about a thing\n\n- point one\n- point two\n")
    drafts = tmp_path / "private" / "drafts.jsonl"

    draft = capture_draft(draft_file, drafts, draft_id="a-thing", notes="started 2 Sep")

    assert draft.input.startswith("rough notes")
    assert len(draft.input_sha256) == 64
    assert draft.intended_venue == "johnjwang.com"
    assert load_jsonl(drafts, ProspectiveDraft) == [draft]
    with pytest.raises(ProspectiveError, match="already exists"):
        capture_draft(draft_file, drafts, draft_id="a-thing")
    with pytest.raises(ProspectiveError, match="must be authentic"):
        capture_draft(draft_file, drafts, draft_id="b", input_method=InputMethod.DERIVED_BRIEF)


def test_promote_matches_captured_drafts_to_published_posts(tmp_path: Path) -> None:
    drafts = tmp_path / "drafts.jsonl"
    posts_path = tmp_path / "posts.jsonl"
    draft_file = tmp_path / "draft.md"
    draft_file.write_text("notes for the post")
    published = capture_draft(draft_file, drafts, draft_id="published-one")
    draft_file.write_text("notes for something unpublished")
    capture_draft(draft_file, drafts, draft_id="still-writing")
    rows = load_jsonl(drafts, ProspectiveDraft)
    rows = [
        row.model_copy(update={"post_id": "a-thing"}) if row.id == published.id else row
        for row in rows
    ]
    atomic_write(drafts, serialize_jsonl(rows))
    atomic_write(
        posts_path,
        serialize_jsonl(
            [
                BlogPost(
                    id="a-thing",
                    lineage_id="a-thing",
                    title="A thing",
                    body_markdown="The finished post.",
                    source_path="a.md",
                    source_url=AnyUrl("https://johnjwang.com/post/2026/09/09/a-thing/"),
                    published_at=date(2026, 9, 9),
                )
            ]
        ),
    )

    counts = promote_prospective_cases(drafts, posts_path, tmp_path / "prospective.jsonl")

    assert counts == {"cases": 1, "pending": 1}
    [case] = load_jsonl(tmp_path / "prospective.jsonl", EvalCase)
    assert case.id == "prospective-published-one"
    assert case.input == "Venue: johnjwang.com (2026)\n\nnotes for the post"
    assert case.reference_output == "# A thing\n\nThe finished post."
    assert case.input_method is InputMethod.ORIGINAL_DRAFT

    # Editing a captured draft after the fact is detected.
    tampered = [
        row.model_copy(update={"input": row.input + " (edited later)"})
        if row.id == published.id
        else row
        for row in load_jsonl(drafts, ProspectiveDraft)
    ]
    atomic_write(drafts, serialize_jsonl(tampered))
    with pytest.raises(ProspectiveError, match="edited after capture"):
        promote_prospective_cases(drafts, posts_path, tmp_path / "p.jsonl")
    assert json.loads(drafts.read_text().splitlines()[0])["id"] == "published-one"
