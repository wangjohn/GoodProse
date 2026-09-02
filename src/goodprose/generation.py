"""Generate matched deterministic outputs for the base model and a LoRA checkpoint."""

from __future__ import annotations

import hashlib
from importlib import import_module
from pathlib import Path
from typing import Any

from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    load_jsonl,
    serialize_jsonl,
    sha256_file,
)
from goodprose.models import (
    DecodingSettings,
    EvalCase,
    GenerationRunManifest,
    ModelOutput,
    SystemLabel,
)
from goodprose.sft import SYSTEM_PROMPT
from goodprose.training import LoraPlusConfig, prepare_lora_plus_run

PROMPT_STRATEGY = "matched-system-prompt:qwen-no-thinking"


class GenerationError(ValueError):
    """A deterministic evaluation generation run is unsafe or incomplete."""


def _module(name: str) -> Any:
    try:
        return import_module(name)
    except ImportError as error:
        raise GenerationError(
            f"generation dependency {name!r} is not installed; run `uv sync --extra train`"
        ) from error


def _validate_cases(cases_path: Path) -> list[EvalCase]:
    cases = load_jsonl(cases_path, EvalCase)
    if not cases:
        raise GenerationError("evaluation case file is empty")
    seen: set[str] = set()
    for case in cases:
        if case.id in seen:
            raise GenerationError(f"duplicate evaluation case ID {case.id!r}")
        seen.add(case.id)
        target_hash = hashlib.sha256(case.reference_output.encode()).hexdigest()
        if target_hash != case.target_sha256:
            raise GenerationError(f"case {case.id!r} has a stale reference target hash")
    return cases


def _adapter_identifier(adapter_path: Path) -> str:
    if not adapter_path.is_dir():
        raise GenerationError(f"adapter checkpoint directory does not exist: {adapter_path}")
    fingerprint_files = [
        path
        for name in ("adapter_config.json", "adapter_model.safetensors", "adapter_model.bin")
        if (path := adapter_path / name).is_file()
    ]
    if not fingerprint_files:
        raise GenerationError(
            f"adapter checkpoint has no adapter config or model weights: {adapter_path}"
        )
    digest = hashlib.sha256()
    for path in fingerprint_files:
        digest.update(path.name.encode())
        digest.update(sha256_file(path).encode())
    return f"{adapter_path.resolve()}@sha256:{digest.hexdigest()}"


def _model_kwargs(config: LoraPlusConfig, torch: Any, transformers: Any) -> dict[str, Any]:
    dtype = None if config.precision == "auto" else getattr(torch, config.precision)
    kwargs: dict[str, Any] = {
        "revision": config.model_revision,
        "trust_remote_code": config.trust_remote_code,
        "low_cpu_mem_usage": True,
        "device_map": "auto",
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
    return kwargs


def _seed_runtime(torch: Any, transformers: Any, seed: int) -> None:
    transformers.set_seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def generate_eval_outputs(
    config_path: Path,
    cases_path: Path,
    output_path: Path,
    manifest_path: Path,
    *,
    role: SystemLabel,
    run_id: str,
    adapter_path: Path | None = None,
    max_new_tokens: int = 8192,
    seed: int = 20260901,
) -> int:
    """Generate one greedy response per frozen case and record complete run provenance."""
    if max_new_tokens < 1:
        raise GenerationError("max_new_tokens must be at least 1")
    normalized_run_id = run_id.strip()
    if not normalized_run_id:
        raise GenerationError("run_id must not be empty")
    if role is SystemLabel.BASELINE and adapter_path is not None:
        raise GenerationError("baseline generation must not specify an adapter")
    if role is SystemLabel.CANDIDATE and adapter_path is None:
        raise GenerationError("candidate generation requires an adapter checkpoint")

    config, plan = prepare_lora_plus_run(config_path)
    if config.dataset_manifest_file is None or plan.dataset_manifest_sha256 is None:
        raise GenerationError("the training config must specify a validated dataset manifest")
    cases = _validate_cases(cases_path)
    cases_sha256 = sha256_file(cases_path)
    adapter_id = _adapter_identifier(adapter_path) if adapter_path is not None else None

    torch = _module("torch")
    transformers = _module("transformers")
    peft = _module("peft") if adapter_path is not None else None
    _seed_runtime(torch, transformers, seed)

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        config.model_id,
        revision=config.model_revision,
        trust_remote_code=config.trust_remote_code,
    )
    if tokenizer.chat_template is None:
        raise GenerationError(f"tokenizer for {config.model_id!r} has no chat template")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = transformers.AutoModelForCausalLM.from_pretrained(
        config.model_id,
        **_model_kwargs(config, torch, transformers),
    )
    resolved_model_revision = (
        getattr(base_model.config, "_commit_hash", None) or config.model_revision
    )
    model = (
        peft.PeftModel.from_pretrained(base_model, str(adapter_path.resolve()), is_trainable=False)
        if peft is not None and adapter_path is not None
        else base_model
    )
    model.eval()

    outputs: list[ModelOutput] = []
    for index, case in enumerate(cases, start=1):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": case.input},
        ]
        rendered_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        encoded = tokenizer(rendered_prompt, return_tensors="pt")
        encoded = {name: tensor.to(model.device) for name, tensor in encoded.items()}
        prompt_length = encoded["input_ids"].shape[-1]
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        output = tokenizer.decode(
            generated[0][prompt_length:],
            skip_special_tokens=True,
        ).strip()
        if not output:
            raise GenerationError(f"model returned an empty response for case {case.id!r}")
        outputs.append(ModelOutput(id=case.id, output=output))
        print(f"generated {index}/{len(cases)}: {case.id}", flush=True)

    resolved_tokenizer_revision = (
        tokenizer.init_kwargs.get("_commit_hash") or config.model_revision
    )
    if sha256_file(cases_path) != cases_sha256:
        raise GenerationError("the frozen evaluation cases changed during generation")
    if sha256_file(config.dataset_manifest_file) != plan.dataset_manifest_sha256:
        raise GenerationError("the dataset manifest changed during generation")
    manifest = GenerationRunManifest(
        run_id=normalized_run_id,
        role=role,
        model_id=config.model_id,
        base_model_id=config.model_id,
        base_model_revision=resolved_model_revision,
        tokenizer_revision=resolved_tokenizer_revision,
        adapter_id=adapter_id,
        prompt_strategy=PROMPT_STRATEGY,
        chat_template_sha256=hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        system_prompt_sha256=hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        cases_sha256=cases_sha256,
        dataset_manifest_sha256=plan.dataset_manifest_sha256,
        decoding=DecodingSettings(
            temperature=0,
            top_p=1,
            max_new_tokens=max_new_tokens,
            seed=seed,
        ),
    )
    atomic_write(output_path, serialize_jsonl(outputs))
    atomic_write_json(manifest_path, manifest.model_dump(mode="json", exclude_none=True))
    return len(outputs)
