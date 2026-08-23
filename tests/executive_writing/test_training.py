from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
from safetensors.numpy import save_file

from goodprose.executive_writing.smoke_data import compile_smoke_dataset
from goodprose.executive_writing.training import (
    load_training_config,
    parse_training_log,
    resolved_mlx_config,
    run_smoke_training,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = (
    REPO_ROOT
    / "programs"
    / "executive-writing"
    / "configs"
    / "training"
    / "qwen2.5-0.5b-mlx-lora-smoke-v1.json"
)
B1_CASES = REPO_ROOT / "evals" / "executive-writing" / "goodprose-b1-v1" / "cases.jsonl"


def test_training_config_is_pinned_and_smoke_labeled() -> None:
    config = load_training_config(CONFIG)

    assert config.run_kind == "pipeline_smoke_fine_tune"
    assert config.framework.version == "0.31.3"
    assert config.base_model.revision == "a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3"
    assert config.optimization.iterations == 40
    assert config.optimization.mask_prompt is True
    assert config.checkpoint_selection == "fixed_final_iteration"
    assert config.settled_cost_usd == 0


def test_resolved_mlx_config_preserves_frozen_parameters(tmp_path: Path) -> None:
    config = load_training_config(CONFIG)
    resolved = resolved_mlx_config(
        config,
        model_path=tmp_path / "model",
        data_dir=tmp_path / "data",
        adapter_path=tmp_path / "adapters",
    )

    assert resolved["model"] == str(tmp_path / "model")
    assert resolved["train"] is True
    assert resolved["test"] is True
    assert resolved["iters"] == 40
    assert resolved["lora_parameters"] == {"dropout": 0.0, "rank": 8, "scale": 20.0}


def test_parse_training_log_extracts_losses_tokens_and_memory() -> None:
    log = (
        "Iter 1: Val loss 2.500, Val took 1.200s\n"
        "Iter 5: Train loss 2.100, Learning Rate 1.000e-04, It/sec 3.200, "
        "Tokens/sec 456.700, Trained Tokens 900, Peak mem 1.234 GB\n"
        "Iter 40: Val loss 1.700, Val took 1.100s\n"
        "Iter 40: Train loss 1.500, Learning Rate 1.000e-04, It/sec 3.500, "
        "Tokens/sec 500.000, Trained Tokens 7200, Peak mem 1.456 GB\n"
        "Test loss 1.800, Test ppl 6.050.\n"
    )

    parsed = parse_training_log(log)

    assert parsed["final_trained_tokens"] == 7200
    assert parsed["peak_memory_gb"] == 1.456
    assert parsed["validation_reports"][-1]["validation_loss"] == 1.7
    assert parsed["test"] == {"loss": 1.8, "perplexity": 6.05}


def test_mocked_training_run_writes_complete_manifest(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    compile_smoke_dataset(
        output_dir=data_dir,
        manifest_path=tmp_path / "rebuilt-manifest.json",
        b1_cases_path=B1_CASES,
    )
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "config.json").write_text('{"model_type":"qwen2"}\n', encoding="utf-8")
    save_file({"weight": np.ones((2, 2), dtype=np.float16)}, model_dir / "model.safetensors")

    def fake_snapshot(**kwargs: Any) -> str:
        assert kwargs["revision"] == "a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3"
        return str(model_dir)

    def fake_command(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        assert kwargs["check"] is False
        resolved = json.loads(Path(command[-1]).read_text(encoding="utf-8"))
        adapter_dir = Path(resolved["adapter_path"])
        adapter_dir.mkdir()
        save_file(
            {"layers.0.lora_a": np.ones((2, 2), dtype=np.float16)},
            adapter_dir / "adapters.safetensors",
        )
        (adapter_dir / "adapter_config.json").write_text("{}\n", encoding="utf-8")
        log = (
            "Iter 40: Train loss 1.500, Learning Rate 1.000e-04, It/sec 3.500, "
            "Tokens/sec 500.000, Trained Tokens 7200, Peak mem 1.456 GB\n"
            "Test loss 1.800, Test ppl 6.050.\n"
        )
        return subprocess.CompletedProcess(command, 0, stdout=log)

    run_dir = run_smoke_training(
        config_path=CONFIG,
        data_dir=data_dir,
        output_root=tmp_path / "runs",
        repo_root=REPO_ROOT,
        code_revision="test-revision",
        started_at="2026-08-23T05:10:00Z",
        snapshot_downloader=fake_snapshot,
        command_runner=fake_command,
    )
    manifest = json.loads((run_dir / "run-manifest.json").read_text(encoding="utf-8"))

    assert manifest["status"] == "completed"
    assert manifest["training_metrics"]["final_trained_tokens"] == 7200
    assert manifest["adapter_artifacts"]["nonzero_tensor_count"] == 1
    assert manifest["settled_cost_usd"] == 0
