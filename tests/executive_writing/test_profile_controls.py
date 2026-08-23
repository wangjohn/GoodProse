from __future__ import annotations

import json
from pathlib import Path

import pytest

from goodprose.executive_writing.baseline import LocalModelIdentity, load_config
from goodprose.executive_writing.benchmark import build_benchmark
from goodprose.executive_writing.profile_controls import (
    EXPECTED_GENERATION_CALLS,
    load_topic_control_inputs,
    plan_topic_control_candidates,
    publish_topic_control_results,
    run_topic_controls,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = (
    REPO_ROOT
    / "programs"
    / "executive-writing"
    / "configs"
    / "source-profile-evaluation"
    / "source-profile-topic-controls-v2.json"
)
BASELINE_PATH = (
    REPO_ROOT
    / "programs"
    / "executive-writing"
    / "configs"
    / "baselines"
    / "qwen2.5-0.5b-profile-v1.json"
)
EVAL_ROOT = REPO_ROOT / "evals" / "executive-writing" / "source-profile-topic-controls-v2"
LIMITATIONS = (
    "Six project-authored cases form three paired topic swaps and provide "
    "exploratory robustness evidence only.",
    "Lexical deterministic checks do not establish semantic writing quality "
    "or detect every unsupported claim.",
    "The source-text-free profile-card candidate has no dated fitting corpus, "
    "so leave-time-out is not applicable here and remains required before "
    "corpus-trained profile evaluation.",
)


class FakeClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(
        self, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int | None]]:
        self.prompts.append(prompt)
        return "Subject: Status\n\nThe source status remains under review.", {
            "prompt_tokens": 10,
            "output_tokens": 8,
            "total_duration_ns": 100,
            "load_duration_ns": 10,
        }


def _identity() -> LocalModelIdentity:
    config = load_config(BASELINE_PATH)
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


def _run(tmp_path: Path) -> tuple[Path, FakeClient]:
    client = FakeClient()
    run_dir = run_topic_controls(
        config_path=CONFIG_PATH,
        output_root=tmp_path / "raw",
        code_revision="test-revision",
        model_identity=_identity(),
        available_disk_bytes=20 * 1024**3,
        client=client,
        started_at="2026-08-23T23:30:00Z",
    )
    return run_dir, client


def test_topic_control_inputs_are_paired_project_owned_and_complete() -> None:
    inputs = load_topic_control_inputs(CONFIG_PATH)
    candidates = plan_topic_control_candidates(inputs)

    assert len(inputs.cases) == 6
    assert len(inputs.pair_manifest.pairs) == 3
    assert len(candidates) == 12
    assert candidates[0].profile is None
    assert all(
        case.provenance.rights_status == "evaluation_approved_project_owned"
        for case in inputs.cases
    )
    assert all("topic_swap" in case.adversarial_features for case in inputs.cases)


def test_committed_topic_control_benchmark_rebuilds_byte_for_byte(tmp_path: Path) -> None:
    cases_path = tmp_path / "cases.jsonl"
    manifest_path = tmp_path / "manifest.json"
    schema_path = tmp_path / "case.schema.json"

    build_benchmark(
        EVAL_ROOT / "cases.source.json",
        cases_path,
        manifest_path,
        schema_path,
        benchmark_id="source-profile-topic-controls-v2",
        limitations=LIMITATIONS,
    )

    assert cases_path.read_bytes() == (EVAL_ROOT / "cases.jsonl").read_bytes()
    assert manifest_path.read_bytes() == (EVAL_ROOT / "manifest.json").read_bytes()
    assert schema_path.read_bytes() == (EVAL_ROOT / "case.schema.json").read_bytes()


def test_topic_control_runner_makes_exact_ordered_source_text_free_matrix(
    tmp_path: Path,
) -> None:
    run_dir, client = _run(tmp_path)

    assert len(client.prompts) == EXPECTED_GENERATION_CALLS == 72
    assert all("http://" not in prompt and "https://" not in prompt for prompt in client.prompts)
    for token in (
        "collison",
        "graham",
        "altman",
        "spolsky",
        "wilson",
        "hansson",
        "fried",
        "willison",
        "doctorow",
        "bezos",
        "jassy",
    ):
        assert all(token not in prompt.casefold() for prompt in client.prompts)
    outputs = [
        json.loads(line)
        for line in (run_dir / "outputs.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(outputs) == 72

    with pytest.raises(ValueError, match="already exists"):
        run_topic_controls(
            config_path=CONFIG_PATH,
            output_root=tmp_path / "raw",
            code_revision="test-revision",
            model_identity=_identity(),
            available_disk_bytes=20 * 1024**3,
            client=FakeClient(),
        )


def test_topic_control_publisher_recomputes_and_omits_outputs(tmp_path: Path) -> None:
    run_dir, _ = _run(tmp_path)
    results_path = tmp_path / "results.json"
    case_results_path = tmp_path / "case-results.json"

    results = publish_topic_control_results(
        config_path=CONFIG_PATH,
        run_dir=run_dir,
        results_path=results_path,
        case_results_path=case_results_path,
        generated_at="2026-08-23T23:35:00Z",
    )

    assert results["topic_swap_posture"].startswith("completed")
    assert results["advancement_decision"] == "none_coverage_only"
    assert len(results["candidates"]) == 12
    assert all(len(item["pair_diagnostics"]) == 3 for item in results["candidates"])
    compact = results_path.read_text(encoding="utf-8") + case_results_path.read_text(
        encoding="utf-8"
    )
    assert "The source status remains under review." not in compact
    assert all("output" not in item for item in json.loads(case_results_path.read_text()))

    with pytest.raises(ValueError, match="already exist"):
        publish_topic_control_results(
            config_path=CONFIG_PATH,
            run_dir=run_dir,
            results_path=results_path,
            case_results_path=tmp_path / "other.json",
            generated_at="2026-08-23T23:36:00Z",
        )


def test_topic_control_publisher_rejects_tampering(tmp_path: Path) -> None:
    run_dir, _ = _run(tmp_path)
    (run_dir / "scores.jsonl").write_text("tampered\n", encoding="utf-8")

    with pytest.raises(ValueError, match="hash mismatch"):
        publish_topic_control_results(
            config_path=CONFIG_PATH,
            run_dir=run_dir,
            results_path=tmp_path / "results.json",
            case_results_path=tmp_path / "case-results.json",
            generated_at="2026-08-23T23:37:00Z",
        )
