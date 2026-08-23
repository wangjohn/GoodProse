"""Deterministic, project-owned data for the first-evidence MLX smoke run."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from goodprose.executive_writing.benchmark import BenchmarkCase, load_cases
from goodprose.jsonl import atomic_write, canonical_json, serialize_jsonl, sha256_bytes, sha256_file

NonEmpty = Annotated[str, StringConstraints(min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
SmokeOutputFormat = Literal["email", "memo", "document", "short_post"]

DATASET_ID = "goodprose-project-authored-smoke-v1"
AUTHORING_TIMESTAMP = "2026-08-23T04:58:03Z"
CONTAMINATION_NGRAM_WORDS = 12
SYSTEM_PROMPT = """You are GoodProse, an executive-writing system.
Use only facts supported by the supplied source. Preserve every number, date,
attribution, uncertainty, caveat, and requested action. Lead with the decision
or purpose, use direct high-information-density prose, and do not imitate a
named writer. Output only the finished artifact."""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SmokeSplit(StrEnum):
    TRAIN = "train"
    VALID = "valid"
    TEST = "test"


class ChatMessage(StrictModel):
    role: Literal["system", "user", "assistant"]
    content: NonEmpty


class SmokeMetadata(StrictModel):
    version: Literal[1]
    example_id: NonEmpty
    dataset_id: Literal["goodprose-project-authored-smoke-v1"]
    split: SmokeSplit
    lineage_group: NonEmpty
    corpus: Literal["task_pairs"]
    profile_id: Literal["executive-house-v1"]
    output_format: SmokeOutputFormat
    creation_method: Literal["deterministic_project_authored_template"]
    authoring_system: Literal["goodprose-smoke-template-v1"]
    rights_status: Literal["training_permitted_project_owned_smoke"]
    intended_use: Literal["pipeline_smoke_test_only"]
    source_sha256: Sha256
    target_sha256: Sha256


class SmokeRecord(StrictModel):
    messages: tuple[ChatMessage, ChatMessage, ChatMessage]
    metadata: SmokeMetadata

    @model_validator(mode="after")
    def validate_chat_and_hashes(self) -> Self:
        if tuple(message.role for message in self.messages) != ("system", "user", "assistant"):
            raise ValueError("smoke chats must contain system, user, assistant in order")
        source_hash = _content_sha256(self.messages[1].content)
        target_hash = _content_sha256(self.messages[2].content)
        if source_hash != self.metadata.source_sha256:
            raise ValueError(f"source hash mismatch for {self.metadata.example_id}")
        if target_hash != self.metadata.target_sha256:
            raise ValueError(f"target hash mismatch for {self.metadata.example_id}")
        return self


class Scenario(StrictModel):
    id: NonEmpty
    project: NonEmpty
    milestone: NonEmpty
    completed_on: NonEmpty
    result: NonEmpty
    boundary: NonEmpty
    action: NonEmpty
    owner: NonEmpty
    deadline: NonEmpty
    audience: NonEmpty


SCENARIOS = (
    Scenario(
        id="orchid-intake",
        project="Orchid intake pilot",
        milestone="the new intake form was enabled for the partner-support queue",
        completed_on="January 12",
        result="median routing time fell from 19 minutes to 11 minutes across 64 requests",
        boundary="the trial covered weekday requests only, so weekend performance is unknown",
        action="extend the trial for two weeks before deciding on a broader rollout",
        owner="Support Operations",
        deadline="January 19",
        audience="customer-support leadership",
    ),
    Scenario(
        id="cedar-labels",
        project="Cedar label trial",
        milestone="two packing stations began using the revised return labels",
        completed_on="February 4",
        result="unreadable-label reports dropped from 17 to 6 during the 10-day trial",
        boundary="the sample excludes international returns, so that workflow remains untested",
        action="add one international station before considering network-wide adoption",
        owner="Fulfillment Systems",
        deadline="February 13",
        audience="operations leadership",
    ),
    Scenario(
        id="lumen-glossary",
        project="Lumen glossary release",
        milestone="the shared product glossary was added to the French localization workflow",
        completed_on="March 7",
        result="terminology corrections declined from 31 to 12 across 420 translated strings",
        boundary="legal notices were outside the trial and still require specialist review",
        action="test the glossary in Spanish while retaining legal review",
        owner="Localization",
        deadline="March 21",
        audience="product and localization leaders",
    ),
    Scenario(
        id="mariner-captions",
        project="Mariner caption pipeline",
        milestone="the revised caption review queue began serving recorded training sessions",
        completed_on="April 9",
        result="median review time decreased from 28 hours to 16 hours for 38 recordings",
        boundary="live-event captions were not included and no live accuracy claim is supported",
        action="run a separate live-event test before changing the event workflow",
        owner="Learning Media",
        deadline="April 18",
        audience="learning and accessibility leadership",
    ),
    Scenario(
        id="northstar-search",
        project="Northstar documentation search",
        milestone="the revised index began serving the internal troubleshooting library",
        completed_on="May 6",
        result="successful first-query searches increased from 58% to 71% across 310 sessions",
        boundary=(
            "the measurement covers English queries only and does not establish "
            "multilingual performance"
        ),
        action="evaluate German queries before expanding the index configuration",
        owner="Developer Experience",
        deadline="May 20",
        audience="engineering leadership",
    ),
    Scenario(
        id="quartz-suppliers",
        project="Quartz supplier portal",
        milestone="the document checklist was enabled for a limited supplier cohort",
        completed_on="June 11",
        result="complete first submissions rose from 44% to 63% among 27 suppliers",
        boundary=(
            "all participants were domestic suppliers, so cross-border requirements remain untested"
        ),
        action="add five cross-border suppliers before selecting a permanent checklist",
        owner="Procurement Operations",
        deadline="June 25",
        audience="finance and procurement leadership",
    ),
    Scenario(
        id="rivulet-scanners",
        project="Rivulet inventory scanner",
        milestone="the revised scan sequence was deployed in one laboratory storeroom",
        completed_on="July 8",
        result="median shelf-audit time fell from 46 minutes to 29 minutes over 22 audits",
        boundary="controlled substances were excluded and must remain on the existing process",
        action="repeat the trial in a second storeroom without changing controlled-item handling",
        owner="Laboratory Operations",
        deadline="July 22",
        audience="research operations leadership",
    ),
    Scenario(
        id="solstice-resets",
        project="Solstice demo resets",
        milestone="automated environment resets were enabled for the sales-engineering sandbox",
        completed_on="August 5",
        result="failed morning demos declined from 9 to 3 across 76 scheduled sessions",
        boundary="the automation does not restore third-party integrations after credential expiry",
        action="add an integration preflight before expanding the reset schedule",
        owner="Sales Engineering",
        deadline="August 14",
        audience="revenue and engineering leadership",
    ),
    Scenario(
        id="tamarind-taxonomy",
        project="Tamarind support taxonomy",
        milestone="the simplified issue categories were introduced to the hardware-help queue",
        completed_on="September 10",
        result="correct first classification increased from 62% to 75% across 188 tickets",
        boundary="billing questions were excluded and should not be assigned using this taxonomy",
        action="review misclassified hardware tickets before adding another queue",
        owner="Support Quality",
        deadline="September 24",
        audience="support and product leadership",
    ),
    Scenario(
        id="umber-chargers",
        project="Umber charger inspection",
        milestone="the mobile inspection checklist was activated for one vehicle depot",
        completed_on="October 3",
        result="incomplete inspections fell from 14% to 5% across 96 charging sessions",
        boundary="winter conditions were not observed, so cold-weather reliability is unknown",
        action="continue through the first cold-weather week before changing depot policy",
        owner="Fleet Reliability",
        deadline="October 17",
        audience="facilities and fleet leadership",
    ),
    Scenario(
        id="verdant-exports",
        project="Verdant analytics export",
        milestone="the queued export path was enabled for three research workspaces",
        completed_on="November 6",
        result="timeouts declined from 23 to 4 across 140 export requests",
        boundary="exports above 20 gigabytes were excluded and retain the manual workflow",
        action="measure one larger workspace before changing the default export path",
        owner="Data Platform",
        deadline="November 19",
        audience="data and research leadership",
    ),
    Scenario(
        id="willow-reviews",
        project="Willow grant review queue",
        milestone="the conflict-check step was added to the internal grant-review workflow",
        completed_on="December 2",
        result="late conflict disclosures declined from 8 to 2 across 51 applications",
        boundary="external reviewers were not included and remain on the current process",
        action="invite a small external-reviewer cohort before adopting the step broadly",
        owner="Research Programs",
        deadline="December 16",
        audience="research and legal leadership",
    ),
)


def _content_sha256(value: str) -> str:
    return sha256(_normalize(value).encode("utf-8")).hexdigest()


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _words(value: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9]+(?:\.[0-9]+)?%?", value.casefold()))


def _ngrams(value: str, size: int) -> set[tuple[str, ...]]:
    words = _words(value)
    return {words[index : index + size] for index in range(len(words) - size + 1)}


def contamination_matches(
    candidate_texts: Iterable[str], reference_texts: Iterable[str], *, ngram_words: int
) -> set[tuple[str, ...]]:
    """Return exact normalized word n-grams shared by candidate and reference text."""

    reference_ngrams: set[tuple[str, ...]] = set()
    for text in reference_texts:
        reference_ngrams.update(_ngrams(text, ngram_words))
    matches: set[tuple[str, ...]] = set()
    for text in candidate_texts:
        matches.update(_ngrams(text, ngram_words) & reference_ngrams)
    return matches


def _scenario_split(index: int) -> SmokeSplit:
    if index < 8:
        return SmokeSplit.TRAIN
    if index < 10:
        return SmokeSplit.VALID
    return SmokeSplit.TEST


def _source_notes(scenario: Scenario) -> str:
    return (
        f"Project: {scenario.project}. Milestone: {scenario.milestone} on "
        f"{scenario.completed_on}. Observed result: {scenario.result}. Boundary: "
        f"{scenario.boundary}. Proposed next step: {scenario.action}. Owner: "
        f"{scenario.owner}. Decision or update due: {scenario.deadline}."
    )


def _prompt(scenario: Scenario, output_format: str, instruction: str) -> str:
    return f"""Output format: {output_format}
