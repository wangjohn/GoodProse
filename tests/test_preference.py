from __future__ import annotations

from pathlib import Path

import pytest

from goodprose.jsonl import atomic_write, atomic_write_json, load_jsonl, serialize_jsonl
from goodprose.models import InputMethod, ModelOutput, PreferencePair, Split, WritingPair
from goodprose.preference import PreferenceBuildError, build_preference_pairs
from goodprose.sft import SYSTEM_PROMPT


def _pair(identifier: str, split: Split) -> WritingPair:
    return WritingPair(
        id=identifier,
        post_id=identifier,
        lineage_id=identifier,
        split=split,
        input=f"Notes for {identifier}",
        input_method=InputMethod.DERIVED_BRIEF,
        title=f"Title {identifier}",
        output=f"Published prose for {identifier}.",
    )


def test_build_preference_pairs_uses_published_text_as_chosen(tmp_path: Path) -> None:
    pairs_path = tmp_path / "pairs.jsonl"
    rejected_path = tmp_path / "rejected.jsonl"
    output_path = tmp_path / "preference.jsonl"
    atomic_write(
        pairs_path,
        serialize_jsonl([_pair("a", Split.TRAIN), _pair("b", Split.TRAIN), _pair("t", Split.TEST)]),
    )
    atomic_write(
        rejected_path,
        serialize_jsonl(
            [
                ModelOutput(id="a", output="A generic model attempt."),
                ModelOutput(id="b", output="Published prose for b."),
            ]
        ),
    )

    counts = build_preference_pairs(
        pairs_path, rejected_path, output_path, rejected_run_id="sft-epoch-3"
    )

    assert counts == {"pairs": 1, "skipped_identical": 1}
    [record] = load_jsonl(output_path, PreferencePair)
    assert record.chosen == "Published prose for a."
    assert record.rejected == "A generic model attempt."
    assert record.prompt[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert record.prompt[1]["content"] == "Notes for a"
    assert record.rejected_run_id == "sft-epoch-3"


def test_build_preference_pairs_rejects_missing_and_heldout_outputs(tmp_path: Path) -> None:
    pairs_path = tmp_path / "pairs.jsonl"
    rejected_path = tmp_path / "rejected.jsonl"
    atomic_write(pairs_path, serialize_jsonl([_pair("a", Split.TRAIN), _pair("t", Split.TEST)]))
    atomic_write(
        rejected_path,
        serialize_jsonl(
            [ModelOutput(id="a", output="x"), ModelOutput(id="t", output="held-out leak")]
        ),
    )

    with pytest.raises(PreferenceBuildError, match="non-training ids"):
        build_preference_pairs(pairs_path, rejected_path, tmp_path / "o.jsonl", rejected_run_id="r")

    atomic_write(rejected_path, serialize_jsonl([]))
    with pytest.raises(PreferenceBuildError, match="have no rejected output"):
        build_preference_pairs(pairs_path, rejected_path, tmp_path / "o.jsonl", rejected_run_id="r")


def test_build_preference_pairs_takes_run_id_from_manifest(tmp_path: Path) -> None:
    pairs_path = tmp_path / "pairs.jsonl"
    rejected_path = tmp_path / "rejected.jsonl"
    manifest_path = tmp_path / "rejected-run.json"
    atomic_write(pairs_path, serialize_jsonl([_pair("a", Split.TRAIN), _pair("t", Split.TEST)]))
    atomic_write(rejected_path, serialize_jsonl([ModelOutput(id="a", output="attempt")]))
    atomic_write_json(
        manifest_path,
        {
            "version": 1,
            "run_id": "checkpoint-9",
            "role": "candidate",
            "model_id": "m",
            "base_model_id": "m",
            "base_model_revision": "r",
            "tokenizer_revision": "r",
            "adapter_id": "adapter@sha256:abc",
            "prompt_strategy": "matched-system-prompt:{}",
            "chat_template_sha256": "0" * 64,
            "system_prompt_sha256": "0" * 64,
            "cases_sha256": "0" * 64,
            "dataset_manifest_sha256": "0" * 64,
            "decoding": {"max_new_tokens": 10, "seed": 1},
        },
    )

    counts = build_preference_pairs(
        pairs_path, rejected_path, tmp_path / "o.jsonl", rejected_manifest_path=manifest_path
    )

    assert counts["pairs"] == 1
    assert load_jsonl(tmp_path / "o.jsonl", PreferencePair)[0].rejected_run_id == "checkpoint-9"
