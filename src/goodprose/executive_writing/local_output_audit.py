"""Hash-bound full-output audit for local visible-B1 candidates."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

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


class LocalOutputAuditConfig(StrictModel):
    version: Literal[1]
    audit_id: NonEmpty
    classification: Literal["post_run_full_output_source_grounding_audit"]
    candidate_id: NonEmpty
    source_run_manifest_sha256: Sha256
    outputs_sha256: Sha256
    benchmark_cases_sha256: Sha256
    source_analysis_sha256: Sha256
    source_case_results_sha256: Sha256
    artifact_prefixes: tuple[NonEmpty, ...] = ()
    artifact_substrings: tuple[NonEmpty, ...] = ()
    manual_findings: tuple[ManualFinding, ...]

    @model_validator(mode="after")
    def validate_patterns_and_findings(self) -> Self:
        case_ids = [finding.case_id for finding in self.manual_findings]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("manual findings must contain unique case IDs")
        if not self.artifact_prefixes and not self.artifact_substrings:
            raise ValueError("at least one deterministic artifact pattern is required")
        return self


def load_local_output_audit_config(path: Path) -> LocalOutputAuditConfig:
    return LocalOutputAuditConfig.model_validate_json(path.read_text(encoding="utf-8"))


def _introduced_placeholders(source: str, output: str) -> list[str]:
    source_placeholders = set(_PLACEHOLDER_PATTERN.findall(source))
    return sorted(set(_PLACEHOLDER_PATTERN.findall(output)) - source_placeholders)


def audit_local_b1_outputs(
    *,
    config_path: Path,
    run_dir: Path,
    cases_path: Path,
    source_analysis_path: Path,
    source_case_results_path: Path,
    output_path: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Publish compact findings without copying local output bodies."""

    config = load_local_output_audit_config(config_path)
    manifest_path = run_dir / "run-manifest.json"
    outputs_path = run_dir / "outputs.jsonl"
    pinned_files = (
        (manifest_path, config.source_run_manifest_sha256, "run manifest"),
        (outputs_path, config.outputs_sha256, "outputs"),
        (cases_path, config.benchmark_cases_sha256, "B1 cases"),
        (source_analysis_path, config.source_analysis_sha256, "analysis"),
        (source_case_results_path, config.source_case_results_sha256, "case results"),
    )
    for path, expected_sha256, label in pinned_files:
        if sha256_file(path) != expected_sha256:
            raise ValueError(f"local {label} hash does not match output-audit config")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    analysis = json.loads(source_analysis_path.read_text(encoding="utf-8"))
    if manifest.get("candidate_id") != config.candidate_id:
        raise ValueError("local run manifest candidate does not match output-audit config")
    if manifest.get("artifact_hashes", {}).get("outputs_jsonl") != config.outputs_sha256:
        raise ValueError("local run manifest does not bind the configured outputs")
    if analysis.get("status") not in {"completed_keep", "completed_reject"}:
        raise ValueError("local source analysis is not complete")
    if analysis.get("candidate", {}).get("candidate_id") != config.candidate_id:
        raise ValueError("local analysis candidate does not match output-audit config")
    if (
        analysis.get("candidate", {}).get("source_artifact_hashes", {}).get("outputs_jsonl")
        != config.outputs_sha256
    ):
        raise ValueError("local analysis does not bind the configured outputs")
    if analysis.get("case_results_sha256") != config.source_case_results_sha256:
        raise ValueError("local analysis does not bind the configured case results")

    cases = load_cases(cases_path)
    generations = load_jsonl(outputs_path, Generation)
    sources = {case.id: case.input.source_material for case in cases}
    by_case = {generation.case_id: generation for generation in generations}
    expected_ids = set(sources)
    if set(by_case) != expected_ids or len(by_case) != len(generations):
        raise ValueError("local outputs must cover every B1 case exactly once")
    if any(generation.candidate_id != config.candidate_id for generation in generations):
        raise ValueError("local output candidate does not match output-audit config")
    manual = {finding.case_id: finding for finding in config.manual_findings}
    if not set(manual).issubset(expected_ids):
        raise ValueError("manual findings contain a case outside the configured B1 set")

    case_records: list[dict[str, Any]] = []
    artifact_case_ids: list[str] = []
    placeholder_case_ids: list[str] = []
    manual_case_ids = sorted(manual)
    for case_id in sorted(expected_ids):
        output = by_case[case_id].output
        source = sources[case_id]
        folded_output = output.casefold().lstrip()
        artifact_commentary = any(
            folded_output.startswith(prefix.casefold()) for prefix in config.artifact_prefixes
        ) or any(substring.casefold() in folded_output for substring in config.artifact_substrings)
        introduced_placeholders = _introduced_placeholders(source, output)
        finding = manual.get(case_id)
        categories: list[str] = []
        if artifact_commentary:
            categories.append("model_prompt_instruction_or_process_commentary")
            artifact_case_ids.append(case_id)
        if introduced_placeholders:
            categories.append("introduced_non_source_placeholder")
            placeholder_case_ids.append(case_id)
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

    all_flagged = sorted(set(artifact_case_ids) | set(placeholder_case_ids) | set(manual_case_ids))
    case_count = len(cases)
    artifact_only_count = case_count - len(artifact_case_ids)
    no_flag_count = case_count - len(all_flagged)
    score_gate_passed = bool(
        analysis.get("preregistered_gate_result", {}).get("all_guardrails_pass", False)
    )
    if all_flagged:
        disposition = "reject_for_artifact_contamination_or_source_grounding_risk"
    elif score_gate_passed:
        disposition = "pass_full_output_audit_for_common_frontier"
    else:
        disposition = "retain_as_diagnostic_only_score_gate_failed"
    result: dict[str, Any] = {
        "version": 1,
        "audit_id": config.audit_id,
        "classification": config.classification,
        "generated_at": generated_at,
        "candidate_id": config.candidate_id,
        "source_run_manifest_sha256": config.source_run_manifest_sha256,
        "outputs_sha256": config.outputs_sha256,
        "benchmark_cases_sha256": config.benchmark_cases_sha256,
        "source_analysis_sha256": config.source_analysis_sha256,
        "source_case_results_sha256": config.source_case_results_sha256,
        "audit_config_sha256": sha256_file(config_path),
        "summary": {
            "case_count": case_count,
            "model_prompt_instruction_or_process_commentary_case_count": len(artifact_case_ids),
            "introduced_non_source_placeholder_case_count": len(placeholder_case_ids),
            "material_source_expansion_risk_case_count": len(manual_case_ids),
            "artifact_only_case_count": artifact_only_count,
            "artifact_only_pass_rate": round(artifact_only_count / case_count, 4),
            "no_audit_flag_case_count": no_flag_count,
            "no_audit_flag_pass_rate": round(no_flag_count / case_count, 4),
            "flagged_case_ids": all_flagged,
        },
        "case_findings": case_records,
        "decision": {
            "candidate_disposition": disposition,
            "score_evidence_disposition": "retain_as_visible_b1_development_diagnostic_only",
            "quality_retry_authorized": False,
        },
        "limitations": [
            "Manual source-expansion findings are reviewer judgments made after generation.",
            "Literal artifact and placeholder checks do not detect every defect.",
            "B1 is visible, small, and project-authored; no sealed or production claim follows.",
        ],
    }
    atomic_write_json(output_path, result)
    return result
