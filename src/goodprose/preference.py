"""Build DPO preference pairs: the author's published text against the model's own attempt."""

from __future__ import annotations

import json
from pathlib import Path

from goodprose.jsonl import atomic_write, load_jsonl, serialize_jsonl
from goodprose.models import GenerationRunManifest, ModelOutput, PreferencePair, Split
from goodprose.pairs import load_pairs
from goodprose.sft import SYSTEM_PROMPT


class PreferenceBuildError(ValueError):
    """Preference pairs cannot be assembled safely."""


def build_preference_pairs(
    pairs_path: Path,
    rejected_outputs_path: Path,
    output_path: Path,
    *,
    rejected_manifest_path: Path | None = None,
    rejected_run_id: str | None = None,
) -> dict[str, int]:
    """Join training pairs to sampled model outputs for the same inputs.

    ``rejected_outputs_path`` should come from ``eval generate`` run on the training cases
    that ``build-sft --train-cases-output`` writes, using the current SFT adapter so the
    negatives are on-policy. Rows whose sampled output equals the published text are skipped.
    Only training-split pairs are used; held-out inputs never enter preference data.
    """
    if rejected_manifest_path is not None:
        manifest = GenerationRunManifest.model_validate(
            json.loads(rejected_manifest_path.read_text(encoding="utf-8"))
        )
        if rejected_run_id is not None and rejected_run_id != manifest.run_id:
            raise PreferenceBuildError("rejected run id does not match the run manifest")
        rejected_run_id = manifest.run_id
    if not rejected_run_id:
        raise PreferenceBuildError("provide a rejected run manifest or an explicit run id")

    train_pairs = [pair for pair in load_pairs(pairs_path) if pair.split is Split.TRAIN]
    if not train_pairs:
        raise PreferenceBuildError("no training pairs found")
    rejected = {record.id: record for record in load_jsonl(rejected_outputs_path, ModelOutput)}
    missing = sorted(pair.id for pair in train_pairs if pair.id not in rejected)
    if missing:
        raise PreferenceBuildError(
            f"{len(missing)} training pair(s) have no rejected output: {', '.join(missing[:5])}"
        )
    extra = sorted(set(rejected) - {pair.id for pair in train_pairs})
    if extra:
        raise PreferenceBuildError(
            f"rejected outputs include non-training ids: {', '.join(extra[:5])}"
        )

    records: list[PreferencePair] = []
    skipped = 0
    for pair in train_pairs:
        rejected_text = rejected[pair.id].output
        if rejected_text.strip() == pair.output.strip():
            skipped += 1
            continue
        records.append(
            PreferencePair(
                id=pair.id,
                lineage_id=pair.lineage_id,
                prompt=(
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": pair.input},
                ),
                chosen=pair.output,
                rejected=rejected_text,
                rejected_run_id=rejected_run_id,
            )
        )
    if not records:
        raise PreferenceBuildError("every sampled output matched its published target")
    atomic_write(output_path, serialize_jsonl(records))
    return {"pairs": len(records), "skipped_identical": skipped}
