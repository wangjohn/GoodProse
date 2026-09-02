from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from goodprose.jsonl import atomic_write, serialize_jsonl
from goodprose.models import (
    BlogPost,
    EvalCase,
    InputMethod,
    ModelOutput,
    Split,
    SplitAssignment,
)
from goodprose.proxy import (
    ProxyError,
    function_word_distance,
    proxy_report,
    style_distance,
    style_features,
)

AUTHOR_TEXT = (
    "I think the honest answer is that most tools are built for engineers, by engineers. "
    "That's fine, but it means the person closest to the problem (usually not an engineer) "
    "gets left out. We noticed this at work. It's probably the most common failure I see.\n\n"
    "So we built something small. It isn't clever, and it doesn't need to be."
)
GENERIC_TEXT = (
    "In today's rapidly evolving technological landscape, organizations must leverage "
    "innovative solutions to empower stakeholders. Furthermore, it is essential to "
    "recognize that comprehensive frameworks facilitate optimal outcomes across teams. "
    "Additionally, robust methodologies ensure scalable, sustainable transformation."
)


def test_style_features_report_rates_per_thousand_words() -> None:
    features = style_features(AUTHOR_TEXT)

    assert features["words"] == len(AUTHOR_TEXT.split())
    assert features["sentences"] >= 6
    assert features["paragraphs"] == 2
    assert features["parenthetical_per_1k"] > 0
    assert features["contraction_per_1k"] > 0
    assert features["first_singular_per_1k"] > features["second_person_per_1k"]
    assert features["repeated_4gram_share"] == 0


def test_style_distance_prefers_text_that_resembles_the_author() -> None:
    reference = style_features(AUTHOR_TEXT * 3)
    close = style_features(AUTHOR_TEXT)
    far = style_features(GENERIC_TEXT)

    assert style_distance(close, reference) < style_distance(far, reference)
    assert function_word_distance(close, reference) < function_word_distance(far, reference)


def _case(case_id: str, reference: str) -> EvalCase:
    return EvalCase(
        id=case_id,
        lineage_id=case_id,
        input="Notes: build a small tool for the people closest to the problem.",
        input_method=InputMethod.ORIGINAL_DRAFT,
        reference_output=reference,
        target_sha256=hashlib.sha256(reference.encode()).hexdigest(),
    )


def test_proxy_report_ranks_systems_and_flags_regurgitated_training_text(
    tmp_path: Path,
) -> None:
    train_post = BlogPost(
        id="train", lineage_id="train", title="Train", body_markdown=AUTHOR_TEXT, source_path="t.md"
    )
    test_post = BlogPost(
        id="test", lineage_id="test", title="Test", body_markdown="Held out.", source_path="h.md"
    )
    posts_path = tmp_path / "posts.jsonl"
    splits_path = tmp_path / "splits.jsonl"
    cases_path = tmp_path / "cases.jsonl"
    atomic_write(posts_path, serialize_jsonl([train_post, test_post]))
    atomic_write(
        splits_path,
        serialize_jsonl(
            [
                SplitAssignment(
                    lineage_id="train", split=Split.TRAIN, frozen_at=date(2026, 9, 1), rationale="t"
                ),
                SplitAssignment(
                    lineage_id="test", split=Split.TEST, frozen_at=date(2026, 9, 1), rationale="h"
                ),
            ]
        ),
    )
    atomic_write(cases_path, serialize_jsonl([_case("test", "The published held-out post.")]))
    close_path = tmp_path / "close.jsonl"
    far_path = tmp_path / "far.jsonl"
    atomic_write(close_path, serialize_jsonl([ModelOutput(id="test", output=AUTHOR_TEXT)]))
    atomic_write(far_path, serialize_jsonl([ModelOutput(id="test", output=GENERIC_TEXT)]))

    report = proxy_report(
        cases_path,
        [("far", far_path), ("close", close_path)],
        posts_path,
        splits_path,
        tmp_path / "proxy.json",
        memorization_run_threshold=10,
    )

    assert report["ranking"] == ["close", "far"]
    close = next(system for system in report["systems"] if system["label"] == "close")
    assert close["memorization_flags"] == 1
    assert close["per_case"][0]["longest_training_post_run"] >= 10
    assert json.loads((tmp_path / "proxy.json").read_text())["ranking"] == ["close", "far"]


def test_proxy_report_requires_outputs(tmp_path: Path) -> None:
    with pytest.raises(ProxyError, match="at least one"):
        proxy_report(
            tmp_path / "cases.jsonl", [], tmp_path / "p.jsonl", tmp_path / "s.jsonl", tmp_path / "o"
        )
