from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from goodprose.jsonl import atomic_write, serialize_jsonl
from goodprose.judge import build_judge_packet, summarize_judge_verdicts
from goodprose.models import (
    BlogPost,
    EvalCase,
    InputMethod,
    ModelOutput,
    ReviewKey,
    Split,
    SplitAssignment,
)


def _post(post_id: str, split_body: str) -> BlogPost:
    return BlogPost(
        id=post_id,
        lineage_id=post_id,
        title=f"Title {post_id}",
        body_markdown=split_body,
        source_path=f"{post_id}.md",
    )


def test_judge_packet_is_blinded_and_summary_unblinds(tmp_path: Path) -> None:
    posts = [_post(f"train-{index}", f"Author words {index}. " * 20) for index in range(3)]
    posts.append(_post("test", "Held out post."))
    assignments = [
        SplitAssignment(
            lineage_id=post.id,
            split=Split.TEST if post.id == "test" else Split.TRAIN,
            frozen_at=date(2026, 9, 1),
            rationale="frozen",
        )
        for post in posts
    ]
    reference = "Held out post."
    case = EvalCase(
        id="test",
        lineage_id="test",
        input="Notes.",
        input_method=InputMethod.ORIGINAL_DRAFT,
        reference_output=reference,
        target_sha256=hashlib.sha256(reference.encode()).hexdigest(),
    )
    paths = {name: tmp_path / f"{name}.jsonl" for name in ("posts", "splits", "cases", "b", "c")}
    atomic_write(paths["posts"], serialize_jsonl(posts))
    atomic_write(paths["splits"], serialize_jsonl(assignments))
    atomic_write(paths["cases"], serialize_jsonl([case]))
    atomic_write(paths["b"], serialize_jsonl([ModelOutput(id="test", output="BASELINE TEXT")]))
    atomic_write(paths["c"], serialize_jsonl([ModelOutput(id="test", output="CANDIDATE TEXT")]))
    packet_path = tmp_path / "judge.jsonl"
    key_path = tmp_path / "judge-key.json"

    count = build_judge_packet(
        paths["cases"],
        paths["b"],
        paths["c"],
        paths["posts"],
        paths["splits"],
        packet_path,
        key_path,
    )

    assert count == 1
    row = json.loads(packet_path.read_text())
    assert "baseline" not in row["prompt"].lower().replace("baseline text", "")
    assert "Author words 0." in row["prompt"] or "Author words 1." in row["prompt"]
    key = ReviewKey.model_validate(json.loads(key_path.read_text()))
    candidate_letter = "a" if key.assignments[0].a.value == "candidate" else "b"

    verdicts_path = tmp_path / "verdicts.jsonl"
    atomic_write(
        verdicts_path,
        serialize_jsonl([{"id": "test", "more_like_author": candidate_letter, "confidence": 0.8}]),
    )
    summary = summarize_judge_verdicts(verdicts_path, key_path, tmp_path / "summary.json")

    assert summary["voice_wins"] == {"baseline": 0, "candidate": 1, "tie": 0}
    assert summary["candidate_win_rate"] == 1.0
