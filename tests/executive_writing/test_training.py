from __future__ import annotations

import json
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from safetensors.numpy import save_file

from goodprose.executive_writing.smoke_data import compile_smoke_dataset
from goodprose.executive_writing.training import (
    load_training_config,
    parse_training_log,
    resolved_mlx_config,
    run_mlx_training,
    run_smoke_training,
)
from goodprose.executive_writing.unified_data import (
    AUTHORING_SYSTEM,
    CREATION_METHOD,
    GENRES,
    INTENDED_USE,
    PROFILES,
    RIGHTS_STATUS,
    compile_unified_dataset,
    normalized_sha256,
)
from goodprose.jsonl import sha256_file

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


def _synthetic_layout(slot: int) -> tuple[str, str]:
    split = "train" if slot < 60 else "valid" if slot < 75 else "test"
    if slot < 14:
        corpus = "preference_pair"
    elif slot < 28 or 60 <= slot < 64 or 75 <= slot < 79:
        corpus = "style_target"
    else:
        corpus = "task_pair"
    return split, corpus


def _synthetic_record(slot: int) -> dict[str, Any]:
    split, corpus = _synthetic_layout(slot)
    target = f"zzqx synthetic runner target slot {slot:03d} qtt{slot:03d}"
    record: dict[str, Any] = {
        "version": 1,
        "example_id": f"synthetic-runner-{slot:03d}",
        "lineage_group": f"synthetic-runner-lineage-{slot // 3:02d}",
        "split": split,
        "corpus": corpus,
        "profile_id": PROFILES[slot % 3],
        "genre": GENRES[slot % 7],
        "creation_method": CREATION_METHOD,
        "authoring_system": AUTHORING_SYSTEM,
        "rights_status": RIGHTS_STATUS,
        "intended_use": INTENDED_USE,
        "system_prompt": f"zzqx synthetic runner system {slot:03d}",
        "user_prompt": f"zzqx synthetic runner user {slot:03d}",
        "assistant_target": target if corpus != "preference_pair" else None,
        "preference": None,
        "system_sha256": "",
        "user_sha256": "",
        "target_sha256": "",
        "rejected_sha256": None,
        "source_provenance": {
            "ownership": "project_owned",
            "named_source": None,
            "external_source_used": False,
            "personal_private_data": False,
            "transformation_history": [f"synthetic runner fixture {slot:03d}"],
        },
    }
    if corpus == "preference_pair":
        record["assistant_target"] = None
        record["preference"] = {
            "chosen": f"zzqx synthetic runner chosen {slot:03d}",
            "rejected": f"zzqx synthetic runner rejected {slot:03d}",
            "rejection_reasons": ["verbosity"],
        }
        target = record["preference"]["chosen"]
        record["rejected_sha256"] = normalized_sha256(record["preference"]["rejected"])
    record["system_sha256"] = normalized_sha256(record["system_prompt"])
    record["user_sha256"] = normalized_sha256(record["user_prompt"])
    record["target_sha256"] = normalized_sha256(target)
    return record


def synthetic_source_lines() -> list[dict[str, Any]]:
    return [_synthetic_record(slot) for slot in range(90)]


def write_source(path: Path, records: list[dict[str, Any]]) -> Path:
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
    return path


def _refresh_manifest_dataset_hash(manifest: dict[str, Any]) -> None:
    digest = sha256()
    for name, split_hash in sorted(manifest["split_sha256"].items()):
        digest.update(f"{name}:{split_hash}\n".encode())
    manifest["dataset_sha256"] = digest.hexdigest()


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


def test_smoke_entry_points_are_aliases_of_the_generic_runner() -> None:
    assert run_smoke_training is run_mlx_training


SMOKE_OPTIMIZATION = {
    "batch_size": 1,
    "fine_tune_type": "lora",
    "grad_accumulation_steps": 1,
    "grad_checkpoint": False,
    "iterations": 40,
    "learning_rate": 0.0001,
    "mask_prompt": True,
    "max_seq_length": 1024,
    "num_layers": 4,
    "optimizer": "adam",
    "save_every": 20,
    "seed": 20260822,
    "steps_per_eval": 10,
    "steps_per_report": 5,
    "test_batches": -1,
    "validation_batches": -1,
}


