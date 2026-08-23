"""Compiler for the project-authored unified three-corpus architecture pilot.

The source records are supplied locally by the project (ignored file); this
module only validates and compiles them into lineage-isolated MLX train/valid/
test JSONL plus a compact committed provenance manifest. It never authors
records, performs network or model calls, or publishes source content.
"""

from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from goodprose.executive_writing.benchmark import BenchmarkCase, load_cases
from goodprose.executive_writing.smoke_data import ChatMessage, contamination_matches
from goodprose.jsonl import (
    atomic_write,
    canonical_json,
    load_jsonl,
    serialize_jsonl,
    sha256_bytes,
    sha256_file,
)

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

DATASET_ID = "goodprose-project-authored-unified-pilot-v1"
RIGHTS_STATUS = "training_permitted_project_owned_architecture_pilot"
INTENDED_USE = "unified_profile_conditioning_architecture_pilot_only"
CREATION_METHOD = "codex_project_authored_v1"
AUTHORING_SYSTEM = "goodprose-unified-pilot-content-v1"
CONTAMINATION_NGRAM_WORDS = 12
RECORD_SCHEMA_ID = "https://goodprose.local/schemas/unified-pilot-source-record-v1.json"

PROFILES: tuple[str, ...] = (
    "concise-decision-v1",
    "technical-explanatory-v1",
    "operational-update-v1",
)
GENRES: tuple[str, ...] = (
    "email",
    "memo",
    "strategy_document",
    "engineering_document",
    "blog_post",
    "short_post",
    "revision",
)
REJECTION_REASONS: tuple[str, ...] = (
    "unsupported_claim",
    "intent_change",
    "caveat_loss",
    "number_error",
    "attribution_error",
    "unnecessary_rewrite",
    "verbosity",
    "organization",
    "audience_mismatch",
)

ProfileId = Literal["concise-decision-v1", "technical-explanatory-v1", "operational-update-v1"]
GenreId = Literal[
    "email",
    "memo",
    "strategy_document",
    "engineering_document",
    "blog_post",
    "short_post",
    "revision",
]
RejectionReasonCode = Literal[
    "unsupported_claim",
    "intent_change",
    "caveat_loss",
    "number_error",
    "attribution_error",
    "unnecessary_rewrite",
    "verbosity",
    "organization",
    "audience_mismatch",
]
UnifiedSplitName = Literal["train", "valid", "test"]
UnifiedCorpusName = Literal["task_pair", "style_target", "preference_pair"]

BUILD_COMMAND = (
    "uv run python -m goodprose.executive_writing unified-data build "
    "--source <ignored-source-records.jsonl> "
    "--output-dir <ignored-derived-directory> "
    "--manifest data/executive-writing/unified-pilot-v1/manifest.json "
    "--b1-cases evals/executive-writing/goodprose-b1-v1/cases.jsonl"
)


class UnifiedStrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CompilationExpectations(UnifiedStrictModel):
    """Count expectations for compilation.

    The committed CLI path always uses `FROZEN_V1_EXPECTATIONS`; smaller
    expectations may be injected only by pure/compiler test functions.
    """

    record_count: int
    lineage_group_count: int
    split_counts: dict[UnifiedSplitName, int]
    corpus_counts: dict[UnifiedCorpusName, int]
    min_genre_count: int


FROZEN_V1_EXPECTATIONS = CompilationExpectations(
    record_count=90,
    lineage_group_count=30,
    split_counts={"train": 60, "valid": 15, "test": 15},
    corpus_counts={"task_pair": 54, "style_target": 22, "preference_pair": 14},
    min_genre_count=6,
)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def normalized_sha256(value: str) -> str:
    return sha256(normalize_text(value).encode("utf-8")).hexdigest()


class PreferenceTarget(UnifiedStrictModel):
    chosen: NonEmpty
    rejected: NonEmpty
    rejection_reasons: tuple[RejectionReasonCode, ...]

    @model_validator(mode="after")
    def validate_preference(self) -> Self:
        if self.chosen == self.rejected:
            raise ValueError("preference chosen and rejected responses must differ")
        if not self.rejection_reasons:
            raise ValueError("preference must declare at least one rejection reason")
        if len(set(self.rejection_reasons)) != len(self.rejection_reasons):
            raise ValueError("rejection reasons must be unique")
        return self


class SourceProvenance(UnifiedStrictModel):
    ownership: Literal["project_owned"]
    named_source: None = None
    external_source_used: Literal[False] = False
    personal_private_data: Literal[False] = False
    transformation_history: tuple[NonEmpty, ...]

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        if not self.transformation_history:
            raise ValueError("transformation history must be nonempty")
        return self


