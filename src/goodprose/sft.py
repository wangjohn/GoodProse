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
    "requested by the user: a sentence, paragraph, section, or complete post. Preserve supported "
    "facts and uncertainty, do not invent details, honor the requested structure and length, "
    "and return only the finished prose."
)

# A deliberately thin prompt: these records exist to teach the unconditional statistics of
# the author's prose (rhythm, hedges, paragraph shape), the way continued pretraining would.
RAW_COMPLETION_PROMPT = "Write a passage from the blog post titled “{title}”."


def _sft_record(pair: WritingPair) -> dict[str, Any]:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": pair.input},
            {"role": "assistant", "content": pair.output},
        ]
    }


def _raw_completion_record(pair: WritingPair) -> dict[str, Any]:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": RAW_COMPLETION_PROMPT.format(title=pair.title)},
            {"role": "assistant", "content": pair.output},
        ]
    }


def raw_completion_records(train_pairs: list[WritingPair]) -> list[dict[str, Any]]:
    """One title-conditioned completion per distinct training target.

    Several prompts may share a target once multiple prompt forms exist per chunk; the raw
    view is emitted once per distinct target text so it does not multiply with them.
    """
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for pair in train_pairs:
        digest = hashlib.sha256(pair.output.encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        records.append(_raw_completion_record(pair))
    return records


def _eval_case(pair: WritingPair) -> EvalCase:
    return EvalCase(
        id=pair.id,
        lineage_id=pair.lineage_id,
        input=pair.input,
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
) -> dict[str, int]:
    """Write train/dev JSONL, the frozen test cases, and a hash-pinned manifest.

    ``raw_completions`` appends promptless-style completions of every distinct training
    target. ``train_cases_output`` writes the training inputs in the evaluation case format so
    the current model can be sampled on them to produce on-policy rejected responses for
    preference optimisation.
    """
    pairs = load_pairs(pair_path)
    counts = Counter(pair.split for pair in pairs)
    if not counts[Split.TRAIN]:
        raise PairBuildError("at least one train pair is required")
    if not counts[Split.TEST]:
        raise PairBuildError("at least one test pair is required")

    train_pairs = [pair for pair in pairs if pair.split == Split.TRAIN]
    train = [_sft_record(pair) for pair in train_pairs]
    raw = raw_completion_records(train_pairs) if raw_completions else []
    train.extend(raw)
    dev = [_sft_record(pair) for pair in pairs if pair.split == Split.DEV]
    cases = [_eval_case(pair) for pair in pairs if pair.split == Split.TEST]

    atomic_write(output_dir / "train.jsonl", serialize_jsonl(train))
    atomic_write(output_dir / "dev.jsonl", serialize_jsonl(dev))
    atomic_write(eval_output, serialize_jsonl(cases))
    if train_cases_output is not None:
        atomic_write(
            train_cases_output,
            serialize_jsonl([_eval_case(pair) for pair in train_pairs]),
        )
    if dev_cases_output is not None:
        atomic_write(
            dev_cases_output,
            serialize_jsonl([_eval_case(pair) for pair in pairs if pair.split == Split.DEV]),
        )
    train_path = output_dir / "train.jsonl"
    dev_path = output_dir / "dev.jsonl"
    summary = {
        "train": len(train),
        "train_pairs": counts[Split.TRAIN],
        "raw_completions": len(raw),
        "dev": counts[Split.DEV],
        "test": counts[Split.TEST],
    }
    manifest: dict[str, Any] = {
        "version": 2,
        "pair_file": pair_path.name,
        "pair_file_sha256": sha256_file(pair_path),
        "system_prompt": SYSTEM_PROMPT,
        "system_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "raw_completion_prompt": RAW_COMPLETION_PROMPT,
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
