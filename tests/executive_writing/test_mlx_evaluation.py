from __future__ import annotations

import json
from pathlib import Path

import pytest

from goodprose.executive_writing.baseline import load_config, load_retrieval_examples
from goodprose.executive_writing.benchmark import load_cases, score_output_v1_1
from goodprose.executive_writing.mlx_evaluation import (
    GeneratedStep,
    StepMetrics,
    generate_case,
    load_eval_config,
    publish_mlx_b1_results,
    summarize_candidate,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM_CONFIG = REPO_ROOT / "programs" / "executive-writing" / "configs"
B1_ROOT = REPO_ROOT / "evals" / "executive-writing" / "goodprose-b1-v1"


class FakeGenerator:
    def __init__(self) -> None:
        self.prompts: list[tuple[str, int]] = []

    def generate(self, prompt: str, *, max_tokens: int) -> GeneratedStep:
        self.prompts.append((prompt, max_tokens))
        output = "ledger output" if "atomic source ledger" in prompt else "finished artifact"
        return GeneratedStep(
            output=output,
            latency_ms=10.0,
            metrics=StepMetrics(
                prompt_tokens=20,
                output_tokens=5,
                prompt_tokens_per_second=100.0,
                generation_tokens_per_second=50.0,
                peak_memory_gb=0.5,
                finish_reason="stop",
            ),
        )


def test_eval_config_pins_adapter_base_and_matched_strategies() -> None:
    config = load_eval_config(PROGRAM_CONFIG / "training" / "MLX_B1_SMOKE_EVAL_v1.json")

    assert config.strategies == ("profile", "ledger_draft")
    assert config.adapter.adapter_sha256.startswith("becaefb39f4f")
    assert config.decoding.temperature == 0
    assert config.settled_cost_usd == 0


def test_unified_eval_config_pins_final_adapter_and_same_comparison() -> None:
    config = load_eval_config(PROGRAM_CONFIG / "training" / "MLX_B1_UNIFIED_PILOT_EVAL_v1.json")

    assert config.strategies == ("profile", "ledger_draft")
    assert config.adapter.training_experiment_id == "qwen2.5-0.5b-mlx-lora-unified-pilot-v1"
    assert config.adapter.candidate_lineage == "qwen2.5-0.5b-unified-pilot-lora-v1"
    assert config.adapter.adapter_sha256 == (
        "3f2826e671c316dca9731179a66299a119ca98c31fefbfad33b747b4c03b2ee6"
    )
    assert config.decoding.temperature == 0


def test_eval_config_rejects_crossed_training_lineage(tmp_path: Path) -> None:
    config_path = PROGRAM_CONFIG / "training" / "MLX_B1_UNIFIED_PILOT_EVAL_v1.json"
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["adapter"]["candidate_lineage"] = "qwen2.5-0.5b-instruct-4bit-lora-smoke-v1"
    crossed = tmp_path / "crossed.json"
    crossed.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(Exception, match="does not match training experiment"):
        load_eval_config(crossed)


def test_profile_generation_uses_one_frozen_call() -> None:
    config = load_eval_config(PROGRAM_CONFIG / "training" / "MLX_B1_SMOKE_EVAL_v1.json")
    case = load_cases(B1_ROOT / "cases.jsonl")[0]
    generator = FakeGenerator()
    profile = load_config(PROGRAM_CONFIG / "baselines" / "qwen2.5-0.5b-profile-v1.json")

    generation, metrics = generate_case(
        case=case,
        candidate_id="candidate",
        strategy="profile",
        generator=generator,
        profile_config=profile,
        retrieval_examples=[],
        decoding=config.decoding,
    )

    assert len(generator.prompts) == 1
    assert generator.prompts[0][1] == 512
    assert generation.pipeline_steps == ()
    assert len(metrics) == 1


def test_ledger_draft_generation_preserves_two_step_provenance() -> None:
    config = load_eval_config(PROGRAM_CONFIG / "training" / "MLX_B1_SMOKE_EVAL_v1.json")
    case = load_cases(B1_ROOT / "cases.jsonl")[0]
    generator = FakeGenerator()
    profile = load_config(PROGRAM_CONFIG / "baselines" / "qwen2.5-0.5b-profile-v1.json")
    examples = load_retrieval_examples(PROGRAM_CONFIG / "baselines/retrieval-examples-v1.json")

    generation, metrics = generate_case(
        case=case,
        candidate_id="candidate",
        strategy="ledger_draft",
        generator=generator,
        profile_config=profile,
        retrieval_examples=examples,
        decoding=config.decoding,
    )

    assert [step.step_id for step in generation.pipeline_steps] == ["ledger", "draft"]
    assert [value for _, value in generator.prompts] == [192, 512]
    assert len(metrics) == 2


def test_candidate_summary_keeps_quality_gate_latency_and_memory() -> None:
    case = load_cases(B1_ROOT / "cases.jsonl")[0]
    generator = FakeGenerator()
    config = load_eval_config(PROGRAM_CONFIG / "training" / "MLX_B1_SMOKE_EVAL_v1.json")
    profile = load_config(PROGRAM_CONFIG / "baselines" / "qwen2.5-0.5b-profile-v1.json")
    generation, metrics = generate_case(
        case=case,
        candidate_id="candidate",
        strategy="profile",
        generator=generator,
        profile_config=profile,
        retrieval_examples=[],
        decoding=config.decoding,
    )
    score = score_output_v1_1(case, generation.output, candidate_id="candidate")

    summary = summarize_candidate([score], [generation], metrics)

    assert summary["case_count"] == 1
    assert summary["latency_ms"]["mean"] == 10.0
    assert summary["peak_memory_gb"] == 0.5
    assert summary["settled_cost_usd"] == 0


def test_publish_refuses_incomplete_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "run-manifest.json").write_text('{"status":"failed"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="incomplete"):
        publish_mlx_b1_results(
            run_dir=run_dir,
            cases_path=B1_ROOT / "cases.jsonl",
            training_record_path=tmp_path / "training.json",
            results_path=tmp_path / "results.json",
            case_results_path=tmp_path / "cases.jsonl",
            generated_at="2026-08-23T05:35:00Z",
        )
