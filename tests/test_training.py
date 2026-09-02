from __future__ import annotations

import json
from pathlib import Path

import pytest

from goodprose.jsonl import atomic_write, atomic_write_json, serialize_jsonl
from goodprose.models import InputMethod, Split, WritingPair
from goodprose.sft import build_sft
from goodprose.training import TrainingError, prepare_lora_plus_run, run_lora_plus


def _pair(identifier: str, split: Split) -> WritingPair:
    return WritingPair(
        id=identifier,
        post_id=identifier,
        lineage_id=identifier,
        split=split,
        input=f"Outline for {identifier}",
        input_method=InputMethod.ORIGINAL_OUTLINE,
        title=f"Title {identifier}",
        output=f"Published output for {identifier}.",
    )


def _config(tmp_path: Path) -> Path:
    pair_path = tmp_path / "pairs.jsonl"
    sft_dir = tmp_path / "sft"
    atomic_write(
        pair_path,
        serialize_jsonl(
            [
                _pair("train", Split.TRAIN),
                _pair("dev", Split.DEV),
                _pair("test", Split.TEST),
            ]
        ),
    )
    build_sft(pair_path, sft_dir, tmp_path / "cases.jsonl")
    config_dir = tmp_path / "configs"
    config_path = config_dir / "lora-plus.json"
    atomic_write_json(
        config_path,
        {
            "version": 1,
            "model_id": "example/model",
            "train_file": "../sft/train.jsonl",
            "eval_file": "../sft/dev.jsonl",
            "dataset_manifest_file": "../sft/manifest.json",
            "output_dir": "../runs/example",
            "eval_strategy": "epoch",
            "learning_rate": 0.00005,
            "loraplus_lr_ratio": 16,
        },
    )
    return config_path


def test_prepare_lora_plus_run_validates_data_and_differential_rates(tmp_path: Path) -> None:
    config_path = _config(tmp_path)

    config, plan = prepare_lora_plus_run(config_path)

    assert config.train_file == tmp_path / "sft" / "train.jsonl"
    assert plan.train_examples == 1
    assert plan.eval_examples == 1
    assert plan.learning_rate_a == pytest.approx(0.00005)
    assert plan.learning_rate_b == pytest.approx(0.0008)
    assert len(plan.train_file_sha256) == 64
    assert len(plan.dataset_manifest_sha256 or "") == 64
    assert run_lora_plus(config_path, validate_only=True)["model_id"] == "example/model"


def test_prepare_lora_plus_run_rejects_stale_system_prompt(tmp_path: Path) -> None:
    config_path = _config(tmp_path)
    config = json.loads(config_path.read_text())
    train_path = (config_path.parent / config["train_file"]).resolve()
    atomic_write(
        train_path,
        serialize_jsonl(
            [
                {
                    "messages": [
                        {"role": "system", "content": "Old system prompt."},
                        {"role": "user", "content": "Outline"},
                        {"role": "assistant", "content": "Published prose."},
                    ]
                }
            ]
        ),
    )

    with pytest.raises(TrainingError, match="stale or unexpected system prompt"):
        prepare_lora_plus_run(config_path)
