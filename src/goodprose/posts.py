"""Import a directory of Markdown blog posts."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin

from pydantic import ValidationError

from goodprose.jsonl import atomic_write, serialize_jsonl
from goodprose.models import BlogPost


class PostImportError(ValueError):
    """A Markdown export cannot be represented as a blog post."""


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.lstrip("\ufeff").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text.strip("\n")

    metadata: dict[str, str] = {}
    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise PostImportError(f"unsupported front matter line: {line.strip()!r}")
        normalized = value.strip()
        if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in "\"'":
            normalized = normalized[1:-1]
        metadata[key.strip().lower()] = normalized
    if closing_index is None:
        raise PostImportError("front matter starts with '---' but has no closing '---'")
    return metadata, "".join(lines[closing_index + 1 :]).strip("\n")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise PostImportError(f"could not make an ID from {value!r}")
    return slug


def _first_heading(body: str) -> str | None:
    match = re.search(r"^#\s+(.+?)\s*$", body, flags=re.MULTILINE)
    return match.group(1) if match else None


def _markdown_paths(root: Path) -> list[Path]:
    paths = [*root.rglob("*.md"), *root.rglob("*.markdown")]
    return sorted(path for path in paths if not any(part.startswith(".") for part in path.parts))


def import_posts(root: Path, output_path: Path, *, url_base: str | None = None) -> int:
    if not root.is_dir():
        raise PostImportError(f"Markdown input directory does not exist: {root}")
    paths = _markdown_paths(root)
    if not paths:
        raise PostImportError(f"no Markdown files found under {root}")

    posts: list[BlogPost] = []
    seen_ids: set[str] = set()
    for path in paths:
        metadata, body = _parse_front_matter(path.read_text(encoding="utf-8"))
        if not body.strip():
            raise PostImportError(f"{path}: post body is empty")
        relative_path = path.relative_to(root).as_posix()
        default_id = str(Path(relative_path).with_suffix(""))
        post_id = _slugify(metadata.get("id", default_id))
        if post_id in seen_ids:
            raise PostImportError(f"duplicate post ID {post_id!r}")
        seen_ids.add(post_id)

        title = metadata.get("title") or _first_heading(body)
        if not title:
            title = Path(relative_path).stem.replace("-", " ").replace("_", " ").strip().title()
        source_url = metadata.get("url") or metadata.get("source_url")
        if source_url is None and url_base:
            source_url = urljoin(url_base.rstrip("/") + "/", post_id + "/")
        lineage_id = metadata.get("series") or metadata.get("lineage_id") or post_id

        try:
            post = BlogPost.model_validate(
                {
                    "id": post_id,
                    "lineage_id": lineage_id,
                    "title": title,
                    "body_markdown": body,
                    "source_path": relative_path,
                    "source_url": source_url,
                    "published_at": metadata.get("date") or metadata.get("published_at"),
                }
            )
        except ValidationError as error:
            raise PostImportError(f"{path}: {error}") from error
        posts.append(post)

    posts.sort(key=lambda post: post.id)
    atomic_write(output_path, serialize_jsonl(posts))
    return len(posts)
