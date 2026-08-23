"""Deterministic, fully synthetic tests for external evaluation adapters.

Every fixture here is project-authored and unmistakably synthetic. No real
benchmark content, no network access, and no model or judge calls exist.
A passing adapter test proves schema and acquisition compatibility only; it
is never a benchmark result.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest

from goodprose.executive_writing import external_evals as external_eval_module
from goodprose.executive_writing.__main__ import main
from goodprose.executive_writing.external_evals import (
    PINNED_ITERATER_TEST_COUNTS,
    WRITINGBENCH_BUSINESS_DEV_INDICES,
    WRITINGBENCH_ENGINEERING_DEV_INDICES,
    YAP_BOOTSTRAP_SEED,
    AdaptedManifest,
    BenchmarkId,
    CriterionAnchor,
    EvaluationCriterion,
    ExecutionStatus,
    ExternalPrediction,
    NormalizedExternalCase,
    RightsStatus,
    SourceRegistry,
    adapt_concision,
    adapt_editeval,
    adapt_iterater,
    adapt_writingbench,
    adapt_yapbench,
    build_source_registry,
    candidate_payload,
    normalize_concision_csv,
    parse_concise_references,
    read_concision_xlsx,
    score_yapbench,
    select_stratified_dev_indices,
    validate_predictions,
    verify_source,
    visible_characters,
)

SHA_A = "aa" * 32
SHA_B = "bb" * 32


def _sha_of_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Frozen registry
# ---------------------------------------------------------------------------


def test_registry_covers_exactly_seven_benchmarks() -> None:
    registry = build_source_registry()
    assert isinstance(registry, SourceRegistry)
    assert {entry.benchmark_id for entry in registry.entries} == set(BenchmarkId)
    assert len(registry.entries) == 7


def test_registry_pins_and_statuses_match_assignment() -> None:
    registry = build_source_registry()
    entries = {entry.benchmark_id: entry for entry in registry.entries}
    writingbench = entries[BenchmarkId.WRITINGBENCH_BUSINESS]
    assert writingbench.source.sha256 == (
        "18fee37c645166eb2e206b36366b2e354265b1e4201db2c86e759e825eaddcbe"
    )
    assert writingbench.source.bytes == 14_726_077
    assert writingbench.expected_source_rows == 1000
    assert writingbench.expected_domain_rows == 210
    assert writingbench.expected_eligible_rows == 115
    assert writingbench.selected_source_indices == WRITINGBENCH_BUSINESS_DEV_INDICES
    engineering = entries[BenchmarkId.WRITINGBENCH_ENGINEERING]
    assert engineering.expected_source_rows == 1000
    assert engineering.expected_domain_rows == 167
    assert engineering.expected_eligible_rows == 107
    assert engineering.selected_source_indices == WRITINGBENCH_ENGINEERING_DEV_INDICES
    for benchmark_id in (BenchmarkId.WRITINGBENCH_BUSINESS, BenchmarkId.WRITINGBENCH_ENGINEERING):
        assert entries[benchmark_id].execution_status == ExecutionStatus.JUDGE_UNPINNED
        assert entries[benchmark_id].rights_status == RightsStatus.EVALUATION_ONLY
    iterater = entries[BenchmarkId.ITERATER_DIAGNOSTIC]
    assert iterater.source.sha256 == (
        "1a30452c33bd5379ff56159016d68ecd7e2669ede1e4ea77244c6e300952e9cb"
    )
    assert iterater.source.bytes == 294_380
    assert iterater.execution_status == ExecutionStatus.ADAPTER_TESTED_NOT_EXECUTED
    concision = entries[BenchmarkId.REVISION_FOR_CONCISION]
    assert concision.source.sha256 == (
        "77f05c87f48f3e6dd25197bc921d38032ef145d834fce2d35e6e0125e798889e"
    )
    assert concision.rights_status == RightsStatus.EVALUATION_ONLY
    yap = entries[BenchmarkId.YAPBENCH]
    assert yap.source.sha256 == ("6bf58b51cef6b26e78cf462ff78d43d1b80d1162268be6019918036212430d5e")
    assert yap.source.bytes == 24_703
    assert yap.execution_status == ExecutionStatus.RIGHTS_BLOCKED
    assert yap.rights_status == RightsStatus.UNVERIFIED_BLOCKED
    assert yap.metric_version is not None and yap.normalization_version is not None


def test_pinned_iterater_counts_match_assignment() -> None:
    assert PINNED_ITERATER_TEST_COUNTS == {
        "clarity": 186,
        "coherence": 36,
        "fluency": 88,
        "meaning-changed": 35,
        "others": 4,
        "style": 15,
    }
    assert sum(PINNED_ITERATER_TEST_COUNTS.values()) == 364


# ---------------------------------------------------------------------------
# Source verification
# ---------------------------------------------------------------------------


def test_verify_source_rejects_hash_and_size_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "source.jsonl"
    path.write_bytes(b"synthetic\n")
    good = _sha_of_bytes(b"synthetic\n")
    assert verify_source(path, good) == good
    with pytest.raises(ValueError, match="sha256 mismatch"):
        verify_source(path, SHA_A)
    with pytest.raises(ValueError, match="byte-size mismatch"):
        verify_source(path, good, expected_bytes=99)


# ---------------------------------------------------------------------------
# WritingBench adapters
# ---------------------------------------------------------------------------


def _writingbench_record(
    index: int,
    domain1: str = "Finance & Business",
    domain2: str | None = None,
    lang: str = "en",
) -> dict[str, Any]:
    subdomains = ("Bid Proposal", "Briefing", "Contract", "Financial Reports")
    subdomain = domain2 if domain2 is not None else subdomains[index % len(subdomains)]
    checklist = [
        {
            "name": f"criterion {position}",
            "criteria_description": f"synthetic criterion {position}",
            "1-2": "synthetic poor anchor",
            "3-4": "synthetic weak anchor",
            "5-6": "synthetic adequate anchor",
            "7-8": "synthetic strong anchor",
            "9-10": "synthetic excellent anchor",
        }
        for position in range(2)
    ]
    return {
        "index": index,
        "domain1": domain1,
        "domain2": subdomain,
        "lang": lang,
        "query": f"synthetic query {index}",
        "checklist": checklist,
    }


def _wb_records(count: int = 40, **kwargs: Any) -> list[tuple[int, dict[str, Any]]]:
    return [(i, _writingbench_record(i, **kwargs)) for i in range(count)]


def test_writingbench_adapter_selects_stratified_dev_subset() -> None:
    cases, manifest = adapt_writingbench(
        _wb_records(40),
        benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
        source_revision="synthetic-rev",
        source_sha256=SHA_A,
        expected_domain_rows=40,
    )
    assert manifest.case_count == 40
    dev = [case for case in cases if case.split == "development"]
    full = [case for case in cases if case.split == "evaluation"]
    assert len(dev) == 32
    assert len(full) == 8
    assert manifest.selected_source_indices == tuple(sorted(case.source_index for case in dev))
    per_group: dict[str, int] = {}
    for case in dev:
        per_group[case.task] = per_group.get(case.task, 0) + 1
    assert set(per_group.values()) == {8}
    assert all(case.criteria for case in dev)


def test_writingbench_selection_is_deterministic() -> None:
    tasks = [f"sub-{i % 4}" for i in range(40)]
    first = select_stratified_dev_indices(tasks, 32)
    second = select_stratified_dev_indices(tasks, 32)
    assert first == second
    _, manifest_a = adapt_writingbench(
        _wb_records(40),
        benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
        source_revision="r",
        source_sha256=SHA_A,
        expected_domain_rows=40,
    )
    _, manifest_b = adapt_writingbench(
        _wb_records(40),
        benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
        source_revision="r",
        source_sha256=SHA_B,
        expected_domain_rows=40,
    )
    assert manifest_a.selected_source_indices == manifest_b.selected_source_indices


def test_writingbench_excludes_non_english_rows_and_rejects_unknown_language() -> None:
    records = _wb_records(40)
    records[0] = (0, _writingbench_record(0, lang="zh"))
    cases, manifest = adapt_writingbench(
        records,
        benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
        source_revision="r",
        source_sha256=SHA_A,
        expected_domain_rows=40,
    )
    assert len(cases) == 39
    assert manifest.excluded_counts == {"non_english_target_domain": 1}
    invalid = _wb_records(40)
    invalid[0] = (0, _writingbench_record(0, lang="fr"))
    with pytest.raises(ValueError, match="invalid language"):
        adapt_writingbench(
            invalid,
            benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
            source_revision="r",
            source_sha256=SHA_A,
            expected_domain_rows=40,
        )


def test_writingbench_rejects_unknown_fields_duplicate_index_empty_query() -> None:
    bad_unknown = dict(_writingbench_record(0))
    bad_unknown["reference"] = "leak"
    with pytest.raises(ValueError, match="unknown fields"):
        adapt_writingbench(
            [(0, bad_unknown)],
            benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
            source_revision="r",
            source_sha256=SHA_A,
            expected_domain_rows=1,
        )
    duplicate = [(3, _writingbench_record(3)), (7, _writingbench_record(3))]
    with pytest.raises(ValueError, match="duplicate source index"):
        adapt_writingbench(
            duplicate,
            benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
            source_revision="r",
            source_sha256=SHA_A,
            expected_domain_rows=2,
        )
    empty = (0, {**_writingbench_record(0), "query": ""})
    with pytest.raises(ValueError, match="non-empty string"):
        adapt_writingbench(
            [empty],
            benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
            source_revision="r",
            source_sha256=SHA_A,
            expected_domain_rows=1,
        )


def test_writingbench_rejects_wrong_row_count() -> None:
    with pytest.raises(ValueError, match="expected 210 rows"):
        adapt_writingbench(
            _wb_records(40),
            benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
            source_revision="r",
            source_sha256=SHA_A,
            expected_domain_rows=None,
        )


# ---------------------------------------------------------------------------
# IteraTeR / EditEval adapters
# ---------------------------------------------------------------------------


SYNTHETIC_LABEL_COUNTS = {
    "clarity": 4,
    "coherence": 2,
    "fluency": 2,
    "meaning-changed": 1,
    "others": 1,
    "style": 2,
}


def _iterater_records() -> list[tuple[int, dict[str, Any]]]:
    labels = [label for label, count in SYNTHETIC_LABEL_COUNTS.items() for _ in range(count)]
    return [
        (
            position + 1,
            {
                "before_sent": f"before sentence {position} with several words.",
                "before_sent_with_intent": f"intent-annotated {position}.",
                "after_sent": f"after sentence {position} revised.",
                "labels": label,
                "doc_id": f"doc-{position}",
                "revision_depth": 1,
            },
        )
        for position, label in enumerate(labels)
    ]


def test_iterater_adapter_emits_canonical_diagnostic_only() -> None:
    cases, manifest = adapt_iterater(
        _iterater_records(),
        source_revision="synthetic-rev",
        source_sha256=SHA_A,
        expected_label_counts=dict(SYNTHETIC_LABEL_COUNTS),
    )
    assert manifest.case_count == 8
    assert set(case.task for case in cases) <= {"clarity", "coherence", "fluency"}
    assert manifest.task_counts == {"clarity": 4, "coherence": 2, "fluency": 2}
    first = cases[0]
    assert isinstance(first, NormalizedExternalCase)
    assert first.input_text.startswith("before sentence")
    assert first.reference.startswith("after sentence")


def test_iterater_adapter_rejects_count_mismatch_bad_labels_multi_labels() -> None:
    with pytest.raises(ValueError, match="label count mismatch"):
        adapt_iterater(
            _iterater_records(),
            source_revision="r",
            source_sha256=SHA_A,
            expected_label_counts={**SYNTHETIC_LABEL_COUNTS, "clarity": 999},
        )
    invalid = _iterater_records()
    invalid[0] = (0, {**invalid[0][1], "labels": "plot"})
    with pytest.raises(ValueError, match="invalid label"):
        adapt_iterater(
            invalid,
            source_revision="r",
            source_sha256=SHA_A,
            expected_label_counts=dict(SYNTHETIC_LABEL_COUNTS),
        )
    multi = _iterater_records()
    multi[0] = (0, {**multi[0][1], "labels": ["clarity", "style"]})
    with pytest.raises(ValueError, match="labels must be a non-empty string"):
        adapt_iterater(
            multi,
            source_revision="r",
            source_sha256=SHA_A,
            expected_label_counts=dict(SYNTHETIC_LABEL_COUNTS),
        )


def test_editeval_filters_short_references_and_other_tasks() -> None:
    records = _iterater_records()
    short_position = next(
        position for position, (_, record) in enumerate(records) if record["labels"] == "clarity"
    )
    records[short_position] = (
        records[short_position][0],
        {**records[short_position][1], "after_sent": "X"},
    )
    cases, manifest = adapt_editeval(
        records,
        benchmark_id=BenchmarkId.EDITEVAL_CLARITY,
        source_revision="r",
        source_sha256=SHA_A,
        expected_label_counts=dict(SYNTHETIC_LABEL_COUNTS),
    )
    assert manifest.case_count == 3
    assert all(case.task == "clarity" for case in cases)
    assert all(len(case.reference) > 1 for case in cases)
    with pytest.raises(ValueError, match="not an EditEval benchmark"):
        adapt_editeval(
            records,
            benchmark_id=BenchmarkId.ITERATER_DIAGNOSTIC,
            source_revision="r",
            source_sha256=SHA_A,
        )


# ---------------------------------------------------------------------------
# Revision for Concision adapter
# ---------------------------------------------------------------------------

_XLSX_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _write_concision_xlsx(path: Path, rows: list[list[str]]) -> None:
    shared: list[str] = []
    for row in rows:
        for value in row:
            if value not in shared:
                shared.append(value)
    sst_items = "".join(f"<si><t>{value}</t></si>" for value in shared)
    shared_xml = (
        f'<?xml version="1.0"?><sst xmlns="{_XLSX_NS}" count="{len(shared)}" '
        f'uniqueCount="{len(shared)}">{sst_items}</sst>'
    )
    sheet_rows = []
    for row_number, row in enumerate(rows, start=1):
        cells = []
        for column_offset, value in enumerate(row):
            reference = f"{chr(ord('A') + column_offset)}{row_number}"
            cells.append(f'<c r="{reference}" t="s"><v>{shared.index(value)}</v></c>')
        sheet_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')
    sheet_xml = (
        f'<?xml version="1.0"?><worksheet xmlns="{_XLSX_NS}">'
        f"<sheetData>{''.join(sheet_rows)}</sheetData></worksheet>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/sharedStrings.xml", shared_xml)
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def _concision_rows(count: int = 3) -> list[list[str]]:
    header = ["id", "cite", "wordy", "concise", "category", "link"]
    rows = [header]
    for i in range(count):
        rows.append(
            [
                str(i + 1),
                f"Writing Center example {i}",
                f"due to the fact that sentence {i} is very wordy indeed",
                f"['because sentence {i} is wordy']",
                "concision",
                f"https://example.com/{i}",
            ]
        )
    return rows


def test_concision_xlsx_reader_and_adapter(tmp_path: Path) -> None:
    xlsx_path = tmp_path / "sac.xlsx"
    rows = _concision_rows()
    _write_concision_xlsx(xlsx_path, rows)
    records = read_concision_xlsx(xlsx_path)
    cases, manifest = adapt_concision(
        records,
        source_revision="DOI synthetic",
        source_sha256=SHA_A,
        expected_rows=len(rows) - 1,
    )
    assert manifest.case_count == 3
    first = cases[0]
    assert first.reference == "because sentence 0 is wordy"
    assert first.attributes["cite"] == "Writing Center example 0"
    assert first.attributes["link"].startswith("https://example.com/")
    assert first.instruction.endswith("preserving meaning.")
    with pytest.raises(ValueError, match="expected 536 rows"):
        adapt_concision(records, source_revision="r", source_sha256=SHA_A)


def test_concision_csv_path_matches_xlsx(tmp_path: Path) -> None:
    rows = _concision_rows()
    csv_path = tmp_path / "sac.csv"
    csv_path.write_text(
        "\n".join(",".join(row) for row in rows) + "\n",
        encoding="utf-8",
    )
    from_csv = normalize_concision_csv(csv_path)
    xlsx_path = tmp_path / "sac.xlsx"
    _write_concision_xlsx(xlsx_path, rows)
    from_xlsx = read_concision_xlsx(xlsx_path)
    assert [record for _, record in from_csv] == [record for _, record in from_xlsx]


def test_concision_rejects_bad_header_and_bad_reference_list(tmp_path: Path) -> None:
    bad_header = tmp_path / "bad.csv"
    bad_header.write_text("cite,wordy,concise,category,link,extra\na,b,c,d,e,f\n")
    with pytest.raises(ValueError, match="unexpected CSV header"):
        normalize_concision_csv(bad_header)
    with pytest.raises(ValueError, match="non-empty list"):
        parse_concise_references("[]")
    with pytest.raises(ValueError, match="invalid concise reference list"):
        parse_concise_references("not a python literal")


# ---------------------------------------------------------------------------
# YapBench adapter
# ---------------------------------------------------------------------------


def _yapbench_records(count: int = 6) -> list[tuple[int, dict[str, Any]]]:
    categories = ["A", "B"]
    return [
        (
            i,
            {
                "id": f"yb-{i:03d}",
                "category": categories[i % 2],
                "prompt": f"synthetic prompt {i}",
                "baseline": f"baseline response {i} with some words",
                "baseline_type": "word",
                "domain": "meta",
                "notes": "synthetic fixture",
            },
        )
        for i in range(count)
    ]


def test_yapbench_adapter_marks_rights_blocked() -> None:
    _cases, manifest = adapt_yapbench(
        _yapbench_records(),
        source_revision="synthetic-rev",
        source_sha256=SHA_A,
        expected_rows=6,
    )
    assert manifest.execution_status == ExecutionStatus.RIGHTS_BLOCKED
    assert manifest.rights_status == RightsStatus.UNVERIFIED_BLOCKED
    assert manifest.case_count == 6
    assert manifest.task_counts == {"A": 3, "B": 3}
    assert any("blocked" in limitation.lower() for limitation in manifest.limitations)
    with pytest.raises(ValueError, match="duplicate case id"):
        adapt_yapbench(
            _yapbench_records()[:1] * 2,
            source_revision="r",
            source_sha256=SHA_A,
            expected_rows=2,
        )


# ---------------------------------------------------------------------------
# Predictions, candidate payloads, leakage separation
# ---------------------------------------------------------------------------


def test_prediction_validation_rejects_duplicates_missing_extra_empty() -> None:
    base = NormalizedExternalCase(
        version=1,
        case_id="case-1",
        benchmark_id=BenchmarkId.YAPBENCH,
        source_revision="r",
        source_sha256=SHA_A,
        split="evaluation",
        task="t",
        source_index=0,
        instruction="i",
        input_text="x",
        reference="ref",
    )
    cases = [base, base.model_copy(update={"case_id": "case-2"})]
    ok = [
        ExternalPrediction(case_id="case-1", output="out"),
        ExternalPrediction(case_id="case-2", output="out"),
    ]
    validated = validate_predictions(cases, ok)
    assert validated.prediction_count == 2
    with pytest.raises(ValueError, match="duplicate prediction"):
        validate_predictions(cases, [*ok, ExternalPrediction(case_id="case-1", output="x")])
    with pytest.raises(ValueError, match="missing predictions"):
        validate_predictions(cases, ok[:1])
    with pytest.raises(ValueError, match="extra predictions"):
        validate_predictions(cases, [*ok, ExternalPrediction(case_id="case-3", output="x")])
    with pytest.raises(ValueError, match="empty prediction"):
        validate_predictions(cases, [ok[0], ExternalPrediction(case_id="case-2", output="   ")])


def test_candidate_payload_never_contains_references_or_criteria() -> None:
    marker_reference = "SECRET-REFERENCE-7f3d"
    marker_criterion = "SECRET-CRITERION-91ab"
    case = NormalizedExternalCase(
        version=1,
        case_id="leak-check",
        benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
        source_revision="r",
        source_sha256=SHA_A,
        split="development",
        task="t",
        source_index=0,
        instruction="public instruction",
        input_text="public input",
        criteria=(
            EvaluationCriterion(
                name=marker_criterion,
                description="private evaluator description",
                anchors=(CriterionAnchor(score_range="1-2", description="private anchor"),),
            ),
        ),
        reference=marker_reference,
    )
    payloads = candidate_payload([case])
    serialized = json.dumps([payload.model_dump(mode="json") for payload in payloads])
    assert marker_reference not in serialized
    assert marker_criterion not in serialized
    assert set(payloads[0].model_dump()) == {"id", "instruction", "input"}


# ---------------------------------------------------------------------------
# YapBench scoring and bootstrap
# ---------------------------------------------------------------------------


def test_visible_characters_freezes_markdown_normalization() -> None:
    assert visible_characters("**Bold** and _it_") == len("Bold and it")
    assert visible_characters("[link](https://example.com)") == len("link")
    assert visible_characters("# Heading\n- item one") == len("Heading item one")
    assert visible_characters("<b>x</b>") == 1
    assert visible_characters("```\ncode\n```") == len("code")


def _scoring_cases_and_predictions() -> tuple[
    list[NormalizedExternalCase], list[ExternalPrediction]
]:
    specs = [
        ("cat-a", "aaaaaaaaaa", "abcdefghijkl"),
        ("cat-a", "abc", "xy"),
        ("cat-b", "12345", "123456789"),
    ]
    cases = [
        NormalizedExternalCase(
            version=1,
            case_id=f"case-{i}",
            benchmark_id=BenchmarkId.YAPBENCH,
            source_revision="r",
            source_sha256=SHA_A,
            split="evaluation",
            task=task,
            source_index=i,
            instruction="respond",
            input_text="prompt",
            reference=baseline,
        )
        for i, (task, baseline, _) in enumerate(specs)
    ]
    predictions = [
        ExternalPrediction(case_id=f"case-{i}", output=response)
        for i, (_, _, response) in enumerate(specs)
    ]
    return cases, predictions


def test_yap_scoring_medians_index_and_clamp() -> None:
    cases, predictions = _scoring_cases_and_predictions()
    result = score_yapbench(cases, predictions, seed=YAP_BOOTSTRAP_SEED, resamples=200)
    by_category = {score.category: score for score in result.category_scores}
    assert by_category["cat-a"].raw_median == 1.0
    assert by_category["cat-b"].raw_median == 4.0
    assert result.yap_index == 2.5
    assert by_category["cat-a"].count == 2
    assert by_category["cat-b"].count == 1
    assert result.metric_version == "goodprose-yap-compat-v1"
    assert result.normalization_version == "goodprose-visible-chars-v1"
    assert result.seed == YAP_BOOTSTRAP_SEED
    assert result.resamples == 200
    assert "quality" in result.disclaimer


def test_yap_bootstrap_is_deterministic_and_bounded() -> None:
    cases, predictions = _scoring_cases_and_predictions()
    first = score_yapbench(cases, predictions, resamples=300)
    second = score_yapbench(cases, predictions, resamples=300)
    third = score_yapbench(cases, predictions, resamples=300, seed=YAP_BOOTSTRAP_SEED + 1)
    assert first == second
    assert first.yap_index_interval_low <= first.yap_index_interval_high
    assert third.yap_index_interval_low <= third.yap_index_interval_high
    assert (first.yap_index_interval_low, first.yap_index_interval_high) != (
        0.0,
        0.0,
    )


def test_score_yapbench_requires_complete_predictions() -> None:
    cases, predictions = _scoring_cases_and_predictions()
    with pytest.raises(ValueError, match="missing predictions"):
        score_yapbench(cases, predictions[:-1])


# ---------------------------------------------------------------------------
# CLI behavior
# ---------------------------------------------------------------------------


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> str:
    payload = ("\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n").encode()
    path.write_bytes(payload)
    return _sha_of_bytes(payload)


def test_cli_validate_registry_reports_all_benchmarks(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["external-evals", "validate-registry"]) == 0
    output = capsys.readouterr().out
    assert "registry valid: 7 benchmarks" in output
    assert "execution_blocked_rights_unverified" in output


def _patch_synthetic_yap_registry(
    monkeypatch: pytest.MonkeyPatch,
    upstream_source: Path,
) -> None:
    original = external_eval_module.find_registry_entry
    real_entry = original(BenchmarkId.YAPBENCH)
    upstream_payload = upstream_source.read_bytes()
    synthetic_source = real_entry.source.model_copy(
        update={"sha256": _sha_of_bytes(upstream_payload), "bytes": len(upstream_payload)}
    )
    synthetic_entry = real_entry.model_copy(
        update={
            "source": synthetic_source,
            "expected_source_rows": 6,
            "expected_eligible_rows": 6,
            "execution_status": ExecutionStatus.ADAPTER_TESTED_NOT_EXECUTED,
            "rights_status": RightsStatus.OPEN_VERIFIED,
        }
    )

    def find(benchmark_id: BenchmarkId):  # type: ignore[no-untyped-def]
        return synthetic_entry if benchmark_id == BenchmarkId.YAPBENCH else original(benchmark_id)

    monkeypatch.setattr(external_eval_module, "find_registry_entry", find)


def test_cli_adapt_candidates_predictions_and_non_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "yapbench.jsonl"
    _write_jsonl(source, [record for _, record in _yapbench_records()])
    upstream_source = tmp_path / "yapbench.parquet"
    upstream_source.write_bytes(b"synthetic parquet placeholder")
    _patch_synthetic_yap_registry(monkeypatch, upstream_source)
    output_dir = tmp_path / "adapted"
    argv = [
        "external-evals",
        "adapt",
        "--benchmark-id",
        "yapbench",
        "--source",
        str(source),
        "--upstream-source",
        str(upstream_source),
        "--output-dir",
        str(output_dir),
    ]
    assert main(argv) == 0
    cases_path = output_dir / "yapbench.cases.jsonl"
    manifest_path = output_dir / "yapbench.manifest.json"
    candidates_path = tmp_path / "yapbench.candidates.jsonl"
    assert cases_path.is_file() and manifest_path.is_file()
    manifest = AdaptedManifest.model_validate_json(manifest_path.read_text())
    assert manifest.case_count == 6
    assert manifest.adapter_input_sha256 == _sha_of_bytes(source.read_bytes())

    emit = [
        "external-evals",
        "emit-candidates",
        "--cases",
        str(cases_path),
        "--output",
        str(candidates_path),
        "--suite",
        "full",
    ]
    assert main(emit) == 0
    candidates = [json.loads(line) for line in candidates_path.read_text().splitlines()]
    assert all(set(entry) == {"id", "instruction", "input"} for entry in candidates)

    # Second adaptation and candidate emission both refuse to overwrite.
    assert main(argv) == 1
    assert main(emit) == 1

    predictions_path = tmp_path / "predictions.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text().splitlines()]
    _write_jsonl(
        predictions_path,
        [
            {"case_id": case["case_id"], "output": "a longer synthetic response text"}
            for case in cases
        ],
    )
    assert (
        main(
            [
                "external-evals",
                "validate-predictions",
                "--cases",
                str(cases_path),
                "--predictions",
                str(predictions_path),
                "--suite",
                "full",
            ]
        )
        == 0
    )

    result_path = tmp_path / "yap.result.json"
    score_argv = [
        "external-evals",
        "score-yapbench",
        "--cases",
        str(cases_path),
        "--predictions",
        str(predictions_path),
        "--result",
        str(result_path),
    ]
    assert main(score_argv) == 0
    assert result_path.is_file()
    assert main(score_argv) == 1


def test_cli_emit_candidates_refuses_overwrite(tmp_path: Path) -> None:
    cases, _predictions = _scoring_cases_and_predictions()
    cases_path = tmp_path / "cases.jsonl"
    _write_jsonl(cases_path, [case.model_dump(mode="json") for case in cases])
    candidates_path = tmp_path / "candidates.jsonl"
    emit = [
        "external-evals",
        "emit-candidates",
        "--cases",
        str(cases_path),
        "--output",
        str(candidates_path),
        "--suite",
        "full",
    ]
    assert main(emit) == 0
    assert main(emit) == 1


def test_cli_adapt_fails_on_wrong_hash(tmp_path: Path) -> None:
    source = tmp_path / "writingbench.jsonl"
    _write_jsonl(source, [record for _, record in _wb_records()])
    assert (
        main(
            [
                "external-evals",
                "adapt",
                "--benchmark-id",
                "writingbench-business",
                "--source",
                str(source),
                "--output-dir",
                str(tmp_path / "out"),
            ]
        )
        == 1
    )


def test_cli_yap_scoring_is_blocked_while_rights_are_unverified(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cases, predictions = _scoring_cases_and_predictions()
    cases_path = tmp_path / "cases.jsonl"
    predictions_path = tmp_path / "predictions.jsonl"
    result_path = tmp_path / "result.json"
    _write_jsonl(cases_path, [case.model_dump(mode="json") for case in cases])
    _write_jsonl(
        predictions_path,
        [prediction.model_dump(mode="json") for prediction in predictions],
    )
    assert (
        main(
            [
                "external-evals",
                "score-yapbench",
                "--cases",
                str(cases_path),
                "--predictions",
                str(predictions_path),
                "--result",
                str(result_path),
            ]
        )
        == 1
    )
    assert "blocked until dataset rights are clarified" in capsys.readouterr().err
    assert not result_path.exists()
