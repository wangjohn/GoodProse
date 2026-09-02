"""Explicit, configured normalization of canonical posts, and code-fence repair.

Two different things live here because both change target text on purpose and both must be
visible rather than silent:

* :func:`normalize_markdown` applies the author's surface conventions (straight quotes,
  ``*italics*``, section headings at one level, reviewed exact-text substitutions) to a raw
  post. The result records which normalizations fired, so ``data/posts/posts.jsonl`` is never a
  silently rewritten import: it is the raw text plus a named, configured transformation.
* :func:`repair_code_blocks` restores fenced code that a public-page snapshot flattened into
  prose lines, by splicing the author's own fenced blocks from a manuscript wherever the
  whitespace-stripped tokens match exactly. Nothing is guessed; unmatched blocks are reported.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import BlogPost, StrictModel, TextSubstitution

_FENCE_LINE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
_FENCED_BLOCK = re.compile(r"^(`{3,}|~{3,})([^\n]*)\n(.*?)\n\1[ \t]*$", re.MULTILINE | re.DOTALL)
_HEADING = re.compile(r"^(#{1,6})[ \t]+\S")
_UNDERSCORE_ITALIC = re.compile(r"(?<![\w*_])_([^_\n]+?)_(?![\w*_])")
_QUOTES = {
    "\N{RIGHT SINGLE QUOTATION MARK}": "'",
    "\N{LEFT SINGLE QUOTATION MARK}": "'",
    "\N{LEFT DOUBLE QUOTATION MARK}": '"',
    "\N{RIGHT DOUBLE QUOTATION MARK}": '"',
}


class NormalizeError(ValueError):
    """A normalization or repair could not be applied safely."""


class NormalizationConfig(StrictModel):
    version: Literal[1] = 1
    straight_quotes: bool = True
    asterisk_italics: bool = True
    heading_base_level: int | None = Field(default=1, ge=1, le=6)
    substitutions: tuple[TextSubstitution, ...] = ()


def load_normalization_config(path: Path) -> NormalizationConfig:
    try:
        return NormalizationConfig.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        raise NormalizeError(f"invalid normalization config {path}: {error}") from error


def _outside_fences(body: str) -> list[tuple[str, bool]]:
    """Split a body into (segment, is_code) pieces so prose rules skip fenced code."""
    pieces: list[tuple[str, bool]] = []
    prose: list[str] = []
    code: list[str] = []
    marker: str | None = None
    for line in body.splitlines(keepends=True):
        match = _FENCE_LINE.match(line)
        if marker is None and match:
            if prose:
                pieces.append(("".join(prose), False))
                prose = []
            marker = match.group(1)[0]
            code.append(line)
            continue
        if marker is not None:
            code.append(line)
            if match and match.group(1)[0] == marker:
                pieces.append(("".join(code), True))
                code = []
                marker = None
            continue
        prose.append(line)
    if prose:
        pieces.append(("".join(prose), False))
    if code:
        pieces.append(("".join(code), True))
    return pieces


def _straighten_quotes(text: str) -> str:
    for curly, straight in _QUOTES.items():
        text = text.replace(curly, straight)
    return text


def _shift_headings(prose_pieces: list[str], base_level: int) -> tuple[list[str], bool]:
    levels = [
        len(match.group(1))
        for piece in prose_pieces
        for line in piece.splitlines()
        if (match := _HEADING.match(line))
    ]
    if not levels:
        return prose_pieces, False
    shift = min(levels) - base_level
    if shift <= 0:
        return prose_pieces, False
    shifted: list[str] = []
    for piece in prose_pieces:
        lines = []
        for line in piece.splitlines(keepends=True):
            match = _HEADING.match(line)
            if match:
                line = line[shift:]
            lines.append(line)
        shifted.append("".join(lines))
    return shifted, True


def apply_substitutions(
    body: str,
    substitutions: list[TextSubstitution],
    *,
    strict: bool = True,
) -> tuple[str, list[str]]:
    """Replace reviewed exact spans once each; strict mode demands exactly one occurrence."""
    applied: list[str] = []
    for substitution in substitutions:
        count = body.count(substitution.text)
        if count == 1:
            body = body.replace(substitution.text, substitution.replacement, 1)
            applied.append(f"substitution:{substitution.reason}")
        elif strict:
            raise NormalizeError(
                f"substitution for {substitution.post_id!r} matched {count} times instead of "
                f"exactly once: {substitution.text[:60]!r}"
            )
    return body, applied


def normalize_markdown(
    body: str,
    config: NormalizationConfig,
    *,
    post_id: str | None = None,
    strict_substitutions: bool = True,
) -> tuple[str, tuple[str, ...]]:
    """Apply the configured conventions to one post body; idempotent for the rule-based steps."""
    applied: list[str] = []
    substitutions = [s for s in config.substitutions if post_id is None or s.post_id == post_id]
    body, sub_applied = apply_substitutions(body, substitutions, strict=strict_substitutions)
    applied.extend(sub_applied)

    pieces = _outside_fences(body)
    prose = [piece for piece, is_code in pieces if not is_code]
    if config.straight_quotes:
        straightened = [_straighten_quotes(piece) for piece in prose]
        if straightened != prose:
            applied.append("straight_quotes")
        prose = straightened
    if config.asterisk_italics:
        converted = [_UNDERSCORE_ITALIC.sub(r"*\1*", piece) for piece in prose]
        if converted != prose:
            applied.append("asterisk_italics")
        prose = converted
    if config.heading_base_level is not None:
        prose, shifted = _shift_headings(prose, config.heading_base_level)
        if shifted:
            applied.append(f"heading_base_level:{config.heading_base_level}")

    prose_iter = iter(prose)
    rebuilt = "".join(piece if is_code else next(prose_iter) for piece, is_code in pieces)
    return rebuilt, tuple(applied)


def normalize_posts(raw_path: Path, config_path: Path, output_path: Path) -> dict[str, int]:
    """Write ``posts.jsonl`` from the raw import, recording which normalizations fired.

    Run this from the raw file every time, never from an already normalized output: the
    reviewed substitutions insist on matching exactly once so a stale or mistyped span fails
    loudly instead of silently doing nothing.
    """
    config = load_normalization_config(config_path)
    posts = load_jsonl(raw_path, BlogPost)
    known_ids = {post.id for post in posts}
    unknown = sorted({s.post_id for s in config.substitutions} - known_ids)
    if unknown:
        raise NormalizeError(f"substitutions reference unknown post(s): {unknown}")
    normalized: list[BlogPost] = []
    counter: Counter[str] = Counter()
    for post in posts:
        body, applied = normalize_markdown(post.body_markdown, config, post_id=post.id)
        counter.update(name.split(":")[0] for name in applied)
        normalized.append(
            post.model_copy(update={"body_markdown": body, "normalizations": applied})
        )
    atomic_write(output_path, serialize_jsonl(normalized))
    return {"posts": len(normalized), **dict(sorted(counter.items()))}


def manuscript_body(text: str) -> str:
    """Strip simple front matter from an author manuscript and return the Markdown body."""
    from goodprose.posts import _parse_front_matter

    _, body = _parse_front_matter(text)
    return body.strip()


def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def repair_code_blocks(snapshot: str, manuscript: str) -> tuple[str, int, list[str]]:
    """Restore fenced code in a flattened snapshot from the author's manuscript.

    For each fenced block in the manuscript, find the shortest run of snapshot lines whose
    whitespace-stripped concatenation equals the block's whitespace-stripped code, and replace
    that run (interior blank lines included) with the manuscript's fenced block verbatim. Blocks
    with no exact match are left alone and returned so the author can decide.
    """
    blocks = [
        (match.group(2).strip(), match.group(3))
        for match in _FENCED_BLOCK.finditer(manuscript)
        if match.group(3).strip()
    ]
    if not blocks:
        return snapshot, 0, []
    lines = snapshot.split("\n")
    squashed = [_squash(line) for line in lines]
    repaired = 0
    unmatched: list[str] = []
    search_from = 0
    for language, code in blocks:
        target = _squash(code)
        found: tuple[int, int] | None = None
        for start in range(search_from, len(lines)):
            if not squashed[start] or not target.startswith(squashed[start]):
                continue
            accumulated = ""
            for end in range(start, len(lines)):
                accumulated += squashed[end]
                if accumulated == target:
                    found = (start, end)
                    break
                if not target.startswith(accumulated):
                    break
            if found:
                break
        if found is None:
            unmatched.append(code.strip().splitlines()[0][:80])
            continue
        start, end = found
        fence = "```" + language
        lines[start : end + 1] = [fence, *code.split("\n"), "```"]
        squashed[start : end + 1] = [_squash(line) for line in lines[start : start + 1]] + [
            _squash(line) for line in lines[start + 1 : start + 2 + code.count("\n") + 1]
        ]
        squashed = [_squash(line) for line in lines]
        search_from = start + code.count("\n") + 2
        repaired += 1
    return "\n".join(lines), repaired, unmatched


_CODE_LINE = re.compile(
    r"^(?:"
    r"(?:func|type|var|const|import|package|return|defer|for|if|switch|case|select|go|break|"
    r"continue|else)\b.*"
    r"|//.*"
    r"|[\}\)\]]+[,;)]*"
    r"|.*(?::=|!=|==|<-|`json:|\bfunc\().*"
    r"|.*[\{\}\(;,]$"
    r"|[A-Za-z_]\w*\s+[\[\]\*]*[A-Za-z_][\w.]*(?:\s*`[^`]*`)?"  # struct field: Name Type
    r"|[A-Za-z_][\w.]*\([^()]*\).*"  # method or call: Name(args) ...
    r")$"
)
_TRAILING_COMMENT = re.compile(r"^(?!.*://).*\S\s+//\s.*$")
_PROSE_HINT = re.compile(r"[.!?]$")


def _looks_like_code(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith(("#", "- ", "* ", ">", "|", "[", "!")):
        return False
    if _PROSE_HINT.search(stripped) and len(stripped.split()) > 8:
        return False
    if _TRAILING_COMMENT.match(stripped):
        return True
    return bool(_CODE_LINE.match(stripped))


def _sandwiched(lines: list[str], index: int) -> bool:
    """A short, unpunctuated line whose next non-blank line is code belongs to the run."""
    stripped = lines[index].strip()
    if len(stripped.split()) > 4 or _PROSE_HINT.search(stripped):
        return False
    following = index + 1
    while following < len(lines) and lines[following].strip() == "":
        following += 1
    return following < len(lines) and _looks_like_code(lines[following])


def fence_code_runs(body: str, language: str, *, min_lines: int = 3) -> tuple[str, int]:
    """Wrap runs of code-looking prose lines in fences when no manuscript block matched.

    Public-page snapshots turn ``<pre>`` blocks into bare lines, sometimes with a blank line
    between each. This heuristic fences any run of at least ``min_lines`` code-looking lines
    (blank lines between them allowed and removed) and tags it with ``language``. It cannot
    restore whitespace the snapshot dropped; :func:`repair_code_blocks` is the exact tool and
    should run first.
    """
    pieces = _outside_fences(body)
    rebuilt: list[str] = []
    fenced_runs = 0
    for piece, is_code in pieces:
        if is_code:
            rebuilt.append(piece)
            continue
        lines = piece.split("\n")
        output: list[str] = []
        index = 0
        while index < len(lines):
            if not _looks_like_code(lines[index]):
                output.append(lines[index])
                index += 1
                continue
            run: list[str] = []
            cursor = index
            while cursor < len(lines):
                if lines[cursor].strip() == "":
                    cursor += 1
                    continue
                if not _looks_like_code(lines[cursor]) and not _sandwiched(lines, cursor):
                    break
                run.append(lines[cursor])
                cursor += 1
            # Give back trailing blank lines to the prose that follows.
            end = cursor
            while end > index and lines[end - 1].strip() == "":
                end -= 1
            if len(run) >= min_lines:
                output.extend([f"```{language}", *run, "```"])
                fenced_runs += 1
            else:
                output.extend(lines[index:end])
            index = end
        rebuilt.append("\n".join(output))
    return "".join(rebuilt), fenced_runs
