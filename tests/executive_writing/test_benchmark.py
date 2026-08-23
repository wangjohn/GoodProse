from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from goodprose.executive_writing.benchmark import (
    BenchmarkCase,
    BenchmarkExpected,
    BenchmarkInput,
    BenchmarkProvenance,
    OutputFormat,
    SourceCase,
    TaskFamily,
    TextExpectation,
    build_benchmark,
    content_sha256,
    load_cases,
    score_output,
)


def _case() -> BenchmarkCase:
    source = (
        "Launch remains uncertain. Pilot starts October 8 with 12 customers. Keep [CLIENT] private."
    )
    return BenchmarkCase(
        version=1,
        id="b1-test",
        tier="B1",
        input=BenchmarkInput(
            task_family=TaskFamily.ROUGH_NOTES_TO_EXECUTIVE_EMAIL,
            output_format=OutputFormat.EMAIL,
            source_material=source,
            audience="leadership team",
            objective="announce the bounded pilot",
            profile_id="executive-house-v1",
            constraints=("Use a subject line.",),
        ),
        expected=BenchmarkExpected(
            required_facts=(
                TextExpectation(
                    id="date",
                    description="pilot date",
                    any_of=("October 8", "Oct. 8", "Oct 8"),
                ),
                TextExpectation(
                    id="size",
                    description="customer count",
                    any_of=("12 customers",),
                ),
                TextExpectation(
                    id="uncertainty",
                    description="uncertainty remains",
                    any_of=("remains uncertain", "still uncertain"),
                ),
            ),
            forbidden_claims=(
                TextExpectation(
                    id="guaranteed",
                    description="do not guarantee launch",
                    any_of=("launch is guaranteed",),
                ),
            ),
            required_placeholders=("[CLIENT]",),
            required_call_to_action=("send feedback", "reply with feedback"),
            opening_any_of=("pilot", "launch"),
            min_words=20,
            max_words=90,
            subject_required=True,
            headings_prohibited=True,
        ),
        provenance=BenchmarkProvenance(
            creation_method="project_authored",
            authored_by="codex",
            authored_at=datetime(2026, 8, 23, 2, 26, 9, tzinfo=UTC),
            rights_status="evaluation_approved_project_owned",
            lineage_group="lineage-test",
            topic="pilot",
            time_bucket="2026-q3",
            source_material_sha256=content_sha256(source),
        ),
        adversarial_features=("uncertainty", "placeholder"),
        difficulty="difficult",
    )


def test_score_output_passes_registered_hard_gates() -> None:
    output = (
        "Subject: Pilot starts October 8\n\n"
        "The pilot starts October 8 with 12 customers, including [CLIENT]. "
        "The broader launch remains uncertain. Please reply with feedback by Friday."
    )

    score = score_output(_case(), output, candidate_id="candidate-pass")

    assert score.passes_hard_gates
    assert score.dimensions["fidelity"] == 100
    assert score.errors == ()


def test_score_output_reports_critical_failures() -> None:
    output = "Subject: Guaranteed launch\n\nThe launch is guaranteed."

    score = score_output(_case(), output, candidate_id="candidate-fail")

    assert not score.passes_hard_gates
    assert "fabrication" in score.errors
    assert "omission" in score.errors
    assert "placeholder_loss" in score.errors


def test_case_rejects_wrong_source_hash() -> None:
    payload = _case().model_dump(mode="json")
    payload["provenance"]["source_material_sha256"] = "0" * 64

    with pytest.raises(ValueError, match="source_material_sha256 mismatch"):
        BenchmarkCase.model_validate(payload)


def test_build_benchmark_is_deterministic(tmp_path: Path) -> None:
    case = _case()
    source_case = SourceCase(
        version=case.version,
        id=case.id,
        tier=case.tier,
        input=case.input,
        expected=case.expected,
        lineage_group=case.provenance.lineage_group,
        topic=case.provenance.topic,
        time_bucket=case.provenance.time_bucket,
        adversarial_features=case.adversarial_features,
        difficulty=case.difficulty,
        authored_by="codex",
        authored_at=case.provenance.authored_at,
        rights_status="evaluation_approved_project_owned",
    )
    source_path = tmp_path / "cases.source.json"
    cases_path = tmp_path / "cases.jsonl"
    manifest_path = tmp_path / "manifest.json"
    schema_path = tmp_path / "case.schema.json"
    source_path.write_text(
        json.dumps([source_case.model_dump(mode="json")], indent=2) + "\n",
        encoding="utf-8",
    )

    first = build_benchmark(source_path, cases_path, manifest_path, schema_path)
    first_cases = cases_path.read_bytes()
    first_schema = schema_path.read_bytes()
    second = build_benchmark(source_path, cases_path, manifest_path, schema_path)

    assert first == second
    assert first_cases == cases_path.read_bytes()
    assert first_schema == schema_path.read_bytes()
    assert first.case_count == 1
    assert load_cases(cases_path) == [_case()]


def test_committed_b1_benchmark_rebuilds_byte_for_byte(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    benchmark_root = repo_root / "evals" / "executive-writing" / "goodprose-b1-v1"
    rebuilt_cases = tmp_path / "cases.jsonl"
    rebuilt_manifest = tmp_path / "manifest.json"
    rebuilt_schema = tmp_path / "case.schema.json"

    manifest = build_benchmark(
        benchmark_root / "cases.source.json",
        rebuilt_cases,
        rebuilt_manifest,
        rebuilt_schema,
    )
    cases = load_cases(rebuilt_cases)
    schema = json.loads(rebuilt_schema.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for case in cases:
        validator.validate(case.model_dump(mode="json"))

    assert len(cases) == 24
    assert manifest.case_count == 24
    assert rebuilt_cases.read_bytes() == (benchmark_root / "cases.jsonl").read_bytes()
    assert rebuilt_manifest.read_bytes() == (benchmark_root / "manifest.json").read_bytes()
    assert rebuilt_schema.read_bytes() == (benchmark_root / "case.schema.json").read_bytes()
