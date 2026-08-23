"""Config-driven MLX fine-tuning with complete local run manifests.

The runner is generic over two frozen dataset/run kinds: the original pipeline
smoke dataset and the unified profile-conditioned architecture pilot. All
model, framework, hardware, and cost boundaries remain pinned.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import datetime
from hashlib import sha256
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Annotated, Any, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.executive_writing.unified_data import PROFILES, UnifiedChatRecord
from goodprose.jsonl import atomic_write, load_jsonl, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
GitRevision = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]

SMOKE_RUN_KIND = "pipeline_smoke_fine_tune"
UNIFIED_RUN_KIND = "unified_profile_conditioned_lora_pilot"
UNIFIED_TASK_PAIRS_RATIO = 54 / 90
UNIFIED_STYLE_TARGETS_RATIO = 22 / 90
UNIFIED_PREFERENCE_PAIRS_RATIO = 14 / 90


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


class SmokeDatasetConfig(StrictModel):
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


class UnifiedDatasetConfig(StrictModel):
    dataset_id: Literal["goodprose-project-authored-unified-pilot-v1"]
    dataset_sha256: Sha256
    manifest_path: NonEmpty
    manifest_sha256: Sha256
    split_sha256: dict[Literal["train", "valid", "test"], Sha256]
    preferences_sha256: Sha256
    source_records_path: NonEmpty | None = None
    source_records_sha256: Sha256 | None = None
    rights_status: Literal["training_permitted_project_owned_architecture_pilot"]
    intended_use: Literal["unified_profile_conditioning_architecture_pilot_only"]
    task_pairs_ratio: float = Field(ge=0, le=1)
    style_targets_ratio: float = Field(ge=0, le=1)
    preference_pairs_ratio: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def unified_mix_only(self) -> Self:
        ratios = (
            self.task_pairs_ratio,
            self.style_targets_ratio,
            self.preference_pairs_ratio,
        )
        if ratios != (
            UNIFIED_TASK_PAIRS_RATIO,
            UNIFIED_STYLE_TARGETS_RATIO,
            UNIFIED_PREFERENCE_PAIRS_RATIO,
        ):
            raise ValueError(
                "unified pilot must use exact ratios 54/90 task pairs, 22/90 "
                "style targets, 14/90 preference pairs"
            )
        if (self.source_records_path is None) != (self.source_records_sha256 is None):
            raise ValueError("source records path and hash must be declared together")
        return self


DatasetConfig = Annotated[
    SmokeDatasetConfig | UnifiedDatasetConfig, Field(discriminator="dataset_id")
]


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
    run_kind: Literal["pipeline_smoke_fine_tune", "unified_profile_conditioned_lora_pilot"]
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

    @model_validator(mode="after")
    def pair_run_kind_with_dataset(self) -> Self:
        expected = (
            UNIFIED_RUN_KIND if isinstance(self.dataset, UnifiedDatasetConfig) else SMOKE_RUN_KIND
        )
        if self.run_kind != expected:
            raise ValueError(
                f"run kind {self.run_kind!r} does not match dataset "
                f"{self.dataset.dataset_id!r}; expected {expected!r}"
            )
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


def validate_training_data(
    config: SmokeTrainingConfig, *, repo_root: Path, data_dir: Path
) -> dict[str, Any]:
    """Verify committed manifest bytes and every materialized record on disk."""

    dataset = config.dataset
    manifest_path = repo_root / dataset.manifest_path
    if sha256_file(manifest_path) != dataset.manifest_sha256:
        raise ValueError("dataset manifest hash does not match training config")
    manifest = _load_json_object(manifest_path)
    if manifest.get("dataset_id") != dataset.dataset_id:
        raise ValueError("dataset ID does not match training config")
    if manifest.get("dataset_sha256") != dataset.dataset_sha256:
        raise ValueError("dataset hash does not match training config")
    if manifest.get("rights_status") != dataset.rights_status:
        raise ValueError("dataset rights status does not match training config")

    split_hashes: dict[str, str] = {}
    for split in ("train", "valid", "test"):
        path = data_dir / f"{split}.jsonl"
        actual = sha256_file(path)
        expected = dataset.split_sha256[split]  # type: ignore[index]
        if actual != expected:
            raise ValueError(f"{split} split hash does not match training config")
        manifest_split_sha256 = manifest.get("split_sha256")
        if (
            not isinstance(manifest_split_sha256, dict)
            or manifest_split_sha256.get(split) != actual
        ):
            raise ValueError(f"manifest {split} split hash disagrees with materialized data")
        split_hashes[split] = actual

    evidence: dict[str, Any] = {
        "manifest_path": str(manifest_path),
        "manifest_sha256": dataset.manifest_sha256,
        "dataset_id": dataset.dataset_id,
        "dataset_sha256": dataset.dataset_sha256,
        "split_sha256": split_hashes,
        "rights_status": dataset.rights_status,
    }

    if not isinstance(dataset, UnifiedDatasetConfig):
        return evidence

    evidence["intended_use"] = dataset.intended_use
    if manifest.get("intended_use") != dataset.intended_use:
        raise ValueError("dataset intended use does not match training config")
    if manifest.get("status") != dataset.intended_use:
        raise ValueError("dataset status does not match training config")
    preferences_path = data_dir / "preferences.jsonl"
    actual_preferences_sha256 = sha256_file(preferences_path)
    if actual_preferences_sha256 != dataset.preferences_sha256:
        raise ValueError("preferences file hash does not match training config")
    manifest_split_sha256 = manifest.get("split_sha256")
    if (
        not isinstance(manifest_split_sha256, dict)
        or manifest_split_sha256.get("preferences") != actual_preferences_sha256
    ):
        raise ValueError("manifest preferences hash disagrees with materialized data")
    evidence["preferences_sha256"] = dataset.preferences_sha256

    dataset_digest = sha256()
    all_hashes = {**split_hashes, "preferences": actual_preferences_sha256}
    for name, split_hash in sorted(all_hashes.items()):
        dataset_digest.update(f"{name}:{split_hash}\n".encode())
    if dataset_digest.hexdigest() != dataset.dataset_sha256:
        raise ValueError("materialized dataset hash does not match training config")

    if dataset.source_records_path is not None and dataset.source_records_sha256 is not None:
        source_path = repo_root / dataset.source_records_path
        if sha256_file(source_path) != dataset.source_records_sha256:
            raise ValueError("declared source-records hash does not match training config")
        if manifest.get("source_records_sha256") != dataset.source_records_sha256:
            raise ValueError("manifest source-records hash does not match training config")
        evidence["source_records_sha256"] = dataset.source_records_sha256

    rows_by_split: dict[str, list[UnifiedChatRecord]] = {}
    record_count = 0
    corpus_counts = {"task_pair": 0, "style_target": 0, "preference_pair": 0}
    corpus_counts_by_split: dict[str, dict[str, int]] = {}
    seen_ids: set[str] = set()
    lineage_splits: dict[str, set[str]] = {}
    for split in ("train", "valid", "test"):
        rows = load_jsonl(data_dir / f"{split}.jsonl", UnifiedChatRecord)
        split_corpus_counts = {"task_pair": 0, "style_target": 0, "preference_pair": 0}
        for row in rows:
            metadata = row.metadata
            if metadata.example_id in seen_ids:
                raise ValueError(f"duplicate materialized example ID: {metadata.example_id}")
            seen_ids.add(metadata.example_id)
            if metadata.dataset_id != dataset.dataset_id:
                raise ValueError(f"{metadata.example_id}: unexpected dataset ID in {split} split")
            if metadata.rights_status != dataset.rights_status:
                raise ValueError(
                    f"{metadata.example_id}: unexpected rights status in {split} split"
                )
            if metadata.split != split:
                raise ValueError(f"{metadata.example_id}: record placed outside its declared split")
            if metadata.intended_use != dataset.intended_use:
                raise ValueError(f"{metadata.example_id}: unexpected intended use in {split} split")
            if metadata.profile_id not in PROFILES or not metadata.lineage_group:
                raise ValueError(f"{metadata.example_id}: missing profile or lineage metadata")
            corpus_counts[metadata.corpus] += 1
            split_corpus_counts[metadata.corpus] += 1
            lineage_splits.setdefault(metadata.lineage_group, set()).add(split)
        record_count += len(rows)
        rows_by_split[split] = rows
        corpus_counts_by_split[split] = split_corpus_counts
    if record_count == 0:
        raise ValueError("unified training data contains no records")
    crossing_lineages = sorted(
        lineage for lineage, splits in lineage_splits.items() if len(splits) != 1
    )
    if crossing_lineages:
        raise ValueError(f"materialized lineage groups cross splits: {crossing_lineages[0]}")
    evidence["record_count"] = record_count

    expected_ratios = (
        (dataset.task_pairs_ratio, "task_pair"),
        (dataset.style_targets_ratio, "style_target"),
        (dataset.preference_pairs_ratio, "preference_pair"),
    )
    recomputed_ratios: dict[str, float] = {}
    for expected_ratio, corpus in expected_ratios:
        actual_ratio = corpus_counts[corpus] / record_count
        if actual_ratio != expected_ratio:
            raise ValueError(
                f"{corpus} ratio {actual_ratio} does not match training config ratio "
                f"{expected_ratio}"
            )
        recomputed_ratios[corpus] = actual_ratio
    evidence["corpus_counts"] = dict(sorted(corpus_counts.items()))
    evidence["corpus_ratios"] = recomputed_ratios
    evidence["split_counts"] = {split: len(rows) for split, rows in rows_by_split.items()}
    evidence["per_split_corpus_counts"] = corpus_counts_by_split

    preference_rows = load_jsonl(preferences_path, UnifiedChatRecord)
    expected_preference_ids = sorted(
        row.metadata.example_id
        for rows in rows_by_split.values()
        for row in rows
        if row.metadata.corpus == "preference_pair"
    )
    actual_preference_ids = [row.metadata.example_id for row in preference_rows]
    if sorted(actual_preference_ids) != expected_preference_ids:
        raise ValueError("preferences file does not match the materialized preference records")
    if len(actual_preference_ids) != len(set(actual_preference_ids)):
        raise ValueError("preferences file contains duplicate example IDs")
    expected_preference_rows = {
        row.metadata.example_id: row.model_dump(mode="json")
        for rows in rows_by_split.values()
        for row in rows
        if row.metadata.corpus == "preference_pair"
    }
    actual_preference_rows = {
        row.metadata.example_id: row.model_dump(mode="json") for row in preference_rows
    }
    if actual_preference_rows != expected_preference_rows:
        raise ValueError("preferences file content disagrees with materialized preference records")

    manifest_split_counts = manifest.get("split_counts")
    if manifest_split_counts != evidence["split_counts"]:
        raise ValueError("manifest split counts disagree with the materialized records")
    manifest_corpus_counts = manifest.get("corpus_counts")
    if manifest_corpus_counts != corpus_counts:
        raise ValueError("manifest corpus counts disagree with the materialized records")
    if manifest.get("record_count") != record_count:
        raise ValueError("manifest record count disagrees with the materialized records")
    if manifest.get("corpus_ratios") != recomputed_ratios:
        raise ValueError("manifest corpus ratios disagree with the materialized records")
    exact_ratio_evidence = {
        corpus: {"numerator": count, "denominator": record_count}
        for corpus, count in corpus_counts.items()
    }
    if manifest.get("corpus_ratio_fractions") != exact_ratio_evidence:
        raise ValueError("manifest exact corpus ratios disagree with the materialized records")
    per_split_ratios = {
        split: {corpus: count / len(rows_by_split[split]) for corpus, count in counts.items()}
        for split, counts in corpus_counts_by_split.items()
    }
    if manifest.get("per_split_corpus_counts") != corpus_counts_by_split:
        raise ValueError("manifest per-split corpus counts disagree with materialized records")
    if manifest.get("per_split_corpus_ratios") != per_split_ratios:
        raise ValueError("manifest per-split corpus ratios disagree with materialized records")
    per_split_ratio_fractions = {
        split: {
            corpus: {"numerator": count, "denominator": len(rows_by_split[split])}
            for corpus, count in counts.items()
        }
        for split, counts in corpus_counts_by_split.items()
    }
    if manifest.get("per_split_corpus_ratio_fractions") != per_split_ratio_fractions:
        raise ValueError("manifest exact per-split ratios disagree with materialized records")
    return evidence


def validate_smoke_data(
    config: SmokeTrainingConfig, *, repo_root: Path, data_dir: Path
) -> dict[str, Any]:
    """Backward-compatible alias for :func:`validate_training_data`."""

    return validate_training_data(config, repo_root=repo_root, data_dir=data_dir)


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


def run_mlx_training(
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

    versions = _runtime_versions(config)
    base_manifest: dict[str, Any] = {
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
        "dataset": {"validation_status": "pending"},
        "settled_cost_usd": 0,
    }
    manifest_path = run_dir / "run-manifest.json"
    _write_json(manifest_path, base_manifest)

    try:
        data_evidence = validate_training_data(config, repo_root=repo_root, data_dir=data_dir)
        base_manifest["dataset"] = data_evidence
        _write_json(manifest_path, base_manifest)
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


# Backward-compatible route to the same core runner for existing smoke callers.
run_smoke_training = run_mlx_training
