"""Build chat-style SFT files and frozen test cases from canonical pairs."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any

from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    load_jsonl,
    serialize_jsonl,
    sha256_file,
)
from goodprose.models import BlogPost, EvalCase, SemanticChunk, Split, WritingPair
from goodprose.pairs import PairBuildError, load_pairs
from goodprose.roles import (
    TrainingRole,
    load_training_roles,
    raw_weight_for,
    role_for,
    venue_line,
)

SYSTEM_PROMPT = (
    "Turn the supplied notes, outline, or rough draft into polished blog prose at the scope "
    "requested by the user: a sentence, paragraph, section, or complete post. Preserve supported "
    "facts and uncertainty, do not invent details, honor the requested structure and length, "
    "and return only the finished prose."
)

# A deliberately thin prompt: these records exist to teach the unconditional statistics of
# the author's prose (rhythm, hedges, paragraph shape), the way continued pretraining would.
RAW_COMPLETION_PROMPT = "Write a passage from the blog post titled “{title}”."


def _venue(pair: WritingPair, roles: dict[str, TrainingRole]) -> str:
    role = roles.get(pair.post_id)
    return venue_line(pair.source_url, pair.published_at, role.venue_note if role else None)


def user_content(pair: WritingPair, roles: dict[str, TrainingRole], *, venue_lines: bool) -> str:
    """The user turn: an optional venue line, then the reviewed input."""
    venue = _venue(pair, roles) if venue_lines else ""
    return f"{venue}\n\n{pair.input}" if venue else pair.input


def _record(user: str, completion: str) -> dict[str, Any]:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
            {"role": "assistant", "content": completion},
        ]
    }


def _raw_user(title: str, venue: str | None) -> str:
    prompt = RAW_COMPLETION_PROMPT.format(title=title)
    return f"{venue}\n\n{prompt}" if venue else prompt


def _is_full_post_pair(pair: WritingPair) -> bool:
    """Whether a promoted prompt pair targets the deterministic ``--full`` chunk.

    Prompt-pair IDs inherit their chunk ID as a prefix during promotion. Keeping this check on
    the pair, rather than its target hash, lets a section with text identical to a short full post
    retain its raw-completion record.
    """
    return pair.id.startswith(f"{pair.post_id}--full--")


def raw_completion_records(
    train_pairs: list[WritingPair],
    roles: dict[str, TrainingRole],
    *,
    venue_lines: bool,
    raw_only_chunks: list[tuple[SemanticChunk, BlogPost]] = (),  # type: ignore[assignment]
) -> list[dict[str, Any]]:
    """One title-conditioned completion per distinct eligible training target.

    Covers section- and sentence-scale supervised targets plus every training chunk of a
    ``raw_only`` post, each distinct text once per unit of its post's ``raw_weight``. Full-post
    supervised pairs are omitted because their long target is already present under a reviewed
    brief; full-post chunks from ``raw_only`` posts remain eligible because they have no supervised
    pair. This lets editor-revised registers still teach sentence-level habits under their own
    venue line and allows the personal-site voice to be weighted up without duplicating its full
    posts under a weak title-only prompt.
    """
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for pair in train_pairs:
        if _is_full_post_pair(pair):
            continue
        digest = hashlib.sha256(pair.output.encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        venue = _venue(pair, roles) if venue_lines else None
        records.extend(
            [_record(_raw_user(pair.title, venue), pair.output)]
            * raw_weight_for(pair.post_id, roles)
        )
    for chunk, post in raw_only_chunks:
        digest = hashlib.sha256(chunk.target.encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        role = roles.get(post.id)
        venue = (
            venue_line(post.source_url, post.published_at, role.venue_note if role else None)
            if venue_lines
            else None
        )
        records.extend(
            [_record(_raw_user(post.title, venue), chunk.target)] * raw_weight_for(post.id, roles)
        )
    return records


def _eval_case(pair: WritingPair, roles: dict[str, TrainingRole], *, venue_lines: bool) -> EvalCase:
    return EvalCase(
        id=pair.id,
        lineage_id=pair.lineage_id,
        input=user_content(pair, roles, venue_lines=venue_lines),
        input_method=pair.input_method,
        reference_output=pair.output,
        target_sha256=hashlib.sha256(pair.output.encode()).hexdigest(),
        source_url=pair.source_url,
    )


def build_sft(
    pair_path: Path,
    output_dir: Path,
    eval_output: Path,
    *,
    raw_completions: bool = False,
    train_cases_output: Path | None = None,
    dev_cases_output: Path | None = None,
    roles_path: Path | None = None,
    chunks_path: Path | None = None,
    posts_path: Path | None = None,
    venue_lines: bool = True,
) -> dict[str, int]:
    """Write train/dev JSONL, the frozen test cases, and a hash-pinned manifest.

    ``raw_completions`` appends promptless-style completions of every distinct sentence- or
    section-scale supervised training target, and with
    ``chunks_path``/``posts_path``/``roles_path`` also of every training chunk (including full
    posts) of a ``raw_only`` post. Reviewed supervised full-post targets are not duplicated under
    a title-only prompt. ``venue_lines`` prepends ``Venue: host (year)`` to every user turn so
    register is a condition the model learns, not an average. ``train_cases_output`` writes the
    training inputs in the evaluation case format for on-policy rejected sampling.
    """
    pairs = load_pairs(pair_path)
    roles = load_training_roles(roles_path)
    dropped = sorted(
        pair.id
        for pair in pairs
        if pair.split is not Split.TEST and role_for(pair.post_id, roles) != "pairs"
    )
    pairs = [pair for pair in pairs if pair.id not in set(dropped)]
    counts = Counter(pair.split for pair in pairs)
    if not counts[Split.TRAIN]:
        raise PairBuildError("at least one train pair is required")
    if not counts[Split.TEST]:
        raise PairBuildError("at least one test pair is required")

    raw_only_chunks: list[tuple[SemanticChunk, BlogPost]] = []
    if raw_completions and chunks_path is not None and posts_path is not None:
        posts_by_id = {post.id: post for post in load_jsonl(posts_path, BlogPost)}
        for chunk in load_jsonl(chunks_path, SemanticChunk):
            if chunk.split is Split.TRAIN and role_for(chunk.post_id, roles) == "raw_only":
                raw_only_chunks.append((chunk, posts_by_id[chunk.post_id]))

    train_pairs = [pair for pair in pairs if pair.split == Split.TRAIN]
    train = [
        _record(user_content(pair, roles, venue_lines=venue_lines), pair.output)
        for pair in train_pairs
    ]
    raw = (
        raw_completion_records(
            train_pairs, roles, venue_lines=venue_lines, raw_only_chunks=raw_only_chunks
        )
        if raw_completions
        else []
    )
    train.extend(raw)
    dev = [
        _record(user_content(pair, roles, venue_lines=venue_lines), pair.output)
        for pair in pairs
        if pair.split == Split.DEV
    ]
    cases = [
        _eval_case(pair, roles, venue_lines=venue_lines)
        for pair in pairs
        if pair.split == Split.TEST
    ]

    atomic_write(output_dir / "train.jsonl", serialize_jsonl(train))
    atomic_write(output_dir / "dev.jsonl", serialize_jsonl(dev))
    atomic_write(eval_output, serialize_jsonl(cases))
    if train_cases_output is not None:
        atomic_write(
            train_cases_output,
            serialize_jsonl(
                [_eval_case(pair, roles, venue_lines=venue_lines) for pair in train_pairs]
            ),
        )
    if dev_cases_output is not None:
        atomic_write(
            dev_cases_output,
            serialize_jsonl(
                [
                    _eval_case(pair, roles, venue_lines=venue_lines)
                    for pair in pairs
                    if pair.split == Split.DEV
                ]
            ),
        )
    train_path = output_dir / "train.jsonl"
    dev_path = output_dir / "dev.jsonl"
    summary = {
        "train": len(train),
        "train_pairs": counts[Split.TRAIN],
        "raw_completions": len(raw),
        "raw_only_chunks": len(raw_only_chunks),
        "dropped_by_role": len(dropped),
        "dev": counts[Split.DEV],
        "test": counts[Split.TEST],
    }
    manifest: dict[str, Any] = {
        "version": 3,
        "pair_file": pair_path.name,
        "pair_file_sha256": sha256_file(pair_path),
        "system_prompt": SYSTEM_PROMPT,
        "system_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "raw_completion_prompt": RAW_COMPLETION_PROMPT,
        "raw_completion_policy": "non-full-pairs-plus-all-raw-only-chunks",
        "venue_lines": venue_lines,
        "training_roles_sha256": sha256_file(roles_path) if roles_path is not None else None,
        "dropped_by_role": dropped,
        "counts": summary,
        "test_cases": eval_output.name,
        "train_file_sha256": sha256_file(train_path),
        "dev_file_sha256": sha256_file(dev_path),
        "test_cases_sha256": sha256_file(eval_output),
    }
    if train_cases_output is not None:
        manifest["train_cases"] = train_cases_output.name
        manifest["train_cases_sha256"] = sha256_file(train_cases_output)
    if dev_cases_output is not None:
        manifest["dev_cases"] = dev_cases_output.name
        manifest["dev_cases_sha256"] = sha256_file(dev_cases_output)
    atomic_write_json(output_dir / "manifest.json", manifest)
    return summary
