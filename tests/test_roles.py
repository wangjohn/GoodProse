from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import AnyUrl

from goodprose.jsonl import atomic_write, serialize_jsonl
from goodprose.models import BlogPost, InputMethod, Split, WritingPair
from goodprose.roles import (
    RolesError,
    TrainingRole,
    load_training_roles,
    role_for,
    validate_roles_against_splits,
    venue_line,
)
from goodprose.sft import RAW_COMPLETION_PROMPT, build_sft


def test_venue_line_names_host_year_and_note() -> None:
    assert venue_line("https://johnjwang.com/post/2026/08/x/", date(2026, 8, 27)) == (
        "Venue: johnjwang.com (2026)"
    )
    assert (
        venue_line("https://www.assembled.com/blog/x", date(2025, 10, 22), "editor-revised")
        == "Venue: assembled.com (2025), editor-revised"
    )
    assert venue_line("https://johnjianwang.medium.com/x-1a", date(2023, 6, 30)) == (
        "Venue: medium.com (2023)"
    )
    assert venue_line(None, None) == ""


def test_roles_file_and_test_split_guard(tmp_path: Path) -> None:
    roles_path = tmp_path / "roles.jsonl"
    atomic_write(
        roles_path,
        serialize_jsonl(
            [
                TrainingRole(post_id="edited", role="raw_only", reason="editor pass"),
                TrainingRole(post_id="frozen", role="excluded", reason="oops"),
            ]
        ),
    )
    roles = load_training_roles(roles_path)
    assert role_for("edited", roles) == "raw_only"
    assert role_for("unlisted", roles) == "pairs"
    posts = {
        pid: BlogPost(id=pid, lineage_id=pid, title=pid, body_markdown="x", source_path="x.md")
        for pid in ("edited", "frozen")
    }
    with pytest.raises(RolesError, match="cannot demote test post"):
        validate_roles_against_splits(roles, {"edited": Split.TRAIN, "frozen": Split.TEST}, posts)
    atomic_write(
        roles_path,
        serialize_jsonl(
            [
                TrainingRole(post_id="dup", role="pairs", reason="a"),
                TrainingRole(post_id="dup", role="pairs", reason="b"),
            ]
        ),
    )
    with pytest.raises(RolesError, match="duplicate"):
        load_training_roles(roles_path)


def _pair(identifier: str, split: Split, *, post_id: str | None = None) -> WritingPair:
    post = post_id or identifier
    return WritingPair(
        id=identifier,
        post_id=post,
        lineage_id=post,
        split=split,
        input=f"Notes for {identifier}",
        input_method=InputMethod.DERIVED_BRIEF,
        title=f"Title {post}",
        output=f"Published {identifier}.",
        source_url=AnyUrl("https://johnjwang.com/post/2026/01/01/x/"),
        published_at=date(2026, 1, 1),
    )