class SourceRecord(UnifiedStrictModel):
    version: Literal[1]
    example_id: NonEmpty
    lineage_group: NonEmpty
    split: UnifiedSplitName
    corpus: UnifiedCorpusName
    profile_id: ProfileId
    genre: GenreId
    creation_method: Literal["codex_project_authored_v1"]
    authoring_system: Literal["goodprose-unified-pilot-content-v1"]
    rights_status: Literal["training_permitted_project_owned_architecture_pilot"]
    intended_use: Literal["unified_profile_conditioning_architecture_pilot_only"]
    system_prompt: NonEmpty
    user_prompt: NonEmpty
    assistant_target: NonEmpty | None = None
    preference: PreferenceTarget | None = None
    system_sha256: Sha256
    user_sha256: Sha256
    target_sha256: Sha256
    rejected_sha256: Sha256 | None = None
    source_provenance: SourceProvenance

    @model_validator(mode="after")
    def validate_record(self) -> Self:
        if self.corpus == "preference_pair":
            if self.assistant_target is not None:
                raise ValueError(
                    f"{self.example_id}: preference records must not carry a standalone target"
                )
            if self.preference is None:
                raise ValueError(f"{self.example_id}: preference records require a preference")
            if self.rejected_sha256 != normalized_sha256(self.preference.rejected):
                raise ValueError(f"{self.example_id}: rejected hash mismatch")
            target_hash = normalized_sha256(self.preference.chosen)
        else:
            if self.preference is not None:
                raise ValueError(
                    f"{self.example_id}: only preference records may carry a preference object"
                )
            if self.assistant_target is None:
                raise ValueError(
                    f"{self.example_id}: task/style records require an assistant target"
                )
            if self.rejected_sha256 is not None:
                raise ValueError(f"{self.example_id}: rejected hash requires a preference record")
            target_hash = normalized_sha256(self.assistant_target)
        if self.target_sha256 != target_hash:
            raise ValueError(f"{self.example_id}: target hash mismatch")
        if self.system_sha256 != normalized_sha256(self.system_prompt):
            raise ValueError(f"{self.example_id}: system prompt hash mismatch")
        if self.user_sha256 != normalized_sha256(self.user_prompt):
            raise ValueError(f"{self.example_id}: user prompt hash mismatch")
        return self


class UnifiedChatMetadata(UnifiedStrictModel):
    version: Literal[1]
    example_id: NonEmpty
    dataset_id: Literal["goodprose-project-authored-unified-pilot-v1"]
    split: UnifiedSplitName
    lineage_group: NonEmpty
    corpus: UnifiedCorpusName
    profile_id: ProfileId
    genre: GenreId
    creation_method: Literal["codex_project_authored_v1"]
    authoring_system: Literal["goodprose-unified-pilot-content-v1"]
    rights_status: Literal["training_permitted_project_owned_architecture_pilot"]
    intended_use: Literal["unified_profile_conditioning_architecture_pilot_only"]
    system_sha256: Sha256
    user_sha256: Sha256
    target_sha256: Sha256
    rejected_sha256: Sha256 | None = None
    rejected_response: NonEmpty | None = None
    rejection_reasons: tuple[RejectionReasonCode, ...] = ()
    source_provenance: SourceProvenance
    transformation_history: tuple[NonEmpty, ...]

    @model_validator(mode="after")
    def validate_metadata(self) -> Self:
        if self.transformation_history != self.source_provenance.transformation_history:
            raise ValueError(f"{self.example_id}: transformation history does not match provenance")
        if self.corpus == "preference_pair":
            if self.rejected_response is None or self.rejected_sha256 is None:
                raise ValueError(
                    f"{self.example_id}: preference metadata must preserve the rejected response"
                )
            if not self.rejection_reasons:
                raise ValueError(f"{self.example_id}: preference metadata requires reasons")
            if normalized_sha256(self.rejected_response) != self.rejected_sha256:
                raise ValueError(f"{self.example_id}: preserved rejected response hash mismatch")
        else:
            if self.rejected_response is not None or self.rejected_sha256 is not None:
                raise ValueError(
                    f"{self.example_id}: non-preference metadata must not carry rejection fields"
                )
            if self.rejection_reasons:
                raise ValueError(
                    f"{self.example_id}: non-preference metadata must not carry rejection reasons"
                )
        return self


