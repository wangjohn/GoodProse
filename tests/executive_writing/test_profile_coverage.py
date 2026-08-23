"""Mocked deterministic tests for the source-profile coverage runner."""

from __future__ import annotations

import json
import statistics
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

from goodprose.executive_writing.baseline import build_prompt
from goodprose.executive_writing.profile_coverage import (
    COMMON_EVALUATION_CASE_IDS,
    EXPECTED_GENERATION_CALLS,
    SCORER_VERSION_REQUIRED,
    CandidateSpec,
    CoverageInputs,
    load_coverage_inputs,
    plan_candidates,
    publish_coverage_results,
    run_coverage,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = (
    REPO_ROOT
    / "programs/executive-writing/configs/source-profile-evaluation/source-profile-coverage-v1.json"
)

PERSON_TOKENS = (
    "collison",
    "graham",
    "altman",
    "spolsky",
    "wilson",
    "heinemeier",
    "hansson",
    "fried",
    "willison",
    "doctorow",
    "bezos",
    "jassy",
)


class FakeClient:
    """Deterministic stand-in for OllamaClient.generate."""

    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.calls: list[tuple[str, str]] = []

    def generate(
        self, prompt: str, *, num_predict: int | None = None
    ) -> tuple[str, dict[str, int | None]]:
        index = len(self.calls)
        self.calls.append((prompt, self.outputs[min(index, len(self.outputs) - 1)]))
        return self.outputs[min(index, len(self.outputs) - 1)], {
            "prompt_tokens": 10,
            "output_tokens": 20,
            "total_duration_ns": 1_000_000,
            "load_duration_ns": None,
        }


@pytest.fixture(scope="module")
def inputs() -> CoverageInputs:
    return load_coverage_inputs(CONFIG_PATH)


def _expected_sequence(inputs: CoverageInputs) -> list[tuple[CandidateSpec, str]]:
    sequence: list[tuple[CandidateSpec, str]] = []
    for candidate in plan_candidates(inputs):
        for case in inputs.cases:
            sequence.append((candidate, case.id))
    return sequence


def _run(inputs: CoverageInputs, tmp_path: Path) -> tuple[Path, FakeClient]:
    sequence = _expected_sequence(inputs)
    outputs = [
        "House artifact body." if spec.profile is None else f"Profile artifact body {index}."
        for index, (spec, _) in enumerate(sequence)
    ]
    client = FakeClient(outputs)
    run_dir = run_coverage(
        inputs=inputs,
        output_root=tmp_path / "raw",
        code_revision="test-revision",
        client=client,
        started_at="2026-08-22T00:00:00+00:00",
    )
    return run_dir, client


def test_load_coverage_inputs_cross_validates_committed_artifacts(inputs: CoverageInputs) -> None:
    assert [case.id for case in inputs.cases] == list(COMMON_EVALUATION_CASE_IDS)
    candidates = plan_candidates(inputs)
    assert len(candidates) == 12
    assert candidates[0].profile is None
    assert [candidate.profile is None for candidate in candidates].count(True) == 1
    assert inputs.baseline_config.decoding.temperature == 0
    assert len(inputs.layout.manifest.people) == 11


def test_run_coverage_makes_exactly_72_ordered_calls(
    inputs: CoverageInputs, tmp_path: Path
) -> None:
    run_dir, client = _run(inputs, tmp_path)
    assert len(client.calls) == EXPECTED_GENERATION_CALLS == 72
    expected = [(spec.candidate_id, case_id) for spec, case_id in _expected_sequence(inputs)]

    # Reconstruct the actual order from per-call artifacts.
    records = [
        json.loads(line)
        for line in (run_dir / "outputs.jsonl").read_text("utf-8").splitlines()
        if line.strip()
    ]
    actual = [(record["candidate_id"], record["case_id"]) for record in records]
    assert actual == expected
    assert client.calls[0][0] == build_prompt(inputs.cases[0], inputs.baseline_config)

    scores = [
        json.loads(line)
        for line in (run_dir / "scores.jsonl").read_text("utf-8").splitlines()
        if line.strip()
    ]
    assert all(score["scorer_version"] == SCORER_VERSION_REQUIRED for score in scores)

    for name in ("outputs.jsonl", "scores.jsonl", "summary.json", "run-manifest.json"):
        assert (run_dir / name).is_file()

    with pytest.raises(ValueError, match="already exists"):
        run_coverage(
            inputs=inputs,
            output_root=tmp_path / "raw",
            code_revision="test-revision",
            client=FakeClient(["x"]),
        )


def test_model_prompts_contain_no_identity_sources_urls_or_rubric(
    inputs: CoverageInputs, tmp_path: Path
) -> None:
    _, client = _run(inputs, tmp_path)
    assert len(client.calls) == 72
    source_ids = {
        route.source_id for entry in inputs.layout.manifest.people for route in entry.source_routes
    }
    for prompt, _ in client.calls:
        lowered = prompt.casefold()
        for token in PERSON_TOKENS:
            assert token not in lowered
        assert "http://" not in prompt and "https://" not in prompt
        assert all(source_id not in prompt for source_id in source_ids)
        for marker in (
            "required_facts",
            "forbidden_claims",
            "must_preserve_spans",
            "development_score",
            "rubric",
            "reference answer",
        ):
            assert marker not in lowered
        # Descriptive prompts state the abstract-register policy explicitly.
        if "Descriptive writing profile" in prompt:
            assert "not a person" in prompt
            assert "do not imply any person" in prompt
            assert "Only the supplied project-authored task source below is authoritative" in prompt


def test_publisher_publishes_compact_source_text_free_results(
    inputs: CoverageInputs, tmp_path: Path
) -> None:
    run_dir, _ = _run(inputs, tmp_path)
    results_path = tmp_path / "results.json"
    case_results_path = tmp_path / "case-results.json"
    results = publish_coverage_results(
        config_path=CONFIG_PATH,
        run_dir=run_dir,
        results_path=results_path,
        case_results_path=case_results_path,
        generated_at="2026-08-22T01:00:00+00:00",
    )
    assert results["advancement_decision"] == "none_coverage_only"
    assert results["generation_call_count"] == 72
    assert results["retrieval_enabled"] is False
    assert results["no_third_party_text_in_prompts"] is True
    assert results["settled_cost_usd"] == 0
    assert len(results["paired_versus_house_control"]) == 11
    assert results["paired_versus_house_control"][0]["win_tie_loss"]["wins"] >= 1

    case_records: list[dict[str, Any]] = json.loads(case_results_path.read_text("utf-8"))
    control_id = inputs.config.house_control_candidate_id
    control = {
        record["case_id"]: record["development_score"]
        for record in case_records
        if record["candidate_id"] == control_id
    }
    first_comparison = results["paired_versus_house_control"][0]
    candidate = {
        record["case_id"]: record["development_score"]
        for record in case_records
        if record["candidate_id"] == first_comparison["candidate_id"]
    }
    deltas = [candidate[case.id] - control[case.id] for case in inputs.cases]
    assert first_comparison["paired_median_difference"] == round(statistics.median(deltas), 4)

    committed = results_path.read_text("utf-8") + case_results_path.read_text("utf-8")
    for line in (run_dir / "outputs.jsonl").read_text("utf-8").splitlines():
        if line.strip():
            assert json.loads(line)["output"] not in committed
    assert len(case_records) == 72
    assert all("output" not in record for record in case_records)
    assert all(record["output_sha256"] for record in case_records)


def test_publisher_rejects_tampered_raw_artifacts(inputs: CoverageInputs, tmp_path: Path) -> None:
    run_dir, _ = _run(inputs, tmp_path)
    outputs_file = run_dir / "outputs.jsonl"
    outputs_file.write_bytes(b"tampered\n")
    with pytest.raises(ValueError, match="tampered"):
        publish_coverage_results(
            config_path=CONFIG_PATH,
            run_dir=run_dir,
            results_path=tmp_path / "results2.json",
            case_results_path=tmp_path / "case-results2.json",
            generated_at="2026-08-22T02:00:00+00:00",
        )


def test_publisher_refuses_to_overwrite_committed_results(
    inputs: CoverageInputs, tmp_path: Path
) -> None:
    run_dir, _ = _run(inputs, tmp_path)
    results_path = tmp_path / "results.json"
    case_results_path = tmp_path / "case-results.json"
    publish_coverage_results(
        config_path=CONFIG_PATH,
        run_dir=run_dir,
        results_path=results_path,
        case_results_path=case_results_path,
        generated_at="2026-08-22T03:00:00+00:00",
    )
    with pytest.raises(ValueError, match="refusing to overwrite"):
        publish_coverage_results(
            config_path=CONFIG_PATH,
            run_dir=run_dir,
            results_path=results_path,
            case_results_path=tmp_path / "other-case-results.json",
            generated_at="2026-08-22T04:00:00+00:00",
        )


def test_config_rejects_unfrozen_posture(tmp_path: Path) -> None:
    from goodprose.executive_writing.profile_coverage import load_coverage_run_config

    data: dict[str, Any] = json.loads(CONFIG_PATH.read_text("utf-8"))
    broken = dict(data, retrieval_enabled=True)
    path = tmp_path / "bad-config.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match=r"retrieval_enabled|False"):
        load_coverage_run_config(path)

    broken = dict(data, settled_cost_usd=5)
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match=r"settled_cost_usd|0"):
        load_coverage_run_config(path)

    broken = dict(data, shared_case_ids=data["shared_case_ids"][:5])
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match="six-case"):
        load_coverage_run_config(path)


