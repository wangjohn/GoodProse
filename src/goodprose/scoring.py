"""Held-out negative log-likelihood of the author's completions under a checkpoint."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

from goodprose.chat import ChatTemplateError, verify_template_parity
from goodprose.generation import adapter_identifier, load_model
from goodprose.jsonl import atomic_write_json, sha256_file
from goodprose.training import (
    TrainingError,
    _load_records,
    load_tokenizer,
    prepare_lora_plus_run,
    text_prompt_completion_records,
)


class ScoringError(ValueError):
    """A likelihood scoring run is unsafe or incomplete."""


def _module(name: str) -> Any:
    try:
        return import_module(name)
    except ImportError as error:
        raise ScoringError(
            f"scoring dependency {name!r} is not installed; run `uv sync --extra train`"
        ) from error


def score_completions(
    config_path: Path,
    records_path: Path,
    output_path: Path,
    *,
    run_id: str,
    adapter_path: Path | None = None,
) -> dict[str, Any]:
    """Mean per-token NLL of each record's completion, rendered exactly as in training.

    Run this on ``data/sft/dev.jsonl`` for every checkpoint. A dev NLL that rises while train
    loss keeps falling is the memorisation signal the four-case human review cannot give you.
    """
    config, plan = prepare_lora_plus_run(config_path)
    try:
        records = _load_records(records_path, kind="scoring")
    except TrainingError as error:
        raise ScoringError(str(error)) from error
    adapter_id = adapter_identifier(adapter_path) if adapter_path is not None else None

    torch = _module("torch")
    transformers = _module("transformers")
    peft = _module("peft") if adapter_path is not None else None
    tokenizer = load_tokenizer(transformers, config)
    try:
        prefix_sha256 = verify_template_parity(
            tokenizer,
            [message.model_dump() for message in records[0].messages[:-1]],
            config.chat_template_kwargs,
        )
    except ChatTemplateError as error:
        raise ScoringError(str(error)) from error
    model = load_model(config, adapter_path, torch=torch, transformers=transformers, peft=peft)

    rendered = text_prompt_completion_records(records, tokenizer, config.chat_template_kwargs)
    per_record: list[dict[str, Any]] = []
    total_nll = 0.0
    total_tokens = 0
    for index, item in enumerate(rendered):
        prompt_ids = tokenizer(item["prompt"], add_special_tokens=False)["input_ids"]
        full_ids = tokenizer(item["prompt"] + item["completion"], add_special_tokens=False)[
            "input_ids"
        ]
        completion_tokens = len(full_ids) - len(prompt_ids)
        if completion_tokens < 1:
            raise ScoringError(f"record {index} has no completion tokens after the prompt")
        input_ids = torch.tensor([full_ids], device=model.device)
        labels = input_ids.clone()
        labels[:, : len(prompt_ids)] = -100
        with torch.inference_mode():
            loss = model(input_ids=input_ids, labels=labels).loss
        nll = float(loss) * completion_tokens
        total_nll += nll
        total_tokens += completion_tokens
        per_record.append(
            {
                "index": index,
                "completion_tokens": completion_tokens,
                "mean_nll": nll / completion_tokens,
            }
        )
        print(f"scored {index + 1}/{len(rendered)}", flush=True)

    report = {
        "version": 1,
        "run_id": run_id,
        "model_id": config.model_id,
        "adapter_id": adapter_id,
        "records_file": str(records_path),
        "records_sha256": sha256_file(records_path),
        "dataset_manifest_sha256": plan.dataset_manifest_sha256,
        "rendered_prompt_prefix_sha256": prefix_sha256,
        "records": len(per_record),
        "completion_tokens": total_tokens,
        "mean_nll": total_nll / total_tokens,
        "per_record": per_record,
    }
    atomic_write_json(output_path, report)
    return report
