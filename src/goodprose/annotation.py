"""Pinned Argilla authoring and review workflows for GoodProse."""

from __future__ import annotations

import os
import secrets
from collections import defaultdict
from pathlib import Path
from typing import Any

from goodprose.jsonl import atomic_write, canonical_json, load_jsonl, serialize_jsonl
from goodprose.models import (
    AnnotationSeed,
    ExampleOutput,
    Review,
    ReviewStatus,
    TrainingExample,
)
from goodprose.privacy import load_privacy_report

AUTHORING_DATASET = "goodprose-authoring-v1"
REVIEW_DATASET = "goodprose-review-v1"
REVIEW_QUESTIONS = (
    "privacy",
    "factuality",
    "objective_fulfillment",
    "audience_fit",
    "channel_fit",
    "house_style",
    "overall_quality",
)


class AnnotationError(RuntimeError):
    """An annotation workflow invariant was violated."""


def _argilla() -> Any:
    try:
        import argilla as rg
    except ImportError as error:
        raise AnnotationError("Argilla is not installed; run `uv sync`") from error
    if rg.__version__ != "2.8.0":
        raise AnnotationError(f"GoodProse requires Argilla 2.8.0, found {rg.__version__}")
    return rg


def connect(api_url: str, api_key: str) -> Any:
    return _argilla().Argilla(api_url=api_url, api_key=api_key)


def _authoring_settings(client: Any) -> Any:
    rg = _argilla()
    return rg.Settings(
        guidelines=(
            "Turn the source material into effective executive communication for the stated "
            "audience, channel, and objective. Preserve facts and uncertainty. Do not invent "
            "evidence, decisions, or commitments. Do not copy secrets or unapproved personal "
            "data. Follow data/style-references/HOUSE_STYLE.md."
        ),
        fields=[
            rg.TextField(
                name="source_material",
                title="Source material",
                use_markdown=True,
                client=client,
            ),
            rg.TextField(
                name="channel",
                title="Channel",
                client=client,
            ),
            rg.TextField(
                name="audience",
                title="Audience",
                client=client,
            ),
            rg.TextField(
                name="objective",
                title="Communication objective",
                client=client,
            ),
            rg.TextField(name="voice_profile_id", title="Voice profile", client=client),
            rg.TextField(
                name="constraints",
                title="Constraints",
                use_markdown=True,
                required=False,
                client=client,
            ),
            rg.TextField(
                name="context",
                title="Supporting context",
                use_markdown=True,
                required=False,
                client=client,
            ),
            rg.TextField(
                name="source_record_json",
                title="Canonical source record (do not edit)",
                required=True,
                client=client,
            ),
        ],
        questions=[
            rg.TextQuestion(
                name="gold_title",
                title="Human-approved title or email subject",
                description="Leave blank when the channel does not need a title or subject.",
                required=False,
                client=client,
            ),
            rg.TextQuestion(
                name="gold_body_markdown",
                title="Human-approved communication",
                description="Write the complete GoodProse output in Markdown.",
                required=True,
                use_markdown=True,
                client=client,
            ),
            rg.TextQuestion(
                name="author_notes",
                title="Author notes",
                description="Record redactions, uncertainty, or decisions for the reviewer.",
                required=False,
                use_markdown=True,
                client=client,
            ),
        ],
        metadata=[
            rg.TermsMetadataProperty(name="split", title="Split", client=client),
            rg.TermsMetadataProperty(
                name="creation_method", title="Creation method", client=client
            ),
            rg.TermsMetadataProperty(name="lineage_group", title="Lineage group", client=client),
        ],
        distribution=rg.TaskDistribution(min_submitted=1),
    )