Audience: {scenario.audience}
Objective: {instruction}
Profile: executive-house-v1
Constraints:
- Preserve the measured result and its scope boundary.
- Do not turn the proposal into an approved decision.
- Name the owner and deadline.

Source material:
{_source_notes(scenario)}"""


def _variant_payloads(scenario: Scenario) -> tuple[tuple[SmokeOutputFormat, str, str], ...]:
    email = f"""Subject: {scenario.project}: bounded next step

{scenario.milestone.capitalize()} on {scenario.completed_on}. {scenario.result.capitalize()}.

This result is limited: {scenario.boundary}. I recommend that we
{scenario.action}. This is a proposal, not an approved rollout.

{scenario.owner} will return the decision update by {scenario.deadline}."""
    memo = f"""# {scenario.project}: decision brief

## Recommendation

{scenario.action.capitalize()}. This remains a proposal.

## Evidence

On {scenario.completed_on}, {scenario.milestone}. {scenario.result.capitalize()}.

## Boundary and next step

{scenario.boundary.capitalize()}. {scenario.owner} owns the follow-up and will
report by {scenario.deadline}."""
    document = f"""# {scenario.project}: measured trial note

## Change observed

On {scenario.completed_on}, {scenario.milestone}. The observed result was that {scenario.result}.

