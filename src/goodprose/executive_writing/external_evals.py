"""Strict adapters and acquisition metadata for external executive-writing evals.

This module normalizes externally acquired benchmark inputs (WritingBench,
IteraTeR/EditEval, Revision for Concision, YapBench) to a single versioned
GoodProse case boundary. It never downloads data, calls a model or judge,
or commits benchmark rows, references, criteria, predictions, or results.

A passing adapter test proves schema and acquisition compatibility only; it is
never a benchmark result and never implies leaderboard reproduction.
"""

from __future__ import annotations

import ast
import csv
import json
import math
import random
import re
import zipfile
from collections import Counter
from enum import StrEnum
from pathlib import Path
from statistics import median
from typing import Annotated, Any, Literal
from xml.etree import ElementTree

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from goodprose.jsonl import atomic_write, serialize_jsonl, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

REGISTRY_VERSION = "external-v1"
ADAPTER_VERSION = "goodprose-external-adapters-v1"
YAP_METRIC_VERSION = "goodprose-yap-compat-v1"
VISIBLE_CHARS_VERSION = "goodprose-visible-chars-v1"
YAP_BOOTSTRAP_SEED = 42
YAP_RESAMPLES = 1000
WRITINGBENCH_DEV_SIZE = 32


class BenchmarkId(StrEnum):
    WRITINGBENCH_BUSINESS = "writingbench-business"
    WRITINGBENCH_ENGINEERING = "writingbench-engineering"
    ITERATER_DIAGNOSTIC = "iterater-diagnostic"
    EDITEVAL_CLARITY = "editeval-clarity"
    EDITEVAL_COHERENCE = "editeval-coherence"
    REVISION_FOR_CONCISION = "revision-for-concision"
    YAPBENCH = "yapbench"


class RightsStatus(StrEnum):
    OPEN_VERIFIED = "open_verified"
    EVALUATION_ONLY = "evaluation_only"
    UNVERIFIED_BLOCKED = "unverified_execution_blocked"


class ExecutionStatus(StrEnum):
    ADAPTER_TESTED_NOT_EXECUTED = "adapter_tested_not_executed"
    JUDGE_UNPINNED = "adapter_tested_unexecuted_judge_unpinned"
    RIGHTS_BLOCKED = "execution_blocked_rights_unverified"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class CriterionAnchor(StrictModel):
    score_range: Literal["1-2", "3-4", "5-6", "7-8", "9-10"]
    description: NonEmpty


class EvaluationCriterion(StrictModel):
    name: NonEmpty
    description: NonEmpty
    anchors: tuple[CriterionAnchor, ...]


class SourceSpec(StrictModel):
    """One immutable external component with its acquisition recipe."""

    name: NonEmpty
    location: NonEmpty
    revision: NonEmpty
    sha256: Sha256 | None = None
    bytes: int | None = Field(default=None, gt=0)
    blob: str | None = None
    component_license: NonEmpty
    rights_status: RightsStatus
    acquisition: NonEmpty


class RegistryEntry(StrictModel):
    benchmark_id: BenchmarkId
    title: NonEmpty
    source: SourceSpec
    execution_status: ExecutionStatus
    rights_status: RightsStatus
    expected_source_rows: int | None = Field(default=None, gt=0)
    expected_domain_rows: int | None = Field(default=None, gt=0)
    expected_eligible_rows: int | None = Field(default=None, gt=0)
    metric_version: str | None = None
    normalization_version: str | None = None
    auxiliary_pins: tuple[SourceSpec, ...] = ()
    selected_source_indices: tuple[int, ...] = ()
    limitations: tuple[NonEmpty, ...] = ()

    @model_validator(mode="after")
    def unique_auxiliary(self) -> RegistryEntry:
        names = [pin.name for pin in self.auxiliary_pins]
        if len(names) != len(set(names)):
            raise ValueError(f"duplicate auxiliary pin name for {self.benchmark_id}")
        if len(self.selected_source_indices) != len(set(self.selected_source_indices)):
            raise ValueError(f"duplicate selected source index for {self.benchmark_id}")
        if any(index < 0 for index in self.selected_source_indices):
            raise ValueError(f"negative selected source index for {self.benchmark_id}")
        return self