def _review_settings(client: Any) -> Any:
    rg = _argilla()
    pass_fail = {"passed": "Passed", "failed": "Failed"}
    return rg.Settings(
        guidelines=(
            "Review the proposed communication against the source record, audience, channel, and "
            "objective. Do not reward plausible but unsupported additions. Every gate is required. "
            "Mark a gate failed when material correction is needed and explain the correction."
        ),
        fields=[
            rg.TextField(
                name="source_material",
                title="Source material",
                use_markdown=True,
                client=client,
            ),
            rg.TextField(name="channel", title="Channel", client=client),
            rg.TextField(name="audience", title="Audience", client=client),
            rg.TextField(name="objective", title="Communication objective", client=client),
            rg.TextField(name="voice_profile_id", title="Voice profile", client=client),
            rg.TextField(
                name="constraints",
                title="Constraints",
                use_markdown=True,
                required=False,
                client=client,
            ),
            rg.TextField(
                name="context",
                title="Supporting context",
                use_markdown=True,
                required=False,
                client=client,
            ),
            rg.TextField(
                name="proposed_title",
                title="Proposed title or email subject",
                required=False,
                client=client,
            ),
            rg.TextField(
                name="proposed_body",
                title="Proposed communication",
                use_markdown=True,
                client=client,
            ),
            rg.TextField(
                name="author_notes",
                title="Author notes",
                use_markdown=True,
                required=False,
                client=client,
            ),
            rg.TextField(
                name="source_record_json",
                title="Canonical source record (do not edit)",
                required=True,
                client=client,
            ),
        ],
        questions=[
            rg.LabelQuestion(
                name="privacy",
                labels=pass_fail,
                title="Privacy and secret handling",
                description="No unapproved sensitive information is present.",
                client=client,
            ),
            rg.LabelQuestion(
                name="factuality",
                labels=pass_fail,
                title="Factual fidelity",
                description="Material claims are grounded and open questions remain open.",
                client=client,
            ),
            rg.LabelQuestion(
                name="objective_fulfillment",
                labels=pass_fail,
                title="Objective fulfillment",
                description=(
                    "The communication accomplishes the stated purpose and preserves the decision."
                ),
                client=client,
            ),
            rg.LabelQuestion(
                name="audience_fit",
                labels=pass_fail,
                title="Audience fit",
                description=(
                    "The level of context, vocabulary, and emphasis suit the stated readers."
                ),
                client=client,
            ),
            rg.LabelQuestion(
                name="channel_fit",
                labels=pass_fail,
                title="Channel fit",
                description=(
                    "The structure and length suit the requested email, blog post, or memo."
                ),
                client=client,
            ),
            rg.LabelQuestion(
                name="house_style",
                labels=pass_fail,
                title="GoodProse house style",
                description="The writing follows the selected voice profile and house-style rules.",
                client=client,
            ),
            rg.LabelQuestion(
                name="overall_quality",
                labels=pass_fail,
                title="Overall communication quality",
                description="The result is ready for its intended executive use.",
                client=client,
            ),
            rg.TextQuestion(
                name="review_notes",
                title="Review notes",
                description="Explain failures and required corrections.",
                required=False,
                use_markdown=True,
                client=client,
            ),
        ],
        metadata=[
            rg.TermsMetadataProperty(name="split", title="Split", client=client),
            rg.TermsMetadataProperty(
                name="creation_method", title="Creation method", client=client
            ),
            rg.TermsMetadataProperty(name="lineage_group", title="Lineage group", client=client),
        ],
        distribution=rg.TaskDistribution(min_submitted=1),
    )


def ensure_workflows(client: Any, workspace: str) -> tuple[Any, Any]:
    rg = _argilla()
    if client.workspaces(workspace) is None:
        rg.Workspace(name=workspace, client=client).create()

    datasets = []
    for name, settings in (
        (AUTHORING_DATASET, _authoring_settings(client)),
        (REVIEW_DATASET, _review_settings(client)),
    ):
        dataset = client.datasets(name=name, workspace=workspace)
        if dataset is None:
            dataset = rg.Dataset(
                name=name,
                workspace=workspace,
                settings=settings,
                client=client,
            ).create()
        else:
            expected_fields = [field.name for field in settings.fields]
            expected_questions = [question.name for question in settings.questions]
            actual_fields = [field.name for field in dataset.settings.fields]
            actual_questions = [question.name for question in dataset.settings.questions]
            if actual_fields != expected_fields or actual_questions != expected_questions:
                raise AnnotationError(
                    f"Argilla dataset {name!r} exists with an incompatible schema; "
                    "create a new versioned workflow instead of mutating it"
                )
        datasets.append(dataset)
    return datasets[0], datasets[1]


def _context_markdown(seed: AnnotationSeed) -> str:
    sections: list[str] = []
    for item in seed.input.context:
        heading = item.kind.value
        if item.label:
            heading += f": {item.label}"
        sections.append(f"### {heading}\n\n{item.content}")
    return "\n\n".join(sections)


def _seed_json(seed: AnnotationSeed) -> str:
    return canonical_json(seed.model_dump(mode="json", exclude_none=True))


