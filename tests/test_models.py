from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from goodprose.models import AnnotationSeed, EvalCase, TrainingExample

REPO_ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / name).read_text(encoding="utf-8"))


def test_training_model_matches_canonical_schema(training_record: dict[str, Any]) -> None:
    model = TrainingExample.model_validate(training_record)
    Draft202012Validator(
        _schema("data/schemas/training-example.schema.json"),
        format_checker=FormatChecker(),
    ).validate(model.model_dump(mode="json", exclude_none=True))


def test_annotation_seed_matches_canonical_schema(annotation_seed: dict[str, Any]) -> None:
    model = AnnotationSeed.model_validate(annotation_seed)
    Draft202012Validator(
        _schema("data/schemas/annotation-seed.schema.json"),
        format_checker=FormatChecker(),
    ).validate(model.model_dump(mode="json", exclude_none=True))


def test_eval_model_matches_canonical_schema() -> None:
    case = {
        "version": 1,
        "id": "eval-1",
        "split": "dev",
        "input": {
            "source_material": "The team implemented the endpoint.",
            "channel": "email",
            "audience": "Executive staff",
            "objective": "Share implementation status without implying deployment.",
            "voice_profile_id": "executive-house-v1",
        },
        "expected": {
            "required_facts": ["The endpoint was implemented."],
            "forbidden_claims": ["The endpoint is deployed."],
        },
        "provenance": {
            "lineage_group": "endpoint-change",
            "target_document_ids": ["go-doc-comment-format"],
            "input_origin": "real_source_material",
        },
    }
    model = EvalCase.model_validate(case)
    Draft202012Validator(
        _schema("evals/schemas/eval-case.schema.json"),
        format_checker=FormatChecker(),
    ).validate(model.model_dump(mode="json", exclude_none=True))


def test_models_reject_extra_fields_and_duplicate_provenance_ids(
    training_record: dict[str, Any],
) -> None:
    training_record["unexpected"] = True
    training_record["provenance"]["license_ids"] = ["MIT", "MIT"]
    with pytest.raises(ValidationError):
        TrainingExample.model_validate(training_record)


def test_models_require_explicit_version(training_record: dict[str, Any]) -> None:
    del training_record["version"]
    with pytest.raises(ValidationError):
        TrainingExample.model_validate(training_record)