## Interpretation limit

The evidence does not support a broad conclusion because {scenario.boundary}.

## Proposed follow-up

The proposed action is to {scenario.action}. {scenario.owner} owns the work,
with a decision update due {scenario.deadline}."""
    short_post = (
        f"{scenario.project}: {scenario.result}. The evidence is bounded because "
        f"{scenario.boundary}. Proposed next step: {scenario.action}. {scenario.owner} "
        f"will report by {scenario.deadline}; no broader rollout is approved."
    )
    return (
        ("email", "write a concise status email that recommends the bounded next step", email),
        ("memo", "write a decision-first internal memo with clear headings", memo),
        (
            "document",
            "write a compact engineering-style trial note that separates evidence from proposal",
            document,
        ),
        ("short_post", "write a short internal update without losing the caveat", short_post),
    )


def build_smoke_records() -> dict[SmokeSplit, list[SmokeRecord]]:
    records = {split: [] for split in SmokeSplit}
    for scenario_index, scenario in enumerate(SCENARIOS):
        split = _scenario_split(scenario_index)
        for variant_index, (output_format, instruction, target) in enumerate(
            _variant_payloads(scenario), start=1
        ):
            user_prompt = _prompt(scenario, output_format, instruction)
            record = SmokeRecord(
                messages=(
                    ChatMessage(role="system", content=SYSTEM_PROMPT),
                    ChatMessage(role="user", content=user_prompt),
                    ChatMessage(role="assistant", content=target),
                ),
                metadata=SmokeMetadata(
                    version=1,
                    example_id=f"smoke-v1-{scenario.id}-{variant_index:02d}",
                    dataset_id=DATASET_ID,
                    split=split,
                    lineage_group=f"smoke-v1-{scenario.id}",
                    corpus="task_pairs",
                    profile_id="executive-house-v1",
                    output_format=output_format,
                    creation_method="deterministic_project_authored_template",
                    authoring_system="goodprose-smoke-template-v1",
                    rights_status="training_permitted_project_owned_smoke",
                    intended_use="pipeline_smoke_test_only",
                    source_sha256=_content_sha256(user_prompt),
                    target_sha256=_content_sha256(target),
                ),
            )
            records[split].append(record)
    return records


def _validate_records(
    records_by_split: dict[SmokeSplit, list[SmokeRecord]], b1_cases: list[BenchmarkCase]
) -> dict[str, object]:
    records = [record for split in SmokeSplit for record in records_by_split[split]]
    ids = [record.metadata.example_id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("smoke example IDs must be unique")

    lineage_splits: dict[str, set[SmokeSplit]] = {}
    for record in records:
        lineage_splits.setdefault(record.metadata.lineage_group, set()).add(record.metadata.split)
    crossing = sorted(lineage for lineage, splits in lineage_splits.items() if len(splits) != 1)
    if crossing:
        raise ValueError(f"smoke lineages cross splits: {', '.join(crossing)}")

    b1_lineages = {case.provenance.lineage_group for case in b1_cases}
    shared_lineages = sorted(set(lineage_splits) & b1_lineages)
    if shared_lineages:
        raise ValueError(f"smoke and B1 lineages overlap: {', '.join(shared_lineages)}")

    candidate_texts = [message.content for record in records for message in record.messages[1:]]
    reference_texts = [case.input.source_material for case in b1_cases]
    matches = contamination_matches(
        candidate_texts, reference_texts, ngram_words=CONTAMINATION_NGRAM_WORDS
    )
    if matches:
        examples = [" ".join(value) for value in sorted(matches)[:3]]
        raise ValueError(f"smoke data shares {CONTAMINATION_NGRAM_WORDS}-grams with B1: {examples}")

    reference_hashes = {_content_sha256(value) for value in reference_texts}
    candidate_hashes = {_content_sha256(value) for value in candidate_texts}
    if reference_hashes & candidate_hashes:
        raise ValueError("smoke data contains exact normalized B1 content")

    return {
        "method": "normalized exact hash plus exact contiguous word n-gram",
        "reference_benchmark": "goodprose-b1-v1",
        "reference_case_count": len(b1_cases),
        "ngram_words": CONTAMINATION_NGRAM_WORDS,
        "exact_hash_matches": 0,
        "ngram_matches": 0,
        "shared_lineages": 0,
        "status": "pass",
    }


def compile_smoke_dataset(
    *, output_dir: Path, manifest_path: Path, b1_cases_path: Path
) -> dict[str, object]:
    """Build ignored MLX JSONL and a compact committed provenance manifest."""

    records_by_split = build_smoke_records()
    b1_cases = load_cases(b1_cases_path)
    contamination = _validate_records(records_by_split, b1_cases)

    payloads = {split.value: serialize_jsonl(records_by_split[split]) for split in SmokeSplit}
    for split_name, payload in payloads.items():
        atomic_write(output_dir / f"{split_name}.jsonl", payload)

    split_hashes = {name: sha256_bytes(payload) for name, payload in sorted(payloads.items())}
    split_counts = {split.value: len(records_by_split[split]) for split in SmokeSplit}
    schema_payload = (canonical_json(SmokeRecord.model_json_schema()) + "\n").encode()
    dataset_digest = sha256()
    for split_name, split_hash in sorted(split_hashes.items()):
        dataset_digest.update(f"{split_name}:{split_hash}\n".encode())

    format_counts = Counter(
        record.metadata.output_format for split in SmokeSplit for record in records_by_split[split]
    )
    manifest: dict[str, object] = {
        "version": 1,
        "dataset_id": DATASET_ID,
        "created_at": AUTHORING_TIMESTAMP,
        "status": "smoke_pipeline_only",
        "creation_method": "deterministic_project_authored_template",
        "authoring_system": "goodprose-smoke-template-v1",
        "rights_status": "training_permitted_project_owned_smoke",
        "authorization_basis": (
            "The research contract explicitly permits a small project-authored corpus for "
            "the end-to-end smoke fine-tune. This does not promote any named external source."
        ),
        "corpus_sampling_ratios": {
            "task_pairs": 1.0,
            "style_targets": 0.0,
            "preference_pairs": 0.0,
        },
        "record_count": sum(split_counts.values()),
        "lineage_group_count": len(SCENARIOS),
        "template_cluster_count": 4,
        "split_counts": split_counts,
        "output_format_counts": dict(sorted(format_counts.items())),
        "split_sha256": split_hashes,
        "dataset_sha256": dataset_digest.hexdigest(),
        "record_schema_sha256": sha256_bytes(schema_payload),
        "compiler_sha256": sha256_file(Path(__file__)),
        "b1_cases_sha256": sha256_file(b1_cases_path),
        "contamination_check": contamination,
        "limitations": [
            (
                "Synthetic project-owned templates validate plumbing and cannot establish "
                "model quality."
            ),
            "Only twelve independent scenario lineages and four templates are represented.",
            "No named-source, imported, private, B2, or Tier C material is included.",
            "The data is authorized only for this project smoke test, not external redistribution.",
        ],
        "rebuild_command": (
            "uv run python -m goodprose.executive_writing smoke-data build "
            "--output-dir data/derived/executive-writing/smoke-v1 "
            "--manifest data/executive-writing/smoke-v1/manifest.json "
            "--b1-cases evals/executive-writing/goodprose-b1-v1/cases.jsonl"
        ),
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    atomic_write(manifest_path, manifest_bytes)
    return manifest