def _record_fields(seed: AnnotationSeed) -> dict[str, str]:
    return {
        "source_material": seed.input.source_material,
        "channel": seed.input.channel.value,
        "audience": seed.input.audience,
        "objective": seed.input.objective,
        "voice_profile_id": seed.input.voice_profile_id,
        "constraints": "\n".join(f"- {item}" for item in seed.input.constraints),
        "context": _context_markdown(seed),
        "source_record_json": _seed_json(seed),
    }


def _metadata(seed: AnnotationSeed) -> dict[str, str]:
    return {
        "split": seed.split.value,
        "creation_method": seed.provenance.creation_method.value,
        "lineage_group": seed.provenance.lineage_group,
    }


def _verify_clean_report(input_path: Path, report_path: Path) -> None:
    report = load_privacy_report(report_path)
    from goodprose.jsonl import sha256_file

    if report.input_sha256 != sha256_file(input_path):
        raise AnnotationError("privacy report does not match the annotation seed JSONL")
    if not report.is_clean:
        raise AnnotationError(
            f"privacy report has {len(report.findings)} finding(s); redact and rescan before import"
        )


def _existing_source_records(dataset: Any) -> dict[str, str]:
    return {
        str(record.id): str(record.fields["source_record_json"])
        for record in dataset.records(with_responses=False, with_suggestions=False)
    }


def import_authoring_seeds(
    client: Any,
    workspace: str,
    input_path: Path,
    privacy_report_path: Path,
) -> tuple[int, int]:
    _verify_clean_report(input_path, privacy_report_path)
    seeds = load_jsonl(input_path, AnnotationSeed)
    authoring, _review = ensure_workflows(client, workspace)
    existing = _existing_source_records(authoring)
    rg = _argilla()
    new_records = []
    skipped = 0
    for seed in seeds:
        source_json = _seed_json(seed)
        if seed.id in existing:
            if existing[seed.id] != source_json:
                raise AnnotationError(
                    f"Argilla authoring record {seed.id!r} already has different source data"
                )
            skipped += 1
            continue
        new_records.append(
            rg.Record(id=seed.id, fields=_record_fields(seed), metadata=_metadata(seed))
        )
    if new_records:
        authoring.records.log(new_records)
    return len(new_records), skipped


def _submitted_values(record: Any, question_name: str) -> list[tuple[str, Any]]:
    values = []
    for response in record.responses[question_name]:
        status = getattr(response.status, "value", response.status)
        if status == "submitted":
            values.append((str(response.user_id), response.value))
    return values


def _single_submitted(
    record: Any, question_name: str, *, required: bool = True
) -> tuple[str, Any] | None:
    values = _submitted_values(record, question_name)
    if not values and not required:
        return None
    if len(values) != 1:
        raise AnnotationError(
            f"record {record.id!r} requires exactly one submitted {question_name!r} response; "
            f"found {len(values)}"
        )
    return values[0]


def prepare_review_records(client: Any, workspace: str) -> tuple[int, int]:
    authoring, review = ensure_workflows(client, workspace)
    existing_records = {
        str(record.id): record
        for record in review.records(with_responses=False, with_suggestions=False)
    }
    rg = _argilla()
    new_records = []
    skipped = 0
    for record in authoring.records(with_responses=True, with_suggestions=False):
        body_response = _single_submitted(record, "gold_body_markdown", required=False)
        if body_response is None:
            continue
        _author_id, gold_body = body_response
        if not isinstance(gold_body, str) or not gold_body.strip():
            raise AnnotationError(f"record {record.id!r} has an empty gold communication")
        title_response = _single_submitted(record, "gold_title", required=False)
        gold_title = str(title_response[1]).strip() if title_response else ""
        notes_response = _single_submitted(record, "author_notes", required=False)
        author_notes = str(notes_response[1]) if notes_response else ""
        source_json = str(record.fields["source_record_json"])
        existing_record = existing_records.get(str(record.id))
        if existing_record is not None:
            if str(existing_record.fields["source_record_json"]) != source_json:
                raise AnnotationError(
                    f"Argilla review record {record.id!r} already has different source data"
                )
            if str(existing_record.fields["proposed_body"]) != gold_body:
                raise AnnotationError(
                    f"Argilla review record {record.id!r} has stale proposed body text; "
                    "create a corrected authoring record with a new ID"
                )
            if str(existing_record.fields["proposed_title"] or "") != gold_title:
                raise AnnotationError(
                    f"Argilla review record {record.id!r} has a stale proposed title; "
                    "create a corrected authoring record with a new ID"
                )
            skipped += 1
            continue
        fields = {
            "source_material": str(record.fields["source_material"]),
            "channel": str(record.fields["channel"]),
            "audience": str(record.fields["audience"]),
            "objective": str(record.fields["objective"]),
            "voice_profile_id": str(record.fields["voice_profile_id"]),
            "constraints": str(record.fields["constraints"] or ""),
            "context": str(record.fields["context"] or ""),
            "proposed_title": gold_title,
            "proposed_body": gold_body,
            "author_notes": author_notes,
            "source_record_json": source_json,
        }
        new_records.append(
            rg.Record(
                id=str(record.id),
                fields=fields,
                metadata=dict(record.metadata),
            )
        )
    if new_records:
        review.records.log(new_records)
    return len(new_records), skipped


