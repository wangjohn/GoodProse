from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest


@pytest.fixture
def training_record() -> dict[str, Any]:
    return {
        "version": 1,
        "id": "example-001",
        "split": "train",
        "input": {
            "source_material": (
                "The parser now rejects malformed input before writing output. "
                "The team added deterministic tests."
            ),
            "channel": "internal_memo",
            "audience": "Engineering and product leadership",
            "objective": "Explain the reliability improvement and its operational impact.",
            "voice_profile_id": "executive-house-v1",
            "constraints": ["Do not claim the change is deployed."],
            "context": [
                {
                    "kind": "constraint",
                    "content": "Malformed input must be rejected without partial writes.",
                }
            ],
        },
        "output": {
            "title": "Safer parser writes",
            "body_markdown": "The parser now rejects malformed input before any write begins.",
        },
        "provenance": {
            "creation_method": "human_revision",
            "lineage_group": "parser-change",
            "source_document_ids": ["go-draft-fuzzing"],
            "style_reference_ids": [],
            "license_ids": ["BSD-3-Clause"],
        },
        "review": {
            "privacy": "passed",
            "factuality": "passed",
            "objective_fulfillment": "passed",
            "audience_fit": "passed",
            "channel_fit": "passed",
            "house_style": "passed",
            "overall_quality": "passed",
            "reviewer": "reviewer-1",
        },
    }


@pytest.fixture
def second_training_record(training_record: dict[str, Any]) -> dict[str, Any]:
    record = deepcopy(training_record)
    record["id"] = "example-002"
    record["split"] = "validation"
    record["input"]["source_material"] = "The worker now has explicit state transitions."
    record["output"]["body_markdown"] = "The worker now moves through explicit states."
    record["provenance"]["lineage_group"] = "worker-state-change"
    return record


@pytest.fixture
def annotation_seed(training_record: dict[str, Any]) -> dict[str, Any]:
    record = deepcopy(training_record)
    del record["output"]
    del record["review"]
    return record