def _write_unified_config(
    path: Path,
    *,
    manifest: dict[str, Any],
    manifest_path: Path,
    source_path: Path | None = None,
    run_kind: str = "unified_profile_conditioned_lora_pilot",
    ratios: tuple[float, float, float] = (54 / 90, 22 / 90, 14 / 90),
) -> Path:
    dataset: dict[str, Any] = {
        "dataset_id": "goodprose-project-authored-unified-pilot-v1",
        "dataset_sha256": manifest["dataset_sha256"],
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "split_sha256": {
            split: manifest["split_sha256"][split] for split in ("train", "valid", "test")
        },
        "preferences_sha256": manifest["split_sha256"]["preferences"],
        "rights_status": RIGHTS_STATUS,
        "intended_use": INTENDED_USE,
        "task_pairs_ratio": ratios[0],
        "style_targets_ratio": ratios[1],
        "preference_pairs_ratio": ratios[2],
    }
    if source_path is not None:
        dataset["source_records_path"] = str(source_path)
        dataset["source_records_sha256"] = sha256_file(source_path)
    config = {
        "version": 1,
        "experiment_id": "unified-pilot-mock-run-v1",
        "candidate_id": "qwen2.5-0.5b-unified-pilot-lora-v1",
        "run_kind": run_kind,
        "framework": {"name": "mlx-lm", "version": "0.31.3", "mlx_version": "0.32.1"},
        "base_model": {
            "repo_id": "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
            "revision": "a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3",
            "source_model_id": "Qwen/Qwen2.5-0.5B-Instruct",
            "license": "Apache-2.0",
            "quantization_bits": 4,
        },
        "dataset": dataset,
        "optimization": SMOKE_OPTIMIZATION,
        "lora": {"rank": 8, "scale": 20.0, "dropout": 0.0},
        "checkpoint_selection": "fixed_final_iteration",
        "expected_hardware": "Apple M3 Pro 18GiB unified memory",
        "timeout_seconds": 1800,
        "settled_cost_usd": 0,
    }
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def _compile_unified_pilot(tmp_path: Path) -> tuple[Path, Path, dict[str, Any]]:
    source_path = write_source(tmp_path / "source.jsonl", synthetic_source_lines())
    data_dir = tmp_path / "data"
    manifest_path = tmp_path / "unified-manifest.json"
    compile_unified_dataset(
        source_path=source_path,
        output_dir=data_dir,
        manifest_path=manifest_path,
        b1_cases_path=B1_CASES,
    )
    return data_dir, manifest_path, json.loads(manifest_path.read_text(encoding="utf-8"))


def _fake_model(tmp_path: Path) -> Path:
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "config.json").write_text('{"model_type":"qwen2"}\n', encoding="utf-8")
    save_file({"weight": np.ones((2, 2), dtype=np.float16)}, model_dir / "model.safetensors")
    return model_dir


def _successful_command(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    del kwargs
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


def test_mocked_unified_run_completes_with_full_evidence(tmp_path: Path) -> None:
    data_dir, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    config_path = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
        source_path=tmp_path / "source.jsonl",
    )

    def fake_snapshot(**kwargs: Any) -> str:
        del kwargs
        return str(_fake_model(tmp_path))

    run_dir = run_mlx_training(
        config_path=config_path,
        data_dir=data_dir,
        output_root=tmp_path / "runs",
        repo_root=tmp_path,
        code_revision="test-revision",
        started_at="2026-08-23T06:00:00Z",
        snapshot_downloader=fake_snapshot,
        command_runner=_successful_command,
    )
    manifest = json.loads((run_dir / "run-manifest.json").read_text(encoding="utf-8"))

    assert manifest["status"] == "completed"
    assert manifest["run_kind"] == "unified_profile_conditioned_lora_pilot"
    assert manifest["dataset"]["corpus_counts"] == {
        "preference_pair": 14,
        "style_target": 22,
        "task_pair": 54,
    }
    assert manifest["dataset"]["record_count"] == 90
    assert manifest["dataset"]["source_records_sha256"]
    assert manifest["training_metrics"]["final_trained_tokens"] == 7200
    assert manifest["adapter_artifacts"]["nonzero_tensor_count"] == 1
    assert manifest["settled_cost_usd"] == 0


def _failed_run_dir(tmp_path: Path) -> Path:
    runs = tmp_path / "runs"
    return next(runs.iterdir())


def _assert_failed(config_path: Path, data_dir: Path, tmp_path: Path, pattern: str) -> None:
    def failing_snapshot(**kwargs: Any) -> str:
        raise AssertionError("snapshot must not be reached")

    with pytest.raises(ValueError, match=pattern):
        run_mlx_training(
            config_path=config_path,
            data_dir=data_dir,
            output_root=tmp_path / "runs",
            repo_root=tmp_path,
            code_revision="test-revision",
            started_at="2026-08-23T06:10:00Z",
            snapshot_downloader=failing_snapshot,
            command_runner=_successful_command,
        )
    failed = json.loads(
        (_failed_run_dir(tmp_path) / "run-manifest.json").read_text(encoding="utf-8")
    )
    assert failed["status"] == "failed"


def test_unified_run_rejects_tampered_split_bytes_and_preserves_failure(
    tmp_path: Path,
) -> None:
    data_dir, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    train = data_dir / "train.jsonl"
    train.write_bytes(train.read_bytes() + b"tampered\n")
    config_path = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
    )
    _assert_failed(config_path, data_dir, tmp_path, "train split hash")


