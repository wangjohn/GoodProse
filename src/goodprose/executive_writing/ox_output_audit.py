"""Hash-bound post-run artifact audit for the Ox Alpha B1 ceiling candidate."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.executive_writing.baseline import Generation
from goodprose.executive_writing.benchmark import load_cases
from goodprose.jsonl import atomic_write_json, load_jsonl, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

_PLACEHOLDER_PATTERN = re.compile(r"\[[A-Za-z][A-Za-z _-]*\]")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ManualFinding(StrictModel):
    case_id: NonEmpty
    category: Literal["material_source_expansion_risk"]
    rationale: NonEmpty


class OxOutputAuditConfig(StrictModel):
    version: Literal[1]
    audit_id: Literal["ox-alpha-b1-ceiling-v1-output-audit"]
    classification: Literal["post_run_exploratory_artifact_and_source_grounding_audit"]
    source_run_id: NonEmpty
    source_run_manifest_sha256: Sha256
    outputs_sha256: Sha256
    benchmark_cases_sha256: Sha256
    source_analysis_sha256: Sha256
    source_case_results_sha256: Sha256
    run_date_marker: NonEmpty
    meta_preamble_prefixes: tuple[NonEmpty, ...] = Field(min_length=1)
    manual_findings: tuple[ManualFinding, ...]

    @model_validator(mode="after")
    def validate_unique_manual_findings(self) -> Self:
        case_ids = [finding.case_id for finding in self.manual_findings]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("manual findings must contain unique case IDs")
        return self


def load_ox_output_audit_config(path: Path) -> OxOutputAuditConfig:
    return OxOutputAuditConfig.model_validate_json(path.read_text(encoding="utf-8"))


def _introduced_placeholders(source: str, output: str) -> list[str]:
    source_placeholders = set(_PLACEHOLDER_PATTERN.findall(source))
    return sorted(set(_PLACEHOLDER_PATTERN.findall(output)) - source_placeholders)


def audit_ox_b1_outputs(
    *,
    config_path: Path,
    run_dir: Path,
    cases_path: Path,
    source_analysis_path: Path,
    source_case_results_path: Path,
    output_path: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Publish an inspectable diagnostic without copying provider output bodies."""

    config = load_ox_output_audit_config(config_path)
    manifest_path = run_dir / "run-manifest.json"
    outputs_path = run_dir / "outputs.jsonl"
    if sha256_file(manifest_path) != config.source_run_manifest_sha256:
        raise ValueError("Ox source run manifest hash does not match output-audit config")
    if sha256_file(outputs_path) != config.outputs_sha256:
        raise ValueError("Ox output hash does not match output-audit config")
    if sha256_file(cases_path) != config.benchmark_cases_sha256:
        raise ValueError("B1 cases hash does not match output-audit config")
    if sha256_file(source_analysis_path) != config.source_analysis_sha256:
        raise ValueError("Ox source analysis hash does not match output-audit config")
    if sha256_file(source_case_results_path) != config.source_case_results_sha256:
        raise ValueError("Ox case-result hash does not match output-audit config")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    analysis = json.loads(source_analysis_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed" or manifest.get("run_id") != config.source_run_id:
        raise ValueError("Ox source run is not the completed configured run")
    if manifest.get("outputs_sha256") != config.outputs_sha256:
        raise ValueError("Ox source manifest does not bind the configured outputs")
    if analysis.get("source_run_id") != config.source_run_id:
        raise ValueError("Ox analysis does not refer to the configured source run")
    if analysis.get("outputs_sha256") != config.outputs_sha256:
        raise ValueError("Ox analysis does not bind the configured outputs")
    if analysis.get("case_results_sha256") != config.source_case_results_sha256:
        raise ValueError("Ox analysis does not bind the configured case results")

    cases = load_cases(cases_path)
    generations = load_jsonl(outputs_path, Generation)
    sources = {case.id: case.input.source_material for case in cases}
    by_case = {generation.case_id: generation for generation in generations}
    expected_ids = set(sources)
    if set(by_case) != expected_ids or len(by_case) != len(generations):
        raise ValueError("Ox outputs must cover every B1 case exactly once")
    manual = {finding.case_id: finding for finding in config.manual_findings}
    if not set(manual).issubset(expected_ids):
        raise ValueError("manual findings contain a case outside the configured B1 set")

    case_records: list[dict[str, Any]] = []
    meta_case_ids: list[str] = []
    placeholder_case_ids: list[str] = []
    run_date_case_ids: list[str] = []
    manual_case_ids = sorted(manual)
    for case_id in sorted(expected_ids):
        output = by_case[case_id].output
        source = sources[case_id]
        folded_output = output.casefold().lstrip()
        meta_preamble = any(
            folded_output.startswith(prefix.casefold()) for prefix in config.meta_preamble_prefixes
        )
        introduced_placeholders = _introduced_placeholders(source, output)
        introduced_run_date = (
            config.run_date_marker.casefold() in output.casefold()
            and config.run_date_marker.casefold() not in source.casefold()
        )
        finding = manual.get(case_id)
        categories: list[str] = []
        if meta_preamble:
            categories.append("agent_or_harness_meta_preamble")
            meta_case_ids.append(case_id)
        if introduced_placeholders:
            categories.append("introduced_non_source_placeholder")
            placeholder_case_ids.append(case_id)
        if introduced_run_date:
            categories.append("introduced_run_date_metadata")
            run_date_case_ids.append(case_id)
        if finding:
            categories.append(finding.category)
        if categories:
            case_records.append(
                {
                    "case_id": case_id,
                    "output_sha256": by_case[case_id].output_sha256,
                    "categories": categories,
                    "introduced_placeholders": introduced_placeholders,
                    "manual_rationale": finding.rationale if finding else None,
                }
            )

    all_flagged = sorted(
        set(meta_case_ids)
        | set(placeholder_case_ids)
        | set(run_date_case_ids)
        | set(manual_case_ids)
    )
    case_count = len(cases)
    artifact_only_count = case_count - len(meta_case_ids)
    no_flag_count = case_count - len(all_flagged)
    result: dict[str, Any] = {
        "version": 1,
        "audit_id": config.audit_id,
        "classification": config.classification,
        "generated_at": generated_at,
        "source_run_id": config.source_run_id,
        "source_run_manifest_sha256": config.source_run_manifest_sha256,
        "outputs_sha256": config.outputs_sha256,
        "benchmark_cases_sha256": config.benchmark_cases_sha256,
        "source_analysis_sha256": config.source_analysis_sha256,
        "source_case_results_sha256": config.source_case_results_sha256,
        "audit_config_sha256": sha256_file(config_path),
        "summary": {
            "case_count": case_count,
            "agent_or_harness_meta_preamble_case_count": len(meta_case_ids),
            "introduced_non_source_placeholder_case_count": len(placeholder_case_ids),
            "introduced_run_date_metadata_case_count": len(run_date_case_ids),
            "material_source_expansion_risk_case_count": len(manual_case_ids),
            "artifact_only_case_count": artifact_only_count,
            "artifact_only_pass_rate": round(artifact_only_count / case_count, 4),
            "no_audit_flag_case_count": no_flag_count,
            "no_audit_flag_pass_rate": round(no_flag_count / case_count, 4),
            "flagged_case_ids": all_flagged,
        },
        "case_findings": case_records,
        "decision": {
            "raw_candidate_disposition": (
                "reject_for_artifact_contamination_and_source_grounding_risk"
            ),
            "score_evidence_disposition": "retain_as_visible_b1_quality_ceiling_diagnostic_only",
            "next_experiment": (
                "preregister a new Ox harness candidate that avoids the one-step finalization "
                "preamble; do not post-process this evaluated output in place"
            ),
        },
        "limitations": [
            (
                "This diagnostic was specified after generation and cannot replace the "
                "preregistered score."
            ),
            "Literal preamble, placeholder, and date checks do not detect every artifact defect.",
            (
                "Material source-expansion findings are reviewer judgments recorded after "
                "inspecting B1."
            ),
            "B1 is visible, small, and project-authored; no sealed or production claim follows.",
        ],
    }
    atomic_write_json(output_path, result)
    return result
