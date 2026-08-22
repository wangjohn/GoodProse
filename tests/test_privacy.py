from __future__ import annotations

import json
from pathlib import Path

from goodprose.privacy import scan_jsonl


def test_scan_reports_hashes_without_copying_sensitive_values(tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    report_path = tmp_path / "report.json"
    redacted_path = tmp_path / "redacted.jsonl"
    secret = "sk-this-is-a-long-test-api-key-123456789"
    source.write_text(
        "\n"
        + json.dumps(
            {
                "id": "sensitive-1",
                "input": {
                    "source_material": f"Contact jane@example.com and use {secret}",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    report = scan_jsonl(
        source,
        report_path=report_path,
        redacted_output=redacted_path,
    )

    assert report.record_count == 1
    assert {finding.entity_type for finding in report.findings} >= {
        "EMAIL_ADDRESS",
        "OPENAI_API_KEY",
    }
    assert secret not in report_path.read_text(encoding="utf-8")
    redacted = redacted_path.read_text(encoding="utf-8")
    assert "[REDACTED_EMAIL_ADDRESS]" in redacted
    assert "[REDACTED_OPENAI_API_KEY]" in redacted
    assert secret not in redacted


def test_clean_scan_is_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    source.write_text('{"id":"clean","text":"No sensitive values."}\n', encoding="utf-8")
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    first = scan_jsonl(source, report_path=first_path)
    second = scan_jsonl(source, report_path=second_path)

    assert first.is_clean
    assert first == second
    assert first_path.read_bytes() == second_path.read_bytes()
