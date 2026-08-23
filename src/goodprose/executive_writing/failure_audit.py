"""Post-run exact-label leakage and severe-repetition audit for MLX B1 outputs."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.executive_writing.baseline import Generation
from goodprose.executive_writing.benchmark import load_cases
from goodprose.jsonl import atomic_write_json, load_jsonl, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AuditComparison(StrictModel):
    strategy: Literal["profile", "ledger_draft"]
    baseline_id: NonEmpty
    candidate_id: NonEmpty


class FailureAuditConfig(StrictModel):
    version: Literal[1]
    audit_id: NonEmpty
    classification: Literal["post_run_exploratory_diagnostic"]
    source_experiment_id: NonEmpty
    source_run_id: NonEmpty
    benchmark_cases_sha256: Sha256
    source_records_sha256: Sha256
    candidate_output_sha256: dict[NonEmpty, Sha256]
    comparisons: tuple[AuditComparison, ...]
    scenario_labels: tuple[NonEmpty, ...]
    exact_line_repetition_threshold: int = Field(ge=2)
    ngram_words: int = Field(ge=2)
    ngram_repetition_threshold: int = Field(ge=2)

    @model_validator(mode="after")
    def validate_candidate_and_label_sets(self) -> Self:
        compared = {
            candidate_id
            for comparison in self.comparisons
            for candidate_id in (comparison.baseline_id, comparison.candidate_id)
        }
        if compared != set(self.candidate_output_sha256):
            raise ValueError("comparison candidates must exactly match candidate_output_sha256")
        folded_labels = [label.casefold() for label in self.scenario_labels]
        if len(folded_labels) != len(set(folded_labels)):
            raise ValueError("scenario_labels must be unique ignoring case")
        return self


def load_failure_audit_config(path: Path) -> FailureAuditConfig:
    return FailureAuditConfig.model_validate_json(path.read_text(encoding="utf-8"))


def _contains_label(text: str, label: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(label)}(?![a-z0-9])"
    return re.search(pattern, text, re.IGNORECASE) is not None


def _max_ngram_repetition(text: str, size: int) -> int:
    words = re.findall(r"[a-z0-9]+", text.casefold())
    counts = Counter(tuple(words[index : index + size]) for index in range(len(words) - size + 1))
    return max(counts.values(), default=0)


def _candidate_audit(
    *,
    outputs_path: Path,
    sources: dict[str, str],
    config: FailureAuditConfig,
) -> dict[str, Any]:
    generations = load_jsonl(outputs_path, Generation)
    case_ids = [generation.case_id for generation in generations]
    if len(case_ids) != len(sources) or set(case_ids) != set(sources):
        raise ValueError("candidate outputs must contain exactly one generation per B1 case")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("candidate outputs contain duplicate case IDs")

    affected_cases: list[dict[str, Any]] = []
    for generation in sorted(generations, key=lambda item: item.case_id):
        source = sources[generation.case_id]
        leaked_labels = sorted(
            label
            for label in config.scenario_labels
            if _contains_label(generation.output, label) and not _contains_label(source, label)
        )
        lines = [line.strip().casefold() for line in generation.output.splitlines() if line.strip()]
        max_line_repetition = max(Counter(lines).values(), default=0)
        max_ngram_repetition = _max_ngram_repetition(generation.output, config.ngram_words)
        severe_repetition = (
            max_line_repetition >= config.exact_line_repetition_threshold
            or max_ngram_repetition >= config.ngram_repetition_threshold
        )
        if leaked_labels or severe_repetition:
            affected_cases.append(
                {
                    "case_id": generation.case_id,
                    "introduced_training_scenario_labels": leaked_labels,
                    "max_exact_line_repetition": max_line_repetition,
                    "max_ngram_repetition": max_ngram_repetition,
                    "severe_repetition": severe_repetition,
                }
            )

    return {
        "case_count": len(generations),
        "introduced_training_label_case_count": sum(
            bool(item["introduced_training_scenario_labels"]) for item in affected_cases
        ),
        "severe_repetition_case_count": sum(
            bool(item["severe_repetition"]) for item in affected_cases
        ),
        "affected_cases": affected_cases,
    }


def audit_mlx_b1_failures(
    *,
    config_path: Path,
    run_dir: Path,
    cases_path: Path,
    output_path: Path,
    generated_at: str,
) -> dict[str, Any]:
    """Validate frozen inputs and publish a compact post-run failure diagnostic."""

    config = load_failure_audit_config(config_path)
    manifest_path = run_dir / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed":
        raise ValueError("source MLX evaluation run must be completed")
    if manifest.get("experiment_id") != config.source_experiment_id:
        raise ValueError("source experiment ID does not match failure-audit config")
    if manifest.get("run_id") != config.source_run_id:
        raise ValueError("source run ID does not match failure-audit config")
    if sha256_file(cases_path) != config.benchmark_cases_sha256:
        raise ValueError("B1 cases hash does not match failure-audit config")

    cases = load_cases(cases_path)
    sources = {case.id: case.input.source_material for case in cases}
    candidates: dict[str, dict[str, Any]] = {}
    for candidate_id, expected_hash in sorted(config.candidate_output_sha256.items()):
        manifest_hash = (
            manifest.get("candidate_artifacts", {}).get(candidate_id, {}).get("outputs_sha256")
        )
        if manifest_hash != expected_hash:
            raise ValueError(f"manifest output hash mismatch for {candidate_id}")
        outputs_path = run_dir / candidate_id / "outputs.jsonl"
        if sha256_file(outputs_path) != expected_hash:
            raise ValueError(f"output bytes do not match frozen hash for {candidate_id}")
        candidates[candidate_id] = _candidate_audit(
            outputs_path=outputs_path,
            sources=sources,
            config=config,
        )

    comparisons = []
    for comparison in config.comparisons:
        baseline = candidates[comparison.baseline_id]
        candidate = candidates[comparison.candidate_id]
        comparisons.append(
            {
                **comparison.model_dump(mode="json"),
                "introduced_training_label_case_difference": (
                    candidate["introduced_training_label_case_count"]
                    - baseline["introduced_training_label_case_count"]
                ),
                "severe_repetition_case_difference": (
                    candidate["severe_repetition_case_count"]
                    - baseline["severe_repetition_case_count"]
                ),
            }
        )

    result: dict[str, Any] = {
        "version": 1,
        "audit_id": config.audit_id,
        "classification": config.classification,
        "generated_at": generated_at,
        "source_experiment_id": config.source_experiment_id,
        "source_run_id": config.source_run_id,
        "source_run_manifest_sha256": sha256_file(manifest_path),
        "audit_config_sha256": sha256_file(config_path),
        "benchmark_cases_sha256": config.benchmark_cases_sha256,
        "source_records_sha256": config.source_records_sha256,
        "method": {
            "introduced_training_label": (
                f"case-insensitive whole-token match to one of the "
                f"{len(config.scenario_labels)} frozen fictional "
                "scenario labels in output and no match in that case's source material"
            ),
            "severe_repetition": (
                f"an exact nonempty line repeated at least "
                f"{config.exact_line_repetition_threshold} times or an exact contiguous "
                f"{config.ngram_words}-word n-gram repeated at least "
                f"{config.ngram_repetition_threshold} times"
            ),
        },
        "candidates": candidates,
        "comparisons": comparisons,
        "decision": {
            "adapter_disposition": "reject_for_quality_and_memorization_risk",
            "training_evidence_disposition": "retain_as_genuine_unified_training_evidence_only",
            "reason": (
                "The tuned candidates introduce training-scenario labels in unseen B1 cases "
                "while both exact-base controls introduce none, and both tuned strategies "
                "retain severe repetition failures."
            ),
        },
        "limitations": [
            (
                "This diagnostic was specified after generation and cannot replace the "
                "preregistered score."
            ),
            (
                "Exact label matching can miss paraphrased memorization and can flag a "
                "coincidental whole-token use."
            ),
            (
                "The repetition rule is a deterministic collapse heuristic, not a "
                "semantic quality measure."
            ),
            "B1 is visible, small, and project-authored, so the evidence remains exploratory.",
        ],
    }
    atomic_write_json(output_path, result)
    return result
