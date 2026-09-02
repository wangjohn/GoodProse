"""Validate and run a short DPO pass on top of a finished SFT adapter."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError

from goodprose.chat import (
    DEFAULT_CHAT_TEMPLATE_KWARGS,
    ChatTemplateError,
    prompt_strategy,
    render_prompt,
    verify_template_parity,
)
from goodprose.generation import adapter_identifier
from goodprose.jsonl import atomic_write_json, load_jsonl, sha256_file
from goodprose.models import NonEmptyString, PreferencePair, StrictModel
from goodprose.sft import SYSTEM_PROMPT


class DpoError(ValueError):
    """A preference-optimisation run is unsafe or cannot be configured."""


class DpoConfig(StrictModel):
    version: Literal[1] = 1
    model_id: NonEmptyString
    model_revision: NonEmptyString = "main"
    sft_adapter: Path
    preference_file: Path
    output_dir: Path
    run_name: NonEmptyString = "goodprose-dpo"
    beta: float = Field(default=0.1, gt=0)
    rpo_alpha: float | None = Field(
        default=1.0,
        ge=0,
        description="Weight of the SFT loss on the chosen text mixed into DPO; null disables it.",
    )
    loss_type: Literal["sigmoid", "ipo", "hinge"] = "sigmoid"
    learning_rate: float = Field(default=1e-5, gt=0)
    num_train_epochs: float = Field(default=1, gt=0)
    per_device_train_batch_size: int = Field(default=1, ge=1)
    gradient_accumulation_steps: int = Field(default=8, ge=1)
    warmup_ratio: float = Field(default=0.1, ge=0, le=1)
    lr_scheduler_type: NonEmptyString = "cosine"
    max_grad_norm: float = Field(default=1, gt=0)
    max_length: int = Field(default=6144, ge=512)
    max_prompt_length: int = Field(default=3072, ge=256)
    precision: Literal["auto", "bfloat16", "float16", "float32"] = "bfloat16"
    load_in_4bit: bool = False
    gradient_checkpointing: bool = True
    chat_template_kwargs: dict[str, bool | int | str] = Field(
        default_factory=lambda: dict(DEFAULT_CHAT_TEMPLATE_KWARGS)
    )
    save_strategy: Literal["no", "steps", "epoch"] = "epoch"
    save_total_limit: int = Field(default=2, ge=1)
    logging_steps: int = Field(default=1, ge=1)
    seed: int = 20260901
    trust_remote_code: bool = False
    report_to: tuple[NonEmptyString, ...] = ()


class DpoPlan(StrictModel):
    version: Literal[1] = 1
    model_id: NonEmptyString
    model_revision: NonEmptyString
    sft_adapter_id: NonEmptyString
    preference_file: Path
    preference_pairs: int
    preference_file_sha256: NonEmptyString
    output_dir: Path
    beta: float
    rpo_alpha: float | None
    optimizer_steps: int
    prompt_strategy: NonEmptyString


def _resolved(config_path: Path, value: Path) -> Path:
    return value.resolve() if value.is_absolute() else (config_path.parent / value).resolve()


def load_dpo_config(config_path: Path) -> DpoConfig:
    path = config_path.resolve()
    try:
        config = DpoConfig.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        raise DpoError(f"invalid DPO config {path}: {error}") from error
    return config.model_copy(
        update={
            "sft_adapter": _resolved(path, config.sft_adapter),
            "preference_file": _resolved(path, config.preference_file),
            "output_dir": _resolved(path, config.output_dir),
        }
    )


def _load_pairs(path: Path) -> list[PreferencePair]:
    if not path.is_file():
        raise DpoError(f"preference file does not exist: {path}")
    try:
        pairs = load_jsonl(path, PreferencePair)
    except ValueError as error:
        raise DpoError(f"invalid preference data: {error}") from error
    if not pairs:
        raise DpoError(f"preference dataset is empty: {path}")
    stale = [pair.id for pair in pairs if pair.prompt[0]["content"] != SYSTEM_PROMPT]
    if stale:
        raise DpoError(f"preference pairs use a stale system prompt: {stale[:3]}")
    return pairs


def prepare_dpo_run(config_path: Path) -> tuple[DpoConfig, DpoPlan]:
    config = load_dpo_config(config_path)
    pairs = _load_pairs(config.preference_file)
    try:
        adapter_id = adapter_identifier(config.sft_adapter)
    except ValueError as error:
        raise DpoError(str(error)) from error
    per_epoch = -(
        -len(pairs) // (config.per_device_train_batch_size * config.gradient_accumulation_steps)
    )
    plan = DpoPlan(
        model_id=config.model_id,
        model_revision=config.model_revision,
        sft_adapter_id=adapter_id,
        preference_file=config.preference_file,
        preference_pairs=len(pairs),
        preference_file_sha256=sha256_file(config.preference_file),
        output_dir=config.output_dir,
        beta=config.beta,
        rpo_alpha=config.rpo_alpha,
        optimizer_steps=int(per_epoch * config.num_train_epochs),
        prompt_strategy=prompt_strategy(config.chat_template_kwargs),
    )
    return config, plan


def _module(name: str) -> Any:
    try:
        return import_module(name)
    except ImportError as error:
        raise DpoError(
            f"training dependency {name!r} is not installed; run `uv sync --extra train`"
        ) from error


def text_preference_records(
    pairs: list[PreferencePair], tokenizer: Any, chat_template_kwargs: dict[str, bool | int | str]
) -> list[dict[str, str]]:
    """Render prompts to text so DPO sees the same assistant prefix as SFT and inference."""
    eos = tokenizer.eos_token or ""
    records: list[dict[str, str]] = []
    for pair in pairs:
        prompt = render_prompt(tokenizer, pair.prompt, chat_template_kwargs)
        records.append(
            {
                "prompt": prompt,
                "chosen": pair.chosen if pair.chosen.endswith(eos) else pair.chosen + eos,
                "rejected": pair.rejected if pair.rejected.endswith(eos) else pair.rejected + eos,
            }
        )
    return records


def run_dpo(config_path: Path, *, validate_only: bool = False) -> dict[str, Any]:
    config, plan = prepare_dpo_run(config_path)
    if validate_only:
        return plan.model_dump(mode="json", exclude_none=True)

    torch = _module("torch")
    datasets = _module("datasets")
    peft = _module("peft")
    transformers = _module("transformers")
    trl = _module("trl")

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        config.model_id, revision=config.model_revision, trust_remote_code=config.trust_remote_code
    )
    if tokenizer.chat_template is None:
        raise DpoError(f"tokenizer for {config.model_id!r} has no chat template")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    pairs = _load_pairs(config.preference_file)
    try:
        prefix_sha256 = verify_template_parity(
            tokenizer, pairs[0].prompt, config.chat_template_kwargs
        )
    except ChatTemplateError as error:
        raise DpoError(str(error)) from error

    dtype = None if config.precision == "auto" else getattr(torch, config.precision)
    model_kwargs: dict[str, Any] = {
        "revision": config.model_revision,
        "trust_remote_code": config.trust_remote_code,
        "low_cpu_mem_usage": True,
    }
    if dtype is not None:
        model_kwargs["dtype"] = dtype
    if config.load_in_4bit:
        model_kwargs["quantization_config"] = transformers.BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=dtype or torch.bfloat16,
        )
        model_kwargs["device_map"] = "auto"
    base_model = transformers.AutoModelForCausalLM.from_pretrained(config.model_id, **model_kwargs)
    if config.load_in_4bit:
        base_model = peft.prepare_model_for_kbit_training(
            base_model, use_gradient_checkpointing=config.gradient_checkpointing
        )
    if config.gradient_checkpointing:
        base_model.config.use_cache = False
    # The SFT adapter continues training; with a PEFT model TRL derives the frozen reference
    # policy by disabling the adapter, so no second copy of the base model is loaded.
    model = peft.PeftModel.from_pretrained(base_model, str(config.sft_adapter), is_trainable=True)
    model.print_trainable_parameters()

    dataset = datasets.Dataset.from_list(
        text_preference_records(pairs, tokenizer, config.chat_template_kwargs)
    )
    args = trl.DPOConfig(
        output_dir=str(config.output_dir),
        run_name=config.run_name,
        beta=config.beta,
        rpo_alpha=config.rpo_alpha,
        loss_type=config.loss_type,
        learning_rate=config.learning_rate,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        warmup_ratio=config.warmup_ratio,
        lr_scheduler_type=config.lr_scheduler_type,
        max_grad_norm=config.max_grad_norm,
        max_length=config.max_length,
        max_prompt_length=config.max_prompt_length,
        gradient_checkpointing=config.gradient_checkpointing,
        bf16=config.precision == "bfloat16",
        fp16=config.precision == "float16",
        save_strategy=config.save_strategy,
        save_total_limit=config.save_total_limit,
        logging_steps=config.logging_steps,
        seed=config.seed,
        report_to=list(config.report_to) or "none",
    )
    trainer = trl.DPOTrainer(
        model=model,
        ref_model=None,
        args=args,
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    result = trainer.train()
    trainer.save_model(str(config.output_dir))
    tokenizer.save_pretrained(str(config.output_dir))
    trainer.save_state()
    manifest = {
        "version": 1,
        "status": "complete",
        "completed_at": datetime.now(UTC).isoformat(),
        "config": config.model_dump(mode="json", exclude_none=True),
        "plan": plan.model_dump(mode="json", exclude_none=True),
        "system_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "chat_template_sha256": hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        "rendered_prompt_prefix_sha256": prefix_sha256,
        "metrics": result.metrics,
        "log_history": trainer.state.log_history,
    }
    atomic_write_json(config.output_dir / "dpo-manifest.json", manifest)
    return manifest