def test_build_sft_prepends_venue_lines_and_applies_roles(tmp_path: Path) -> None:
    pairs_path = tmp_path / "pairs.jsonl"
    roles_path = tmp_path / "roles.jsonl"
    posts_path = tmp_path / "posts.jsonl"
    chunks_path = tmp_path / "chunks.jsonl"
    edited = _pair("edited", Split.TRAIN).model_copy(
        update={
            "source_url": AnyUrl("https://www.assembled.com/blog/edited"),
            "output": "Edited text.",
        }
    )
    atomic_write(
        pairs_path,
        serialize_jsonl(
            [
                _pair("personal", Split.TRAIN),
                edited,
                _pair("devpost", Split.DEV),
                _pair("testpost", Split.TEST),
            ]
        ),
    )
    atomic_write(
        roles_path,
        serialize_jsonl(
            [
                TrainingRole(
                    post_id="edited", role="raw_only", venue_note="editor-revised", reason="r"
                )
            ]
        ),
    )
    atomic_write(
        posts_path,
        serialize_jsonl(
            [
                BlogPost(
                    id="edited",
                    lineage_id="edited",
                    title="Title edited",
                    body_markdown="Edited text.\n\n# Second\n\nMore edited text.",
                    source_path="e.md",
                    source_url=AnyUrl("https://www.assembled.com/blog/edited"),
                    published_at=date(2026, 1, 1),
                )
            ]
        ),
    )
    chunks_path.write_text(
        "\n".join(
            json.dumps(
                {
                    "version": 1,
                    "id": chunk_id,
                    "post_id": "edited",
                    "lineage_id": "edited",
                    "split": "train",
                    "ordinal": n,
                    "target": target,
                    "source_start": 0,
                    "source_end": len(target),
                    "word_count": 2,
                    "approx_token_count": 4,
                    "target_sha256": "0" * 64,
                }
            )
            for chunk_id, n, target in (
                ("edited--001", 1, "Edited text."),
                ("edited--002", 2, "# Second\n\nMore edited text."),
                ("edited--full", 3, "Edited text.\n\n# Second\n\nMore edited text."),
            )
        )
        + "\n"
    )

    counts = build_sft(
        pairs_path,
        tmp_path / "sft",
        tmp_path / "cases.jsonl",
        raw_completions=True,
        roles_path=roles_path,
        chunks_path=chunks_path,
        posts_path=posts_path,
    )

    assert counts["dropped_by_role"] == 1
    assert counts["train_pairs"] == 1
    assert counts["raw_only_chunks"] == 3
    records = [
        json.loads(line) for line in (tmp_path / "sft" / "train.jsonl").read_text().splitlines()
    ]
    users = [record["messages"][1]["content"] for record in records]
    assert users[0] == "Venue: johnjwang.com (2026)\n\nNotes for personal"
    # Raw completion of the personal target, then all raw-only chunks under their own venue.
    raw_prompt = RAW_COMPLETION_PROMPT.format(title="Title personal")
    assert users[1] == f"Venue: johnjwang.com (2026)\n\n{raw_prompt}"
    assert users[2].startswith("Venue: assembled.com (2026), editor-revised\n\n")
    assert records[2]["messages"][2]["content"] == "Edited text."
    assert records[3]["messages"][2]["content"] == "# Second\n\nMore edited text."
    assert records[4]["messages"][2]["content"] == (
        "Edited text.\n\n# Second\n\nMore edited text."
    )
    # The edited post's supervised pair is gone; its text survives only as a raw completion.
    assert not any(
        record["messages"][1]["content"].endswith("Notes for edited") for record in records
    )
    case = json.loads((tmp_path / "cases.jsonl").read_text())
    assert case["input"].startswith("Venue: johnjwang.com (2026)\n\n")
    manifest = json.loads((tmp_path / "sft" / "manifest.json").read_text())
    assert manifest["venue_lines"] is True
    assert manifest["dropped_by_role"] == ["edited"]


def test_raw_weight_repeats_a_posts_raw_completions(tmp_path: Path) -> None:
    pairs_path = tmp_path / "pairs.jsonl"
    roles_path = tmp_path / "roles.jsonl"
    atomic_write(
        pairs_path,
        serialize_jsonl([_pair("personal", Split.TRAIN), _pair("testpost", Split.TEST)]),
    )
    atomic_write(
        roles_path,
        serialize_jsonl(
            [TrainingRole(post_id="personal", role="pairs", raw_weight=2, reason="voice")]
        ),
    )

    counts = build_sft(
        pairs_path,
        tmp_path / "sft",
        tmp_path / "cases.jsonl",
        raw_completions=True,
        roles_path=roles_path,
    )

    assert counts["raw_completions"] == 2
    records = [
        json.loads(line) for line in (tmp_path / "sft" / "train.jsonl").read_text().splitlines()
    ]
    assert len(records) == 3
    assert records[1] == records[2]
