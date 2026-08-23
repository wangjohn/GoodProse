from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from goodprose.executive_writing.baseline import Generation
from goodprose.executive_writing.benchmark import load_cases, score_output_v1_1
from goodprose.executive_writing.ox_ceiling import (
    OxInvocation,
    build_ox_prompt,
    load_ox_ceiling_config,
    publish_ox_b1_ceiling_results,
    run_ox_b1_ceiling,
)
from goodprose.jsonl import (
    atomic_write,
    atomic_write_json,
    serialize_jsonl,
    sha256_bytes,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
B1_CASES = REPO_ROOT / "evals/executive-writing/goodprose-b1-v1/cases.jsonl"


class FakeInvoker:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def invoke(self, *, prompt: str, title: str, runtime_dir: Path) -> OxInvocation:
        self.prompts.append(prompt)
        output = "Subject: Update\n\nThe source-backed update and requested next step are recorded."
        return OxInvocation(
            output=output,
            session_id=f"synthetic-{len(self.prompts):02d}",
            raw_events=(json.dumps({"type": "text", "title": title}) + "\n").encode(),
            latency_ms=10.0,
            prompt_tokens=100,
            output_tokens=20,
            cache_read_tokens=0,
            cache_write_tokens=0,
            finish_reason="stop",
            cost_usd=Decimal(0),
            model_id="stealth/ox-alpha",
            provider="openrouter",
            opencode_version="1.18.21",
        )


def _write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    opencode_config = tmp_path / "opencode.json"
    opencode_config.write_text(
        json.dumps(
            {
                "$schema": "https://opencode.ai/config.json",
                "agent": {
                    "goodprose-ceiling": {
                        "description": "synthetic test agent",
                        "mode": "primary",
                        "permission": {"*": "deny"},
                        "steps": 1,
                        "temperature": 0,
                        "top_p": 1,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    cases = load_cases(B1_CASES)
    baseline_dir = tmp_path / "baseline"
    baseline_dir.mkdir()
    baseline_id = "qwen2.5-0.5b-retrieval-ledger-draft-v2"
    outputs = [
        Generation(
            case_id=case.id,
            candidate_id=baseline_id,
            prompt_sha256="0" * 64,
            output=case.input.source_material,
            output_sha256=sha256_bytes(case.input.source_material.encode()),
            latency_ms=1,
        )
        for case in cases
    ]
    scores = [
        score_output_v1_1(case, case.input.source_material, candidate_id=baseline_id)
        for case in cases
    ]
    outputs_path = baseline_dir / "outputs.jsonl"
    scores_path = baseline_dir / "scores.jsonl"
    summary_path = baseline_dir / "summary.json"
    atomic_write(outputs_path, serialize_jsonl(outputs))
    atomic_write(scores_path, serialize_jsonl(scores))
    atomic_write_json(summary_path, {"candidate_id": baseline_id})

    config_path = tmp_path / "config.json"
    atomic_write_json(
        config_path,
        {
            "version": 1,
            "experiment_id": "ox-alpha-b1-ceiling-v1",
            "candidate_id": "ox-alpha-b1-profile-v1",
            "benchmark_id": "goodprose-b1-v1",
            "benchmark_cases_sha256": sha256_file(B1_CASES),
            "scorer_version": "goodprose-deterministic-v1.1",
            "provider": "openrouter",
            "model_id": "stealth/ox-alpha",
            "input_classification": "sanitized_project_authored_visible_b1",
            "intended_use": "strong_quality_ceiling_and_candidate_baseline_only",
            "prompt_version": "goodprose-ox-ceiling-prompt-v1",
            "harness": {
                "ori_path": "/synthetic/ori",
                "ori_version": "0.8.0+3511459",
                "opencode_path": "/synthetic/opencode",
                "opencode_version": "1.18.21",
                "opencode_install_source": "official npm package opencode-ai@1.18.21",
                "opencode_config_path": "opencode.json",
                "opencode_config_sha256": sha256_file(opencode_config),
                "agent": "goodprose-ceiling",
                "reasoning_effort": "high",
                "temperature": 0,
                "top_p": 1,
                "max_agent_steps": 1,
                "pure": True,
                "timeout_seconds": 180,
                "max_attempts": 2,
            },
            "inventory": {
                "minimum_context_length": 1048576,
                "minimum_max_completion_tokens": 131072,
                "required_supported_parameters": ["reasoning_effort", "temperature", "top_p"],
                "require_all_reported_prices_zero": True,
            },
            "comparison_baseline": {
                "candidate_id": baseline_id,
                "scores_path": "baseline/scores.jsonl",
                "scores_sha256": sha256_file(scores_path),
                "outputs_path": "baseline/outputs.jsonl",
                "outputs_sha256": sha256_file(outputs_path),
                "summary_path": "baseline/summary.json",
                "summary_sha256": sha256_file(summary_path),
            },
            "advancement_minimum_effect_points": 2.0,
            "require_no_hard_gate_regression": True,
            "settled_cost_usd": 0,
        },
    )
    return config_path, opencode_config


def test_prompt_contains_only_input_side_material(tmp_path: Path) -> None:
    config_path, _ = _write_fixture(tmp_path)
    config = load_ox_ceiling_config(config_path, repo_root=tmp_path)
    case = load_cases(B1_CASES)[0]

    prompt = build_ox_prompt(case, config)

    assert case.input.source_material in prompt
    assert case.input.objective in prompt
    assert "required_facts" not in prompt
    assert "forbidden_claims" not in prompt
    assert "development_score" not in prompt


def test_mocked_run_and_publisher_preserve_provenance(tmp_path: Path) -> None:
    config_path, _ = _write_fixture(tmp_path)
    invoker = FakeInvoker()
    run_dir = run_ox_b1_ceiling(
        config_path=config_path,
        cases_path=B1_CASES,
        output_root=tmp_path / "runs",
        repo_root=tmp_path,
        code_revision="1" * 40,
        started_at="2026-08-23T20:00:00Z",
        invoker=invoker,
        inventory={"id": "stealth/ox-alpha", "pricing": {"prompt": "0"}},
    )

    manifest = json.loads((run_dir / "run-manifest.json").read_text())
    assert manifest["status"] == "completed"
    assert manifest["case_count"] == 24
    assert len(manifest["sessions"]) == 24
    assert manifest["aggregate_tokens"] == {
        "input": 2400,
        "output": 480,
        "cache_read": 0,
        "cache_write": 0,
    }
    assert len(invoker.prompts) == 24

    results_path = tmp_path / "analysis.json"
    case_results_path = tmp_path / "case-results.jsonl"
    result = publish_ox_b1_ceiling_results(
        config_path=config_path,
        run_dir=run_dir,
        cases_path=B1_CASES,
        repo_root=tmp_path,
        results_path=results_path,
        case_results_path=case_results_path,
        generated_at="2026-08-23T20:01:00Z",
    )

    assert result["source_run_manifest_sha256"] == sha256_file(run_dir / "run-manifest.json")
    assert result["candidate"]["case_count"] == 24
    assert result["settled_cost_usd"] == 0
    assert len(case_results_path.read_text().splitlines()) == 24


def test_config_rejects_agent_config_hash_drift(tmp_path: Path) -> None:
    config_path, opencode_config = _write_fixture(tmp_path)
    opencode_config.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="agent config hash"):
        load_ox_ceiling_config(config_path, repo_root=tmp_path)
