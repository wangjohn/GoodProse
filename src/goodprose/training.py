"""Validate and run a small PEFT/TRL LoRA or LoRA+ supervised fine-tune."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from importlib import import_module, metadata
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError, model_validator

from goodprose.chat import (
    DEFAULT_CHAT_TEMPLATE_KWARGS,
    ChatTemplateError,
    prompt_strategy,
    render_prompt,
    verify_template_parity,
)
from goodprose.jsonl import atomic_write_json, load_jsonl, sha256_file
from goodprose.models import NonEmptyString, StrictModel
from goodprose.sft import SYSTEM_PROMPT


class TrainingError(ValueError):
    """A fine-tuning run is unsafe or cannot be configured."""


class TrainingMessage(StrictModel):
    role: Literal["system", "user", "assistant"]
    content: NonEmptyString


class TrainingRecord(StrictModel):
    messages: tuple[TrainingMessage, ...]

    @model_validator(mode="after")
    def validate_conversation(self) -> TrainingRecord:
        roles = tuple(message.role for message in self.messages)
        if roles != ("system", "user", "assistant"):
            raise ValueError("messages must contain exactly system, user, and assistant turns")
        if self.messages[0].content != SYSTEM_PROMPT:
            raise ValueError("training record uses a stale or unexpected system prompt")
        return self


class LoraPlusConfig(StrictModel):
    version: Literal[1] = 1
    model_id: NonEmptyString
    model_revision: NonEmptyString = "main"
    train_file: Path
    eval_file: Path | None = None
    dataset_manifest_file: Path | None = None
    output_dir: Path
    run_name: NonEmptyString = "goodprose-lora-plus"
    max_length: int = Field(default=2048, ge=256)
    num_train_epochs: float = Field(default=3, gt=0)
    per_device_train_batch_size: int = Field(default=1, ge=1)
    per_device_eval_batch_size: int = Field(default=1, ge=1)
    gradient_accumulation_steps: int = Field(default=8, ge=1)
    learning_rate: float = Field(default=5e-5, gt=0)
    loraplus_lr_ratio: float = Field(
        default=16,
        ge=1,
        description="LoRA B/A learning-rate ratio; exactly 1 trains plain LoRA with one rate.",
    )
    weight_decay: float = Field(default=0, ge=0)
    warmup_ratio: float = Field(default=0.05, ge=0, le=1)
    lr_scheduler_type: NonEmptyString = "cosine"
    max_grad_norm: float = Field(default=1, gt=0)
    lora_r: int = Field(default=32, ge=1)
    lora_alpha: int = Field(default=64, ge=1)
    lora_dropout: float = Field(default=0.05, ge=0, lt=1)
    target_modules: NonEmptyString | tuple[NonEmptyString, ...] = "all-linear"
    modules_to_save: tuple[NonEmptyString, ...] = ()
    optimizer: Literal["adamw_torch", "adam8bit"] = "adamw_torch"
    precision: Literal["auto", "bfloat16", "float16", "float32"] = "bfloat16"
    load_in_4bit: bool = False
    gradient_checkpointing: bool = True
    packing: bool = False
    chat_template_kwargs: dict[str, bool | int | str] = Field(
        default_factory=lambda: dict(DEFAULT_CHAT_TEMPLATE_KWARGS)
    )
    eval_strategy: Literal["no", "steps", "epoch"] = "no"
    eval_steps: int | None = Field(default=None, ge=1)
    save_strategy: Literal["no", "steps", "epoch"] = "epoch"
    save_steps: int | None = Field(default=None, ge=1)
    save_total_limit: int = Field(default=2, ge=1)
    logging_steps: int = Field(default=1, ge=1)
    seed: int = 20260901
    trust_remote_code: bool = False
    report_to: tuple[NonEmptyString, ...] = ()

    @model_validator(mode="after")
    def validate_strategy(self) -> LoraPlusConfig:
        if self.eval_strategy != "no" and self.eval_file is None:
            raise ValueError("eval_file is required when eval_strategy is enabled")
        if self.eval_strategy == "steps" and self.eval_steps is None:
            raise ValueError("eval_steps is required for step-based evaluation")
        if self.save_strategy == "steps" and self.save_steps is None:
            raise ValueError("save_steps is required for step-based checkpointing")
        return self


class LoraPlusPlan(StrictModel):
    version: Literal[1] = 1
    model_id: NonEmptyString
    model_revision: NonEmptyString
    train_file: Path
    train_examples: int
    train_file_sha256: NonEmptyString
    eval_file: Path | None = None
    eval_examples: int = 0
    eval_file_sha256: NonEmptyString | None = None
    dataset_manifest_sha256: NonEmptyString | None = None
    output_dir: Path
    learning_rate_a: float
    learning_rate_b: float
    loraplus_lr_ratio: float
    optimizer_steps: int
    prompt_strategy: NonEmptyString


def _resolved_path(config_path: Path, value: Path | None) -> Path | None:
    if value is None:
        return None
    return value.resolve() if value.is_absolute() else (config_path.parent / value).resolve()


def load_lora_plus_config(config_path: Path) -> LoraPlusConfig:
    """Load a strict JSON config and resolve its paths relative to the config file."""
    path = config_path.resolve()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        config = LoraPlusConfig.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        raise TrainingError(f"invalid LoRA+ config {path}: {error}") from error
    return config.model_copy(
        update={
            "train_file": _resolved_path(path, config.train_file),
            "eval_file": _resolved_path(path, config.eval_file),
            "dataset_manifest_file": _resolved_path(path, config.dataset_manifest_file),
            "output_dir": _resolved_path(path, config.output_dir),
        }
    )


def _load_records(path: Path, *, kind: str) -> list[TrainingRecord]:
    if not path.is_file():
        raise TrainingError(f"{kind} file does not exist: {path}")
    try:
        records = load_jsonl(path, TrainingRecord)
    except ValueError as error:
        raise TrainingError(f"invalid {kind} data: {error}") from error
    if not records:
        raise TrainingError(f"{kind} dataset is empty: {path}")
    return records


def _validate_dataset_manifest(
    path: Path | None,
    *,
    train_file: Path,
    train_count: int,
    eval_file: Path | None,
    eval_count: int,
) -> str | None:
    if path is None:
        return None
    if not path.is_file():
        raise TrainingError(f"dataset manifest does not exist: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise TrainingError(f"invalid dataset manifest {path}: {error}") from error
    expected = {
        "system_prompt": SYSTEM_PROMPT,
        "train_file_sha256": sha256_file(train_file),
    }
    if eval_file is not None:
        expected["dev_file_sha256"] = sha256_file(eval_file)
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise TrainingError(f"dataset manifest {key!r} does not match generated data")
    counts = manifest.get("counts", {})
    if counts.get("train") != train_count:
        raise TrainingError("dataset manifest train count does not match generated data")
    if eval_file is not None and counts.get("dev") != eval_count:
        raise TrainingError("dataset manifest dev count does not match generated data")
    return sha256_file(path)


def optimizer_steps(config: LoraPlusConfig, train_examples: int) -> int:
    """Total optimizer updates the schedule will see; tiny counts make cosine meaningless."""
    per_epoch = -(
        -train_examples // (config.per_device_train_batch_size * config.gradient_accumulation_steps)
    )
    return int(per_epoch * config.num_train_epochs)


def prepare_lora_plus_run(config_path: Path) -> tuple[LoraPlusConfig, LoraPlusPlan]:
    """Validate config, conversational data, and the frozen dataset manifest."""
    config = load_lora_plus_config(config_path)
    train_records = _load_records(config.train_file, kind="training")
    eval_records = (
        _load_records(config.eval_file, kind="development") if config.eval_file is not None else []
    )
    manifest_hash = _validate_dataset_manifest(
        config.dataset_manifest_file,
        train_file=config.train_file,
        train_count=len(train_records),
        eval_file=config.eval_file,
        eval_count=len(eval_records),
    )
    plan = LoraPlusPlan(
        model_id=config.model_id,
        model_revision=config.model_revision,
        train_file=config.train_file,
        train_examples=len(train_records),
        train_file_sha256=sha256_file(config.train_file),
        eval_file=config.eval_file,
        eval_examples=len(eval_records),
        eval_file_sha256=(sha256_file(config.eval_file) if config.eval_file is not None else None),
        dataset_manifest_sha256=manifest_hash,
        output_dir=config.output_dir,
        learning_rate_a=config.learning_rate,
        learning_rate_b=config.learning_rate * config.loraplus_lr_ratio,
        loraplus_lr_ratio=config.loraplus_lr_ratio,
        optimizer_steps=optimizer_steps(config, len(train_records)),
        prompt_strategy=prompt_strategy(config.chat_template_kwargs),
    )
    return config, plan


def _module(name: str) -> Any:
    try:
        return import_module(name)
    except ImportError as error:
        raise TrainingError(
            f"training dependency {name!r} is not installed; run `uv sync --extra train`"
        ) from error


def text_prompt_completion_records(
    records: list[TrainingRecord],
    tokenizer: Any,
    chat_template_kwargs: dict[str, bool | int | str],
) -> list[dict[str, str]]:
    """Render prompts ourselves so training sees exactly the inference prefix.

    TRL's conversational path applies the chat template with its own defaults, which for
    Qwen3 omits the empty think block that ``enable_thinking=False`` adds at inference.
    Rendering to text here removes that mismatch. The EOS token is appended explicitly so
    the completion ends the assistant turn the same way the template does.
    """
    eos = tokenizer.eos_token or ""
    rendered: list[dict[str, str]] = []
    for record in records:
        prompt_messages = [message.model_dump() for message in record.messages[:-1]]
        prompt = render_prompt(tokenizer, prompt_messages, chat_template_kwargs)
        completion = record.messages[-1].content
        if eos and not completion.endswith(eos):
            completion = completion + eos
        rendered.append({"prompt": prompt, "completion": completion})
    return rendered


def _package_version(package: str) -> str | None:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return None


def load_tokenizer(transformers: Any, config: LoraPlusConfig) -> Any:
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        config.model_id,
        revision=config.model_revision,
        trust_remote_code=config.trust_remote_code,
    )
    if tokenizer.chat_template is None:
        raise TrainingError(
            f"tokenizer for {config.model_id!r} has no chat template; choose an instruction model "
            "or configure a compatible template"
        )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def base_model_kwargs(config: LoraPlusConfig, torch: Any, transformers: Any) -> dict[str, Any]:
    dtype = None if config.precision == "auto" else getattr(torch, config.precision)
    kwargs: dict[str, Any] = {
        "revision": config.model_revision,
        "trust_remote_code": config.trust_remote_code,
        "low_cpu_mem_usage": True,
    }
    if dtype is not None:
        kwargs["dtype"] = dtype
    if config.load_in_4bit:
        kwargs["quantization_config"] = transformers.BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=dtype or torch.bfloat16,
        )
        kwargs["device_map"] = "auto"
    return kwargs


def run_lora_plus(
    config_path: Path,
    *,
    validate_only: bool = False,
    resume_from_checkpoint: Path | None = None,
) -> dict[str, Any]:
    """Run LoRA (ratio 1) or LoRA+ through PEFT and TRL's SFT trainer."""
    config, plan = prepare_lora_plus_run(config_path)
    if validate_only:
        return plan.model_dump(mode="json", exclude_none=True)

    torch = _module("torch")
    datasets = _module("datasets")
    peft = _module("peft")
    transformers = _module("transformers")
    trl = _module("trl")
    bitsandbytes = (
        _module("bitsandbytes") if config.optimizer == "adam8bit" or config.load_in_4bit else None
    )

    tokenizer = load_tokenizer(transformers, config)
    train_records = _load_records(config.train_file, kind="training")
    eval_records = (
        _load_records(config.eval_file, kind="development") if config.eval_file is not None else []
    )
    try:
        prefix_sha256 = verify_template_parity(
            tokenizer,
            [message.model_dump() for message in train_records[0].messages[:-1]],
            config.chat_template_kwargs,
        )
    except ChatTemplateError as error:
        raise TrainingError(str(error)) from error

    base_model = transformers.AutoModelForCausalLM.from_pretrained(
        config.model_id,
        **base_model_kwargs(config, torch, transformers),
    )
    if config.load_in_4bit:
        base_model = peft.prepare_model_for_kbit_training(
            base_model,
            use_gradient_checkpointing=config.gradient_checkpointing,
        )
    if config.gradient_checkpointing:
        base_model.config.use_cache = False

    lora_config = peft.LoraConfig(
        task_type="CAUSAL_LM",
        inference_mode=False,
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.target_modules,
        modules_to_save=list(config.modules_to_save) or None,
        bias="none",
    )
    model = peft.get_peft_model(base_model, lora_config)
    model.print_trainable_parameters()

    optimizer_cls = (
        bitsandbytes.optim.Adam8bit
        if config.optimizer == "adam8bit" and bitsandbytes is not None
        else torch.optim.AdamW
    )
    if config.loraplus_lr_ratio == 1:
        optimizer = optimizer_cls(
            [parameter for parameter in model.parameters() if parameter.requires_grad],
            lr=config.learning_rate,
            weight_decay=config.weight_decay,
        )
    else:
        peft_optimizers = _module("peft.optimizers")
        optimizer = peft_optimizers.create_loraplus_optimizer(
            model=model,
            optimizer_cls=optimizer_cls,
            lr=config.learning_rate,
            loraplus_lr_ratio=config.loraplus_lr_ratio,
            loraplus_weight_decay=config.weight_decay,
        )

    train_dataset = datasets.Dataset.from_list(
        text_prompt_completion_records(train_records, tokenizer, config.chat_template_kwargs)
    )
    eval_dataset = (
        datasets.Dataset.from_list(
            text_prompt_completion_records(eval_records, tokenizer, config.chat_template_kwargs)
        )
        if eval_records and config.eval_strategy != "no"
        else None
    )
    training_kwargs: dict[str, Any] = {
        "output_dir": str(config.output_dir),
        "run_name": config.run_name,
        "num_train_epochs": config.num_train_epochs,
        "per_device_train_batch_size": config.per_device_train_batch_size,
        "per_device_eval_batch_size": config.per_device_eval_batch_size,
        "gradient_accumulation_steps": config.gradient_accumulation_steps,
        "learning_rate": config.learning_rate,
        "lr_scheduler_type": config.lr_scheduler_type,
        # Transformers 5 accepts a float in [0, 1) here as a ratio of total steps.
        "warmup_steps": config.warmup_ratio,
        "weight_decay": config.weight_decay,
        "max_grad_norm": config.max_grad_norm,
        "max_length": config.max_length,
        "completion_only_loss": True,
        "packing": config.packing,
        "gradient_checkpointing": config.gradient_checkpointing,
        "bf16": config.precision == "bfloat16",
        "fp16": config.precision == "float16",
        "eval_strategy": config.eval_strategy,
        "save_strategy": config.save_strategy,
        "save_total_limit": config.save_total_limit,
        "logging_steps": config.logging_steps,
        "seed": config.seed,
        "data_seed": config.seed,
        "report_to": list(config.report_to) or "none",
    }
    if config.eval_steps is not None:
        training_kwargs["eval_steps"] = config.eval_steps
    if config.save_steps is not None:
        training_kwargs["save_steps"] = config.save_steps
    training_args = trl.SFTConfig(**training_kwargs)
    trainer = trl.SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
        optimizers=(optimizer, None),
    )
    train_result = trainer.train(
        resume_from_checkpoint=(
            str(resume_from_checkpoint.resolve()) if resume_from_checkpoint is not None else None
        )
    )
    trainer.save_model(str(config.output_dir))
    tokenizer.save_pretrained(str(config.output_dir))
    trainer.save_state()

    resolved_model_revision = getattr(model.config, "_commit_hash", None) or config.model_revision
    resolved_tokenizer_revision = tokenizer.init_kwargs.get("_commit_hash") or config.model_revision
    manifest = {
        "version": 2,
        "status": "complete",
        "completed_at": datetime.now(UTC).isoformat(),
        "config": config.model_dump(mode="json", exclude_none=True),
        "plan": plan.model_dump(mode="json", exclude_none=True),
        "resolved_model_revision": resolved_model_revision,
        "resolved_tokenizer_revision": resolved_tokenizer_revision,
        "system_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "chat_template_sha256": hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        "rendered_prompt_prefix_sha256": prefix_sha256,
        "packages": {
            package: _package_version(package)
            for package in ("torch", "transformers", "peft", "trl", "datasets", "accelerate")
        },
        "metrics": train_result.metrics,
        "log_history": trainer.state.log_history,
    }
    atomic_write_json(config.output_dir / "training-manifest.json", manifest)
    return manifest
