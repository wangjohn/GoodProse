"""Validation and immutable snapshot creation for GoodProse training data."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from goodprose.jsonl import (
    atomic_write,
    load_jsonl,
    serialize_jsonl,
    sha256_bytes,
    sha256_file,
)
from goodprose.models import EvalCase, Split, TrainingExample
from goodprose.privacy import PrivacyReport, load_privacy_report

SNAPSHOT_VERSION = 1


class DatasetValidationError(ValueError):
    """The dataset cannot be compiled without violating an invariant."""


class TokenCounter(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def revision(self) -> str | None: ...

    def count(self, text: str) -> int: ...


@dataclass(frozen=True)
class ApproximateTokenCounter:
    name: str = "approximate_utf8_bytes_div4"
    revision: str | None = None

    def count(self, text: str) -> int:
        if not text:
            return 0
        return max(1, (len(text.encode("utf-8")) + 3) // 4)


class HuggingFaceTokenCounter:
    def __init__(self, model_name: str, revision: str | None = None) -> None:
        try:
            from transformers import AutoTokenizer  # pyright: ignore[reportMissingImports]
        except ImportError as error:
            raise DatasetValidationError(
                "Transformers is not installed; run `uv sync --extra tokenizers`"
            ) from error
        self.name = model_name
        self.revision = revision
        self._tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)

    def count(self, text: str) -> int:
        token_ids: list[int] = self._tokenizer.encode(text, add_special_tokens=False)
        return len(token_ids)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def _normalized_example(example: TrainingExample) -> str:
    parts = [
        example.input.source_material,
        example.input.channel.value,
        example.input.audience,
        example.input.objective,
        example.input.voice_profile_id,
        *example.input.constraints,
    ]
    for context in example.input.context:
        parts.extend((context.kind.value, context.label or "", context.content))
    parts.extend((example.output.title or "", example.output.body_markdown))
    return "\n".join(_normalize_text(part) for part in parts)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DatasetValidationError(f"{path} must contain a JSON object")
    return value


def _reference_errors(records: list[TrainingExample], repo_root: Path) -> list[str]:
    sources = _load_json(repo_root / "data" / "sources.json")
    style_references = _load_json(repo_root / "data" / "style-references" / "index.json")
    voice_profiles = _load_json(repo_root / "data" / "voice-profiles" / "index.json")

    source_splits = {
        document["id"]: document["split"]
        for source in sources.get("sources", [])
        for document in source.get("documents", [])
    }
    style_reference_ids = {
        entry["id"] for entry in style_references.get("approved_examples", []) if "id" in entry
    }
    voice_profile_ids = {
        entry["id"] for entry in voice_profiles.get("profiles", []) if "id" in entry
    }

    errors: list[str] = []
    for record in records:
        for document_id in record.provenance.source_document_ids:
            split = source_splits.get(document_id)
            if split is None:
                errors.append(f"{record.id}: unknown source document {document_id!r}")
            elif split != "train_reference":
                errors.append(f"{record.id}: source document {document_id!r} is in {split}")
        for example_id in record.provenance.style_reference_ids:
            if example_id not in style_reference_ids:
                errors.append(f"{record.id}: unknown approved style-reference ID {example_id!r}")
        if record.input.voice_profile_id not in voice_profile_ids:
            errors.append(f"{record.id}: unknown voice profile {record.input.voice_profile_id!r}")
    return errors


def discover_eval_cases(paths: list[Path]) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for root in paths:
        if not root.exists():
            continue
        candidates = (
            [root]
            if root.is_file()
            else sorted(root.rglob("*.json")) + sorted(root.rglob("*.jsonl"))
        )
        for path in candidates:
            if path.name == "README.md":
                continue
            if path.suffix == ".jsonl":
                cases.extend(load_jsonl(path, EvalCase))
                continue
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, list):
                cases.extend(EvalCase.model_validate(item) for item in value)
            elif isinstance(value, dict):
                cases.append(EvalCase.model_validate(value))
            else:
                raise DatasetValidationError(f"{path} must contain an eval case or list of cases")
    return cases


def validate_training_records(
    records: list[TrainingExample], *, repo_root: Path, eval_cases: list[EvalCase] | None = None
) -> list[str]:
    errors: list[str] = []
    if not records:
        errors.append("training dataset is empty")
    ids: set[str] = set()
    normalized: dict[str, str] = {}
    lineage_splits: dict[str, set[Split]] = defaultdict(set)

    for record in records:
        if record.id in ids:
            errors.append(f"duplicate training example ID: {record.id}")
        ids.add(record.id)
        if not record.review.is_fully_approved():
            errors.append(f"{record.id}: all review gates must be passed")
        lineage_splits[record.provenance.lineage_group].add(record.split)
        content_hash = sha256_bytes(_normalized_example(record).encode("utf-8"))
        prior = normalized.get(content_hash)
        if prior is not None:
            errors.append(f"normalized duplicate examples: {prior} and {record.id}")
        else:
            normalized[content_hash] = record.id

    for lineage, splits in lineage_splits.items():
        if len(splits) > 1:
            errors.append(f"lineage {lineage!r} crosses training and validation splits")

    if eval_cases:
        eval_lineages = {case.provenance.lineage_group: case.id for case in eval_cases}
        for lineage in lineage_splits:
            if lineage in eval_lineages:
                eval_case_id = eval_lineages[lineage]
                errors.append(
                    f"lineage {lineage!r} appears in training and eval case {eval_case_id!r}"
                )

    errors.extend(_reference_errors(records, repo_root))
    return errors


def _record_token_counts(record: TrainingExample, counter: TokenCounter) -> dict[str, Any]:
    context_tokens = [counter.count(item.content) for item in record.input.context]
    constraint_tokens = [counter.count(item) for item in record.input.constraints]
    source_tokens = counter.count(record.input.source_material)
    audience_tokens = counter.count(record.input.audience)
    objective_tokens = counter.count(record.input.objective)
    title_tokens = counter.count(record.output.title or "")
    body_tokens = counter.count(record.output.body_markdown)
    output_tokens = title_tokens + body_tokens
    total = (
        source_tokens
        + audience_tokens
        + objective_tokens
        + sum(constraint_tokens)
        + sum(context_tokens)
        + output_tokens
    )
    return {
        "id": record.id,
        "split": record.split.value,
        "source_material_tokens": source_tokens,
        "audience_tokens": audience_tokens,
        "objective_tokens": objective_tokens,
        "constraint_tokens": constraint_tokens,
        "context_tokens": context_tokens,
        "output_title_tokens": title_tokens,
        "output_body_tokens": body_tokens,
        "output_tokens": output_tokens,
        "total_content_tokens": total,
    }


def _token_report(
    records: list[TrainingExample], counter: TokenCounter, max_tokens: int
) -> dict[str, Any]:
    per_record = [_record_token_counts(record, counter) for record in records]
    totals = [item["total_content_tokens"] for item in per_record]
    outputs = [item["output_tokens"] for item in per_record]
    return {
        "version": 1,
        "tokenizer": {"name": counter.name, "revision": counter.revision},
        "counting_scope": "sum of content fields before model-specific chat-template overhead",
        "max_tokens": max_tokens,
        "record_count": len(per_record),
        "total_content_tokens": sum(totals),
        "maximum_record_tokens": max(totals, default=0),
        "maximum_output_tokens": max(outputs, default=0),
        "over_limit_ids": [
            item["id"] for item in per_record if item["total_content_tokens"] > max_tokens
        ],
        "records": per_record,
    }


def _validate_privacy_evidence(input_path: Path, report: PrivacyReport) -> None:
    if report.input_sha256 != sha256_file(input_path):
        raise DatasetValidationError("privacy report does not match the training JSONL bytes")
    if not report.is_clean:
        raise DatasetValidationError(
            f"privacy report contains {len(report.findings)} finding(s); redact and rescan first"
        )


def create_snapshot(
    input_path: Path,
    output_root: Path,
    *,
    repo_root: Path,
    privacy_report_path: Path,
    eval_paths: list[Path],
    tokenizer_name: str | None = None,
    tokenizer_revision: str | None = None,
    max_tokens: int = 32768,
    allow_over_limit: bool = False,
) -> Path:
    if max_tokens < 1:
        raise DatasetValidationError("max_tokens must be at least 1")
    records = load_jsonl(input_path, TrainingExample)
    records.sort(key=lambda item: item.id)
    eval_cases = discover_eval_cases(eval_paths)
    errors = validate_training_records(records, repo_root=repo_root, eval_cases=eval_cases)
    if errors:
        raise DatasetValidationError("\n".join(errors))

    privacy_report = load_privacy_report(privacy_report_path)
    _validate_privacy_evidence(input_path, privacy_report)

    counter: TokenCounter
    if tokenizer_name:
        counter = HuggingFaceTokenCounter(tokenizer_name, tokenizer_revision)
    else:
        counter = ApproximateTokenCounter()
    token_report = _token_report(records, counter, max_tokens)
    if token_report["over_limit_ids"] and not allow_over_limit:
        ids = ", ".join(token_report["over_limit_ids"])
        raise DatasetValidationError(f"records exceed the {max_tokens}-token limit: {ids}")

    payload = serialize_jsonl(records)
    dataset_hash = sha256_bytes(payload)
    snapshot_dir = output_root / dataset_hash[:12]
    split_counts = Counter(record.split.value for record in records)
    method_counts = Counter(record.provenance.creation_method.value for record in records)
    manifest = {
        "version": SNAPSHOT_VERSION,
        "dataset_sha256": dataset_hash,
        "source_jsonl_sha256": sha256_file(input_path),
        "privacy_report_sha256": sha256_file(privacy_report_path),
        "record_count": len(records),
        "split_counts": dict(sorted(split_counts.items())),
        "creation_method_counts": dict(sorted(method_counts.items())),
        "lineage_group_count": len({record.provenance.lineage_group for record in records}),
        "eval_case_count_checked": len(eval_cases),
        "tokenizer": token_report["tokenizer"],
        "max_tokens": max_tokens,
        "contains_over_limit_records": bool(token_report["over_limit_ids"]),
    }

    expected_files = {
        snapshot_dir / "training.jsonl": payload,
        snapshot_dir / "manifest.json": (
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        ).encode(),
        snapshot_dir / "token-report.json": (
            json.dumps(token_report, indent=2, sort_keys=True) + "\n"
        ).encode(),
    }
    for path, expected in expected_files.items():
        if path.exists() and path.read_bytes() != expected:
            raise DatasetValidationError(f"immutable snapshot file already differs: {path}")
    for path, expected in expected_files.items():
        if not path.exists():
            atomic_write(path, expected)
    return snapshot_dir


def validate_jsonl(input_path: Path, *, repo_root: Path, eval_paths: list[Path]) -> list[str]:
    records = load_jsonl(input_path, TrainingExample)
    eval_cases = discover_eval_cases(eval_paths)
    return validate_training_records(records, repo_root=repo_root, eval_cases=eval_cases)
