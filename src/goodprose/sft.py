"""Build chat-style SFT files and frozen test cases from canonical pairs."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any

from goodprose.jsonl import atomic_write, atomic_write_json, serialize_jsonl, sha256_file
from goodprose.models import EvalCase, Split, WritingPair
from goodprose.pairs import PairBuildError, load_pairs

SYSTEM_PROMPT = (
    "Turn the supplied notes, outline, or rough draft into polished blog prose at the scope "
    "requested by the user: a paragraph, section, or complete post. Preserve supported facts "
    "and uncertainty, do not invent details, honor the requested structure and length, and "
    "return only the finished prose."
)


def _sft_record(pair: WritingPair) -> dict[str, Any]:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": pair.input},
            {"role": "assistant", "content": pair.output},
        ]
    }


def build_sft(pair_path: Path, output_dir: Path, eval_output: Path) -> dict[str, int]:
    pairs = load_pairs(pair_path)
    counts = Counter(pair.split for pair in pairs)
    if not counts[Split.TRAIN]:
        raise PairBuildError("at least one train pair is required")
    if not counts[Split.TEST]:
        raise PairBuildError("at least one test pair is required")

    train = [_sft_record(pair) for pair in pairs if pair.split == Split.TRAIN]
    dev = [_sft_record(pair) for pair in pairs if pair.split == Split.DEV]
    cases = [
        EvalCase(
            id=pair.id,
            lineage_id=pair.lineage_id,
            input=pair.input,
            input_method=pair.input_method,
            reference_output=pair.output,
            target_sha256=hashlib.sha256(pair.output.encode()).hexdigest(),
            source_url=pair.source_url,
        )
        for pair in pairs
        if pair.split == Split.TEST
    ]

    atomic_write(output_dir / "train.jsonl", serialize_jsonl(train))
    atomic_write(output_dir / "dev.jsonl", serialize_jsonl(dev))
    atomic_write(eval_output, serialize_jsonl(cases))
    train_path = output_dir / "train.jsonl"
    dev_path = output_dir / "dev.jsonl"
    summary = {split.value: counts[split] for split in Split}
    atomic_write_json(
        output_dir / "manifest.json",
        {
            "version": 1,
            "pair_file": pair_path.name,
            "pair_file_sha256": sha256_file(pair_path),
            "system_prompt": SYSTEM_PROMPT,
            "system_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
            "counts": summary,
            "test_cases": eval_output.name,
            "train_file_sha256": sha256_file(train_path),
            "dev_file_sha256": sha256_file(dev_path),
            "test_cases_sha256": sha256_file(eval_output),
        },
    )
    return summary
