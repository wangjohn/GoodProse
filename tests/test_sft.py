from __future__ import annotations

import json
from pathlib import Path

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import EvalCase, InputMethod, Split, WritingPair
from goodprose.sft import RAW_COMPLETION_PROMPT, SYSTEM_PROMPT, build_sft


def _pair(identifier: str, split: Split) -> WritingPair:
    return WritingPair(
        id=identifier,
        post_id=identifier,
        lineage_id=identifier,
        split=split,
        input=f"Outline for {identifier}",
        input_method=InputMethod.ORIGINAL_OUTLINE,
        title=f"Title {identifier}",
        output=f"# Title {identifier}\n\nPublished output.",
    )


def test_builds_train_dev_and_frozen_test_cases(tmp_path: Path) -> None:
    pair_path = tmp_path / "pairs.jsonl"
    output_dir = tmp_path / "sft"
    eval_output = tmp_path / "evals" / "cases.jsonl"
    atomic_write(
        pair_path,
        serialize_jsonl(
            [
                _pair("train-post", Split.TRAIN),
                _pair("dev-post", Split.DEV),
                _pair("test-post", Split.TEST),
            ]
        ),
    )

    counts = build_sft(pair_path, output_dir, eval_output)

    assert counts == {"train": 1, "train_pairs": 1, "raw_completions": 0, "dev": 1, "test": 1}
    train_record = json.loads((output_dir / "train.jsonl").read_text().strip())
    assert train_record["messages"][0]["content"] == SYSTEM_PROMPT
    assert "sentence, paragraph, section, or complete post" in SYSTEM_PROMPT
    assert "do not invent details" in SYSTEM_PROMPT
    assert "test-post" not in (output_dir / "train.jsonl").read_text()
    assert "test-post" not in (output_dir / "dev.jsonl").read_text()
    cases = load_jsonl(eval_output, EvalCase)
    assert [case.id for case in cases] == ["test-post"]
    manifest = json.loads((output_dir / "manifest.json").read_text())
    assert len(manifest["train_file_sha256"]) == 64
    assert len(manifest["dev_file_sha256"]) == 64
    assert len(manifest["test_cases_sha256"]) == 64


def test_raw_completions_add_one_record_per_distinct_training_target(tmp_path: Path) -> None:
    pair_path = tmp_path / "pairs.jsonl"
    output_dir = tmp_path / "sft"
    duplicate_target = _pair("train-post-bullets", Split.TRAIN).model_copy(
        update={
            "post_id": "train-post",
            "lineage_id": "train-post",
            "title": "Title train-post",
            "output": "# Title train-post\n\nPublished output.",
        }
    )
    atomic_write(
        pair_path,
        serialize_jsonl(
            [
                _pair("train-post", Split.TRAIN),
                duplicate_target,
                _pair("test-post", Split.TEST),
            ]
        ),
    )

    counts = build_sft(
        pair_path,
        output_dir,
        tmp_path / "cases.jsonl",
        raw_completions=True,
        train_cases_output=tmp_path / "train-cases.jsonl",
    )

    assert counts["train_pairs"] == 2
    assert counts["raw_completions"] == 1
    assert counts["train"] == 3
    records = [json.loads(line) for line in (output_dir / "train.jsonl").read_text().splitlines()]
    raw = records[-1]["messages"]
    assert raw[1]["content"] == RAW_COMPLETION_PROMPT.format(title="Title train-post")
    assert raw[2]["content"] == "# Title train-post\n\nPublished output."
    train_cases = load_jsonl(tmp_path / "train-cases.jsonl", EvalCase)
    assert [case.id for case in train_cases] == ["train-post", "train-post-bullets"]
    manifest = json.loads((output_dir / "manifest.json").read_text())
    assert manifest["counts"]["train"] == 3
    assert len(manifest["train_cases_sha256"]) == 64
