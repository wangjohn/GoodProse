"""Build a private human-review packet from pinned licensed handbook histories."""

from __future__ import annotations

import csv
import io
import re
import subprocess
from collections.abc import Sequence
from difflib import SequenceMatcher
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.jsonl import atomic_write, atomic_write_json, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
GitCommit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
ReviewId = Annotated[str, StringConstraints(pattern=r"^(style|pair)-[0-9]{2}$")]

FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
IMPORT_PATTERN = re.compile(r"^import\s+.*$", re.MULTILINE)
PRIVATE_LINK_PATTERN = re.compile(
    r"<PrivateLink\b[^>]*>(.*?)</PrivateLink>", re.DOTALL | re.IGNORECASE
)
SMALL_TEAM_PATTERN = re.compile(r"<SmallTeam\b[^>]*/>", re.IGNORECASE)
TEAM_MEMBER_PATTERN = re.compile(r"<TeamMember\b[^>]*/>", re.IGNORECASE)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^\n)]*(?:\)[^\n)]*)?\)")
EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
RAW_URL_PATTERN = re.compile(r"https?://[^\s)>]+")
EXCESS_BLANK_PATTERN = re.compile(r"\n{3,}")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceSpec(StrictModel):
    source_id: NonEmpty
    repository_dir: NonEmpty
    repository_url: NonEmpty
    revision: GitCommit
    license_id: NonEmpty
    license_file: NonEmpty
    license_sha256: Sha256
    allowed_prefixes: tuple[NonEmpty, ...] = Field(min_length=1)


class StyleSelection(StrictModel):
    review_id: ReviewId
    source_id: NonEmpty
    relative_path: NonEmpty
    title: NonEmpty
    genre: Literal[
        "company_values",
        "management_guidance",
        "marketing_principles",
        "operating_process",
        "product_strategy",
        "company_strategy",
    ]
    start_marker: str | None = None
    end_marker: str | None = None


class PairSelection(StrictModel):
    review_id: ReviewId
    source_id: NonEmpty
    relative_path: NonEmpty
    target_revision: GitCommit
    title: NonEmpty
    genre: Literal[
        "communication_policy",
        "executive_business_review",
        "pricing_strategy",
        "status_update",
        "strategy_document",
        "company_introduction",
    ]
    selection_note: NonEmpty
    context_lines: int = Field(default=5, ge=2, le=20)


