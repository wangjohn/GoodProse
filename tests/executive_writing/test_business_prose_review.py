from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from goodprose.executive_writing.business_prose_review import (
    build_business_prose_review_packet,
    sanitize_markdown,
)
from goodprose.jsonl import sha256_file


def _git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _fixture_repo(tmp_path: Path) -> tuple[Path, str, str, str]:
    repo = tmp_path / "source"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Fixture Author")
    _git(repo, "config", "user.email", "fixture-author@example.com")
    _git(repo, "remote", "add", "origin", "https://example.com/handbook.git")
    (repo / "LICENSE").write_text("fixture license\n", encoding="utf-8")
    (repo / "content").mkdir()
    document = repo / "content" / "strategy.md"
    document.write_text(
        "---\ntitle: Strategy\n---\n# Strategy\n\n"
        "Email owner@example.com. Read [private context](https://example.com/private).\n\n"
        "We utilize a process in order to make a decision.\n",
        encoding="utf-8",
    )
    _git(repo, "add", "LICENSE", "content/strategy.md")
    _git(repo, "commit", "-m", "initial")
    before = _git(repo, "rev-parse", "HEAD")
    document.write_text(
        "---\ntitle: Strategy\n---\n# Strategy\n\n"
        "Email owner@example.com. Read [private context](https://example.com/private).\n\n"
        "We decide.\n",
        encoding="utf-8",
    )
    _git(repo, "add", "content/strategy.md")
    _git(repo, "commit", "-m", "tighten wording")
    after = _git(repo, "rev-parse", "HEAD")
    return repo, before, after, sha256_file(repo / "LICENSE")


def _config(repo: Path, after: str, license_hash: str) -> dict[str, object]:
    return {
        "version": 1,
        "review_packet_id": "business-prose-human-review-v1",
        "intended_use": "internal_user_only_human_corpus_review",
        "training_approved": False,
        "sources": [
            {
                "source_id": "fixture",
                "repository_dir": repo.name,
                "repository_url": "https://example.com/handbook.git",
                "revision": after,
                "license_id": "Fixture",
                "license_file": "LICENSE",
                "license_sha256": license_hash,
                "allowed_prefixes": ["content/"],
            }
        ],
        "style_selections": [
            {
                "review_id": "style-01",
                "source_id": "fixture",
                "relative_path": "content/strategy.md",
                "title": "Strategy",
                "genre": "company_strategy",
            }
        ],
        "pair_selections": [
            {
                "review_id": "pair-01",
                "source_id": "fixture",
                "relative_path": "content/strategy.md",
                "target_revision": after,
                "title": "Tighten a decision sentence",
                "genre": "strategy_document",
                "selection_note": "Same stated decision; shorter wording.",
                "context_lines": 2,
            }
        ],
    }


def test_sanitize_markdown_removes_transport_and_contact_data() -> None:
    value = sanitize_markdown(
        '---\ntitle: X\n---\n<TeamMember name="Person" /> '
        "user@example.com [label](https://example.com/x) <b>bold</b>"
    )
    assert "title:" not in value
    assert "Person" not in value
    assert "user@example.com" not in value
    assert "https://" not in value
    assert value == "[team member] [email removed] label bold\n"


def test_build_private_review_packet_has_provenance_and_blank_ratings(tmp_path: Path) -> None:
    repo, before, after, license_hash = _fixture_repo(tmp_path)
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(_config(repo, after, license_hash), indent=2) + "\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "packet"

    manifest = build_business_prose_review_packet(
        config_path=config_path,
        source_root=tmp_path,
        output_dir=output_dir,
        generated_at="2026-08-24T00:00:00Z",
    )

    assert manifest["style_item_count"] == 1
    assert manifest["pair_item_count"] == 1
    assert manifest["training_approved"] is False
    assert output_dir.stat().st_mode & 0o777 == 0o700
    assert (output_dir / "style").stat().st_mode & 0o777 == 0o700
    assert (output_dir / "pairs").stat().st_mode & 0o777 == 0o700
    assert (output_dir / "README.md").stat().st_mode & 0o777 == 0o600
    style_text = (output_dir / "style/style-01.md").read_text(encoding="utf-8")
    pair_text = (output_dir / "pairs/pair-01.md").read_text(encoding="utf-8")
    ratings = (output_dir / "ratings.csv").read_text(encoding="utf-8")
    packet_text = style_text + pair_text
    assert "fixture-author@example.com" not in packet_text
    assert "owner@example.com" not in packet_text
    assert "https://example.com/private" not in packet_text
    assert before in pair_text
    assert after in pair_text
    assert "We utilize a process in order to make a decision." in pair_text
    assert "We decide." in pair_text
    assert "style-01,style,Strategy,,,,,,,,,," in ratings
    assert "pair-01,pair,Tighten a decision sentence,,,,,,,,,," in ratings


def test_build_rejects_source_revision_drift(tmp_path: Path) -> None:
    repo, _, after, license_hash = _fixture_repo(tmp_path)
    config = _config(repo, after, license_hash)
    config["sources"][0]["revision"] = "0" * 40  # type: ignore[index]
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValueError, match="source revision mismatch"):
        build_business_prose_review_packet(
            config_path=config_path,
            source_root=tmp_path,
            output_dir=tmp_path / "packet",
            generated_at="2026-08-24T00:00:00Z",
        )
