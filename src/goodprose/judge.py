"""Blinded pairwise judge packets for a frontier model, and their unblinded summary.

The judge is asked one narrow question, "which response is more likely written by the author
of these samples", with the author's published training posts as the only evidence. It is a
ranking proxy for the inner loop, deliberately kept apart from the human review packet.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from goodprose.evaluation import EvaluationError
from goodprose.jsonl import atomic_write, atomic_write_json, load_jsonl, serialize_jsonl
from goodprose.models import (
    BlogPost,
    EvalCase,
    ModelOutput,
    ReviewAssignment,
    ReviewChoice,
    ReviewKey,
    Split,
    SplitAssignment,
    StrictModel,
    SystemLabel,
)
from goodprose.text import words

JUDGE_INSTRUCTIONS = """You are comparing two candidate blog passages against samples of one \
author's published writing. Judge only voice and craft: sentence rhythm, word choice, how \
claims are hedged, how paragraphs open and close, how examples are used. Ignore which \
response is longer, ignore formatting differences, and do not reward polish that the author's \
samples do not show. Do not judge factual accuracy.

Answer with a single JSON object and nothing else:
{"more_like_author": "a" | "b" | "tie", "confidence": 0.0-1.0, "reason": "one or two sentences"}"""


class JudgeVerdict(StrictModel):
    id: str
    more_like_author: ReviewChoice
    confidence: float | None = None
    reason: str | None = None


def _author_samples(
    posts_path: Path, splits_path: Path, *, count: int, sample_words: int, seed: int
) -> list[tuple[str, str]]:
    splits = {
        assignment.lineage_id: assignment.split
        for assignment in load_jsonl(splits_path, SplitAssignment)
    }
    train_posts = [
        post
        for post in load_jsonl(posts_path, BlogPost)
        if splits.get(post.lineage_id) is Split.TRAIN
    ]
    if len(train_posts) < count:
        raise EvaluationError(f"need at least {count} training posts for author samples")
    chosen = random.Random(seed).sample(sorted(train_posts, key=lambda post: post.id), count)
    samples: list[tuple[str, str]] = []
    for post in chosen:
        tokens = post.body_markdown.split()
        excerpt = " ".join(tokens[:sample_words])
        if len(tokens) > sample_words:
            excerpt += " […]"
        samples.append((post.title, excerpt))
    return samples


def render_judge_prompt(
    samples: list[tuple[str, str]], case: EvalCase, response_a: str, response_b: str
) -> str:
    parts = [JUDGE_INSTRUCTIONS, "", "# Author samples"]
    for index, (title, excerpt) in enumerate(samples, start=1):
        parts.extend(["", f"## Sample {index}: {title}", "", excerpt])
    parts.extend(
        [
            "",
            "# The brief both responses were written from",
            "",
            case.input,
            "",
            "# Response A",
            "",
            response_a,
            "",
            "# Response B",
            "",
            response_b,
            "",
            "Which response is more likely written by the author of the samples? Reply with the "
            "JSON object only.",
        ]
    )
    return "\n".join(parts)


def build_judge_packet(
    cases_path: Path,
    baseline_path: Path,
    candidate_path: Path,
    posts_path: Path,
    splits_path: Path,
    packet_path: Path,
    key_path: Path,
    *,
    seed: int = 20260902,
    sample_count: int = 3,
    sample_words: int = 400,
) -> int:
    cases = {case.id: case for case in load_jsonl(cases_path, EvalCase)}
    if not cases:
        raise EvaluationError("evaluation case file is empty")
    baseline = {record.id: record for record in load_jsonl(baseline_path, ModelOutput)}
    candidate = {record.id: record for record in load_jsonl(candidate_path, ModelOutput)}
    for label, outputs in (("baseline", baseline), ("candidate", candidate)):
        missing = sorted(set(cases) - set(outputs))
        if missing:
            raise EvaluationError(f"{label} outputs are missing cases {missing}")
    samples = _author_samples(
        posts_path, splits_path, count=sample_count, sample_words=sample_words, seed=seed
    )
    randomizer = random.Random(seed)
    rows: list[dict[str, Any]] = []
    assignments: list[ReviewAssignment] = []
    for case_id in sorted(cases):
        if randomizer.getrandbits(1):
            a_label, b_label = SystemLabel.CANDIDATE, SystemLabel.BASELINE
            response_a, response_b = candidate[case_id].output, baseline[case_id].output
        else:
            a_label, b_label = SystemLabel.BASELINE, SystemLabel.CANDIDATE
            response_a, response_b = baseline[case_id].output, candidate[case_id].output
        rows.append(
            {
                "id": case_id,
                "prompt": render_judge_prompt(samples, cases[case_id], response_a, response_b),
                "response_a_words": len(words(response_a)),
                "response_b_words": len(words(response_b)),
            }
        )
        assignments.append(ReviewAssignment(id=case_id, a=a_label, b=b_label))
    atomic_write(packet_path, serialize_jsonl(rows))
    atomic_write_json(
        key_path,
        ReviewKey(seed=seed, assignments=tuple(assignments)).model_dump(mode="json"),
    )
    return len(rows)


def summarize_judge_verdicts(
    verdicts_path: Path, key_path: Path, output_path: Path
) -> dict[str, Any]:
    import json

    key = ReviewKey.model_validate(json.loads(key_path.read_text(encoding="utf-8")))
    assignments = {assignment.id: assignment for assignment in key.assignments}
    verdicts = {verdict.id: verdict for verdict in load_jsonl(verdicts_path, JudgeVerdict)}
    missing = sorted(set(assignments) - set(verdicts))
    if missing:
        raise EvaluationError(f"judge verdicts are missing cases {missing}")
    wins = {SystemLabel.BASELINE.value: 0, SystemLabel.CANDIDATE.value: 0, "tie": 0}
    per_case: list[dict[str, Any]] = []
    for case_id in sorted(assignments):
        assignment = assignments[case_id]
        verdict = verdicts[case_id]
        if verdict.more_like_author is ReviewChoice.TIE:
            winner = "tie"
        elif verdict.more_like_author is ReviewChoice.A:
            winner = assignment.a.value
        else:
            winner = assignment.b.value
        wins[winner] += 1
        per_case.append(
            {
                "id": case_id,
                "winner": winner,
                "confidence": verdict.confidence,
                "reason": verdict.reason,
            }
        )
    summary = {
        "version": 1,
        "case_count": len(per_case),
        "voice_wins": wins,
        "candidate_win_rate": wins[SystemLabel.CANDIDATE.value] / len(per_case),
        "per_case": per_case,
    }
    atomic_write_json(output_path, summary)
    return summary
