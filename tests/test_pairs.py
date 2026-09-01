from __future__ import annotations

from pathlib import Path

import pytest

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import BlogPost, Brief, InputMethod, Split, WritingPair
from goodprose.pairs import PairBuildError, build_pairs, validate_pairs


def test_builds_pair_from_reviewed_brief_and_exact_post(tmp_path: Path) -> None:
    posts_path = tmp_path / "posts.jsonl"
    briefs_path = tmp_path / "briefs.jsonl"
    output_path = tmp_path / "pairs.jsonl"
    atomic_write(
        posts_path,
        serialize_jsonl(
            [
                BlogPost(
                    id="post-1",
                    lineage_id="series-1",
                    title="Post title",
                    body_markdown="Exact body.",
                    source_path="post-1.md",
                )
            ]
        ),
    )
    atomic_write(
        briefs_path,
        serialize_jsonl(
            [
                Brief(
                    id="pair-1",
                    post_id="post-1",
                    split=Split.TRAIN,
                    input="Outline written by the author.",
                    input_method=InputMethod.ORIGINAL_OUTLINE,
                )
            ]
        ),
    )

    assert build_pairs(posts_path, briefs_path, output_path) == 1
    pair = load_jsonl(output_path, WritingPair)[0]
    assert pair.lineage_id == "series-1"
    assert pair.output == "# Post title\n\nExact body."


def test_rejects_lineage_crossing_splits() -> None:
    common = {
        "post_id": "post-1",
        "lineage_id": "series-1",
        "input": "Outline",
        "input_method": InputMethod.ORIGINAL_OUTLINE,
        "title": "Title",
        "output": "Output",
    }
    pairs = [
        WritingPair(id="one", split=Split.TRAIN, **common),
        WritingPair(id="two", split=Split.TEST, **{**common, "post_id": "post-2"}),
    ]

    with pytest.raises(PairBuildError, match=r"lineage .* crosses splits"):
        validate_pairs(pairs)
