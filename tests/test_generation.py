from __future__ import annotations

import contextlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import goodprose.generation as generation
from goodprose.generation import GenerationError, generate_eval_outputs
from goodprose.jsonl import atomic_write_json, load_jsonl
from goodprose.models import (
    GenerationRunManifest,
    InputMethod,
    ModelOutput,
    Split,
    SystemLabel,
    WritingPair,
)
from goodprose.sft import SYSTEM_PROMPT, build_sft


class _FakeTensor:
    shape = (1, 2)

    def to(self, device: str) -> _FakeTensor:
        assert device == "cuda"
        return self

    def __getitem__(self, key: slice) -> list[int]:
        assert key == slice(2, None)
        return [99]


class _FakeTokenizer:
    chat_template = "frozen chat template"
    pad_token: str | None = None
    eos_token = "<eos>"
    pad_token_id = 0
    eos_token_id = 1
    def __init__(self) -> None:
        self.init_kwargs = {"_commit_hash": "resolved-tokenizer-revision"}
        self.template_kwargs: dict[str, Any] = {}
        self.messages: list[dict[str, str]] = []

    def apply_chat_template(
        self, messages: list[dict[str, str]], **kwargs: Any
    ) -> str:
        self.messages = messages
        self.template_kwargs = kwargs
        return "rendered prompt"

    def __call__(self, prompt: str, *, return_tensors: str) -> dict[str, _FakeTensor]:
        assert prompt == "rendered prompt"
        assert return_tensors == "pt"
        return {"input_ids": _FakeTensor(), "attention_mask": _FakeTensor()}

    def decode(self, tokens: list[int], *, skip_special_tokens: bool) -> str:
        assert tokens == [99]
        assert skip_special_tokens is True
        return "  Generated blog prose.  "


class _FakeModel:
    device = "cuda"

    def __init__(self) -> None:
        self.config = SimpleNamespace(_commit_hash="resolved-model-revision")
        self.generate_kwargs: dict[str, Any] = {}
        self.evaluating = False

    def eval(self) -> None:
        self.evaluating = True

    def generate(self, **kwargs: Any) -> list[_FakeTensor]:
        self.generate_kwargs = kwargs
        return [_FakeTensor()]


def _pair(identifier: str, split: Split) -> WritingPair:
    return WritingPair(
        id=identifier,
        post_id=identifier,
        lineage_id=identifier,
        split=split,
        input=f"Notes for {identifier}",
        input_method=InputMethod.ORIGINAL_OUTLINE,
        title=f"Title {identifier}",
        output=f"Published {identifier}",
    )


def _config(tmp_path: Path) -> tuple[Path, Path]:
    pairs_path = tmp_path / "pairs.jsonl"
    pairs_path.write_text(
        "\n".join(
            pair.model_dump_json()
            for pair in (
                _pair("train", Split.TRAIN),
                _pair("dev", Split.DEV),
                _pair("test", Split.TEST),
            )
        )
        + "\n"
    )
    cases_path = tmp_path / "cases.jsonl"
    build_sft(pairs_path, tmp_path / "sft", cases_path)
    config_path = tmp_path / "config.json"
    atomic_write_json(
        config_path,
        {
            "version": 1,
            "model_id": "example/model",
            "model_revision": "configured-revision",
            "train_file": "sft/train.jsonl",
            "eval_file": "sft/dev.jsonl",
            "dataset_manifest_file": "sft/manifest.json",
            "output_dir": "run",
            "precision": "bfloat16",
        },
    )
    return config_path, cases_path


def test_generate_eval_outputs_uses_matched_greedy_qwen_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path, cases_path = _config(tmp_path)
    tokenizer = _FakeTokenizer()
    model = _FakeModel()
    fake_transformers = SimpleNamespace(
        AutoTokenizer=SimpleNamespace(from_pretrained=lambda *args, **kwargs: tokenizer),
        AutoModelForCausalLM=SimpleNamespace(from_pretrained=lambda *args, **kwargs: model),
        set_seed=lambda seed: None,
    )
    fake_torch = SimpleNamespace(
        bfloat16="bfloat16",
        float16="float16",
        float32="float32",
        manual_seed=lambda seed: None,
        cuda=SimpleNamespace(is_available=lambda: False, manual_seed_all=lambda seed: None),
        inference_mode=contextlib.nullcontext,
    )
    monkeypatch.setattr(
        generation,
        "_module",
        lambda name: {"torch": fake_torch, "transformers": fake_transformers}[name],
    )
    output_path = tmp_path / "base.jsonl"
    manifest_path = tmp_path / "base-run.json"

    assert (
        generate_eval_outputs(
            config_path,
            cases_path,
            output_path,
            manifest_path,
            role=SystemLabel.BASELINE,
            run_id="base-run",
            max_new_tokens=256,
            seed=7,
        )
        == 1
    )

    assert load_jsonl(output_path, ModelOutput) == [
        ModelOutput(id="test", output="Generated blog prose.")
    ]
    assert tokenizer.messages == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Notes for test"},
    ]
    assert tokenizer.template_kwargs == {
        "tokenize": False,
        "add_generation_prompt": True,
        "enable_thinking": False,
    }
    assert model.evaluating is True
    assert model.generate_kwargs["do_sample"] is False
    assert model.generate_kwargs["max_new_tokens"] == 256
    manifest = GenerationRunManifest.model_validate(json.loads(manifest_path.read_text()))
    assert manifest.base_model_revision == "resolved-model-revision"
    assert manifest.tokenizer_revision == "resolved-tokenizer-revision"
    assert manifest.decoding.temperature == 0
    assert manifest.decoding.seed == 7


def test_generate_eval_outputs_requires_adapter_only_for_candidate(tmp_path: Path) -> None:
    with pytest.raises(GenerationError, match="candidate generation requires"):
        generate_eval_outputs(
            tmp_path / "missing-config.json",
            tmp_path / "cases.jsonl",
            tmp_path / "output.jsonl",
            tmp_path / "manifest.json",
            role=SystemLabel.CANDIDATE,
            run_id="candidate",
        )

    with pytest.raises(GenerationError, match="baseline generation must not"):
        generate_eval_outputs(
            tmp_path / "missing-config.json",
            tmp_path / "cases.jsonl",
            tmp_path / "output.jsonl",
            tmp_path / "manifest.json",
            role=SystemLabel.BASELINE,
            run_id="baseline",
            adapter_path=tmp_path / "checkpoint",
        )
