"""Validate and render synthetic prompt candidates for human review."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from goodprose.chunks import _markdown_fence
from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import (
    DRAFT_PROMPT_FORMS,
    BlogPost,
    InputMethod,
    PairTextExclusion,
    ReviewStatus,
    SemanticChunk,
    Split,
    SyntheticPromptCandidate,
    SyntheticPromptDraft,
    WritingPair,
)
from goodprose.pairs import load_pairs, validate_pairs
from goodprose.roles import load_training_roles, role_for, venue_line_for_post
from goodprose.sft import SYSTEM_PROMPT
from goodprose.text import URL, longest_shared_word_run

_PROMOTIONAL_CTA = re.compile(
    r"(?i)(?:"
    r"we[\N{RIGHT SINGLE QUOTATION MARK}']?re hiring|we are hiring|assembled is hiring|"
    r"check out our (?:open )?(?:roles|positions)|come join us|"
    r"apply (?:on|through) our careers|interested in joining the team|"
    r"interested in helping us|(?:email|reach out to) me at john@assembled|"
    r"join(?:ing)? our team|reach out if|john@assembled|assembled\.com/careers|"
    r"i really hope you like it"
    r")"
)


class PromptReviewError(ValueError):
    """Synthetic prompts do not safely match the frozen training chunks."""


def system_prompt_sha256() -> str:
    """Hash of the system prompt every approved example is trained and evaluated with."""
    return hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()


def _system_prompt_section() -> list[str]:
    """The exact system turn, quoted once, so approval covers the whole conversation."""
    return [
        "## System prompt",
        "",
        "Every record below is trained as this system turn, then the input, then the exact",
        "completion. Approving a record approves the whole conversation, not the input alone.",
        "",
        "```text",
        SYSTEM_PROMPT,
        "```",
        "",
        f"SHA-256: `{system_prompt_sha256()}`",
        "",
    ]


def _urls(value: str) -> set[str]:
    return {match.group(0).rstrip(".,;:") for match in URL.finditer(value)}


_longest_shared_word_run = longest_shared_word_run


def _candidate_chunk_map(
    candidates: list[SyntheticPromptCandidate], chunks: list[SemanticChunk]
) -> dict[str, SemanticChunk]:
    chunk_counts = Counter(chunk.id for chunk in chunks)
    duplicate_chunks = sorted(chunk_id for chunk_id, count in chunk_counts.items() if count > 1)
    if duplicate_chunks:
        raise PromptReviewError(f"duplicate chunk id(s): {', '.join(duplicate_chunks)}")

    candidate_counts = Counter(candidate.id for candidate in candidates)
    duplicate_candidates = sorted(
        candidate_id for candidate_id, count in candidate_counts.items() if count > 1
    )
    if duplicate_candidates:
        raise PromptReviewError(
            f"duplicate prompt candidate id(s): {', '.join(duplicate_candidates)}"
        )

    form_counts = Counter(
        (candidate.chunk_id, candidate.prompt_form.value) for candidate in candidates
    )
    repeated_forms = sorted(
        f"{chunk_id}:{form}" for (chunk_id, form), count in form_counts.items() if count > 1
    )
    if repeated_forms:
        raise PromptReviewError(
            "multiple prompt candidates use the same form for the same chunk: "
            + ", ".join(repeated_forms)
        )

    chunks_by_id = {chunk.id: chunk for chunk in chunks}
    for candidate in candidates:
        chunk = chunks_by_id.get(candidate.chunk_id)
        if chunk is None:
            raise PromptReviewError(
                f"prompt candidate {candidate.id!r} references missing chunk {candidate.chunk_id!r}"
            )
        if chunk.split is not Split.TRAIN or candidate.split is not Split.TRAIN:
            raise PromptReviewError(
                f"prompt candidate {candidate.id!r} must reference a training chunk"
            )
        expected = (chunk.post_id, chunk.lineage_id, chunk.split, chunk.target_sha256)
        actual = (
            candidate.post_id,
            candidate.lineage_id,
            candidate.split,
            candidate.target_sha256,
        )
        if actual != expected:
            raise PromptReviewError(
                f"prompt candidate {candidate.id!r} does not match chunk metadata or target hash"
            )
        missing_urls = sorted(_urls(chunk.target) - _urls(candidate.input))
        if missing_urls:
            raise PromptReviewError(
                f"prompt candidate {candidate.id!r} is missing target source URL(s): "
                + ", ".join(missing_urls)
            )
        missing_code = [
            block for block in _fenced_code(chunk.target) if block not in candidate.input
        ]
        if missing_code:
            raise PromptReviewError(
                f"prompt candidate {candidate.id!r} must carry the target's code block(s) "
                f"verbatim so the model copies code rather than composing it; missing "
                f"{len(missing_code)} block(s) starting {missing_code[0].splitlines()[0][:60]!r}"
            )
    return chunks_by_id


_FENCED = re.compile(r"^(`{3,}|~{3,})[^\n]*\n(.*?)\n\1[ \t]*$", re.MULTILINE | re.DOTALL)


def _fenced_code(target: str) -> list[str]:
    """The inner text of every fenced block in a target."""
    return [match.group(2).strip() for match in _FENCED.finditer(target) if match.group(2).strip()]


def render_prompt_review(
    candidates: list[SyntheticPromptCandidate],
    chunks: list[SemanticChunk],
    posts: list[BlogPost] | None = None,
    roles_path: Path | None = None,
) -> bytes:
    """Render prompts beside exact completions after validating lineage and hashes."""
    chunks_by_id = _candidate_chunk_map(candidates, chunks)
    posts_by_id = {post.id: post for post in posts} if posts else {}
    roles = load_training_roles(roles_path)
    form_counts = Counter(candidate.prompt_form.value for candidate in candidates)
    lines = [
        "# Synthetic prompt candidate review",
        "",
        "These inputs were reverse-engineered from published training targets. They are",
        "unreviewed derived briefs, not canonical SFT examples. No development or test target",
        "was used. Every completion below remains the author's exact published text.",
        "",
        *_system_prompt_section(),
        "## Approval rubric",
        "",
        "- The input resembles notes or instructions you might genuinely have written,",
        "  including the roughness of your real drafts (typos, fragments, bullet dumps).",
        "- It contains the facts needed by the completion without prescribing finished prose.",
        "- Its level of detail matches the requested transformation.",
        "- Distinctive target phrasing has not leaked into the input unnecessarily; the",
        "  `rough_draft` and `near_final_draft` forms are the exception and may share long runs.",
        "- Several forms may target one chunk; each (chunk, form) pair appears at most once.",
        "- The system prompt above is part of every example: judge the input as the user turn",
        "  that follows it, and re-review if that system prompt ever changes.",
        "- Edit the JSONL candidate directly; approval and canonicalization happen later.",
        "",
        f"Candidates: {len(candidates)}",
        "",
        "Forms: " + ", ".join(f"{key}={form_counts[key]}" for key in sorted(form_counts)),
        "",
    ]
    for candidate in candidates:
        chunk = chunks_by_id[candidate.chunk_id]
        shared_run = _longest_shared_word_run(candidate.input, chunk.target)
        if candidate.prompt_form in DRAFT_PROMPT_FORMS:
            leakage_note = " - draft form; long shared runs are expected"
        else:
            leakage_note = " - inspect for copying" if shared_run >= 8 else ""
        prompt_fence = _markdown_fence(candidate.input)
        target_fence = _markdown_fence(chunk.target)
        lines.extend(
            [
                f"## {candidate.id}",
                "",
                f"Form: `{candidate.prompt_form.value}`  ",
                f"Chunk: `{candidate.chunk_id}`  ",
                f"System prompt: `{system_prompt_sha256()[:12]}` (the one quoted above)  ",
                *(
                    [
                        "Venue line prepended at export: "
                        f"`{venue_line_for_post(posts_by_id[candidate.post_id], roles)}`  "
                    ]
                    if candidate.post_id in posts_by_id
                    else []
                ),
                f"Longest exact shared word run (URLs excluded): {shared_run}{leakage_note}",
                "",
                "### Synthetic input",
                "",
                f"{prompt_fence}text",
                candidate.input,
                prompt_fence,
                "",
                "### Exact completion",
                "",
                f"{target_fence}markdown",
                chunk.target,
                target_fence,
                "",
            ]
        )
    return ("\n".join(lines).rstrip() + "\n").encode()


def build_prompt_review(
    prompts_path: Path,
    chunks_path: Path,
    output_path: Path,
    *,
    posts_path: Path | None = None,
    roles_path: Path | None = None,
) -> int:
    candidates = load_jsonl(prompts_path, SyntheticPromptCandidate)
    chunks = load_jsonl(chunks_path, SemanticChunk)
    posts = load_jsonl(posts_path, BlogPost) if posts_path is not None else None
    atomic_write(
        output_path, render_prompt_review(candidates, chunks, posts, roles_path=roles_path)
    )
    return len(candidates)


def approve_prompt_candidates(
    prompts_path: Path,
    chunks_path: Path,
    *,
    reviewer_note: str,
) -> dict[str, int]:
    """Approve reviewed training prompts and only their referenced exact chunks."""
    candidates = load_jsonl(prompts_path, SyntheticPromptCandidate)
    chunks = load_jsonl(chunks_path, SemanticChunk)
    _candidate_chunk_map(candidates, chunks)
    note = reviewer_note.strip()
    if not note:
        raise PromptReviewError("reviewer note must not be empty")

    approved_candidates = [
        candidate.model_copy(
            update={
                "review_status": ReviewStatus.APPROVED,
                "approved_system_prompt_sha256": system_prompt_sha256(),
                "reviewer_notes": (
                    candidate.reviewer_notes
                    if note in candidate.reviewer_notes
                    else (*candidate.reviewer_notes, note)
                ),
            }
        )
        for candidate in candidates
    ]
    referenced_chunk_ids = {candidate.chunk_id for candidate in candidates}
    approved_chunks = [
        chunk.model_copy(update={"review_status": ReviewStatus.APPROVED})
        if chunk.id in referenced_chunk_ids
        else chunk
        for chunk in chunks
    ]
    atomic_write(prompts_path, serialize_jsonl(approved_candidates))
    atomic_write(chunks_path, serialize_jsonl(approved_chunks))
    return {
        "prompts": len(approved_candidates),
        "chunks": len(referenced_chunk_ids),
    }


def build_prompt_candidates(
    drafts_path: Path,
    chunks_path: Path,
    output_path: Path,
    *,
    base_prompts_path: Path | None = None,
    replace_lineages: Sequence[str] = (),
) -> int:
    """Attach frozen chunk metadata to compact, human-authored prompt drafts."""
    drafts = load_jsonl(drafts_path, SyntheticPromptDraft)
    chunks = load_jsonl(chunks_path, SemanticChunk)
    chunks_by_id = {chunk.id: chunk for chunk in chunks}
    training_lineages = {chunk.lineage_id for chunk in chunks if chunk.split is Split.TRAIN}
    requested_lineages = set(replace_lineages)
    unknown_lineages = sorted(requested_lineages - training_lineages)
    if unknown_lineages:
        raise PromptReviewError(
            "replacement lineage(s) are not in the training chunks: " + ", ".join(unknown_lineages)
        )
    draft_counts = Counter((draft.chunk_id, draft.prompt_form.value) for draft in drafts)
    duplicates = sorted(
        f"{chunk_id}:{form}" for (chunk_id, form), count in draft_counts.items() if count > 1
    )
    if duplicates:
        raise PromptReviewError(
            f"duplicate prompt draft chunk/form pair(s): {', '.join(duplicates)}"
        )

    generated: list[SyntheticPromptCandidate] = []
    for draft in drafts:
        chunk = chunks_by_id.get(draft.chunk_id)
        if chunk is None:
            raise PromptReviewError(f"prompt draft references missing chunk {draft.chunk_id!r}")
        if chunk.split is not Split.TRAIN:
            raise PromptReviewError(f"prompt draft {draft.chunk_id!r} must target a training chunk")
        generated.append(
            SyntheticPromptCandidate(
                id=f"{chunk.id}--{draft.prompt_form.value}",
                chunk_id=chunk.id,
                post_id=chunk.post_id,
                lineage_id=chunk.lineage_id,
                split=chunk.split,
                prompt_form=draft.prompt_form,
                input=draft.input,
                target_sha256=chunk.target_sha256,
            )
        )

    replaced_forms = set(draft_counts)
    base = (
        load_jsonl(base_prompts_path, SyntheticPromptCandidate)
        if base_prompts_path is not None
        else []
    )
    candidates = [
        candidate
        for candidate in base
        if (candidate.chunk_id, candidate.prompt_form.value) not in replaced_forms
        and candidate.lineage_id not in requested_lineages
        and candidate.chunk_id in chunks_by_id
        and chunks_by_id[candidate.chunk_id].split is Split.TRAIN
    ]
    candidates.extend(generated)
    candidates.sort(key=lambda candidate: candidate.id)
    _candidate_chunk_map(candidates, chunks)
    atomic_write(output_path, serialize_jsonl(candidates))
    return len(candidates)


def _require_approved(
    candidates: list[SyntheticPromptCandidate], chunks_by_id: dict[str, SemanticChunk]
) -> None:
    pending_prompts = sorted(
        candidate.id
        for candidate in candidates
        if candidate.review_status is not ReviewStatus.APPROVED
    )
    pending_chunks = sorted(
        candidate.chunk_id
        for candidate in candidates
        if chunks_by_id[candidate.chunk_id].review_status is not ReviewStatus.APPROVED
    )
    stale_system_prompt = sorted(
        candidate.id
        for candidate in candidates
        if candidate.review_status is ReviewStatus.APPROVED
        and candidate.approved_system_prompt_sha256 != system_prompt_sha256()
    )
    findings: list[str] = []
    if stale_system_prompt:
        findings.append(
            f"{len(stale_system_prompt)} prompt candidate(s) were approved against a different "
            "system prompt; re-review and re-run approve-prompts: "
            + ", ".join(stale_system_prompt[:3])
        )
    if pending_prompts:
        findings.append(
            f"{len(pending_prompts)} prompt candidate(s) are not approved: "
            + ", ".join(pending_prompts[:3])
        )
    if pending_chunks:
        findings.append(
            f"{len(pending_chunks)} semantic chunk(s) are not approved: "
            + ", ".join(pending_chunks[:3])
        )
    if findings:
        raise PromptReviewError("; ".join(findings))


def _reject_promotional_training_material(
    candidates: list[SyntheticPromptCandidate], chunks_by_id: dict[str, SemanticChunk]
) -> None:
    promotional = sorted(
        candidate.id
        for candidate in candidates
        if _PROMOTIONAL_CTA.search(candidate.input)
        or _PROMOTIONAL_CTA.search(chunks_by_id[candidate.chunk_id].target)
    )
    if promotional:
        raise PromptReviewError(
            "training prompt/target contains a promotional or hiring call to action: "
            + ", ".join(promotional[:5])
        )


def _reject_promotional_pairs(pairs: list[WritingPair]) -> None:
    promotional = sorted(
        pair.id
        for pair in pairs
        if _PROMOTIONAL_CTA.search(pair.input) or _PROMOTIONAL_CTA.search(pair.output)
    )
    if promotional:
        raise PromptReviewError(
            "canonical pair input/target contains a promotional or hiring call to action: "
            + ", ".join(promotional[:5])
        )


def _apply_pair_text_exclusions(
    pairs: list[WritingPair], exclusions_path: Path | None
) -> list[WritingPair]:
    if exclusions_path is None:
        return pairs
    exclusions = load_jsonl(exclusions_path, PairTextExclusion)
    pairs_by_id = {pair.id: pair for pair in pairs}
    seen: set[tuple[str, str, str]] = set()
    for exclusion in exclusions:
        key = (exclusion.pair_id, exclusion.field, exclusion.text)
        if key in seen:
            raise PromptReviewError(f"duplicate pair text exclusion for {exclusion.pair_id!r}")
        seen.add(key)
        pair = pairs_by_id.get(exclusion.pair_id)
        if pair is None:
            raise PromptReviewError(
                f"pair text exclusion references missing pair {exclusion.pair_id!r}"
            )
        value = getattr(pair, exclusion.field)
        occurrences = value.count(exclusion.text)
        if occurrences != 1:
            raise PromptReviewError(
                f"pair text exclusion for {exclusion.pair_id!r} field "
                f"{exclusion.field!r} matched {occurrences} times instead of exactly once"
            )
        updated = value.replace(exclusion.text, "", 1)
        if not updated.strip():
            raise PromptReviewError(
                f"pair text exclusion emptied {exclusion.pair_id!r} field {exclusion.field!r}"
            )
        pairs_by_id[pair.id] = pair.model_copy(update={exclusion.field: updated})
    return [pairs_by_id[pair.id] for pair in pairs]


def build_prompt_pairs(
    prompts_path: Path,
    chunks_path: Path,
    posts_path: Path,
    output_path: Path,
    *,
    heldout_pairs_paths: Sequence[Path] = (),
    text_exclusions_path: Path | None = None,
    roles_path: Path | None = None,
) -> dict[str, int]:
    """Promote approved training prompts and exact chunks into canonical pairs.

    Training roles gate which posts may supply supervised pairs: ``raw_only`` and ``excluded``
    posts are rejected here (they may still enter the raw-completion mix at export), and
    ``excluded`` development pairs are dropped. Test pairs are never affected.
    """
    candidates = load_jsonl(prompts_path, SyntheticPromptCandidate)
    if not candidates:
        raise PromptReviewError("prompt candidate dataset is empty")
    roles = load_training_roles(roles_path)
    demoted = sorted(
        f"{candidate.id} ({role_for(candidate.post_id, roles)})"
        for candidate in candidates
        if role_for(candidate.post_id, roles) != "pairs"
    )
    if demoted:
        raise PromptReviewError(
            f"{len(demoted)} prompt candidate(s) target posts whose training role is not "
            "'pairs'; drop them from the candidate file: " + ", ".join(demoted[:3])
        )
    chunks = load_jsonl(chunks_path, SemanticChunk)
    chunks_by_id = _candidate_chunk_map(candidates, chunks)
    _reject_promotional_training_material(candidates, chunks_by_id)
    _require_approved(candidates, chunks_by_id)

    posts = load_jsonl(posts_path, BlogPost)
    posts_by_id = {post.id: post for post in posts}
    if len(posts_by_id) != len(posts):
        raise PromptReviewError("canonical post file contains duplicate post IDs")

    pairs: list[WritingPair] = []
    for candidate in candidates:
        chunk = chunks_by_id[candidate.chunk_id]
        post = posts_by_id.get(candidate.post_id)
        if post is None:
            raise PromptReviewError(
                f"prompt candidate {candidate.id!r} references missing post {candidate.post_id!r}"
            )
        if post.lineage_id != candidate.lineage_id:
            raise PromptReviewError(
                f"prompt candidate {candidate.id!r} does not match canonical post lineage"
            )
        pairs.append(
            WritingPair(
                id=candidate.id,
                post_id=post.id,
                lineage_id=post.lineage_id,
                split=Split.TRAIN,
                input=candidate.input,
                input_method=InputMethod.DERIVED_BRIEF,
                title=post.title,
                output=chunk.target,
                source_url=post.source_url,
                published_at=post.published_at,
            )
        )

    for heldout_pairs_path in heldout_pairs_paths:
        heldout = load_pairs(heldout_pairs_path)
        training_heldout = sorted(pair.id for pair in heldout if pair.split is Split.TRAIN)
        if training_heldout:
            raise PromptReviewError(
                "held-out pair file contains training records: " + ", ".join(training_heldout[:3])
            )
        for pair in heldout:
            if pair.split is Split.DEV and role_for(pair.post_id, roles) == "excluded":
                continue
            pairs.extend([pair])

    pairs = _apply_pair_text_exclusions(pairs, text_exclusions_path)
    _reject_promotional_pairs(pairs)
    validate_pairs(pairs)
    pairs.sort(key=lambda pair: pair.id)
    atomic_write(output_path, serialize_jsonl(pairs))
    return {split.value: sum(pair.split is split for pair in pairs) for split in Split}
