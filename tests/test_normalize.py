from __future__ import annotations

import json
from pathlib import Path

import pytest

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import BlogPost, TextSubstitution
from goodprose.normalize import (
    NormalizationConfig,
    NormalizeError,
    manuscript_body,
    normalize_markdown,
    normalize_posts,
    repair_code_blocks,
)

CONFIG = NormalizationConfig()


def test_normalize_straightens_quotes_converts_italics_and_lifts_headings() -> None:
    body = (
        "## Section\n\nIt\u2019s \u201cfine\u201d, _really_.\n\n### Sub\n\n"
        "```go\nx := \u201cquoted\u201d // _keep_\n```\n"
    )

    normalized, applied = normalize_markdown(body, CONFIG)

    assert normalized.startswith('# Section\n\nIt\'s "fine", *really*.\n\n## Sub')
    # Fenced code is left exactly as written.
    assert "x := \u201cquoted\u201d // _keep_" in normalized
    assert set(applied) == {"straight_quotes", "asterisk_italics", "heading_base_level:1"}
    again, applied_again = normalize_markdown(normalized, CONFIG)
    assert again == normalized
    assert applied_again == ()


def test_italics_rule_leaves_snake_case_alone() -> None:
    body = "Use `related_docs` and my_var_name here, but _this_ is italic."

    normalized, _ = normalize_markdown(body, CONFIG)

    assert "related_docs" in normalized
    assert "my_var_name" in normalized
    assert "*this* is italic" in normalized


def test_substitutions_must_match_exactly_once() -> None:
    config = NormalizationConfig(
        substitutions=(
            TextSubstitution(post_id="p", text="<span>x</span>", replacement="x", reason="html"),
        )
    )

    normalized, applied = normalize_markdown("a <span>x</span> b", config, post_id="p")
    assert normalized == "a x b"
    assert applied == ("substitution:html",)

    with pytest.raises(NormalizeError, match="matched 0 times"):
        normalize_markdown("already clean", config, post_id="p")
    lenient, applied = normalize_markdown(
        "already clean", config, post_id="p", strict_substitutions=False
    )
    assert lenient == "already clean" and applied == ()
    # Substitutions scoped to another post do not apply.
    assert (
        normalize_markdown("a <span>x</span> b", config, post_id="other")[0] == "a <span>x</span> b"
    )


def test_normalize_posts_records_what_fired(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jsonl"
    config_path = tmp_path / "normalization.json"
    output = tmp_path / "posts.jsonl"
    atomic_write(
        raw,
        serialize_jsonl(
            [
                BlogPost(
                    id="a",
                    lineage_id="a",
                    title="A",
                    body_markdown="## H\n\nIt\u2019s here.",
                    source_path="a.md",
                ),
                BlogPost(
                    id="b", lineage_id="b", title="B", body_markdown="Plain.", source_path="b.md"
                ),
            ]
        ),
    )
    config_path.write_text(json.dumps({"version": 1}))

    counts = normalize_posts(raw, config_path, output)

    posts = {post.id: post for post in load_jsonl(output, BlogPost)}
    assert counts == {"posts": 2, "heading_base_level": 1, "straight_quotes": 1}
    assert posts["a"].body_markdown == "# H\n\nIt's here."
    assert posts["a"].normalizations == ("straight_quotes", "heading_base_level:1")
    assert posts["b"].normalizations == ()


SNAPSHOT = (
    "Here is the type:\n\n"
    "type Order struct {\n\n ID string\n\n Price int\n\n}\n"
    "func GetOrder(id string) (*Order, error) {\n\n var order Order\n\n return &order, nil\n\n}\n\n"
    "Then some prose about it.\n\n"
    "if err!=nil {\nreturn nil, err\n}\n\n"
    "The end."
)
MANUSCRIPT = (
    "---\ntitle: Orders\n---\n\nHere is the type:\n\n"
    "```go\ntype Order struct {\n    ID    string\n    Price int\n}\n"
    "func GetOrder(id string) (*Order, error) {\n    var order Order\n"
    "    return &order, nil\n}\n```\n\n"
    "Then some prose about it.\n\n"
    "```go\nif err != nil {\n    return nil, err\n}\n```\n\n"
    "```go\nfunc Missing() {}\n```\n"
)


def test_repair_code_blocks_splices_manuscript_fences_over_flattened_runs() -> None:
    repaired, count, unmatched = repair_code_blocks(SNAPSHOT, MANUSCRIPT)

    assert count == 2
    assert unmatched == ["func Missing() {}"]
    assert "```go\ntype Order struct {\n    ID    string\n    Price int\n}\n" in repaired
    assert "```go\nif err != nil {\n    return nil, err\n}\n```" in repaired
    assert "if err!=nil" not in repaired
    assert repaired.startswith("Here is the type:\n\n```go\n")
    assert repaired.endswith("The end.")
    assert "Then some prose about it." in repaired


def test_manuscript_body_strips_front_matter() -> None:
    assert manuscript_body(MANUSCRIPT).startswith("Here is the type:")
    assert manuscript_body("No front matter.") == "No front matter."


def test_fence_code_runs_wraps_flattened_code_and_leaves_prose() -> None:
    from goodprose.normalize import fence_code_runs

    body = (
        "Here is the method:\n\n"
        "type Order struct {\n\n ID string\n\n}\n"
        "func GetOrder(id string) (*Order, error) {\n\n return nil, nil\n\n}\n\n"
        "This is great if you only need one order, but what about many orders in a page?\n\n"
        "Short line.\n"
    )

    fenced, runs = fence_code_runs(body, "go")

    assert runs == 1
    assert fenced.startswith("Here is the method:\n\n```go\ntype Order struct {\n ID string\n}\n")
    assert "return nil, nil\n}\n```\n\nThis is great" in fenced
    assert fenced.endswith("Short line.\n")
    # Idempotent: already fenced code is not touched again.
    assert fence_code_runs(fenced, "go") == (fenced, 0)
