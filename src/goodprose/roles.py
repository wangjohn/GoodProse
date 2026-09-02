"""Per-post training roles and the venue line that tags every example with where it ran.

The author's voice is the personal site. Posts from other venues are still the author's words
but carry a different register (a company blog with an editor's pass, a 2021 Medium essay), so
each post gets a role that says how it may train, and every user turn opens with a venue line
so the adapter learns the register as a condition rather than an average.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import AnyUrl, Field

from goodprose.jsonl import load_jsonl
from goodprose.models import BlogPost, NonEmptyString, Split, StrictModel

TrainingRoleKind = Literal["pairs", "raw_only", "excluded"]
PERSONAL_HOST = "johnjwang.com"


class RolesError(ValueError):
    """Training roles are inconsistent with the posts or splits."""


class TrainingRole(StrictModel):
    version: Literal[1] = 1
    post_id: NonEmptyString
    role: TrainingRoleKind
    venue_note: NonEmptyString | None = None
    raw_weight: int = Field(
        default=1,
        ge=0,
        description="How many times this post's raw completions appear in the mix; 0 skips them.",
    )
    reason: NonEmptyString


def raw_weight_for(post_id: str, roles: dict[str, TrainingRole]) -> int:
    role = roles.get(post_id)
    return role.raw_weight if role is not None else 1


def load_training_roles(path: Path | None) -> dict[str, TrainingRole]:
    if path is None:
        return {}
    roles = load_jsonl(path, TrainingRole)
    indexed: dict[str, TrainingRole] = {}
    for role in roles:
        if role.post_id in indexed:
            raise RolesError(f"duplicate training role for {role.post_id!r}")
        indexed[role.post_id] = role
    return indexed


def role_for(post_id: str, roles: dict[str, TrainingRole]) -> TrainingRoleKind:
    role = roles.get(post_id)
    return role.role if role is not None else "pairs"


def venue_host(source_url: AnyUrl | str | None) -> str:
    if source_url is None:
        return "unknown venue"  # only reachable when a date exists without a URL
    host = (urlparse(str(source_url)).netloc or str(source_url)).lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith("medium.com"):
        return "medium.com"
    return host


def venue_line(
    source_url: AnyUrl | str | None,
    published_at: datetime | date | None,
    note: str | None = None,
) -> str:
    """``Venue: johnjwang.com (2026)`` or ``Venue: assembled.com (2025), edited``.

    Empty when neither a URL nor a date is known, so such records get no venue line.
    """
    if source_url is None and published_at is None:
        return ""
    host = venue_host(source_url)
    year = f" ({published_at.year})" if published_at is not None else ""
    suffix = f", {note}" if note else ""
    return f"Venue: {host}{year}{suffix}"


def venue_line_for_post(post: BlogPost, roles: dict[str, TrainingRole]) -> str:
    role = roles.get(post.id)
    return venue_line(post.source_url, post.published_at, role.venue_note if role else None)


def validate_roles_against_splits(
    roles: dict[str, TrainingRole], splits: dict[str, Split], posts: dict[str, BlogPost]
) -> None:
    unknown = sorted(set(roles) - set(posts))
    if unknown:
        raise RolesError(f"training roles reference unknown post(s): {unknown}")
    for post_id, role in roles.items():
        if splits.get(posts[post_id].lineage_id) is Split.TEST and role.role != "pairs":
            raise RolesError(
                f"training roles cannot demote test post {post_id!r}; the test set is frozen"
            )
