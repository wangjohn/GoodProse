from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from goodprose.executive_writing.baseline import (
    BaselineConfig,
    Generation,
    LocalModelIdentity,
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
    validate_local_model_identity,
    validate_local_resources,
)
from goodprose.executive_writing.benchmark import load_cases

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = REPO_ROOT / "programs" / "executive-writing" / "configs" / "baselines"
BENCHMARK_ROOT = REPO_ROOT / "evals" / "executive-writing" / "goodprose-b1-v1"


def _identity(config_path: Path) -> LocalModelIdentity:
    config = load_config(config_path)
    return LocalModelIdentity(
        model_id=config.model_id,
        ollama_version=config.ollama_version,
        manifest_sha256=config.model_manifest_sha256,
        blob_sha256=config.model_blob_sha256,
        installed_size_bytes=397_000_000,
        format="gguf",
        architecture="qwen2",
        parameter_count=494_000_000,
        quantization="Q4_K_M",
        context_length=32_768,
        license="Apache-2.0",
    )


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
    h11 = load_config(CONFIG_ROOT / "qwen2.5-7b-retrieval-ledger-draft-h11-v1.json")

    assert config.strategy == "ledger_draft"
    assert config.pipeline_token_limits is not None
    assert config.pipeline_token_limits.ledger == 192
    assert config.pipeline_token_limits.draft == 512
    assert h11.model_id == "qwen2.5:7b-instruct"
    assert h11.prompt_version == config.prompt_version
    assert h11.retrieval_examples_path == config.retrieval_examples_path
    assert h11.pipeline_token_limits == config.pipeline_token_limits
    assert h11.decoding == config.decoding
    assert h11.resource_limits is not None


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


def test_local_model_identity_rejects_manifest_and_blob_drift() -> None:
    config = load_config(CONFIG_ROOT / "qwen2.5-0.5b-minimal-v1.json")
    tags = {
        "models": [
            {
                "name": config.model_id,
                "digest": config.model_manifest_sha256,
                "size": 397_000_000,
            }
        ]
    }
    show = {
        "modelfile": f"FROM /models/blobs/sha256-{config.model_blob_sha256}",
        "details": {"format": "gguf", "quantization_level": "Q4_K_M"},
        "model_info": {
            "general.license": "apache-2.0",
            "general.parameter_count": 494_000_000,
            "general.architecture": "qwen2",
            "qwen2.context_length": 32_768,
        },
    }

    identity = validate_local_model_identity(
        config,
        version_payload={"version": config.ollama_version},
        tags_payload=tags,
        show_payload=show,
    )
    assert identity.manifest_sha256 == config.model_manifest_sha256
    assert identity.blob_sha256 == config.model_blob_sha256

    tags["models"][0]["digest"] = "f" * 64
    with pytest.raises(ValueError, match="manifest digest drifted"):
        validate_local_model_identity(
            config,
            version_payload={"version": config.ollama_version},
            tags_payload=tags,
            show_payload=show,
        )

    tags["models"][0]["digest"] = config.model_manifest_sha256
    show["modelfile"] = f"FROM /models/blobs/sha256-{'f' * 64}"
    with pytest.raises(ValueError, match="primary blob digest drifted"):
        validate_local_model_identity(
            config,
            version_payload={"version": config.ollama_version},
            tags_payload=tags,
            show_payload=show,
        )


def test_local_resource_limits_are_enforced() -> None:
    config = load_config(CONFIG_ROOT / "qwen2.5-7b-retrieval-ledger-draft-h11-v1.json")
    identity = LocalModelIdentity(
        model_id=config.model_id,
        ollama_version=config.ollama_version,
        manifest_sha256=config.model_manifest_sha256,
        blob_sha256=config.model_blob_sha256,
        installed_size_bytes=4_683_087_332,
        format="gguf",
        architecture="qwen2",
        parameter_count=7_615_616_512,
        quantization="Q4_K_M",
        context_length=32_768,
        license="Apache-2.0",
    )

    result = validate_local_resources(config, identity, available_disk_bytes=40 * 1024**3)
    assert result["limits_required"] is True

    with pytest.raises(RuntimeError, match="below the frozen"):
        validate_local_resources(config, identity, available_disk_bytes=29 * 1024**3)


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
        model_identity=_identity(CONFIG_ROOT / "qwen2.5-0.5b-minimal-v1.json"),
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
        model_identity=_identity(CONFIG_ROOT / "qwen2.5-0.5b-retrieval-ledger-verify-v1.json"),
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