class SourceRegistry(StrictModel):
    version: Literal[1]
    registry_id: Literal["goodprose-external-eval-sources-v1"]
    adapter_version: Literal["goodprose-external-adapters-v1"]
    entries: tuple[RegistryEntry, ...]

    @model_validator(mode="after")
    def unique_benchmarks(self) -> SourceRegistry:
        ids = [entry.benchmark_id for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate benchmark_id in source registry")
        required = set(BenchmarkId)
        if set(ids) != required:
            raise ValueError(f"registry must cover exactly {sorted(required)}")
        return self


class NormalizedExternalCase(StrictModel):
    """Local-only normalized case; references/criteria never leave the machine."""

    version: Literal[1]
    case_id: NonEmpty
    benchmark_id: BenchmarkId
    source_revision: NonEmpty
    source_sha256: Sha256
    split: Literal["development", "evaluation"]
    task: NonEmpty
    source_index: int = Field(ge=0)
    instruction: NonEmpty
    input_text: NonEmpty
    reference: str = ""
    criteria: tuple[EvaluationCriterion, ...] = ()
    attributes: dict[str, str] = Field(default_factory=dict)


class AdaptedManifest(StrictModel):
    version: Literal[1]
    benchmark_id: BenchmarkId
    adapter_version: Literal["goodprose-external-adapters-v1"]
    source_name: NonEmpty
    source_revision: NonEmpty
    source_sha256: Sha256
    adapter_input_sha256: Sha256 | None = None
    execution_status: ExecutionStatus
    rights_status: RightsStatus
    split: Literal["development", "evaluation", "mixed"]
    case_count: int = Field(ge=1)
    task_counts: dict[str, int]
    expected_source_rows: int | None
    source_row_count: int = Field(ge=1)
    excluded_counts: dict[str, int] = Field(default_factory=dict)
    selected_source_indices: tuple[int, ...] = ()
    metric_version: str | None = None
    normalization_version: str | None = None
    limitations: tuple[NonEmpty, ...]

    @model_validator(mode="after")
    def validate_counts(self) -> AdaptedManifest:
        if any(count <= 0 for count in self.task_counts.values()):
            raise ValueError("task counts must be positive")
        if sum(self.task_counts.values()) != self.case_count:
            raise ValueError("task counts must sum to case_count")
        if any(count < 0 for count in self.excluded_counts.values()):
            raise ValueError("excluded counts must be non-negative")
        return self


class CandidatePayloadCase(StrictModel):
    """Candidate-generation payload: ID and prompt only, never reference material."""

    id: NonEmpty
    instruction: NonEmpty
    input: NonEmpty


class ExternalPrediction(StrictModel):
    case_id: NonEmpty
    output: NonEmpty


class PredictionSet(StrictModel):
    benchmark_id: BenchmarkId
    case_count: int = Field(ge=1)
    prediction_count: int = Field(ge=1)


class YapCategoryScore(StrictModel):
    category: NonEmpty
    count: int = Field(ge=1)
    raw_median: float
    interval_low: float
    interval_high: float


class YapBenchResult(StrictModel):
    version: Literal[1]
    benchmark_id: Literal[BenchmarkId.YAPBENCH]
    metric_version: Literal["goodprose-yap-compat-v1"]
    normalization_version: Literal["goodprose-visible-chars-v1"]
    seed: int
    resamples: int = Field(gt=0)
    case_count: int = Field(ge=1)
    category_scores: tuple[YapCategoryScore, ...]
    yap_index: float
    yap_index_interval_low: float
    yap_index_interval_high: float
    disclaimer: NonEmpty


# ---------------------------------------------------------------------------
# Frozen public source registry
# ---------------------------------------------------------------------------

_WRITINGBENCH_SOURCE = SourceSpec(
    name="WritingBench benchmark_query/benchmark_all.jsonl",
    location="https://github.com/X-PLUG/WritingBench",
    revision="ae2d5176449b7b769815482641d35926f26793eb",
    sha256="18fee37c645166eb2e206b36366b2e354265b1e4201db2c86e759e825eaddcbe",
    bytes=14_726_077,
    blob="2d04c2d4c82f8c2d615e963393c7808f64b97129",
    component_license=(
        "Apache-2.0 repository license; bundled query/material components are "
        "not separately licensed upstream"
    ),
    rights_status=RightsStatus.EVALUATION_ONLY,
    acquisition=(
        "git clone https://github.com/X-PLUG/WritingBench && "
        "git checkout ae2d5176449b7b769815482641d35926f26793eb; "
        "use benchmark_query/benchmark_all.jsonl"
    ),
)

_WRITINGBENCH_AUXILIARY = (
    SourceSpec(
        name="WritingBench prompt.py",
        location="https://github.com/X-PLUG/WritingBench",
        revision="ae2d5176449b7b769815482641d35926f26793eb",
        sha256="c5bf21f28d4b4e54b682236cbe815831f3e362ff9b4f3e8c7c10467c491ecad1",
        blob="8f81b8670e2b09717c4d25c7328ecb87a2e657ec",
        component_license="Apache-2.0",
        rights_status=RightsStatus.OPEN_VERIFIED,
        acquisition="included in the pinned clone at prompt.py",
    ),
    SourceSpec(
        name="WritingBench evaluate_benchmark.py",
        location="https://github.com/X-PLUG/WritingBench",
        revision="ae2d5176449b7b769815482641d35926f26793eb",
        sha256="64707256e39e0533a020fe8042152b63ec706b63cbaa18d251030c71b0095e34",
        blob="f22c145567472d25ed6368cfb2465e4be27e9fd8",
        component_license="Apache-2.0",
        rights_status=RightsStatus.OPEN_VERIFIED,
        acquisition="included in the pinned clone at evaluate_benchmark.py",
    ),
    SourceSpec(
        name="WritingBench LLM wrapper",
        location="https://github.com/X-PLUG/WritingBench",
        revision="ae2d5176449b7b769815482641d35926f26793eb",
        sha256="28a609a8ed070b2ab54fa8ff659b700175c20945c2b7cc670d106156aee2c0d5",
        component_license="Apache-2.0",
        rights_status=RightsStatus.OPEN_VERIFIED,
        acquisition=(
            "included in the pinned clone; freezes temperature 1, top-p 0.95, "
            "max 2048 tokens, but leaves judge model and endpoint blank"
        ),
    ),
)

_WRITINGBENCH_LIMITATIONS = (
    "The upstream LLM wrapper does not pin an exact judge API model version; "
    "the README names Claude Sonnet 4.5 without a version pin.",
    "Adapter tests prove schema and acquisition compatibility only; upstream "
    "leaderboard scores are not reproducible from the repository alone and are "
    "never claimed.",
    "The pinned domains contain 210/167 multilingual rows. GoodProse excludes "
    "non-English rows, leaving 115/107 eligible cases; only the frozen 32-case "
    "development subset may drive iteration and the remaining eligible cases "
    "are reserved for finalist/milestone use.",
)

_ITERATER_SOURCE = SourceSpec(
    name="wanyu/IteraTeR_human_sent test split",
    location="https://huggingface.co/datasets/wanyu/IteraTeR_human_sent",
    revision="e22e0371dac444239b944f9293f5b491d62b73f0",
    sha256="1a30452c33bd5379ff56159016d68ecd7e2669ede1e4ea77244c6e300952e9cb",
    bytes=294_380,
    blob="04b93aef8a9db2576dd81541343f841bd7081971",
    component_license="Apache-2.0",
    rights_status=RightsStatus.OPEN_VERIFIED,
    acquisition=(
        'python -c "from huggingface_hub import hf_hub_download; '
        "print(hf_hub_download('wanyu/IteraTeR_human_sent', "
        "'test.json', revision="
        "'e22e0371dac444239b944f9293f5b491d62b73f0'))\"; verify SHA-256 before use"
    ),
)

_ITERATER_REPO_PIN = SourceSpec(
    name="IteraTeR dataset/IteraTeR.zip",
    location="https://github.com/vipulraheja/iterater",
    revision="41adc0818356f78b362a9382a3732e0529f3fe35",
    sha256="386824f3310fca318351c0c76ed6475f99ed85dee0512e0da623af27b35e3ca7",
    blob="d8ad5197667fe015007280dc24117beca9a67b84",
    component_license="Apache-2.0",
    rights_status=RightsStatus.OPEN_VERIFIED,
    acquisition=(
        "git clone https://github.com/vipulraheja/iterater && "
        "git checkout 41adc0818356f78b362a9382a3732e0529f3fe35; use dataset/IteraTeR.zip"
    ),
)

_EDITEVAL_REPO_PIN = SourceSpec(
    name="EditEval ITERProcessor",
    location="https://github.com/facebookresearch/EditEval",
    revision="013cd20aa73be0016041201454b3fcd7c2250fb4",
    sha256="93c810c62c7aefa2723cf5e951e6bf6d59ce77ffef060cdbb4116ee35586cd29",
    component_license="CC0-1.0 (code); dataset rights remain IteraTeR's Apache-2.0",
    rights_status=RightsStatus.OPEN_VERIFIED,
    acquisition=(
        "git clone https://github.com/facebookresearch/EditEval && "
        "git checkout 013cd20aa73be0016041201454b3fcd7c2250fb4"
    ),
)

WRITINGBENCH_BUSINESS_DEV_INDICES = (
    48,
    49,
    55,
    60,
    61,
    64,
    65,
    77,
    81,
    82,
    88,
    89,
    91,
    92,
    99,
    103,
    104,
    106,
    108,
    111,
    113,
    114,
    119,
    309,
    322,
    505,
    565,
    568,
    624,
    671,
    771,
    842,
)
WRITINGBENCH_ENGINEERING_DEV_INDICES = (
    2,
    3,
    7,
    8,
    12,
    13,
    19,
    20,
    22,
    23,
    24,
    26,
    27,
    29,
    30,
    31,
    33,
    34,
    36,
    38,
    39,
    40,
    43,
    46,
    258,
    489,
    490,
    491,
    493,
    658,
    719,
    956,
)


def build_source_registry() -> SourceRegistry:
    """Return the frozen public registry of external evaluation sources."""

    entries = (
        RegistryEntry(
            benchmark_id=BenchmarkId.WRITINGBENCH_BUSINESS,
            title="WritingBench Business (Finance & Business domain)",
            source=_WRITINGBENCH_SOURCE,
            execution_status=ExecutionStatus.JUDGE_UNPINNED,
            rights_status=RightsStatus.EVALUATION_ONLY,
            expected_source_rows=1000,
            expected_domain_rows=210,
            expected_eligible_rows=115,
            auxiliary_pins=_WRITINGBENCH_AUXILIARY,
            selected_source_indices=WRITINGBENCH_BUSINESS_DEV_INDICES,
            limitations=_WRITINGBENCH_LIMITATIONS,
        ),
        RegistryEntry(
            benchmark_id=BenchmarkId.WRITINGBENCH_ENGINEERING,
            title="WritingBench Engineering (Academic & Engineering domain)",
            source=_WRITINGBENCH_SOURCE,
            execution_status=ExecutionStatus.JUDGE_UNPINNED,
            rights_status=RightsStatus.EVALUATION_ONLY,
            expected_source_rows=1000,
            expected_domain_rows=167,
            expected_eligible_rows=107,
            auxiliary_pins=_WRITINGBENCH_AUXILIARY,
            selected_source_indices=WRITINGBENCH_ENGINEERING_DEV_INDICES,
            limitations=_WRITINGBENCH_LIMITATIONS,
        ),
        RegistryEntry(
            benchmark_id=BenchmarkId.ITERATER_DIAGNOSTIC,
            title="IteraTeR human sentence-level diagnostic (clarity+coherence+fluency)",
            source=_ITERATER_SOURCE,
            execution_status=ExecutionStatus.ADAPTER_TESTED_NOT_EXECUTED,
            rights_status=RightsStatus.OPEN_VERIFIED,
            expected_source_rows=364,
            expected_eligible_rows=308,
            auxiliary_pins=(_ITERATER_REPO_PIN,),
            limitations=(
                "Diagnostic uses the human sentence-level test split only; the "
                "model-labeled full set and IteraTeR-v2/IteraTeR-plus require "
                "Newsela acquisition or author contact and are out of scope.",
                "Labels act as task filters only. The released intent classifier "
                "(F1 0.69 clarity / 0.32 coherence / 0.13 style) is never an "
                "authoritative long-form judge.",
            ),
        ),
        RegistryEntry(
            benchmark_id=BenchmarkId.EDITEVAL_CLARITY,
            title="EditEval clarity diagnostic (IteraTeR clarity labels)",
            source=_ITERATER_SOURCE,
            execution_status=ExecutionStatus.ADAPTER_TESTED_NOT_EXECUTED,
            rights_status=RightsStatus.OPEN_VERIFIED,
            expected_source_rows=364,
            expected_eligible_rows=185,
            auxiliary_pins=(_EDITEVAL_REPO_PIN,),
            limitations=(
                "The pinned ITERProcessor field mapping and len(after_sent) > 1 "
                "filter are reproduced exactly; this does not claim parity with "
                "any separate generation or scoring stack.",
                "Dataset rights remain IteraTeR's, not EditEval's CC0 code license.",
            ),
        ),
        RegistryEntry(
            benchmark_id=BenchmarkId.EDITEVAL_COHERENCE,
            title="EditEval coherence diagnostic (IteraTeR coherence labels)",
            source=_ITERATER_SOURCE,
            execution_status=ExecutionStatus.ADAPTER_TESTED_NOT_EXECUTED,
            rights_status=RightsStatus.OPEN_VERIFIED,
            expected_source_rows=364,
            expected_eligible_rows=35,
            auxiliary_pins=(_EDITEVAL_REPO_PIN,),
            limitations=(
                "The pinned ITERProcessor field mapping and len(after_sent) > 1 "
                "filter are reproduced exactly; this does not claim parity with "
                "any separate generation or scoring stack.",
                "Dataset rights remain IteraTeR's, not EditEval's CC0 code license.",
            ),
        ),
        RegistryEntry(
            benchmark_id=BenchmarkId.REVISION_FOR_CONCISION,
            title="Revision for Concision sentence pairs",
            source=SourceSpec(
                name="2022.tsar-1.6 sac.xlsx",
                location="https://aclanthology.org/attachments/2022.tsar-1.6.dataset.zip",
                revision="DOI 10.18653/v1/2022.tsar-1.6",
                sha256="77f05c87f48f3e6dd25197bc921d38032ef145d834fce2d35e6e0125e798889e",
                component_license=(
                    "ACL Anthology CC BY 4.0 applies to post-2016 Anthology "
                    "materials, but the spreadsheet compiles college writing-center "
                    "examples; treated as evaluation_only regardless"
                ),
                rights_status=RightsStatus.EVALUATION_ONLY,
                acquisition=(
                    "curl -O https://aclanthology.org/attachments/"
                    "2022.tsar-1.6.dataset.zip && unzip 2022.tsar-1.6.dataset.zip; "
                    "verify ZIP SHA-256 "
                    "6ae45cc974caf9ffc7d7eca305b2f6d5fe1045af34bbe4073c30cd103652d9b2 "
                    "and sac.xlsx SHA-256 "
                    "77f05c87f48f3e6dd25197bc921d38032ef145d834fce2d35e6e0125e798889e"
                ),
            ),
            execution_status=ExecutionStatus.ADAPTER_TESTED_NOT_EXECUTED,
            rights_status=RightsStatus.EVALUATION_ONLY,
            expected_source_rows=536,
            expected_eligible_rows=536,
            auxiliary_pins=(
                SourceSpec(
                    name="2022.tsar-1.6.dataset.zip",
                    location="https://aclanthology.org/attachments/2022.tsar-1.6.dataset.zip",
                    revision="DOI 10.18653/v1/2022.tsar-1.6",
                    sha256="6ae45cc974caf9ffc7d7eca305b2f6d5fe1045af34bbe4073c30cd103652d9b2",
                    component_license="See paper/data page",
                    rights_status=RightsStatus.EVALUATION_ONLY,
                    acquisition="curl -O https://aclanthology.org/attachments/2022.tsar-1.6.dataset.zip",
                ),
            ),
            limitations=(
                "Do not redistribute the spreadsheet or adapted rows; keep per-row "
                "citation/link metadata only in local adapted artifacts.",
            ),
        ),
        RegistryEntry(
            benchmark_id=BenchmarkId.YAPBENCH,
            title="YapBench v0.1 verbosity diagnostic",
            source=SourceSpec(
                name="tabularisai/yapbench_dataset train parquet",
                location="https://huggingface.co/datasets/tabularisai/yapbench_dataset",
                revision="be8427ddf7780201b73676c1563bc3ea6d0a71ca",
                sha256="6bf58b51cef6b26e78cf462ff78d43d1b80d1162268be6019918036212430d5e",
                bytes=24_703,
                component_license="No license metadata on the dataset repository",
                rights_status=RightsStatus.UNVERIFIED_BLOCKED,
                acquisition=(
                    'python -c "from huggingface_hub import hf_hub_download; '
                    "print(hf_hub_download('tabularisai/yapbench_dataset', "
                    "'data/train-00000-of-00001.parquet', revision="
                    "'be8427ddf7780201b73676c1563bc3ea6d0a71ca'))\"; verify LFS "
                    "SHA-256 before converting to normalized JSONL outside this "
                    "repository (parquet support is intentionally not vendored)"
                ),
            ),
            execution_status=ExecutionStatus.RIGHTS_BLOCKED,
            rights_status=RightsStatus.UNVERIFIED_BLOCKED,
            expected_source_rows=304,
            expected_eligible_rows=300,
            metric_version=YAP_METRIC_VERSION,
            normalization_version=VISIBLE_CHARS_VERSION,
            auxiliary_pins=(
                SourceSpec(
                    name="YapBench leaderboard Space",
                    location="https://huggingface.co/spaces/tabularisai/yapbench",
                    revision="fd2f0e6ba21f4311a2e667bd2ce470bafa50788e",
                    component_license="Apache-2.0",
                    rights_status=RightsStatus.OPEN_VERIFIED,
                    acquisition=(
                        "pinned Space revision; Apache-2.0 does not cure the "
                        "dataset-license omission"
                    ),
                ),
            ),
            limitations=(
                "Dataset rights are unverified; redistribution is prohibited and "
                "execution stays blocked until clarified.",
                "YapScore measures visible length difference only; it is never an "
                "executive-writing quality score and brevity never bypasses "
                "fidelity gates.",
                "Metric is a GoodProse-labeled compatibility variant of the "
                "published deterministic definition; upstream implementation "
                "parity of markdown normalization is not proven and is labeled.",
            ),
        ),
    )
    return SourceRegistry(
        version=1,
        registry_id="goodprose-external-eval-sources-v1",
        adapter_version=ADAPTER_VERSION,
        entries=entries,
    )


def find_registry_entry(benchmark_id: BenchmarkId) -> RegistryEntry:
    for entry in build_source_registry().entries:
        if entry.benchmark_id == benchmark_id:
            return entry
    raise AssertionError(f"unregistered benchmark {benchmark_id}")


# ---------------------------------------------------------------------------
# Verification and parsing helpers
# ---------------------------------------------------------------------------


def verify_source(
    path: Path,
    expected_sha256: str,
    *,
    expected_bytes: int | None = None,
) -> str:
    """Verify exact file identity before any parsing occurs."""

    if not path.is_file():
        raise ValueError(f"source file not found: {path}")
    digest = sha256_file(path)
    if digest != expected_sha256:
        raise ValueError(f"sha256 mismatch for {path}: expected {expected_sha256}, got {digest}")
    actual_bytes = path.stat().st_size
    if expected_bytes is not None and actual_bytes != expected_bytes:
        raise ValueError(
            f"byte-size mismatch for {path}: expected {expected_bytes}, got {actual_bytes}"
        )
    return digest


def _read_jsonl_records(path: Path) -> list[tuple[int, dict[str, Any]]]:
    records: list[tuple[int, dict[str, Any]]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {error.msg}") from error
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            records.append((line_number, value))
    if not records:
        raise ValueError(f"{path}: no JSONL records found")
    return records


def _require_exact_fields(
    record: dict[str, Any],
    fields: tuple[str, ...],
    *,
    where: str,
) -> None:
    keys = set(record)
    missing = sorted(set(fields) - keys)
    extra = sorted(keys - set(fields))
    problems = []
    if missing:
        problems.append(f"missing fields {missing}")
    if extra:
        problems.append(f"unknown fields {extra}")
    if problems:
        raise ValueError(f"{where}: {'; '.join(problems)}")


def _require_non_empty_str(value: Any, *, field: str, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: {field} must be a non-empty string")
    return value


def _require_str_list(value: Any, *, field: str, where: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{where}: {field} must be a non-empty list")
    return [_require_non_empty_str(item, field=f"{field}[]", where=where) for item in value]


def _make_case(
    *,
    case_id: str,
    benchmark_id: BenchmarkId,
    source_revision: str,
    source_sha256: str,
    split: Literal["development", "evaluation"],
    task: str,
    source_index: int,
    instruction: str,
    input_text: str,
    reference: str = "",
    criteria: tuple[EvaluationCriterion, ...] = (),
    attributes: dict[str, str] | None = None,
) -> NormalizedExternalCase:
    return NormalizedExternalCase(
        version=1,
        case_id=case_id,
        benchmark_id=benchmark_id,
        source_revision=source_revision,
        source_sha256=source_sha256,
        split=split,
        task=task,
        source_index=source_index,
        instruction=instruction,
        input_text=input_text,
        reference=reference,
        criteria=criteria,
        attributes=attributes or {},
    )


def _build_manifest(
    *,
    entry: RegistryEntry,
    source_sha256: str,
    split: Literal["development", "evaluation", "mixed"],
    cases: list[NormalizedExternalCase],
    expected_source_rows: int | None,
    source_row_count: int,
    excluded_counts: dict[str, int] | None = None,
    adapter_input_sha256: str | None = None,
    selected_source_indices: tuple[int, ...] = (),
) -> AdaptedManifest:
    counts = Counter(case.task for case in cases)
    return AdaptedManifest(
        version=1,
        benchmark_id=entry.benchmark_id,
        adapter_version=ADAPTER_VERSION,
        source_name=entry.source.name,
        source_revision=entry.source.revision,
        source_sha256=source_sha256,
        adapter_input_sha256=adapter_input_sha256,
        execution_status=entry.execution_status,
        rights_status=entry.rights_status,
        split=split,
        case_count=len(cases),
        task_counts=dict(sorted(counts.items())),
        expected_source_rows=expected_source_rows,
        source_row_count=source_row_count,
        excluded_counts=dict(sorted((excluded_counts or {}).items())),
        selected_source_indices=selected_source_indices,
        metric_version=entry.metric_version,
        normalization_version=entry.normalization_version,
        limitations=entry.limitations,
    )


def _check_expected_rows(actual: int, expected: int | None, *, label: str) -> None:
    if expected is not None and actual != expected:
        raise ValueError(f"{label}: expected {expected} rows, found {actual}")


# ---------------------------------------------------------------------------
# WritingBench adapters
# ---------------------------------------------------------------------------

WRITINGBENCH_DOMAINS = {
    BenchmarkId.WRITINGBENCH_BUSINESS: ("Finance & Business", 210),
    BenchmarkId.WRITINGBENCH_ENGINEERING: ("Academic & Engineering", 167),
}
WRITINGBENCH_ELIGIBLE_ROWS = {
    BenchmarkId.WRITINGBENCH_BUSINESS: 115,
    BenchmarkId.WRITINGBENCH_ENGINEERING: 107,
}
WRITINGBENCH_ALL_DOMAINS = frozenset(
    {
        "Academic & Engineering",
        "Advertising & Marketing",
        "Education",
        "Finance & Business",
        "Literature & Arts",
        "Politics & Law",
    }
)
WRITINGBENCH_SUBDOMAINS = {
    BenchmarkId.WRITINGBENCH_BUSINESS: frozenset(
        {
            "Bid Proposal",
            "Briefing",
            "Business Correspondence",
            "Contract",
            "Event Planning",
            "Financial Reports",
            "Human Resource Management",
            "Investment Analysis",
            "Market Analysis",
            "Market Research",
            "Meeting Minutes",
            "Pitch Deck",
            "Product Proposal",
            "Recruitment",
            "Requirements Specification",
            "Risk Management",
            "Sales Report",
            "Strategic Planning",
            "Tender Document",
            "User Research",
        }
    ),
    BenchmarkId.WRITINGBENCH_ENGINEERING: frozenset(
        {
            "Abstract",
            "Acknowledgements",
            "Conclusion",
            "Contributions",
            "Defense Presentation",
            "Defense Script",
            "Engineering Report",
            "Experiments",
            "Internship Report",
            "Introduction",
            "Limitations",
            "Literature Review",
            "Paper Outline",
            "Patent",
            "Research Proposal",
            "Technical Documentation",
            "Test Report",
        }
    ),
}
WRITINGBENCH_FIELDS = ("index", "domain1", "domain2", "lang", "query", "checklist")
WRITINGBENCH_CRITERION_FIELDS = (
    "name",
    "criteria_description",
    "1-2",
    "3-4",
    "5-6",
    "7-8",
    "9-10",
)


def _parse_writingbench_checklist(value: Any, *, where: str) -> tuple[EvaluationCriterion, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{where}: checklist must be a non-empty list")
    criteria: list[EvaluationCriterion] = []
    seen_names: set[str] = set()
    for position, raw in enumerate(value):
        criterion_where = f"{where} checklist[{position}]"
        if not isinstance(raw, dict):
            raise ValueError(f"{criterion_where}: expected an object")
        _require_exact_fields(raw, WRITINGBENCH_CRITERION_FIELDS, where=criterion_where)
        name = _require_non_empty_str(raw["name"], field="name", where=criterion_where)
        if name in seen_names:
            raise ValueError(f"{criterion_where}: duplicate criterion name {name!r}")
        seen_names.add(name)
        criteria.append(
            EvaluationCriterion(
                name=name,
                description=_require_non_empty_str(
                    raw["criteria_description"],
                    field="criteria_description",
                    where=criterion_where,
                ),
                anchors=tuple(
                    CriterionAnchor(
                        score_range=score_range,
                        description=_require_non_empty_str(
                            raw[score_range], field=score_range, where=criterion_where
                        ),
                    )
                    for score_range in ("1-2", "3-4", "5-6", "7-8", "9-10")
                ),
            )
        )
    return tuple(criteria)


def select_stratified_dev_indices(tasks: list[str], size: int) -> tuple[int, ...]:
    """Round-robin over lexicographically sorted task groups, preserving order."""

    groups: dict[str, list[int]] = {}
    for index, task in enumerate(tasks):
        groups.setdefault(task, []).append(index)
    selected: list[int] = []
    cursor = 0
    while len(selected) < size:
        progressed = False
        for key in sorted(groups):
            if cursor < len(groups[key]):
                selected.append(groups[key][cursor])
                progressed = True
                if len(selected) == size:
                    break
        if not progressed:
            available = len(tasks)
            raise ValueError(f"insufficient rows: {available} available, cannot select {size}")
        cursor += 1
    return tuple(sorted(selected))


def adapt_writingbench(
    records: list[tuple[int, dict[str, Any]]],
    *,
    benchmark_id: BenchmarkId,
    source_revision: str,
    source_sha256: str,
    expected_domain_rows: int | None,
    expected_source_rows: int | None = None,
    dev_size: int = WRITINGBENCH_DEV_SIZE,
) -> tuple[list[NormalizedExternalCase], AdaptedManifest]:
    """Normalize one WritingBench domain and freeze its stratified dev subset."""

    if benchmark_id not in WRITINGBENCH_DOMAINS:
        raise ValueError(f"{benchmark_id} is not a WritingBench benchmark")
    domain, default_domain_rows = WRITINGBENCH_DOMAINS[benchmark_id]
    entry = find_registry_entry(benchmark_id)
    expected_domain = default_domain_rows if expected_domain_rows is None else expected_domain_rows
    pinned_source = source_sha256 == entry.source.sha256
    expected_source = (
        entry.expected_source_rows
        if expected_source_rows is None and pinned_source
        else expected_source_rows
    )
    _check_expected_rows(len(records), expected_source, label="writingbench source")
    domain_cases: list[NormalizedExternalCase] = []
    tasks: list[str] = []
    upstream_indices: list[int] = []
    seen_indices: set[int] = set()
    seen_ids: set[str] = set()
    target_domain_rows = 0
    excluded_non_english = 0
    for line_number, record in records:
        where = f"writingbench line {line_number}"
        _require_exact_fields(record, WRITINGBENCH_FIELDS, where=where)
        row_domain = _require_non_empty_str(record["domain1"], field="domain1", where=where)
        if row_domain not in WRITINGBENCH_ALL_DOMAINS:
            raise ValueError(f"{where}: invalid domain1 {row_domain!r}")
        language = _require_non_empty_str(record["lang"], field="lang", where=where)
        if language not in {"en", "zh"}:
            raise ValueError(f"{where}: invalid language {language!r}")
        index_value = record["index"]
        if not isinstance(index_value, int) or isinstance(index_value, bool) or index_value < 0:
            raise ValueError(f"{where}: index must be a non-negative integer")
        if index_value in seen_indices:
            raise ValueError(f"{where}: duplicate source index {index_value}")
        seen_indices.add(index_value)
        subdomain = _require_non_empty_str(record["domain2"], field="domain2", where=where)
        query = _require_non_empty_str(record["query"], field="query", where=where)
        checklist = _parse_writingbench_checklist(record["checklist"], where=where)
        if row_domain != domain:
            continue
        target_domain_rows += 1
        if subdomain not in WRITINGBENCH_SUBDOMAINS[benchmark_id]:
            raise ValueError(f"{where}: invalid domain2 {subdomain!r} for {domain}")
        if language != "en":
            excluded_non_english += 1
            continue
        case_id = f"{benchmark_id.value}-full-{index_value}"
        if case_id in seen_ids:
            raise ValueError(f"{where}: duplicate case id {case_id}")
        seen_ids.add(case_id)
        domain_cases.append(
            _make_case(
                case_id=case_id,
                benchmark_id=benchmark_id,
                source_revision=source_revision,
                source_sha256=source_sha256,
                split="evaluation",
                task=subdomain,
                source_index=index_value,
                instruction="Complete the requested writing task.",
                input_text=query,
                criteria=checklist,
            )
        )
        tasks.append(subdomain)
        upstream_indices.append(index_value)
    _check_expected_rows(target_domain_rows, expected_domain, label=f"{benchmark_id.value} domain")
    if pinned_source:
        _check_expected_rows(
            len(domain_cases),
            WRITINGBENCH_ELIGIBLE_ROWS[benchmark_id],
            label=f"{benchmark_id.value} English-eligible domain",
        )
    if len(domain_cases) < dev_size:
        raise ValueError(
            f"{benchmark_id.value}: need at least {dev_size} domain rows, found {len(domain_cases)}"
        )
    selected_positions = select_stratified_dev_indices(tasks, dev_size)
    selected = tuple(sorted(upstream_indices[position] for position in selected_positions))
    if pinned_source and selected != entry.selected_source_indices:
        raise ValueError(
            f"{benchmark_id.value}: selected indices do not match frozen registry; "
            f"expected {entry.selected_source_indices}, got {selected}"
        )
    selected_set = set(selected)
    cases = [
        case.model_copy(update={"split": "development"})
        if case.source_index in selected_set
        else case
        for case in domain_cases
    ]
    cases.sort(key=lambda case: (case.split != "development", case.case_id))
    manifest = _build_manifest(
        entry=entry,
        source_sha256=source_sha256,
        split="mixed",
        cases=cases,
        expected_source_rows=expected_source,
        source_row_count=len(records),
        excluded_counts={"non_english_target_domain": excluded_non_english},
        selected_source_indices=selected,
    )
    return cases, manifest


# ---------------------------------------------------------------------------
# IteraTeR / EditEval adapters
# ---------------------------------------------------------------------------

ITERATER_FIELDS = (
    "before_sent",
    "before_sent_with_intent",
    "after_sent",
    "labels",
    "doc_id",
    "revision_depth",
)
VALID_ITERATER_LABELS = frozenset(
    {"clarity", "coherence", "fluency", "meaning-changed", "others", "style"}
)
DIAGNOSTIC_LABELS = frozenset({"clarity", "coherence", "fluency"})
PINNED_ITERATER_TEST_COUNTS: dict[str, int] = {
    "clarity": 186,
    "coherence": 36,
    "fluency": 88,
    "meaning-changed": 35,
    "others": 4,
    "style": 15,
}


def parse_iterater_records(
    records: list[tuple[int, dict[str, Any]]],
) -> list[tuple[int, str, int, str, str, str]]:
    """Validate IteraTeR rows as released by the pinned HF revision."""

    parsed: list[tuple[int, str, int, str, str, str]] = []
    seen_rows: set[tuple[str, int, str, str, str]] = set()
    for line_number, record in records:
        where = f"iterater line {line_number}"
        _require_exact_fields(record, ITERATER_FIELDS, where=where)
        before = _require_non_empty_str(record["before_sent"], field="before_sent", where=where)
        after_value = record["after_sent"]
        if not isinstance(after_value, str):
            raise ValueError(f"{where}: after_sent must be a string")
        after = after_value
        _require_non_empty_str(
            record["before_sent_with_intent"], field="before_sent_with_intent", where=where
        )
        doc_id = _require_non_empty_str(record["doc_id"], field="doc_id", where=where)
        revision_depth = record["revision_depth"]
        if (
            not isinstance(revision_depth, int)
            or isinstance(revision_depth, bool)
            or revision_depth < 0
        ):
            raise ValueError(f"{where}: revision_depth must be a non-negative integer")
        label = _require_non_empty_str(record["labels"], field="labels", where=where)
        if label not in VALID_ITERATER_LABELS:
            raise ValueError(f"{where}: invalid label {label!r}")
        identity = (doc_id, revision_depth, before, after, label)
        if identity in seen_rows:
            raise ValueError(f"{where}: duplicate source record")
        seen_rows.add(identity)
        parsed.append((line_number, doc_id, revision_depth, before, after, label))
    return parsed


def _validate_label_counts(
    parsed: list[tuple[int, str, int, str, str, str]],
    expected: dict[str, int],
) -> None:
    observed = Counter(label for *_, label in parsed)
    if observed != Counter(expected):
        raise ValueError(
            "iterater label count mismatch: "
            f"expected {dict(sorted(expected.items()))}, got {dict(sorted(observed.items()))}"
        )


def _resolve_label_expectations(
    expected_label_counts: dict[str, int] | None,
) -> dict[str, int]:
    return (
        dict(PINNED_ITERATER_TEST_COUNTS)
        if expected_label_counts is None
        else expected_label_counts
    )


def adapt_iterater(
    records: list[tuple[int, dict[str, Any]]],
    *,
    source_revision: str,
    source_sha256: str,
    expected_label_counts: dict[str, int] | None = None,
) -> tuple[list[NormalizedExternalCase], AdaptedManifest]:
    """Emit 308 usable cases from the 310 pinned diagnostic-labeled rows."""

    benchmark_id = BenchmarkId.ITERATER_DIAGNOSTIC
    entry = find_registry_entry(benchmark_id)
    expected = _resolve_label_expectations(expected_label_counts)
    parsed = parse_iterater_records(records)
    _validate_label_counts(parsed, expected)
    cases: list[NormalizedExternalCase] = []
    seen_ids: set[str] = set()
    excluded_empty_reference = 0
    for line_number, doc_id, revision_depth, before, after, label in parsed:
        if label not in DIAGNOSTIC_LABELS:
            continue
        if not after.strip():
            excluded_empty_reference += 1
            continue
        source_index = line_number - 1
        case_id = f"{benchmark_id.value}-{source_index:05d}"
        if case_id in seen_ids:
            raise ValueError(f"duplicate case id {case_id}")
        seen_ids.add(case_id)
        cases.append(
            _make_case(
                case_id=case_id,
                benchmark_id=benchmark_id,
                source_revision=source_revision,
                source_sha256=source_sha256,
                split="evaluation",
                task=label,
                source_index=source_index,
                instruction=("Revise the sentence according to the requested editorial intent."),
                input_text=before,
                reference=after,
                attributes={"doc_id": doc_id, "revision_depth": str(revision_depth)},
            )
        )
    if not cases:
        raise ValueError("iterater diagnostic produced no cases")
    if source_sha256 == entry.source.sha256:
        _check_expected_rows(
            len(cases), entry.expected_eligible_rows, label="iterater usable diagnostic"
        )
    manifest = _build_manifest(
        entry=entry,
        source_sha256=source_sha256,
        split="evaluation",
        cases=cases,
        expected_source_rows=sum(expected.values()),
        source_row_count=len(parsed),
        excluded_counts={"empty_reference": excluded_empty_reference},
    )
    return cases, manifest


def adapt_editeval(
    records: list[tuple[int, dict[str, Any]]],
    *,
    benchmark_id: BenchmarkId,
    source_revision: str,
    source_sha256: str,
    expected_label_counts: dict[str, int] | None = None,
) -> tuple[list[NormalizedExternalCase], AdaptedManifest]:
    """Adapt EditEval clarity/coherence from the IteraTeR human sentence file.

    Follows the pinned ITERProcessor exactly at this boundary: map
    ``before_sent`` to the input, ``after_sent`` to the edit reference, filter
    the exact task label, and retain only references whose string length is > 1.
    """

    if benchmark_id not in (BenchmarkId.EDITEVAL_CLARITY, BenchmarkId.EDITEVAL_COHERENCE):
        raise ValueError(f"{benchmark_id} is not an EditEval benchmark")
    task = "clarity" if benchmark_id == BenchmarkId.EDITEVAL_CLARITY else "coherence"
    entry = find_registry_entry(benchmark_id)
    expected = _resolve_label_expectations(expected_label_counts)
    parsed = parse_iterater_records(records)
    _validate_label_counts(parsed, expected)
    cases: list[NormalizedExternalCase] = []
    seen_ids: set[str] = set()
    excluded_short_reference = 0
    for line_number, doc_id, revision_depth, before, after, label in parsed:
        if label != task:
            continue
        if len(after) <= 1:
            excluded_short_reference += 1
            continue
        source_index = line_number - 1
        case_id = f"{benchmark_id.value}-{source_index:05d}"
        if case_id in seen_ids:
            raise ValueError(f"duplicate case id {case_id}")
        seen_ids.add(case_id)
        cases.append(
            _make_case(
                case_id=case_id,
                benchmark_id=benchmark_id,
                source_revision=source_revision,
                source_sha256=source_sha256,
                split="evaluation",
                task=label,
                source_index=source_index,
                instruction=(f"Revise the sentence for {task}."),
                input_text=before,
                reference=after,
                attributes={"doc_id": doc_id, "revision_depth": str(revision_depth)},
            )
        )
    if not cases:
        raise ValueError(f"editeval {task} produced no cases")
    if source_sha256 == entry.source.sha256:
        _check_expected_rows(
            len(cases), entry.expected_eligible_rows, label=f"editeval {task} usable diagnostic"
        )
    manifest = _build_manifest(
        entry=entry,
        source_sha256=source_sha256,
        split="evaluation",
        cases=cases,
        expected_source_rows=sum(expected.values()),
        source_row_count=len(parsed),
        excluded_counts={"reference_length_le_1": excluded_short_reference},
    )
    return cases, manifest


# ---------------------------------------------------------------------------
# Revision for Concision adapter
# ---------------------------------------------------------------------------

CONCISION_COLUMNS = ("cite", "wordy", "concise", "category", "link", "id")

_XLSX_MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _column_index(reference: str) -> int:
    match = re.fullmatch(r"([A-Z]+)(\d+)", reference)
    if not match:
        raise ValueError(f"invalid xlsx cell reference {reference!r}")
    index = 0
    for character in match.group(1):
        index = index * 26 + (ord(character) - ord("A") + 1)
    return index - 1


def _parse_shared_strings(data: bytes) -> list[str]:
    root = ElementTree.fromstring(data)
    values: list[str] = []
    for item in root.findall(f"{_XLSX_MAIN_NS}si"):
        values.append("".join(node.text or "" for node in item.iter(f"{_XLSX_MAIN_NS}t")))
    return values


def read_concision_xlsx(path: Path) -> list[tuple[int, dict[str, Any]]]:
    """Dependency-free reader for the narrow shared-strings XLSX form."""

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "xl/sharedStrings.xml" not in names:
            raise ValueError(f"{path}: missing xl/sharedStrings.xml")
        if "xl/worksheets/sheet1.xml" not in names:
            raise ValueError(f"{path}: missing xl/worksheets/sheet1.xml")
        shared = _parse_shared_strings(archive.read("xl/sharedStrings.xml"))
        root = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    grid: list[list[str]] = []
    for row in root.iter(f"{_XLSX_MAIN_NS}row"):
        cells: dict[int, str] = {}
        for cell in row.iter(f"{_XLSX_MAIN_NS}c"):
            cell_ref = cell.get("r")
            if cell_ref is None:
                raise ValueError(f"{path}: xlsx cell without reference")
            column = _column_index(cell_ref)
            cell_type = cell.get("t")
            if cell_type == "s":
                raw = cell.findtext(f"{_XLSX_MAIN_NS}v")
                if raw is None:
                    raise ValueError(f"{path}: shared-string cell {cell_ref} without value")
                cells[column] = shared[int(raw)]
            elif cell_type == "inlineStr":
                inline = cell.find(f"{_XLSX_MAIN_NS}is")
                if inline is None:
                    raise ValueError(f"{path}: inline-string cell {cell_ref} without value")
                text = "".join(node.text or "" for node in inline.iter(f"{_XLSX_MAIN_NS}t"))
                cells[column] = text
            else:
                cells[column] = cell.findtext(f"{_XLSX_MAIN_NS}v") or ""
        width = max(cells, default=-1) + 1
        grid.append([cells.get(column, "") for column in range(width)])
    if not grid:
        raise ValueError(f"{path}: empty worksheet")
    header = grid[0]
    if len(header) != len(CONCISION_COLUMNS) or set(header) != set(CONCISION_COLUMNS):
        raise ValueError(f"{path}: unexpected header {tuple(header)}")
    records: list[tuple[int, dict[str, Any]]] = []
    for line_number, row in enumerate(grid[1:], start=2):
        if len(row) != len(header) or all(not cell for cell in row):
            raise ValueError(f"{path}:{line_number}: malformed or blank row")
        records.append((line_number, dict(zip(header, row, strict=True))))
    return records


def normalize_concision_csv(path: Path) -> list[tuple[int, dict[str, Any]]]:
    """Strict CSV normalization path matching the XLSX reader output shape."""

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if fieldnames is None or tuple(sorted(fieldnames)) != tuple(sorted(CONCISION_COLUMNS)):
            raise ValueError(f"{path}: unexpected CSV header {fieldnames}")
        records: list[tuple[int, dict[str, Any]]] = []
        for line_number, row in enumerate(reader, start=2):
            if any(key is None for key in row) or any(value is None for value in row.values()):
                raise ValueError(f"{path}:{line_number}: malformed CSV row")
            records.append((line_number, dict(row)))
    if not records:
        raise ValueError(f"{path}: no CSV records found")
    return records


def parse_concise_references(value: str) -> tuple[str, ...]:
    """Parse the Python-style reference list stored in the ``concise`` column."""

    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError) as error:
        raise ValueError(f"invalid concise reference list {value!r}") from error
    if not isinstance(parsed, list) or not parsed:
        raise ValueError(f"concise must be a non-empty list, got {value!r}")
    return tuple(
        _require_non_empty_str(item, field="concise[]", where="concision row") for item in parsed
    )


def adapt_concision(
    records: list[tuple[int, dict[str, Any]]],
    *,
    source_revision: str,
    source_sha256: str,
    adapter_input_sha256: str | None = None,
    expected_rows: int | None = 536,
) -> tuple[list[NormalizedExternalCase], AdaptedManifest]:
    """Normalize Revision for Concision sentence pairs from XLSX or CSV rows."""

    benchmark_id = BenchmarkId.REVISION_FOR_CONCISION
    entry = find_registry_entry(benchmark_id)
    if expected_rows is None:
        expected_rows = entry.expected_source_rows
    _check_expected_rows(len(records), expected_rows, label="revision-for-concision source")
    cases: list[NormalizedExternalCase] = []
    seen_ids: set[str] = set()
    for position, (line_number, record) in enumerate(records):
        where = f"concision row {line_number}"
        _require_exact_fields(record, CONCISION_COLUMNS, where=where)
        wordy = _require_non_empty_str(record["wordy"], field="wordy", where=where)
        category = _require_non_empty_str(record["category"], field="category", where=where)
        cite = _require_non_empty_str(record["cite"], field="cite", where=where)
        link = _require_non_empty_str(record["link"], field="link", where=where)
        row_id = _require_non_empty_str(str(record["id"]), field="id", where=where)
        concise_raw = _require_non_empty_str(record["concise"], field="concise", where=where)
        references = parse_concise_references(concise_raw)
        case_id = f"{benchmark_id.value}-{row_id}"
        if case_id in seen_ids:
            raise ValueError(f"{where}: duplicate case id {case_id}")
        seen_ids.add(case_id)
        cases.append(
            _make_case(
                case_id=case_id,
                benchmark_id=benchmark_id,
                source_revision=source_revision,
                source_sha256=source_sha256,
                split="evaluation",
                task=category,
                source_index=position,
                instruction="Revise the sentence to be concise while preserving meaning.",
                input_text=wordy,
                reference="\n".join(references),
                attributes={"cite": cite, "link": link, "row_id": row_id},
            )
        )
    if not cases:
        raise ValueError("revision-for-concision produced no cases")
    if source_sha256 == entry.source.sha256:
        _check_expected_rows(
            len(cases), entry.expected_eligible_rows, label="revision-for-concision usable cases"
        )
    manifest = _build_manifest(
        entry=entry,
        source_sha256=source_sha256,
        split="evaluation",
        cases=cases,
        expected_source_rows=expected_rows,
        source_row_count=len(records),
        adapter_input_sha256=adapter_input_sha256,
    )
    return cases, manifest


# ---------------------------------------------------------------------------
# YapBench adapter
# ---------------------------------------------------------------------------

YAPBENCH_FIELDS = ("id", "category", "prompt", "baseline", "baseline_type", "domain", "notes")
YAPBENCH_CATEGORIES = frozenset({"A", "B", "C"})
YAPBENCH_BASELINE_TYPES = frozenset(
    {"acknowledgment", "clarification", "command", "output", "word"}
)
YAPBENCH_DOMAINS = frozenset(
    {
        "art",
        "astronomy",
        "biology",
        "chemistry",
        "economics",
        "everyday life",
        "general knowledge",
        "geography",
        "geology",
        "git",
        "history",
        "http",
        "java",
        "javascript",
        "linguistics",
        "literature",
        "math",
        "meta",
        "nonsense",
        "phatic",
        "physics",
        "python",
        "regex",
        "rust",
        "science",
        "shell",
        "sports",
        "sql",
    }
)


def adapt_yapbench(
    records: list[tuple[int, dict[str, Any]]],
    *,
    source_revision: str,
    source_sha256: str,
    adapter_input_sha256: str | None = None,
    expected_rows: int | None = 304,
) -> tuple[list[NormalizedExternalCase], AdaptedManifest]:
    """Normalize locally converted YapBench rows (normalized JSONL form)."""

    benchmark_id = BenchmarkId.YAPBENCH
    entry = find_registry_entry(benchmark_id)
    if expected_rows is None:
        expected_rows = entry.expected_source_rows
    _check_expected_rows(len(records), expected_rows, label="yapbench source")
    cases: list[NormalizedExternalCase] = []
    seen_ids: set[str] = set()
    excluded_empty_prompt = 0
    for position, (line_number, record) in enumerate(records):
        where = f"yapbench line {line_number}"
        _require_exact_fields(record, YAPBENCH_FIELDS, where=where)
        row_id = _require_non_empty_str(record["id"], field="id", where=where)
        category = _require_non_empty_str(record["category"], field="category", where=where)
        if category not in YAPBENCH_CATEGORIES:
            raise ValueError(f"{where}: invalid category {category!r}")
        prompt_value = record["prompt"]
        if not isinstance(prompt_value, str):
            raise ValueError(f"{where}: prompt must be a string")
        prompt = prompt_value
        baseline = _require_non_empty_str(record["baseline"], field="baseline", where=where)
        baseline_type = _require_non_empty_str(
            record["baseline_type"], field="baseline_type", where=where
        )
        if baseline_type not in YAPBENCH_BASELINE_TYPES:
            raise ValueError(f"{where}: invalid baseline_type {baseline_type!r}")
        domain = _require_non_empty_str(record["domain"], field="domain", where=where)
        if domain not in YAPBENCH_DOMAINS:
            raise ValueError(f"{where}: invalid domain {domain!r}")
        notes = _require_non_empty_str(record["notes"], field="notes", where=where)
        case_id = f"{benchmark_id.value}-{row_id}"
        if case_id in seen_ids:
            raise ValueError(f"{where}: duplicate case id {case_id}")
        seen_ids.add(case_id)
        if not prompt.strip():
            excluded_empty_prompt += 1
            continue
        cases.append(
            _make_case(
                case_id=case_id,
                benchmark_id=benchmark_id,
                source_revision=source_revision,
                source_sha256=source_sha256,
                split="evaluation",
                task=category,
                source_index=position,
                instruction="Respond to the prompt.",
                input_text=prompt,
                reference=baseline,
                attributes={
                    "baseline_type": baseline_type,
                    "domain": domain,
                    "notes": notes,
                    "row_id": row_id,
                },
            )
        )
    if not cases:
        raise ValueError("yapbench produced no cases")
    if source_sha256 == entry.source.sha256:
        _check_expected_rows(
            len(cases), entry.expected_eligible_rows, label="yapbench nonempty-prompt cases"
        )
    manifest = _build_manifest(
        entry=entry,
        source_sha256=source_sha256,
        split="evaluation",
        cases=cases,
        expected_source_rows=len(records),
        source_row_count=len(records),
        excluded_counts={"empty_prompt": excluded_empty_prompt},
        adapter_input_sha256=adapter_input_sha256,
    )
    return cases, manifest


# ---------------------------------------------------------------------------
# Predictions and candidate payloads
# ---------------------------------------------------------------------------


def select_case_suite(
    cases: list[NormalizedExternalCase], suite: Literal["development", "full"]
) -> list[NormalizedExternalCase]:
    """Select the frozen development screen or complete adapted suite."""

    if not cases:
        raise ValueError("case suite is empty")
    benchmark_ids = {case.benchmark_id for case in cases}
    if len(benchmark_ids) != 1:
        raise ValueError("case suite mixes benchmark IDs")
    selected = (
        [case for case in cases if case.split == "development"]
        if suite == "development"
        else list(cases)
    )
    if not selected:
        raise ValueError(f"case suite has no {suite} cases")
    return selected


def candidate_payload(cases: list[NormalizedExternalCase]) -> list[CandidatePayloadCase]:
    """Build candidate-generation payloads exposing only ID, instruction, input."""

    payloads = [
        CandidatePayloadCase(id=case.case_id, instruction=case.instruction, input=case.input_text)
        for case in cases
    ]
    identifiers = [payload.id for payload in payloads]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate IDs in candidate payload")
    return payloads


def load_normalized_cases(path: Path) -> list[NormalizedExternalCase]:
    cases: list[NormalizedExternalCase] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                cases.append(NormalizedExternalCase.model_validate_json(line))
            except Exception as error:
                raise ValueError(
                    f"{path}:{line_number}: invalid normalized case: {error}"
                ) from error
    identifiers = [case.case_id for case in cases]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"{path}: duplicate case IDs")
    if not cases:
        raise ValueError(f"{path}: no cases found")
    if len({case.benchmark_id for case in cases}) != 1:
        raise ValueError(f"{path}: mixed benchmark IDs")
    return cases


def validate_predictions(
    cases: list[NormalizedExternalCase],
    predictions: list[ExternalPrediction],
) -> PredictionSet:
    """Require exactly one nonempty prediction per case, no dup/missing/extra."""

    if not cases:
        raise ValueError("cannot validate predictions for an empty case suite")
    if len({case.benchmark_id for case in cases}) != 1:
        raise ValueError("prediction case suite mixes benchmark IDs")
    expected_ids = [case.case_id for case in cases]
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError("prediction case suite has duplicate case IDs")
    seen: set[str] = set()
    for prediction in predictions:
        if prediction.case_id in seen:
            raise ValueError(f"duplicate prediction for {prediction.case_id}")
        seen.add(prediction.case_id)
        if not prediction.output.strip():
            raise ValueError(f"empty prediction for {prediction.case_id}")
    missing = sorted(set(expected_ids) - seen)
    extra = sorted(seen - set(expected_ids))
    problems = []
    if missing:
        problems.append(f"missing predictions for {len(missing)} cases (e.g. {missing[:3]})")
    if extra:
        problems.append(f"extra predictions {extra[:3]}")
    if problems:
        raise ValueError("; ".join(problems))
    return PredictionSet(
        benchmark_id=cases[0].benchmark_id,
        case_count=len(cases),
        prediction_count=len(predictions),
    )


def load_predictions(path: Path) -> list[ExternalPrediction]:
    predictions: list[ExternalPrediction] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                predictions.append(ExternalPrediction.model_validate_json(line))
            except Exception as error:
                raise ValueError(f"{path}:{line_number}: invalid prediction: {error}") from error
    return predictions


# ---------------------------------------------------------------------------
# YapBench scoring (GoodProse compatibility variant)
# ---------------------------------------------------------------------------

_MARKDOWN_FENCES = re.compile(r"```[a-zA-Z0-9_-]*\n?")
_MARKDOWN_IMAGES = re.compile(r"!\[([^\]]*)\]\([^)\s]*\)")
_MARKDOWN_LINKS = re.compile(r"\[([^\]]*)\]\([^)\s]*\)")
_HTML_TAGS = re.compile(r"</?[a-zA-Z][^>]*>")
_HEADING_PREFIX = re.compile(r"(?m)^#{1,6}\s+")
_QUOTE_PREFIX = re.compile(r"(?m)^>\s?")
_LIST_PREFIX = re.compile(r"(?m)^[-+*]\s+")
_EMPHASIS = re.compile(r"[*_`~]{1,3}")
_WHITESPACE_RUNS = re.compile(r"\s+")


def visible_characters(text: str) -> int:
    """Frozen goodprose-visible-chars-v1 markdown normalization length."""

    value = _MARKDOWN_FENCES.sub("", text)
    value = _MARKDOWN_IMAGES.sub(r"\1", value)
    value = _MARKDOWN_LINKS.sub(r"\1", value)
    value = _HTML_TAGS.sub("", value)
    value = _HEADING_PREFIX.sub("", value)
    value = _QUOTE_PREFIX.sub("", value)
    value = _LIST_PREFIX.sub("", value)
    value = _EMPHASIS.sub("", value)
    value = _WHITESPACE_RUNS.sub(" ", value).strip()
    return len(value)


def _percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.floor(quantile * len(ordered))))
    return ordered[index]


def score_yapbench(
    cases: list[NormalizedExternalCase],
    predictions: list[ExternalPrediction],
    *,
    seed: int = YAP_BOOTSTRAP_SEED,
    resamples: int = YAP_RESAMPLES,
) -> YapBenchResult:
    """Deterministic YapScore/YapIndex plus stratified percentile intervals.

    Per-case score: max(0, visible(response chars) - visible(baseline chars)).
    Category score: median. YapIndex: uniform mean of category medians.
    Intervals: category-stratified bootstrap with a pinned seed.
    """

    if resamples <= 0:
        raise ValueError("resamples must be positive")
    if not cases or any(case.benchmark_id != BenchmarkId.YAPBENCH for case in cases):
        raise ValueError("YapBench scoring requires only YapBench cases")
    if any(not case.reference.strip() for case in cases):
        raise ValueError("YapBench scoring requires a nonempty baseline for every case")
    validate_predictions(cases, predictions)
    outputs_by_id = {prediction.case_id: prediction.output for prediction in predictions}
    scores_by_category: dict[str, list[float]] = {}
    for case in cases:
        delta = visible_characters(outputs_by_id[case.case_id]) - visible_characters(case.reference)
        scores_by_category.setdefault(case.task, []).append(max(0, delta))
    categories = sorted(scores_by_category)
    rng = random.Random(seed)
    raw_medians = {category: median(scores_by_category[category]) for category in categories}
    index_samples: list[float] = []
    category_samples: dict[str, list[float]] = {category: [] for category in categories}
    for _ in range(resamples):
        medians = []
        for category in categories:
            population = scores_by_category[category]
            sample = [population[rng.randrange(len(population))] for _ in population]
            sample_median = median(sample)
            medians.append(sample_median)
            category_samples[category].append(sample_median)
        index_samples.append(sum(medians) / len(medians))
    category_scores = tuple(
        YapCategoryScore(
            category=category,
            count=len(scores_by_category[category]),
            raw_median=round(raw_medians[category], 4),
            interval_low=round(_percentile(category_samples[category], 0.025), 4),
            interval_high=round(_percentile(category_samples[category], 0.975), 4),
        )
        for category in categories
    )
    yap_index = sum(raw_medians.values()) / len(raw_medians)
    return YapBenchResult(
        version=1,
        benchmark_id=BenchmarkId.YAPBENCH,
        metric_version=YAP_METRIC_VERSION,
        normalization_version=VISIBLE_CHARS_VERSION,
        seed=seed,
        resamples=resamples,
        case_count=len(cases),
        category_scores=category_scores,
        yap_index=round(yap_index, 4),
        yap_index_interval_low=round(_percentile(index_samples, 0.025), 4),
        yap_index_interval_high=round(_percentile(index_samples, 0.975), 4),
        disclaimer=(
            "Compatibility variant of the published deterministic YapBench metric. "
            "Measures visible verbosity only; never an executive-writing quality "
            "score and never a substitute for fidelity gates."
        ),
    )


# ---------------------------------------------------------------------------
# CLI surface (no downloads, no model/judge calls, never overwrites)
# ---------------------------------------------------------------------------


def cli_validate_registry() -> SourceRegistry:
    return build_source_registry()


def _ensure_absent(path: Path) -> None:
    if path.exists():
        raise ValueError(f"refusing to overwrite existing artifact: {path}")


def _load_external_records(path: Path) -> list[tuple[int, dict[str, Any]]]:
    return _read_jsonl_records(path)


def _adapt_dispatch(
    benchmark_id: BenchmarkId,
    records: list[tuple[int, dict[str, Any]]],
    source_revision: str,
    source_sha256: str,
) -> tuple[list[NormalizedExternalCase], AdaptedManifest]:
    if benchmark_id in WRITINGBENCH_DOMAINS:
        return adapt_writingbench(
            records,
            benchmark_id=benchmark_id,
            source_revision=source_revision,
            source_sha256=source_sha256,
            expected_domain_rows=None,
        )
    if benchmark_id == BenchmarkId.ITERATER_DIAGNOSTIC:
        return adapt_iterater(
            records,
            source_revision=source_revision,
            source_sha256=source_sha256,
        )
    if benchmark_id in (BenchmarkId.EDITEVAL_CLARITY, BenchmarkId.EDITEVAL_COHERENCE):
        return adapt_editeval(
            records,
            benchmark_id=benchmark_id,
            source_revision=source_revision,
            source_sha256=source_sha256,
        )
    if benchmark_id == BenchmarkId.YAPBENCH:
        return adapt_yapbench(
            records,
            source_revision=source_revision,
            source_sha256=source_sha256,
            expected_rows=None,
        )
    raise AssertionError(f"unhandled benchmark {benchmark_id}")


def cli_adapt(
    benchmark_id: str,
    source: Path,
    output_dir: Path,
    *,
    upstream_source: Path | None = None,
) -> AdaptedManifest:
    """Verify, adapt, and write local artifacts without ever overwriting."""

    resolved_id = BenchmarkId(benchmark_id)
    entry = find_registry_entry(resolved_id)
    pinned_hash = entry.source.sha256
    if pinned_hash is None:
        raise ValueError(f"{resolved_id.value}: no pinned sha256 available")
    normalized_derivative = resolved_id == BenchmarkId.YAPBENCH or (
        resolved_id == BenchmarkId.REVISION_FOR_CONCISION and source.suffix.lower() == ".csv"
    )
    if normalized_derivative:
        if upstream_source is None:
            raise ValueError(
                f"{resolved_id.value} normalized input requires --upstream-source "
                "pointing to the pinned external artifact"
            )
        digest = verify_source(upstream_source, pinned_hash, expected_bytes=entry.source.bytes)
        if not source.is_file():
            raise ValueError(f"normalized source file not found: {source}")
        adapter_input_sha256 = sha256_file(source)
    else:
        if upstream_source is not None:
            raise ValueError("--upstream-source is only valid for normalized derivative inputs")
        digest = verify_source(source, pinned_hash, expected_bytes=entry.source.bytes)
        adapter_input_sha256 = None
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_path = output_dir / f"{resolved_id.value}.cases.jsonl"
    manifest_path = output_dir / f"{resolved_id.value}.manifest.json"
    for artifact in (cases_path, manifest_path):
        _ensure_absent(artifact)
    if resolved_id == BenchmarkId.REVISION_FOR_CONCISION:
        if source.suffix.lower() == ".xlsx":
            records = read_concision_xlsx(source)
        elif source.suffix.lower() == ".csv":
            records = normalize_concision_csv(source)
        else:
            raise ValueError("revision-for-concision source must be .xlsx or .csv")
        cases, manifest = adapt_concision(
            records,
            source_revision=entry.source.revision,
            source_sha256=digest,
            adapter_input_sha256=adapter_input_sha256,
            expected_rows=None,
        )
    else:
        records = _load_external_records(source)
        if resolved_id == BenchmarkId.YAPBENCH:
            cases, manifest = adapt_yapbench(
                records,
                source_revision=entry.source.revision,
                source_sha256=digest,
                adapter_input_sha256=adapter_input_sha256,
                expected_rows=None,
            )
        else:
            cases, manifest = _adapt_dispatch(
                resolved_id,
                records,
                entry.source.revision,
                digest,
            )
    atomic_write(cases_path, serialize_jsonl(cases))
    atomic_write(
        manifest_path,
        (json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True) + "\n").encode(),
    )
    return manifest