def test_publisher_recomputes_scores_instead_of_trusting_saved_fields(
    inputs: CoverageInputs, tmp_path: Path
) -> None:
    run_dir, _ = _run(inputs, tmp_path)
    scores_path = run_dir / "scores.jsonl"
    records = [json.loads(line) for line in scores_path.read_text("utf-8").splitlines()]
    records[0]["development_score"] = 0.0
    payload = (
        "\n".join(json.dumps(item, sort_keys=True, separators=(",", ":")) for item in records)
        + "\n"
    ).encode()
    scores_path.write_bytes(payload)
    manifest_path = run_dir / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    manifest["artifact_hashes"]["scores_jsonl"] = sha256(payload).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match=r"v1\.1 rescoring"):
        publish_coverage_results(
            config_path=CONFIG_PATH,
            run_dir=run_dir,
            results_path=tmp_path / "results.json",
            case_results_path=tmp_path / "case-results.json",
            generated_at="2026-08-22T05:00:00Z",
        )


def test_timestamp_inputs_require_timezones(inputs: CoverageInputs, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="timezone"):
        run_coverage(
            inputs=inputs,
            output_root=tmp_path / "raw",
            code_revision="test-revision",
            client=FakeClient(["x"]),
            started_at="2026-08-22T00:00:00",
        )
