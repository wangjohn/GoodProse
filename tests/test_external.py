from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from pydantic import AnyUrl

from goodprose.external import (
    ExternalSourceError,
    build_authentic_eval_briefs,
    build_external_posts,
    build_external_samples,
    normalize_published_snapshot,
)
from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import (
    AuthenticInputMapping,
    BlogPost,
    Brief,
    ExternalPlatform,
    ExternalPostCatalog,
    ExternalPostSample,
    ExternalSourceMapping,
    ExternalSourceStatus,
    InputMethod,
    ReviewStatus,
    Split,
    SplitAssignment,
)


def _catalog() -> ExternalPostCatalog:
    return ExternalPostCatalog(
        id="external-post",
        lineage_id="external-post",
        title="External post",
        platform=ExternalPlatform.MEDIUM,
        source_url=AnyUrl("https://example.com/post"),
        published_at=date(2025, 1, 2),
        source_status=ExternalSourceStatus.PRIVATE_MARKDOWN_RECOVERED,
        notes="Private source export found.",
    )


def test_build_external_samples_preserves_raw_private_source(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source = "# Draft title\n\nExact raw author source."
    (source_root / "post.md").write_text(source)
    catalog_path = tmp_path / "catalog.jsonl"
    source_map_path = tmp_path / "map.jsonl"
    output_path = tmp_path / "samples.jsonl"
    atomic_write(catalog_path, serialize_jsonl([_catalog()]))
    atomic_write(
        source_map_path,
        serialize_jsonl([ExternalSourceMapping(post_id="external-post", source_path="post.md")]),
    )

    counts = build_external_samples(catalog_path, source_map_path, source_root, output_path)

    assert counts == {"medium": 1}
    sample = load_jsonl(output_path, ExternalPostSample)[0]
    assert sample.raw_markdown == source
    assert sample.word_count == 6


def test_build_external_samples_rejects_path_escape(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    source_root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("Private source")
    catalog_path = tmp_path / "catalog.jsonl"
    source_map_path = tmp_path / "map.jsonl"
    atomic_write(catalog_path, serialize_jsonl([_catalog()]))
    atomic_write(
        source_map_path,
        serialize_jsonl(
            [ExternalSourceMapping(post_id="external-post", source_path="../outside.md")]
        ),
    )

    with pytest.raises(ExternalSourceError, match="escapes source root"):
        build_external_samples(catalog_path, source_map_path, source_root, tmp_path / "out.jsonl")


def test_normalize_medium_snapshot_removes_page_chrome_and_images() -> None:
    snapshot = """Title: Example

Markdown Content:
[![Image 1: John Wang](avatar)](profile)

2 min read

Jan 2, 2025

Intro paragraph.

## Get John Wang\N{RIGHT SINGLE QUOTATION MARK}s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

Press enter or click to view image in full size

![Image 2](image)

This file contains hidden or bidirectional Unicode text. [Learn more](hidden)

[Show hidden characters](reveal)

## Real section

Exact article text.
"""

    assert normalize_published_snapshot(snapshot, ExternalPlatform.MEDIUM) == (
        "Intro paragraph.\n\n## Real section\n\nExact article text."
    )


def test_build_external_posts_requires_approval_and_merges_base_posts(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.jsonl"
    snapshot_root = tmp_path / "published-raw"
    snapshot_root.mkdir()
    approved = _catalog().model_copy(update={"review_status": ReviewStatus.APPROVED})
    atomic_write(catalog_path, serialize_jsonl([approved]))
    (snapshot_root / "external-post.md").write_text(
        "Title: External\n\nMarkdown Content:\nPublished external prose.\n"
    )

    output_path = tmp_path / "posts.jsonl"
    counts = build_external_posts(catalog_path, snapshot_root, output_path)

    assert counts == {
        "base": 0,
        "external": 1,
        "manuscript_targets": 0,
        "repaired_code_blocks": 0,
        "unmatched_code_blocks": 0,
        "heuristic_code_runs": 0,
        "total": 1,
    }
    posts = load_jsonl(output_path, BlogPost)
    assert posts[0].body_markdown == "Published external prose."

    atomic_write(catalog_path, serialize_jsonl([_catalog()]))
    with pytest.raises(ExternalSourceError, match="not approved"):
        build_external_posts(catalog_path, snapshot_root, output_path)


def test_build_authentic_eval_briefs_extracts_exact_line_range(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "draft.md").write_text("metadata\nfirst draft line\nsecond draft line\nnotes")
    mapping_path = tmp_path / "mapping.jsonl"
    splits_path = tmp_path / "splits.jsonl"
    output_path = tmp_path / "briefs.jsonl"
    atomic_write(
        mapping_path,
        serialize_jsonl(
            [
                AuthenticInputMapping(
                    post_id="external-post",
                    source_path="draft.md",
                    start_line=2,
                    end_line=3,
                    input_method=InputMethod.ORIGINAL_DRAFT,
                )
            ]
        ),
    )
    atomic_write(
        splits_path,
        serialize_jsonl(
            [
                SplitAssignment(
                    lineage_id="external-post",
                    split=Split.TEST,
                    frozen_at=date(2026, 9, 1),
                    rationale="Held out with an authentic draft.",
                )
            ]
        ),
    )

    assert build_authentic_eval_briefs(mapping_path, source_root, splits_path, output_path) == {
        "test": 1
    }
    brief = load_jsonl(output_path, Brief)[0]
    assert brief.input == "first draft line\nsecond draft line"
    assert brief.input_method is InputMethod.ORIGINAL_DRAFT


def test_build_external_posts_repairs_code_and_uses_manuscript_targets(tmp_path: Path) -> None:
    from goodprose.models import (
        ExternalPlatform,
        ExternalPostCatalog,
        ExternalSourceMapping,
        ExternalSourceStatus,
    )

    catalog_path = tmp_path / "catalog.jsonl"
    snapshot_root = tmp_path / "snapshots"
    source_root = tmp_path / "manuscripts"
    source_map = tmp_path / "source-map.jsonl"
    snapshot_root.mkdir()
    source_root.mkdir()
    entries = []
    for post_id in ("external-repair", "external-manuscript"):
        entries.append(
            ExternalPostCatalog(
                id=post_id,
                lineage_id=post_id,
                title=post_id,
                platform=ExternalPlatform.MEDIUM,
                source_url=AnyUrl(f"https://johnjianwang.medium.com/{post_id}"),
                published_at=date(2023, 6, 30),
                source_status=ExternalSourceStatus.PRIVATE_MARKDOWN_RECOVERED,
                review_status=ReviewStatus.APPROVED,
                notes="test",
            )
        )
    atomic_write(catalog_path, serialize_jsonl(entries))
    (snapshot_root / "external-repair.md").write_text(
        "Title\n\nMarkdown Content:\nIntro prose.\n\ntype T struct {\n\n A int\n\n}\n\nOutro.\n"
    )
    (snapshot_root / "external-manuscript.md").write_text(
        "Title\n\nMarkdown Content:\nEdited by someone else.\n"
    )
    (source_root / "repair.md").write_text(
        "Intro prose.\n\n```go\ntype T struct {\n    A int\n}\n```\n\nOutro.\n"
    )
    (source_root / "manuscript.md").write_text("---\ntitle: M\n---\n\nThe author's own words.\n")
    atomic_write(
        source_map,
        serialize_jsonl(
            [
                ExternalSourceMapping(post_id="external-repair", source_path="repair.md"),
                ExternalSourceMapping(post_id="external-manuscript", source_path="manuscript.md"),
            ]
        ),
    )
    output = tmp_path / "posts.jsonl"

    counts = build_external_posts(
        catalog_path,
        snapshot_root,
        output,
        source_map_path=source_map,
        source_root=source_root,
        repair_code=True,
        manuscript_target_ids=["external-manuscript"],
    )

    assert counts["repaired_code_blocks"] == 1
    assert counts["unmatched_code_blocks"] == 0
    assert counts["heuristic_code_runs"] == 0
    assert counts["manuscript_targets"] == 1
    posts = {post.id: post for post in load_jsonl(output, BlogPost)}
    assert posts["external-repair"].body_markdown == (
        "Intro prose.\n\n```go\ntype T struct {\n    A int\n}\n```\n\nOutro."
    )
    assert posts["external-manuscript"].body_markdown == "The author's own words."
    assert posts["external-manuscript"].source_path.startswith("external/blogposts-source/")