def test_unified_run_rejects_tampered_record_metadata_even_with_matching_hash(
    tmp_path: Path,
) -> None:
    data_dir, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    train_path = data_dir / "train.jsonl"
    rows = [json.loads(line) for line in train_path.read_text(encoding="utf-8").splitlines()]
    rows[0]["metadata"]["rights_status"] = "training_permitted_project_owned_smoke"
    train_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    unified_manifest["split_sha256"]["train"] = sha256_file(train_path)
    _refresh_manifest_dataset_hash(unified_manifest)
    manifest_path.write_text(
        json.dumps(unified_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    config_path = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
    )
    _assert_failed(config_path, data_dir, tmp_path, "rights_status")


def test_unified_run_rejects_tampered_preference_metadata(tmp_path: Path) -> None:
    data_dir, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    preferences_path = data_dir / "preferences.jsonl"
    rows = [json.loads(line) for line in preferences_path.read_text(encoding="utf-8").splitlines()]
    rows[0]["metadata"]["rejection_reasons"] = []
    preferences_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    unified_manifest["split_sha256"]["preferences"] = sha256_file(preferences_path)
    _refresh_manifest_dataset_hash(unified_manifest)
    manifest_path.write_text(
        json.dumps(unified_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    config_path = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
    )
    _assert_failed(config_path, data_dir, tmp_path, "preference metadata requires reasons")


def test_unified_run_rejects_preference_content_that_differs_from_split(
    tmp_path: Path,
) -> None:
    data_dir, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    preferences_path = data_dir / "preferences.jsonl"
    rows = [json.loads(line) for line in preferences_path.read_text(encoding="utf-8").splitlines()]
    replacement_history = ["synthetic runner fixture deliberately altered"]
    rows[0]["metadata"]["transformation_history"] = replacement_history
    rows[0]["metadata"]["source_provenance"]["transformation_history"] = replacement_history
    preferences_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    unified_manifest["split_sha256"]["preferences"] = sha256_file(preferences_path)
    _refresh_manifest_dataset_hash(unified_manifest)
    manifest_path.write_text(
        json.dumps(unified_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    config_path = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
    )
    _assert_failed(config_path, data_dir, tmp_path, "content disagrees")


def test_unified_run_rejects_manifest_split_hash_that_config_does_not_trust(
    tmp_path: Path,
) -> None:
    data_dir, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    unified_manifest["split_sha256"]["train"] = "0" * 64
    manifest_path.write_text(
        json.dumps(unified_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    config_path = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
    )
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["dataset"]["split_sha256"]["train"] = sha256_file(data_dir / "train.jsonl")
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _assert_failed(config_path, data_dir, tmp_path, "manifest train split hash")


def test_unified_run_rejects_tampered_declared_source_hash(tmp_path: Path) -> None:
    data_dir, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    config_payload = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
        source_path=tmp_path / "source.jsonl",
    )
    payload = json.loads(config_payload.read_text(encoding="utf-8"))
    payload["dataset"]["source_records_sha256"] = "0" * 64
    config_payload.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _assert_failed(config_payload, data_dir, tmp_path, "source-records hash")


def test_unified_run_rejects_manifest_source_hash_mismatch(tmp_path: Path) -> None:
    data_dir, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    unified_manifest["source_records_sha256"] = "0" * 64
    manifest_path.write_text(
        json.dumps(unified_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    config_path = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
        source_path=tmp_path / "source.jsonl",
    )
    _assert_failed(config_path, data_dir, tmp_path, "manifest source-records hash")


@pytest.mark.parametrize(
    ("mutate", "pattern"),
    [
        (
            lambda d: d.update(run_kind="pipeline_smoke_fine_tune"),
            "does not match dataset",
        ),
        (
            lambda d: d["dataset"].update(task_pairs_ratio=0.7),
            "exact ratios",
        ),
    ],
)
def test_invalid_cross_combinations_are_rejected(tmp_path: Path, mutate: Any, pattern: str) -> None:
    _, manifest_path, unified_manifest = _compile_unified_pilot(tmp_path)
    config_path = _write_unified_config(
        tmp_path / "unified-config.json",
        manifest=unified_manifest,
        manifest_path=manifest_path,
    )
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    mutate(payload)
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with pytest.raises(Exception, match=pattern):
        load_training_config(config_path)


def test_smoke_dataset_with_unified_run_kind_is_rejected(tmp_path: Path) -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    payload["run_kind"] = "unified_profile_conditioned_lora_pilot"
    config_path = tmp_path / "cross-config.json"
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with pytest.raises(Exception, match="does not match dataset"):
        load_training_config(config_path)
