from __future__ import annotations

import json
from pathlib import Path

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import EvalCase, InputMethod, Split, WritingPair
from goodprose.sft import SYSTEM_PROMPT, build_sft


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

    assert counts == {"train": 1, "dev": 1, "test": 1}
    train_record = json.loads((output_dir / "train.jsonl").read_text().strip())
    assert train_record["messages"][0]["content"] == SYSTEM_PROMPT
    assert "paragraph, section, or complete post" in SYSTEM_PROMPT
    assert "do not invent details" in SYSTEM_PROMPT
    assert "test-post" not in (output_dir / "train.jsonl").read_text()
    assert "test-post" not in (output_dir / "dev.jsonl").read_text()
    cases = load_jsonl(eval_output, EvalCase)
    assert [case.id for case in cases] == ["test-post"]
    manifest = json.loads((output_dir / "manifest.json").read_text())
    assert len(manifest["train_file_sha256"]) == 64
    assert len(manifest["dev_file_sha256"]) == 64
    assert len(manifest["test_cases_sha256"]) == 64
