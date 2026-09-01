from __future__ import annotations

from pathlib import Path

import pytest

from goodprose.jsonl import load_jsonl
from goodprose.models import BlogPost
from goodprose.posts import PostImportError, import_posts


def test_imports_markdown_with_simple_front_matter(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "first.md").write_text(
        "---\n"
        "title: A useful tool\n"
        "date: 2025-01-02T09:30:00-08:00\n"
        "series: tools\n"
        "---\n"
        "The exact published body.\n",
        encoding="utf-8",
    )
    (source / "second.markdown").write_text(
        "# Another post\n\nAnother exact body.\n", encoding="utf-8"
    )
    output = tmp_path / "posts.jsonl"

    count = import_posts(source, output, url_base="https://example.com/blog/")

    assert count == 2
    posts = load_jsonl(output, BlogPost)
    assert posts[0].id == "first"
    assert posts[0].lineage_id == "tools"
    assert posts[0].body_markdown == "The exact published body."
    assert str(posts[0].source_url) == "https://example.com/blog/first/"
    assert posts[1].title == "Another post"
    assert posts[1].body_markdown.startswith("# Another post")


def test_rejects_duplicate_post_ids(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    for filename in ("one.md", "two.md"):
        (source / filename).write_text(
            "---\nid: duplicate\ntitle: Post\n---\nBody\n", encoding="utf-8"
        )

    with pytest.raises(PostImportError, match="duplicate post ID"):
        import_posts(source, tmp_path / "posts.jsonl")


def test_builds_dated_url_from_front_matter_template(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "source-name.md").write_text(
        "---\n"
        "title: Templated post\n"
        "slug: published-slug\n"
        "date: 2026-03-07\n"
        "---\n"
        "Exact published body.\n",
        encoding="utf-8",
    )
    output = tmp_path / "posts.jsonl"

    import_posts(
        source,
        output,
        url_template="https://example.com/post/{year}/{month}/{day}/{slug}/",
    )

    post = load_jsonl(output, BlogPost)[0]
    assert str(post.source_url) == "https://example.com/post/2026/03/07/published-slug/"


def test_rejects_unknown_url_template_field(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "post.md").write_text("# Post\n\nBody.\n", encoding="utf-8")

    with pytest.raises(PostImportError, match="unsupported URL template field"):
        import_posts(
            source,
            tmp_path / "posts.jsonl",
            url_template="https://example.com/{unknown}/",
        )