def _review_for_record(record: Any) -> Review | None:
    responses_by_user: dict[str, dict[str, Any]] = defaultdict(dict)
    for question_name in (*REVIEW_QUESTIONS, "review_notes"):
        for user_id, value in _submitted_values(record, question_name):
            responses_by_user[user_id][question_name] = value

    complete_users = [
        user_id
        for user_id, answers in responses_by_user.items()
        if all(question in answers for question in REVIEW_QUESTIONS)
    ]
    if not complete_users:
        return None
    if len(complete_users) != 1:
        raise AnnotationError(
            f"record {record.id!r} requires exactly one reviewer with all gates submitted; "
            f"found {len(complete_users)}"
        )
    user_id = complete_users[0]
    answers = responses_by_user[user_id]
    return Review(
        privacy=ReviewStatus(str(answers["privacy"])),
        factuality=ReviewStatus(str(answers["factuality"])),
        objective_fulfillment=ReviewStatus(str(answers["objective_fulfillment"])),
        audience_fit=ReviewStatus(str(answers["audience_fit"])),
        channel_fit=ReviewStatus(str(answers["channel_fit"])),
        house_style=ReviewStatus(str(answers["house_style"])),
        overall_quality=ReviewStatus(str(answers["overall_quality"])),
        reviewer=user_id,
        notes=str(answers["review_notes"]) if answers.get("review_notes") else None,
    )


def export_reviewed(client: Any, workspace: str, output_path: Path) -> int:
    _authoring, review_dataset = ensure_workflows(client, workspace)
    examples: list[TrainingExample] = []
    for record in review_dataset.records(with_responses=True, with_suggestions=False):
        seed = AnnotationSeed.model_validate_json(str(record.fields["source_record_json"]))
        if seed.id != str(record.id):
            raise AnnotationError(f"record {record.id!r} does not match its embedded source ID")
        review = _review_for_record(record)
        if review is None:
            continue
        proposed_title = str(record.fields["proposed_title"] or "").strip() or None
        proposed_body = str(record.fields["proposed_body"])
        examples.append(
            TrainingExample(
                version=seed.version,
                id=seed.id,
                split=seed.split,
                input=seed.input,
                output=ExampleOutput(title=proposed_title, body_markdown=proposed_body),
                provenance=seed.provenance,
                review=review,
            )
        )
    examples.sort(key=lambda item: item.id)
    atomic_write(output_path, serialize_jsonl(examples))
    return len(examples)


def backup_dataset(client: Any, workspace: str, dataset_name: str, output_path: Path) -> Path:
    dataset = client.datasets(name=dataset_name, workspace=workspace)
    if dataset is None:
        raise AnnotationError(f"Argilla dataset {dataset_name!r} does not exist")
    if output_path.exists():
        raise AnnotationError(f"backup destination already exists: {output_path}")
    dataset.to_disk(str(output_path), with_records=True)
    return output_path


def initialize_env(output_path: Path) -> Path:
    if output_path.exists():
        raise AnnotationError(f"refusing to replace existing environment file: {output_path}")
    values = {
        "ARGILLA_BOOTSTRAP_USER": "goodprose-admin",
        "ARGILLA_BOOTSTRAP_PASSWORD": secrets.token_urlsafe(24),
        "ARGILLA_API_KEY": f"goodprose.{secrets.token_urlsafe(32)}",
        "ARGILLA_WORKSPACE": "goodprose",
        "ARGILLA_POSTGRES_PASSWORD": secrets.token_urlsafe(24),
        "ARGILLA_PORT": "6900",
    }
    payload = "".join(f"{key}={value}\n" for key, value in values.items()).encode("utf-8")
    atomic_write(output_path, payload)
    os.chmod(output_path, 0o600)
    return output_path