class ReviewConfig(StrictModel):
    version: Literal[1]
    review_packet_id: Literal["business-prose-human-review-v1"]
    intended_use: Literal["internal_user_only_human_corpus_review"]
    training_approved: Literal[False]
    sources: tuple[SourceSpec, ...] = Field(min_length=1)
    style_selections: tuple[StyleSelection, ...] = Field(min_length=1)
    pair_selections: tuple[PairSelection, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source IDs must be unique")
        review_ids = [item.review_id for item in self.style_selections] + [
            item.review_id for item in self.pair_selections
        ]
        if len(review_ids) != len(set(review_ids)):
            raise ValueError("review IDs must be unique")
        known_sources = set(source_ids)
        if any(item.source_id not in known_sources for item in self.style_selections):
            raise ValueError("a style selection references an unknown source")
        if any(item.source_id not in known_sources for item in self.pair_selections):
            raise ValueError("a pair selection references an unknown source")
        if any(not item.review_id.startswith("style-") for item in self.style_selections):
            raise ValueError("style review IDs must start with style-")
        if any(not item.review_id.startswith("pair-") for item in self.pair_selections):
            raise ValueError("pair review IDs must start with pair-")
        return self


def _git_text(repo_path: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _git_bytes(repo_path: Path, *arguments: str) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    return result.stdout


def _validate_relative_path(path: str, allowed_prefixes: Sequence[str]) -> None:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or ".." in parsed.parts:
        raise ValueError(f"unsafe source path: {path}")
    if not any(
        path == prefix.rstrip("/") or path.startswith(prefix) for prefix in allowed_prefixes
    ):
        raise ValueError(f"source path is outside the licensed allowlist: {path}")


def _validate_source(source: SourceSpec, source_root: Path) -> Path:
    repo_path = (source_root / source.repository_dir).resolve()
    if not repo_path.is_relative_to(source_root.resolve()):
        raise ValueError("repository directory escapes source root")
    if _git_text(repo_path, "rev-parse", "HEAD").strip() != source.revision:
        raise ValueError(f"source revision mismatch: {source.source_id}")
    if _git_text(repo_path, "remote", "get-url", "origin").strip() != source.repository_url:
        raise ValueError(f"source origin mismatch: {source.source_id}")
    if _git_text(repo_path, "status", "--porcelain").strip():
        raise ValueError(f"source working tree is not clean: {source.source_id}")
    if sha256_file(repo_path / source.license_file) != source.license_sha256:
        raise ValueError(f"source license hash mismatch: {source.source_id}")
    return repo_path


def _extract_section(text: str, start_marker: str | None, end_marker: str | None) -> str:
    start = 0
    if start_marker is not None:
        if text.count(start_marker) != 1:
            raise ValueError(f"section start marker must occur exactly once: {start_marker}")
        start = text.index(start_marker)
    end = len(text)
    if end_marker is not None:
        if text.count(end_marker) != 1:
            raise ValueError(f"section end marker must occur exactly once: {end_marker}")
        end = text.index(end_marker)
    if end <= start:
        raise ValueError("section end marker must follow section start marker")
    return text[start:end]


def sanitize_markdown(text: str) -> str:
    """Remove transport markup and obvious contact/private-link data."""

    value = text.replace("\r\n", "\n").replace("\r", "\n")
    value = FRONTMATTER_PATTERN.sub("", value)
    value = IMPORT_PATTERN.sub("", value)
    value = PRIVATE_LINK_PATTERN.sub(r"\1", value)
    value = SMALL_TEAM_PATTERN.sub("[team]", value)
    value = TEAM_MEMBER_PATTERN.sub("[team member]", value)
    value = MARKDOWN_LINK_PATTERN.sub(r"\1", value)
    value = HTML_TAG_PATTERN.sub("", value)
    value = EMAIL_PATTERN.sub("[email removed]", value)
    value = RAW_URL_PATTERN.sub("[link removed]", value)
    value = "\n".join(line.rstrip() for line in value.splitlines())
    value = EXCESS_BLANK_PATTERN.sub("\n\n", value)
    return value.strip() + "\n"


def _grouped_excerpts(before: str, after: str, context_lines: int) -> list[tuple[str, str]]:
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    matcher = SequenceMatcher(None, before_lines, after_lines, autojunk=False)
    groups = list(matcher.get_grouped_opcodes(n=context_lines))
    excerpts: list[tuple[str, str]] = []
    for group in groups:
        before_start = group[0][1]
        before_end = group[-1][2]
        after_start = group[0][3]
        after_end = group[-1][4]
        excerpts.append(
            (
                "\n".join(before_lines[before_start:before_end]).strip(),
                "\n".join(after_lines[after_start:after_end]).strip(),
            )
        )
    if not excerpts:
        raise ValueError("selected revision pair has no sanitized text change")
    return excerpts


def _style_document(selection: StyleSelection, source: SourceSpec, body: str) -> bytes:
    header = (
        f"# {selection.title}\n\n"
        f"- Review ID: `{selection.review_id}`\n"
        f"- Genre: `{selection.genre}`\n"
        f"- Source: `{source.source_id}` at `{source.revision}`\n"
        f"- Path: `{selection.relative_path}`\n"
        "- Status: private review candidate; not training-approved\n\n"
        "---\n\n"
    )
    return (header + body).encode("utf-8")


def _pair_document(
    selection: PairSelection,
    source: SourceSpec,
    parent_revision: str,
    excerpts: Sequence[tuple[str, str]],
) -> bytes:
    parts = [
        f"# {selection.title}",
        "",
        f"- Review ID: `{selection.review_id}`",
        f"- Genre: `{selection.genre}`",
        f"- Source: `{source.source_id}`",
        f"- Path: `{selection.relative_path}`",
        f"- Before revision: `{parent_revision}`",
        f"- After revision: `{selection.target_revision}`",
        f"- Selection note: {selection.selection_note}",
        "- Status: private review candidate; not training-approved",
        "",
        "Rate whether the two versions preserve the same intended facts and decision, "
        "then whether the after version is materially better prose.",
        "",
    ]
    for index, (before, after) in enumerate(excerpts, start=1):
        parts.extend(
            [
                f"## Changed region {index}",
                "",
                "### Before",
                "",
                "```text",
                before,
                "```",
                "",
                "### After",
                "",
                "```text",
                after,
                "```",
                "",
            ]
        )
    return ("\n".join(parts).rstrip() + "\n").encode("utf-8")


RATING_COLUMNS = (
    "review_id",
    "item_type",
    "title",
    "overall_quality_1_5",
    "executive_relevance_1_5",
    "clarity_1_5",
    "concision_1_5",
    "decision_usefulness_1_5",
    "same_intent_yes_no_unclear",
    "after_better_1_5",
    "factual_change_none_minor_material",
    "keep_yes_no",
    "notes",
)


def _ratings_csv(config: ReviewConfig) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=RATING_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for selection in config.style_selections:
        writer.writerow(
            {"review_id": selection.review_id, "item_type": "style", "title": selection.title}
        )
    for selection in config.pair_selections:
        writer.writerow(
            {"review_id": selection.review_id, "item_type": "pair", "title": selection.title}
        )
    return output.getvalue().encode("utf-8")


def _readme(config: ReviewConfig) -> bytes:
    lines = [
        "# Business prose human review packet",
        "",
        "This packet is private, user-only, and not training-approved. Review finished",
        "pieces first, then before/after pairs. Enter ratings in `ratings.csv`.",
        "",
        "## Rating guide",
        "",
        "Use 1-5 for quality dimensions. For pairs, `same_intent` is the hard gate:",
        "reject a pair if the after version changes material facts, policy, strategy, or",
        "audience rather than simply improving the writing. `after_better` asks whether",
        "the revision is a useful model of the transformation GoodProse should learn.",
        "",
        "## Finished pieces",
        "",
    ]
    lines.extend(
        f"- [{item.review_id}: {item.title}](style/{item.review_id}.md) — `{item.genre}`"
        for item in config.style_selections
    )
    lines.extend(["", "## Revision pairs", ""])
    lines.extend(
        f"- [{item.review_id}: {item.title}](pairs/{item.review_id}.md) — `{item.genre}`"
        for item in config.pair_selections
    )
    lines.extend(
        [
            "",
            "## Decision rule",
            "",
            "A style piece is a keep candidate when its overall quality and executive",
            "relevance are both at least 4/5. A pair is a keep candidate only when",
            "`same_intent=yes`, factual change is `none`, and `after_better` is at least",
            "4/5. These are review thresholds, not automatic training approval.",
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def _write_private(path: Path, data: bytes) -> None:
    atomic_write(path, data)
    path.chmod(0o600)


def build_business_prose_review_packet(
    *,
    config_path: Path,
    source_root: Path,
    output_dir: Path,
    generated_at: str,
) -> dict[str, object]:
    """Validate pinned sources and build a local-only review packet."""

    config = ReviewConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("review packet output directory must be absent or empty")
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    output_dir.chmod(0o700)
    style_dir = output_dir / "style"
    pairs_dir = output_dir / "pairs"
    style_dir.mkdir(mode=0o700)
    pairs_dir.mkdir(mode=0o700)

    source_by_id = {source.source_id: source for source in config.sources}
    repo_by_id = {
        source.source_id: _validate_source(source, source_root) for source in config.sources
    }
    item_records: list[dict[str, object]] = []

    for selection in config.style_selections:
        source = source_by_id[selection.source_id]
        repo_path = repo_by_id[selection.source_id]
        _validate_relative_path(selection.relative_path, source.allowed_prefixes)
        raw = _git_bytes(repo_path, "show", f"{source.revision}:{selection.relative_path}").decode(
            "utf-8"
        )
        section = _extract_section(raw, selection.start_marker, selection.end_marker)
        body = sanitize_markdown(section)
        relative_output = Path("style") / f"{selection.review_id}.md"
        output_path = output_dir / relative_output
        _write_private(output_path, _style_document(selection, source, body))
        item_records.append(
            {
                "review_id": selection.review_id,
                "item_type": "style",
                "title": selection.title,
                "source_id": selection.source_id,
                "source_revision": source.revision,
                "relative_path": selection.relative_path,
                "output_path": relative_output.as_posix(),
                "output_sha256": sha256_file(output_path),
                "training_approved": False,
            }
        )

    for selection in config.pair_selections:
        source = source_by_id[selection.source_id]
        repo_path = repo_by_id[selection.source_id]
        _validate_relative_path(selection.relative_path, source.allowed_prefixes)
        if (
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", selection.target_revision, source.revision],
                cwd=repo_path,
                check=False,
            ).returncode
            != 0
        ):
            raise ValueError(f"pair target is not in pinned source history: {selection.review_id}")
        parent_revision = _git_text(repo_path, "rev-parse", f"{selection.target_revision}^").strip()
        before = sanitize_markdown(
            _git_bytes(repo_path, "show", f"{parent_revision}:{selection.relative_path}").decode(
                "utf-8"
            )
        )
        after = sanitize_markdown(
            _git_bytes(
                repo_path, "show", f"{selection.target_revision}:{selection.relative_path}"
            ).decode("utf-8")
        )
        excerpts = _grouped_excerpts(before, after, selection.context_lines)
        relative_output = Path("pairs") / f"{selection.review_id}.md"
        output_path = output_dir / relative_output
        _write_private(
            output_path,
            _pair_document(selection, source, parent_revision, excerpts),
        )
        item_records.append(
            {
                "review_id": selection.review_id,
                "item_type": "pair",
                "title": selection.title,
                "source_id": selection.source_id,
                "before_revision": parent_revision,
                "after_revision": selection.target_revision,
                "relative_path": selection.relative_path,
                "changed_region_count": len(excerpts),
                "output_path": relative_output.as_posix(),
                "output_sha256": sha256_file(output_path),
                "training_approved": False,
            }
        )

    _write_private(output_dir / "README.md", _readme(config))
    _write_private(output_dir / "ratings.csv", _ratings_csv(config))
    manifest: dict[str, object] = {
        "version": 1,
        "review_packet_id": config.review_packet_id,
        "generated_at": generated_at,
        "intended_use": config.intended_use,
        "config_sha256": sha256_file(config_path),
        "source_count": len(config.sources),
        "style_item_count": len(config.style_selections),
        "pair_item_count": len(config.pair_selections),
        "items": item_records,
        "contains_private_review_bodies": True,
        "git_ignored_output_required": True,
        "ratings_status": "pending_user_review",
        "training_approved": False,
    }
    atomic_write_json(output_dir / "manifest.json", manifest)
    (output_dir / "manifest.json").chmod(0o600)
    return manifest
