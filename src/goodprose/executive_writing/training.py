"""Config-driven MLX smoke training with complete local run manifests."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import datetime
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Annotated, Any, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.jsonl import atomic_write, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
GitRevision = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FrameworkConfig(StrictModel):
    name: Literal["mlx-lm"]
    version: Literal["0.31.3"]
    mlx_version: Literal["0.32.1"]


class BaseModelConfig(StrictModel):
    repo_id: Literal["mlx-community/Qwen2.5-0.5B-Instruct-4bit"]
    revision: GitRevision
    source_model_id: Literal["Qwen/Qwen2.5-0.5B-Instruct"]
    license: Literal["Apache-2.0"]
    quantization_bits: Literal[4]


class DatasetConfig(StrictModel):
    dataset_id: Literal["goodprose-project-authored-smoke-v1"]
    dataset_sha256: Sha256
    manifest_path: NonEmpty
    manifest_sha256: Sha256
    split_sha256: dict[Literal["train", "valid", "test"], Sha256]
    rights_status: Literal["training_permitted_project_owned_smoke"]
    task_pairs_ratio: float = Field(ge=0, le=1)
    style_targets_ratio: float = Field(ge=0, le=1)
    preference_pairs_ratio: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def smoke_mix_only(self) -> Self:
        ratios = (
            self.task_pairs_ratio,
            self.style_targets_ratio,
            self.preference_pairs_ratio,
        )
        if ratios != (1.0, 0.0, 0.0):
            raise ValueError("smoke v1 must contain only task_pairs")
        return self


class LoraConfig(StrictModel):
    rank: int = Field(ge=1)
    scale: float = Field(gt=0)
    dropout: float = Field(ge=0, lt=1)


class OptimizationConfig(StrictModel):
    fine_tune_type: Literal["lora"]
    optimizer: Literal["adam"]
    seed: int
    num_layers: int = Field(ge=1)
    batch_size: int = Field(ge=1)
    iterations: int = Field(ge=1)
    learning_rate: float = Field(gt=0)
    mask_prompt: Literal[True]
    max_seq_length: int = Field(ge=128)
    validation_batches: int
    test_batches: int
    steps_per_report: int = Field(ge=1)
    steps_per_eval: int = Field(ge=1)
    save_every: int = Field(ge=1)
    grad_checkpoint: bool
    grad_accumulation_steps: int = Field(ge=1)


class SmokeTrainingConfig(StrictModel):
    version: Literal[1]
    experiment_id: NonEmpty
    candidate_id: NonEmpty
    run_kind: Literal["pipeline_smoke_fine_tune"]
    framework: FrameworkConfig
    base_model: BaseModelConfig
    dataset: DatasetConfig
    optimization: OptimizationConfig
    lora: LoraConfig
    checkpoint_selection: Literal["fixed_final_iteration"]
    expected_hardware: Literal["Apple M3 Pro 18GiB unified memory"]
    timeout_seconds: int = Field(ge=60)
    settled_cost_usd: Literal[0]

    @model_validator(mode="after")
    def consistent_checkpoint_policy(self) -> Self:
        if self.optimization.save_every > self.optimization.iterations:
            raise ValueError("save_every cannot exceed iterations")
        return self


class CommandResult(Protocol):
    returncode: int
    stdout: str


CommandRunner = Callable[..., CommandResult]
SnapshotDownloader = Callable[..., str]


def load_training_config(path: Path) -> SmokeTrainingConfig:
    return SmokeTrainingConfig.model_validate_json(path.read_text(encoding="utf-8"))


def _load_json_object(path: Path) -> dict[str, Any]:
    value: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def validate_smoke_data(
    config: SmokeTrainingConfig, *, repo_root: Path, data_dir: Path
) -> dict[str, Any]:
    manifest_path = repo_root / config.dataset.manifest_path
    if sha256_file(manifest_path) != config.dataset.manifest_sha256:
        raise ValueError("smoke dataset manifest hash does not match training config")
    manifest = _load_json_object(manifest_path)
    if manifest.get("dataset_sha256") != config.dataset.dataset_sha256:
        raise ValueError("smoke dataset ID hash does not match training config")
    if manifest.get("rights_status") != config.dataset.rights_status:
        raise ValueError("smoke dataset rights status does not match training config")

    split_hashes: dict[str, str] = {}
    for split in ("train", "valid", "test"):
        path = data_dir / f"{split}.jsonl"
        actual = sha256_file(path)
        expected = config.dataset.split_sha256[split]  # type: ignore[index]
        if actual != expected:
            raise ValueError(f"{split} split hash does not match training config")
        split_hashes[split] = actual
    return {
        "manifest_path": str(manifest_path),
        "manifest_sha256": config.dataset.manifest_sha256,
        "dataset_sha256": config.dataset.dataset_sha256,
        "split_sha256": split_hashes,
        "rights_status": config.dataset.rights_status,
    }


def resolved_mlx_config(
    config: SmokeTrainingConfig, *, model_path: Path, data_dir: Path, adapter_path: Path
) -> dict[str, Any]:
    optimization = config.optimization
    return {
        "model": str(model_path),
        "train": True,
        "fine_tune_type": optimization.fine_tune_type,
        "optimizer": optimization.optimizer,
        "data": str(data_dir),
        "seed": optimization.seed,
        "num_layers": optimization.num_layers,
        "batch_size": optimization.batch_size,
        "iters": optimization.iterations,
        "val_batches": optimization.validation_batches,
        "learning_rate": optimization.learning_rate,
        "steps_per_report": optimization.steps_per_report,
        "steps_per_eval": optimization.steps_per_eval,
        "adapter_path": str(adapter_path),
        "save_every": optimization.save_every,
        "test": True,
        "test_batches": optimization.test_batches,
        "max_seq_length": optimization.max_seq_length,
        "grad_checkpoint": optimization.grad_checkpoint,
        "grad_accumulation_steps": optimization.grad_accumulation_steps,
        "mask_prompt": optimization.mask_prompt,
        "report_to": None,
        "lora_parameters": config.lora.model_dump(mode="json"),
    }


_TRAIN_PATTERN = re.compile(
    r"Iter (?P<iteration>\d+): Train loss (?P<loss>[0-9.]+), "
    r"Learning Rate (?P<learning_rate>[0-9.e+-]+), It/sec (?P<iters_sec>[0-9.]+), "
    r"Tokens/sec (?P<tokens_sec>[0-9.]+), Trained Tokens (?P<tokens>\d+), "
    r"Peak mem (?P<peak_mem>[0-9.]+) GB"
)
_VALID_PATTERN = re.compile(
    r"Iter (?P<iteration>\d+): Val loss (?P<loss>[0-9.]+), "
    r"Val took (?P<seconds>[0-9.]+)s"
)
_TEST_PATTERN = re.compile(r"Test loss (?P<loss>[0-9.]+), Test ppl (?P<ppl>[0-9.]+)\.")


def parse_training_log(log: str) -> dict[str, Any]:
    train_reports = [
        {
            "iteration": int(match["iteration"]),
            "train_loss": float(match["loss"]),
            "learning_rate": float(match["learning_rate"]),
            "iterations_per_second": float(match["iters_sec"]),
            "tokens_per_second": float(match["tokens_sec"]),
            "trained_tokens": int(match["tokens"]),
            "peak_memory_gb": float(match["peak_mem"]),
        }
        for match in _TRAIN_PATTERN.finditer(log)
    ]
    validation_reports = [
        {
            "iteration": int(match["iteration"]),
            "validation_loss": float(match["loss"]),
            "validation_seconds": float(match["seconds"]),
        }
        for match in _VALID_PATTERN.finditer(log)
    ]
    test_match = _TEST_PATTERN.search(log)
    return {
        "train_reports": train_reports,
        "validation_reports": validation_reports,
        "test": (
            {
                "loss": float(test_match["loss"]),
                "perplexity": float(test_match["ppl"]),
            }
            if test_match
            else None
        ),
        "final_trained_tokens": train_reports[-1]["trained_tokens"] if train_reports else 0,
        "peak_memory_gb": max((report["peak_memory_gb"] for report in train_reports), default=None),
    }


def _model_artifacts(model_path: Path) -> dict[str, Any]:
    files = sorted(
        path
        for pattern in ("*.json", "*.safetensors", "*.model", "*.jinja")
        for path in model_path.glob(pattern)
        if path.is_file()
    )
    return {
        "path": str(model_path),
        "files": {
            path.name: {"sha256": sha256_file(path), "size_bytes": path.stat().st_size}
            for path in files
        },
        "total_size_bytes": sum(path.stat().st_size for path in files),
    }


def _adapter_artifacts(adapter_path: Path) -> dict[str, Any]:
    adapter_file = adapter_path / "adapters.safetensors"
    if not adapter_file.is_file() or adapter_file.stat().st_size == 0:
        raise ValueError("MLX did not produce a nonempty adapter safetensors file")
    try:
        from safetensors.numpy import load_file
    except ImportError as error:
        raise ValueError("safetensors is required to validate the trained adapter") from error
    tensors = load_file(adapter_file)
    nonzero_names = [name for name, value in tensors.items() if bool((value != 0).any())]
    if not nonzero_names:
        raise ValueError("trained adapter contains no nonzero tensors")
    files = sorted(path for path in adapter_path.rglob("*") if path.is_file())
    return {
        "adapter_sha256": sha256_file(adapter_file),
        "adapter_size_bytes": adapter_file.stat().st_size,
        "tensor_count": len(tensors),
        "nonzero_tensor_count": len(nonzero_names),
        "files": {
            str(path.relative_to(adapter_path)): {
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for path in files
        },
    }


def _runtime_versions(config: SmokeTrainingConfig) -> dict[str, str]:
    versions = {
        "mlx-lm": package_version("mlx-lm"),
        "mlx": package_version("mlx"),
        "transformers": package_version("transformers"),
        "huggingface-hub": package_version("huggingface-hub"),
        "safetensors": package_version("safetensors"),
    }
    if versions["mlx-lm"] != config.framework.version:
        raise ValueError("installed mlx-lm version does not match training config")
    if versions["mlx"] != config.framework.mlx_version:
        raise ValueError("installed MLX version does not match training config")
    return versions


def _default_snapshot_download(**kwargs: Any) -> str:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as error:
        raise ValueError("run `uv sync --extra training` before smoke training") from error
    return snapshot_download(**kwargs)


def run_smoke_training(
    *,
    config_path: Path,
    data_dir: Path,
    output_root: Path,
    repo_root: Path,
    code_revision: str,
    started_at: str,
    snapshot_downloader: SnapshotDownloader = _default_snapshot_download,
    command_runner: CommandRunner = subprocess.run,
) -> Path:
    """Download the pinned base, run MLX LoRA once, and preserve every outcome."""

    config = load_training_config(config_path)
    timestamp = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("started_at must include a timezone")
    run_id = f"{config.experiment_id}-{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = output_root / run_id
    if run_dir.exists():
        raise ValueError(f"refusing to overwrite existing training run: {run_dir}")
    run_dir.mkdir(parents=True)

    data_evidence = validate_smoke_data(config, repo_root=repo_root, data_dir=data_dir)
    versions = _runtime_versions(config)
    base_manifest = {
        "version": 1,
        "experiment_id": config.experiment_id,
        "candidate_id": config.candidate_id,
        "run_id": run_id,
        "run_kind": config.run_kind,
        "status": "running",
        "started_at": started_at,
        "code_revision": code_revision,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "framework_versions": versions,
        "base_model": config.base_model.model_dump(mode="json"),
        "dataset": data_evidence,
        "settled_cost_usd": 0,
    }
    manifest_path = run_dir / "run-manifest.json"
    _write_json(manifest_path, base_manifest)

    try:
        model_path = Path(
            snapshot_downloader(
                repo_id=config.base_model.repo_id,
                revision=config.base_model.revision,
                allow_patterns=[
                    "*.json",
                    "*.safetensors",
                    "*.model",
                    "*.txt",
                    "*.jinja",
                ],
            )
        ).resolve()
        model_evidence = _model_artifacts(model_path)
        if not any(name.endswith(".safetensors") for name in model_evidence["files"]):
            raise ValueError("pinned base snapshot contains no safetensors weights")

        adapter_path = run_dir / "adapters"
        mlx_config = resolved_mlx_config(
            config, model_path=model_path, data_dir=data_dir, adapter_path=adapter_path
        )
        resolved_config_path = run_dir / "resolved-mlx-config.json"
        _write_json(resolved_config_path, mlx_config)
        command = [sys.executable, "-m", "mlx_lm.lora", "--config", str(resolved_config_path)]
        run_started = time.perf_counter()
        result = command_runner(
            command,
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=config.timeout_seconds,
            check=False,
        )
        elapsed_seconds = time.perf_counter() - run_started
        atomic_write(run_dir / "training.log", result.stdout.encode())
        parsed_metrics = parse_training_log(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(f"MLX training exited with status {result.returncode}")
        if parsed_metrics["final_trained_tokens"] <= 0:
            raise ValueError("MLX training log contains no positive trained-token report")
        if parsed_metrics["test"] is None:
            raise ValueError("MLX training log contains no test loss")
        adapter_evidence = _adapter_artifacts(adapter_path)

        final_manifest = {
            **base_manifest,
            "status": "completed",
            "completed_at": datetime.now(timestamp.tzinfo).isoformat().replace("+00:00", "Z"),
            "elapsed_seconds": round(elapsed_seconds, 6),
            "command": command,
            "resolved_mlx_config_sha256": sha256_file(resolved_config_path),
            "base_model_artifacts": model_evidence,
            "training_metrics": parsed_metrics,
            "adapter_artifacts": adapter_evidence,
            "checkpoint_selection": config.checkpoint_selection,
            "genuine_update_evidence": (
                "positive trained-token count plus nonempty, nonzero LoRA tensors"
            ),
        }
        _write_json(manifest_path, final_manifest)
        return run_dir
    except Exception as error:
        failed_manifest = {
            **base_manifest,
            "status": "failed",
            "failed_at": datetime.now(timestamp.tzinfo).isoformat().replace("+00:00", "Z"),
            "error_type": type(error).__name__,
            "error": str(error),
        }
        _write_json(manifest_path, failed_manifest)
        raise
