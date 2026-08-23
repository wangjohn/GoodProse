from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from goodprose.executive_writing.baseline import (
    BaselineConfig,
    Generation,
    OllamaClient,
    build_compact_ledger_prompt,
    build_ledger_draft_prompt,
    build_ledger_prompt,
    build_prompt,
    build_revision_prompt,
    build_structured_draft_prompt,
    build_verification_prompt,
    load_config,
    load_retrieval_examples,
    retrieve_example,
    run_baseline,
    run_ledger_draft_pipeline,
    run_structured_pipeline,
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


def test_structured_config_is_pinned_and_uses_approved_retrieval() -> None:
    config = load_config(CONFIG_ROOT / "qwen2.5-0.5b-retrieval-ledger-verify-v1.json")

    assert config.strategy == "structured"
    assert config.model_id == "qwen2.5:0.5b-instruct"
    assert config.retrieval_examples_path is not None
    assert config.decoding.temperature == 0
    assert config.decoding.seed == 20260822


def test_ledger_draft_config_has_frozen_step_limits() -> None:
    config = load_config(CONFIG_ROOT / "qwen2.5-0.5b-retrieval-ledger-draft-v2.json")

    assert config.strategy == "ledger_draft"
    assert config.pipeline_token_limits is not None
    assert config.pipeline_token_limits.ledger == 192
    assert config.pipeline_token_limits.draft == 512


def test_generation_accepts_omitted_optional_runtime_metrics() -> None:
    generation = Generation.model_validate(
        {
            "case_id": "case-1",
            "candidate_id": "candidate-1",
            "prompt_sha256": "0" * 64,
            "output": "Finished artifact.",
            "output_sha256": "1" * 64,
            "latency_ms": 1.5,
        }
    )

    assert generation.prompt_tokens is None
    assert generation.total_duration_ns is None


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


def test_structured_prompts_are_rubric_isolated() -> None:
    case = load_cases(BENCHMARK_ROOT / "cases.jsonl")[0]
    examples = load_retrieval_examples(CONFIG_ROOT / "retrieval-examples-v1.json")
    prompts = (
        build_ledger_prompt(case),
        build_compact_ledger_prompt(case),
        build_structured_draft_prompt(case, "SUPPORTED FACTS — Wave 2", examples),
        build_ledger_draft_prompt(case, "FACT — Wave 2", examples),
        build_verification_prompt(case, "SUPPORTED FACTS — Wave 2", "Draft artifact"),
        build_revision_prompt(
            case,
            "SUPPORTED FACTS — Wave 2",
            "Draft artifact",
            "NO CORRECTIONS",
        ),
    )

    assert all(case.input.source_material in prompt for prompt in prompts)
    assert all("required_facts" not in prompt for prompt in prompts)
    assert all("forbidden_claims" not in prompt for prompt in prompts)


def test_structured_pipeline_records_all_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_generate(
        self: OllamaClient, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int]]:
        calls.append(prompt)
        return (
            f"step output {len(calls)}",
            {
                "prompt_tokens": 10,
                "output_tokens": 4,
                "total_duration_ns": 100,
                "load_duration_ns": 10,
            },
        )

    monkeypatch.setattr(OllamaClient, "generate", fake_generate)
    config = load_config(CONFIG_ROOT / "qwen2.5-0.5b-retrieval-ledger-verify-v1.json")
    case = load_cases(BENCHMARK_ROOT / "cases.jsonl")[0]
    examples = load_retrieval_examples(CONFIG_ROOT / "retrieval-examples-v1.json")

    generation = run_structured_pipeline(
        case,
        OllamaClient(config),
        examples,
        candidate_id=config.candidate_id,
    )

    assert len(calls) == 4
    assert [step.step_id for step in generation.pipeline_steps] == [
        "ledger",
        "draft",
        "verify",
        "revise",
    ]
    assert generation.output == "step output 4"
    assert generation.prompt_tokens == 40
    assert generation.output_tokens == 16


def test_ledger_draft_pipeline_applies_per_step_token_limits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    limits_seen: list[int | None] = []

    def fake_generate(
        self: OllamaClient, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int]]:
        limits_seen.append(num_predict)
        return (
            f"step output {len(limits_seen)}",
            {
                "prompt_tokens": 10,
                "output_tokens": 4,
                "total_duration_ns": 100,
                "load_duration_ns": 10,
            },
        )

    monkeypatch.setattr(OllamaClient, "generate", fake_generate)
    config = load_config(CONFIG_ROOT / "qwen2.5-0.5b-retrieval-ledger-draft-v2.json")
    case = load_cases(BENCHMARK_ROOT / "cases.jsonl")[0]
    examples = load_retrieval_examples(CONFIG_ROOT / "retrieval-examples-v1.json")
    assert config.pipeline_token_limits is not None

    generation = run_ledger_draft_pipeline(
        case,
        OllamaClient(config),
        examples,
        candidate_id=config.candidate_id,
        token_limits=config.pipeline_token_limits,
    )

    assert limits_seen == [192, 512]
    assert [step.step_id for step in generation.pipeline_steps] == ["ledger", "draft"]
    assert generation.output == "step output 2"


def test_run_baseline_writes_provenance_complete_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_generate(
        self: OllamaClient, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int]]:
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


def test_run_structured_baseline_writes_four_step_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def fake_generate(
        self: OllamaClient, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int]]:
        nonlocal calls
        calls += 1
        return (
            f"artifact step {calls}",
            {
                "prompt_tokens": 20,
                "output_tokens": 5,
                "total_duration_ns": 1_000_000,
                "load_duration_ns": 100_000,
            },
        )

    monkeypatch.setattr(OllamaClient, "generate", fake_generate)
    run_dir = run_baseline(
        config_path=CONFIG_ROOT / "qwen2.5-0.5b-retrieval-ledger-verify-v1.json",
        cases_path=BENCHMARK_ROOT / "cases.jsonl",
        benchmark_manifest_path=BENCHMARK_ROOT / "manifest.json",
        output_root=tmp_path,
        code_revision="test-structured-revision",
    )

    outputs = [
        json.loads(line)
        for line in (run_dir / "outputs.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    manifest = json.loads((run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    assert calls == 96
    assert all(len(item["pipeline_steps"]) == 4 for item in outputs)
    assert all(item["prompt_tokens"] == 80 for item in outputs)
    assert manifest["strategy"] == "structured"
    assert manifest["pipeline_step_ids"] == ["ledger", "draft", "verify", "revise"]
