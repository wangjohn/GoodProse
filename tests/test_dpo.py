from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from goodprose.dpo import DpoError, prepare_dpo_run, run_dpo, text_preference_records
from goodprose.jsonl import atomic_write, atomic_write_json, serialize_jsonl
from goodprose.models import PreferencePair
from goodprose.sft import SYSTEM_PROMPT


def _preference(identifier: str) -> PreferencePair:
    return PreferencePair(
        id=identifier,
        lineage_id=identifier,
        prompt=(
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Notes for {identifier}"},
        ),
        chosen=f"Published {identifier}.",
        rejected=f"Model attempt {identifier}.",
        rejected_run_id="sft",
    )


def _config(tmp_path: Path, *, with_adapter: bool = True) -> Path:
    adapter = tmp_path / "runs" / "sft"
    if with_adapter:
        adapter.mkdir(parents=True, exist_ok=True)
        (adapter / "adapter_config.json").write_text("{}")
        (adapter / "adapter_model.safetensors").write_bytes(b"weights")
    preference_path = tmp_path / "sft" / "preference.jsonl"
    atomic_write(preference_path, serialize_jsonl([_preference("a"), _preference("b")]))
    config_path = tmp_path / "configs" / "dpo.json"
    atomic_write_json(
        config_path,
        {
            "version": 1,
            "model_id": "example/model",
            "sft_adapter": "../runs/sft",
            "preference_file": "../sft/preference.jsonl",
            "output_dir": "../runs/dpo",
            "gradient_accumulation_steps": 1,
        },
    )
    return config_path


def test_prepare_dpo_run_validates_pairs_and_adapter(tmp_path: Path) -> None:
    config, plan = prepare_dpo_run(_config(tmp_path))

    assert plan.preference_pairs == 2
    assert plan.optimizer_steps == 2
    assert plan.sft_adapter_id.startswith(str(config.sft_adapter))
    assert run_dpo(_config(tmp_path), validate_only=True)["rpo_alpha"] == 1.0


def test_prepare_dpo_run_requires_the_sft_adapter(tmp_path: Path) -> None:
    with pytest.raises(DpoError, match="does not exist"):
        prepare_dpo_run(_config(tmp_path, with_adapter=False))


class _Tokenizer:
    eos_token = "<eos>"

    def apply_chat_template(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return "".join(f"[{m['role']}]{m['content']}" for m in messages) + "[assistant]"


def test_text_preference_records_render_prompt_and_terminate_completions() -> None:
    [record] = text_preference_records([_preference("a")], _Tokenizer(), {})

    assert record["prompt"].endswith("Notes for a[assistant]")
    assert record["chosen"] == "Published a.<eos>"
    assert record["rejected"] == "Model attempt a.<eos>"
