from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from goodprose.annotation import _authoring_settings, _review_settings, initialize_env


def test_argilla_workflow_schemas_are_versioned_and_complete() -> None:
    client = SimpleNamespace(api=SimpleNamespace(fields=None, questions=None, metadata=None))
    authoring = _authoring_settings(client)
    review = _review_settings(client)

    assert [question.name for question in authoring.questions] == [
        "gold_title",
        "gold_body_markdown",
        "author_notes",
    ]
    assert [question.name for question in review.questions] == [
        "privacy",
        "factuality",
        "objective_fulfillment",
        "audience_fit",
        "channel_fit",
        "house_style",
        "overall_quality",
        "review_notes",
    ]


def test_environment_initialization_uses_private_random_values(tmp_path: Path) -> None:
    path = initialize_env(tmp_path / ".env")
    text = path.read_text(encoding="utf-8")

    assert "replace-with" not in text
    assert "ARGILLA_API_KEY=goodprose." in text
    assert path.stat().st_mode & 0o777 == 0o600