class UnifiedChatRecord(UnifiedStrictModel):
    messages: tuple[ChatMessage, ChatMessage, ChatMessage]
    metadata: UnifiedChatMetadata

    @model_validator(mode="after")
    def validate_chat_and_hashes(self) -> Self:
        if tuple(message.role for message in self.messages) != ("system", "user", "assistant"):
            raise ValueError("chat records must contain system, user, assistant in order")
        checks = (
            ("system", self.messages[0].content, self.metadata.system_sha256),
            ("user", self.messages[1].content, self.metadata.user_sha256),
            ("target", self.messages[2].content, self.metadata.target_sha256),
        )
        for label, content, expected in checks:
            if normalized_sha256(content) != expected:
                raise ValueError(f"{self.metadata.example_id}: {label} hash mismatch")
        return self


def build_chat_record(record: SourceRecord) -> UnifiedChatRecord:
    """Materialize one MLX chat row without dropping any source information."""

    if record.corpus == "preference_pair":
        assert record.preference is not None
        assistant_content = record.preference.chosen
        rejected_response: str | None = record.preference.rejected
        reasons: tuple[RejectionReasonCode, ...] = record.preference.rejection_reasons
    else:
        assert record.assistant_target is not None
        assistant_content = record.assistant_target
        rejected_response = None
        reasons = ()
    return UnifiedChatRecord(
        messages=(
            ChatMessage(role="system", content=record.system_prompt),
            ChatMessage(role="user", content=record.user_prompt),
            ChatMessage(role="assistant", content=assistant_content),
        ),
        metadata=UnifiedChatMetadata(
            version=record.version,
            example_id=record.example_id,
            dataset_id=DATASET_ID,
            split=record.split,
            lineage_group=record.lineage_group,
            corpus=record.corpus,
            profile_id=record.profile_id,
            genre=record.genre,
            creation_method=record.creation_method,
            authoring_system=record.authoring_system,
            rights_status=record.rights_status,
            intended_use=record.intended_use,
            system_sha256=record.system_sha256,
            user_sha256=record.user_sha256,
            target_sha256=record.target_sha256,
            rejected_sha256=record.rejected_sha256,
            rejected_response=rejected_response,
            rejection_reasons=reasons,
            source_provenance=record.source_provenance,
            transformation_history=record.source_provenance.transformation_history,
        ),
    )


def source_record_schema() -> dict[str, Any]:
    """Return the canonical public source schema represented by SourceRecord."""

    return {"$id": RECORD_SCHEMA_ID, **SourceRecord.model_json_schema()}


def _exact_ratio_evidence(counts: dict[str, int], denominator: int) -> dict[str, object]:
    return {key: {"numerator": count, "denominator": denominator} for key, count in counts.items()}


def _refuse_existing_outputs(output_dir: Path, manifest_path: Path) -> None:
    targets = [output_dir / f"{split}.jsonl" for split in ("train", "valid", "test")]
    targets.append(output_dir / "preferences.jsonl")
    targets.append(manifest_path)
    existing = [str(path) for path in targets if path.exists()]
    if existing:
        raise ValueError(f"refusing to overwrite existing artifacts: {', '.join(existing)}")


