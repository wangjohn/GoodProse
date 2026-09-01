"""Build chat-style SFT files and frozen test cases from canonical pairs."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from goodprose.jsonl import atomic_write, atomic_write_json, serialize_jsonl, sha256_file
from goodprose.models import EvalCase, Split, WritingPair
from goodprose.pairs import PairBuildError, load_pairs

SYSTEM_PROMPT = (
    "Turn the supplied notes, outline, or rough draft into a finished blog post. "
    "Preserve supported facts and uncertainty, do not invent details, and return only the post."
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
            input=pair.input,
            reference_output=pair.output,
            source_url=pair.source_url,
        )
        for pair in pairs
        if pair.split == Split.TEST
    ]

    atomic_write(output_dir / "train.jsonl", serialize_jsonl(train))
    atomic_write(output_dir / "dev.jsonl", serialize_jsonl(dev))
    atomic_write(eval_output, serialize_jsonl(cases))
    summary = {split.value: counts[split] for split in Split}
    atomic_write_json(
        output_dir / "manifest.json",
        {
            "version": 1,
            "pair_file": pair_path.name,
            "pair_file_sha256": sha256_file(pair_path),
            "system_prompt": SYSTEM_PROMPT,
            "counts": summary,
            "test_cases": eval_output.name,
        },
    )
    return summary
