from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from goodprose.executive_writing.baseline import (
    BaselineConfig,
    OllamaClient,
    build_prompt,
    load_config,
    load_retrieval_examples,
    retrieve_example,
    run_baseline,
)
from goodprose.executive_writing.benchmark import load_cases

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = REPO_ROOT / "programs" / "executive-writing" / "configs" / "baselines"
BENCHMARK_ROOT = REPO_ROOT / "evals" / "executive-writing" / "goodprose-b1-v1"


def test_all_baseline_configs_are_pinned_and_local() -> None:
    configs = [
        load_config(CONFIG_ROOT / "qwen2.5-0.5b-minimal-v1.json"),
        load_config(CONFIG_ROOT / "qwen2.5-0.5b-profile-v1.json"),
        load_config(CONFIG_ROOT / "qwen2.5-0.5b-retrieval-v1.json"),
    ]

    assert {config.strategy for config in configs} == {"minimal", "profile", "retrieval"}
    assert {config.model_id for config in configs} == {"qwen2.5:0.5b-instruct"}
    assert {config.decoding.seed for config in configs} == {20260822}
    assert {config.decoding.temperature for config in configs} == {0}


def test_external_baseline_endpoint_is_rejected() -> None:
    payload = load_config(CONFIG_ROOT / "qwen2.5-0.5b-minimal-v1.json").model_dump(mode="json")
    payload["endpoint"] = "https://example.com"

    with pytest.raises(ValidationError, match="local loopback"):
        BaselineConfig.model_validate(payload)


def test_retrieval_and_prompt_are_deterministic() -> None:
    case = load_cases(BENCHMARK_ROOT / "cases.jsonl")[0]
    config = load_config(CONFIG_ROOT / "qwen2.5-0.5b-retrieval-v1.json")
    examples = load_retrieval_examples(CONFIG_ROOT / "retrieval-examples-v1.json")

    selected = retrieve_example(case, examples)
    first = build_prompt(case, config, examples)
    second = build_prompt(case, config, examples)

    assert selected.id == "retrieval-email-parking-v1"
    assert first == second
    assert case.input.source_material in first
    assert selected.output in first
    assert "required_facts" not in first
    assert "forbidden_claims" not in first


def test_run_baseline_writes_provenance_complete_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_generate(self: OllamaClient, prompt: str) -> tuple[str, dict[str, int]]:
        assert "Source material:" in prompt
        return (
            "Subject: Update\n\nPlease review the supplied facts and reply by Friday.",
            {
                "prompt_tokens": 40,
                "output_tokens": 14,
                "total_duration_ns": 1_000_000,
                "load_duration_ns": 100_000,
            },
        )

    monkeypatch.setattr(OllamaClient, "generate", fake_generate)
    run_dir = run_baseline(
        config_path=CONFIG_ROOT / "qwen2.5-0.5b-minimal-v1.json",
        cases_path=BENCHMARK_ROOT / "cases.jsonl",
        benchmark_manifest_path=BENCHMARK_ROOT / "manifest.json",
        output_root=tmp_path,
        code_revision="test-revision",
    )

    manifest = json.loads((run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    assert manifest["model_id"] == "qwen2.5:0.5b-instruct"
    assert manifest["provider"] == "local_ollama"
    assert manifest["settled_cost_usd"] == 0
    assert set(manifest["artifact_hashes"]) == {
        "outputs_jsonl",
        "scores_jsonl",
        "summary_json",
    }
    assert summary["case_count"] == 24
    assert len((run_dir / "outputs.jsonl").read_text(encoding="utf-8").splitlines()) == 24