def _validate_structure(
    records: list[SourceRecord], expectations: CompilationExpectations
) -> dict[str, object]:
    total = len(records)
    if total != expectations.record_count:
        raise ValueError(f"expected exactly {expectations.record_count} records, found {total}")

    ids = [record.example_id for record in records]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        raise ValueError(f"duplicate example IDs: {', '.join(duplicates)}")

    cells = [
        (record.lineage_group, record.profile_id, record.genre, record.corpus) for record in records
    ]
    duplicate_cells = {cell for cell in cells if cells.count(cell) > 1}
    if duplicate_cells:
        raise ValueError(
            f"duplicate lineage/profile/genre/corpus cells: {sorted(duplicate_cells)[0]}"
        )

    for split_name in ("train", "valid", "test"):
        split_records = [record for record in records if record.split == split_name]
        prompts = [normalize_text(record.user_prompt) for record in split_records]
        duplicated_prompts = {prompt for prompt in prompts if prompts.count(prompt) > 1}
        if duplicated_prompts:
            raise ValueError(
                f"duplicate normalized user prompts within split {split_name}: "
                f"{sorted(duplicated_prompts)[0]}"
            )

    lineages = {record.lineage_group for record in records}
    if len(lineages) != expectations.lineage_group_count:
        raise ValueError(
            f"expected exactly {expectations.lineage_group_count} lineage groups, "
            f"found {len(lineages)}"
        )
    lineage_splits: dict[str, set[str]] = {}
    for record in records:
        lineage_splits.setdefault(record.lineage_group, set()).add(record.split)
    crossing = sorted(lineage for lineage, splits in lineage_splits.items() if len(splits) != 1)
    if crossing:
        raise ValueError(f"lineage groups cross splits: {', '.join(crossing)}")

    actual_split_counts = {
        split_name: sum(1 for record in records if record.split == split_name)
        for split_name in ("train", "valid", "test")
    }
    if actual_split_counts != expectations.split_counts:
        raise ValueError(
            f"split counts {actual_split_counts} do not match expectations "
            f"{expectations.split_counts}"
        )

    corpora = ("task_pair", "style_target", "preference_pair")
    actual_corpus_counts = {
        corpus: sum(1 for record in records if record.corpus == corpus) for corpus in corpora
    }
    if actual_corpus_counts != expectations.corpus_counts:
        raise ValueError(
            f"corpus counts {actual_corpus_counts} do not match expectations "
            f"{expectations.corpus_counts}"
        )

    per_split_corpus_counts: dict[str, dict[str, int]] = {}
    for split_name in ("train", "valid", "test"):
        split_records = [record for record in records if record.split == split_name]
        counts = {
            corpus: sum(1 for record in split_records if record.corpus == corpus)
            for corpus in corpora
        }
        per_split_corpus_counts[split_name] = counts
        present = {corpus for corpus, count in counts.items() if count > 0}
        if split_name == "train":
            missing = sorted(set(corpora) - present)
            if missing:
                raise ValueError(f"train split is missing corpora: {', '.join(missing)}")
        elif split_records:
            missing = sorted({"task_pair", "style_target"} - present)
            if missing:
                raise ValueError(f"{split_name} split is missing corpora: {', '.join(missing)}")

    profiles_present = {record.profile_id for record in records}
    if profiles_present != set(PROFILES):
        raise ValueError(f"profile coverage incomplete: {sorted(profiles_present)}")
    train_profiles = {record.profile_id for record in records if record.split == "train"}
    if train_profiles != set(PROFILES):
        raise ValueError("every profile must occur in train")
    profile_counts = {
        profile: sum(1 for record in records if record.profile_id == profile)
        for profile in PROFILES
    }
    if max(profile_counts.values()) - min(profile_counts.values()) > 1:
        raise ValueError(f"pathological profile imbalance: {profile_counts}")

    genres_present = {record.genre for record in records}
    if genres_present != set(GENRES):
        raise ValueError(f"genre coverage incomplete: {sorted(genres_present)}")
    train_genres = {record.genre for record in records if record.split == "train"}
    if train_genres != set(GENRES):
        raise ValueError("every genre must occur in train")
    genre_counts = {
        genre: sum(1 for record in records if record.genre == genre) for genre in GENRES
    }
    below_minimum = sorted(
        genre for genre, count in genre_counts.items() if count < expectations.min_genre_count
    )
    if below_minimum:
        raise ValueError(
            f"genres below minimum count {expectations.min_genre_count}: {', '.join(below_minimum)}"
        )

    ratios = {corpus: (actual_corpus_counts[corpus] / total) for corpus in corpora}
    ratio_fractions = _exact_ratio_evidence(actual_corpus_counts, total)
    per_split_ratios: dict[str, dict[str, float]] = {}
    per_split_ratio_fractions: dict[str, dict[str, object]] = {}
    for split_name, counts in per_split_corpus_counts.items():
        split_size = sum(counts.values())
        per_split_ratios[split_name] = (
            {corpus: (count / split_size) for corpus, count in counts.items()} if split_size else {}
        )
        per_split_ratio_fractions[split_name] = (
            _exact_ratio_evidence(counts, split_size) if split_size else {}
        )
    return {
        "record_count": total,
        "lineage_group_count": len(lineages),
        "split_counts": actual_split_counts,
        "corpus_counts": actual_corpus_counts,
        "corpus_ratios": ratios,
        "corpus_ratio_fractions": ratio_fractions,
        "per_split_corpus_counts": per_split_corpus_counts,
        "per_split_corpus_ratios": per_split_ratios,
        "per_split_corpus_ratio_fractions": per_split_ratio_fractions,
        "profile_counts": profile_counts,
        "genre_counts": genre_counts,
    }