def cli_emit_candidates(
    cases_path: Path,
    output_path: Path,
    *,
    suite: Literal["development", "full"],
) -> int:
    cases = select_case_suite(load_normalized_cases(cases_path), suite)
    _ensure_absent(output_path)
    atomic_write(output_path, serialize_jsonl(candidate_payload(cases)))
    return len(cases)


def cli_validate_predictions_file(
    cases_path: Path,
    predictions_path: Path,
    *,
    suite: Literal["development", "full"],
) -> PredictionSet:
    cases = select_case_suite(load_normalized_cases(cases_path), suite)
    predictions = load_predictions(predictions_path)
    return validate_predictions(cases, predictions)


def cli_score_yapbench(
    cases_path: Path,
    predictions_path: Path,
    result_path: Path,
    *,
    seed: int = YAP_BOOTSTRAP_SEED,
) -> YapBenchResult:
    entry = find_registry_entry(BenchmarkId.YAPBENCH)
    if entry.execution_status == ExecutionStatus.RIGHTS_BLOCKED:
        raise ValueError("yapbench execution is blocked until dataset rights are clarified")
    cases = load_normalized_cases(cases_path)
    if cases[0].benchmark_id != BenchmarkId.YAPBENCH:
        raise ValueError("score-yapbench requires adapted YapBench cases")
    predictions = load_predictions(predictions_path)
    result = score_yapbench(cases, predictions, seed=seed)
    _ensure_absent(result_path)
    atomic_write(
        result_path,
        (json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True) + "\n").encode(),
    )
    return result