def _validate_b1_separation(
    chat_rows: list[UnifiedChatRecord], b1_cases: list[BenchmarkCase]
) -> dict[str, object]:
    b1_lineages = {case.provenance.lineage_group for case in b1_cases}
    shared_lineages = sorted({row.metadata.lineage_group for row in chat_rows} & b1_lineages)
    if shared_lineages:
        raise ValueError(f"pilot and B1 lineages overlap: {', '.join(shared_lineages)}")

    candidate_texts: list[str] = []
    for row in chat_rows:
        candidate_texts.extend(message.content for message in row.messages[1:])
        if row.metadata.rejected_response is not None:
            candidate_texts.append(row.metadata.rejected_response)
    reference_texts = [case.input.source_material for case in b1_cases]

    matches = contamination_matches(
        candidate_texts, reference_texts, ngram_words=CONTAMINATION_NGRAM_WORDS
    )
    if matches:
        examples = [" ".join(value) for value in sorted(matches)[:3]]
        raise ValueError(f"pilot data shares {CONTAMINATION_NGRAM_WORDS}-grams with B1: {examples}")

    reference_hashes = {normalized_sha256(value) for value in reference_texts}
    candidate_hashes = {normalized_sha256(value) for value in candidate_texts}
    if reference_hashes & candidate_hashes:
        raise ValueError("pilot data contains exact normalized B1 content")

    return {
        "method": "lineage disjointness plus normalized exact hash plus exact contiguous n-gram",
        "reference_benchmark": "goodprose-b1-v1",
        "reference_case_count": len(b1_cases),
        "ngram_words": CONTAMINATION_NGRAM_WORDS,
        "exact_hash_matches": 0,
        "ngram_matches": 0,
        "shared_lineages": 0,
        "status": "pass",
    }


def compile_unified_dataset(
    *,
    source_path: Path,
    output_dir: Path,
    manifest_path: Path,
    b1_cases_path: Path,
    expectations: CompilationExpectations = FROZEN_V1_EXPECTATIONS,
) -> dict[str, object]:
    """Validate the ignored source file and compile deterministic MLX JSONL."""

    _refuse_existing_outputs(output_dir, manifest_path)
    records = load_jsonl(source_path, SourceRecord)
    evidence = _validate_structure(records, expectations)

    chat_rows = [build_chat_record(record) for record in records]
    b1_cases = load_cases(b1_cases_path)
    contamination = _validate_b1_separation(chat_rows, b1_cases)

    rows_by_split: dict[str, list[UnifiedChatRecord]] = {"train": [], "valid": [], "test": []}
    for row in chat_rows:
        rows_by_split[row.metadata.split].append(row)
    payloads = {
        split_name: serialize_jsonl(rows_by_split[split_name])
        for split_name in sorted(rows_by_split)
    }
    payloads["preferences"] = serialize_jsonl(
        [row for row in chat_rows if row.metadata.corpus == "preference_pair"]
    )
    split_hashes = {name: sha256_bytes(payload) for name, payload in sorted(payloads.items())}
    dataset_digest = sha256()
    for name, split_hash in sorted(split_hashes.items()):
        dataset_digest.update(f"{name}:{split_hash}\n".encode())

    schema_payload = (canonical_json(source_record_schema()) + "\n").encode()
    manifest: dict[str, object] = {
        "version": 1,
        "dataset_id": DATASET_ID,
        "status": "unified_profile_conditioning_architecture_pilot_only",
        "creation_method": CREATION_METHOD,
        "authoring_system": AUTHORING_SYSTEM,
        "rights_status": RIGHTS_STATUS,
        "intended_use": INTENDED_USE,
        **evidence,
        "split_sha256": split_hashes,
        "dataset_sha256": dataset_digest.hexdigest(),
        "source_records_sha256": sha256_file(source_path),
        "record_schema_sha256": sha256_bytes(schema_payload),
        "compiler_sha256": sha256_file(Path(__file__)),
        "b1_cases_sha256": sha256_file(b1_cases_path),
        "contamination_check": contamination,
        "build_command": BUILD_COMMAND,
        "limitations": [
            (
                "Project-authored synthetic records pilot architecture plumbing only and cannot "
                "establish model quality."
            ),
            (
                "The data is not authentic human writing, not named-source data, and not final "
                "model-quality evidence."
            ),
            "Authorization covers this project's pilot only; external redistribution is forbidden.",
            (
                "Lineage isolation means related records share one split; ratios are fixed by the "
                "frozen v1 expectations."
            ),
        ],
    }
    for split_name, payload in payloads.items():
        atomic_write(output_dir / f"{split_name}.jsonl", payload)
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    atomic_write(manifest_path, manifest_bytes)
    return manifest
