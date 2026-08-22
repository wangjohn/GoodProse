"""Deterministic privacy and secret scanning for GoodProse JSONL records."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict

from goodprose.jsonl import atomic_write, atomic_write_json, canonical_json, sha256_file

PRIVACY_REPORT_VERSION = 1
BUILTIN_SCANNER_VERSION = "1"


class PrivacyFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    record_id: str
    line_number: int
    field_path: str
    category: Literal["pii", "secret"]
    entity_type: str
    detector: str
    start: int
    end: int
    confidence: float
    value_sha256: str


class PrivacyReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal[1]
    input_sha256: str
    record_count: int
    scanners: tuple[str, ...]
    findings: tuple[PrivacyFinding, ...]

    @property
    def is_clean(self) -> bool:
        return not self.findings


@dataclass(frozen=True)
class _Match:
    path: tuple[str | int, ...]
    category: Literal["pii", "secret"]
    entity_type: str
    detector: str
    start: int
    end: int
    confidence: float
    value: str


@dataclass(frozen=True)
class _Pattern:
    category: Literal["pii", "secret"]
    entity_type: str
    expression: re.Pattern[str]
    group: int | str = 0
    confidence: float = 1.0


_PATTERNS = (
    _Pattern(
        "secret",
        "PRIVATE_KEY",
        re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    ),
    _Pattern("secret", "AWS_ACCESS_KEY", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    _Pattern(
        "secret",
        "GITHUB_TOKEN",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{20,255})\b"),
    ),
    _Pattern("secret", "SLACK_TOKEN", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,200}\b")),
    _Pattern("secret", "OPENAI_API_KEY", re.compile(r"\bsk-[A-Za-z0-9_-]{20,200}\b")),
    _Pattern(
        "secret",
        "ASSIGNED_CREDENTIAL",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password)"
            r"\s*[:=]\s*[\"']?(?P<value>[A-Za-z0-9_./+=:@-]{8,})"
        ),
        group="value",
        confidence=0.8,
    ),
    _Pattern(
        "pii",
        "EMAIL_ADDRESS",
        re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.I),
    ),
    _Pattern("pii", "US_SSN", re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")),
    _Pattern(
        "pii",
        "PHONE_NUMBER",
        re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)"),
        confidence=0.7,
    ),
)


class _PresidioResult(Protocol):
    entity_type: str
    start: int
    end: int
    score: float


class PrivacyScanError(RuntimeError):
    """Privacy scanning could not be completed safely."""


def _json_path(path: tuple[str | int, ...]) -> str:
    value = "$"
    for part in path:
        if isinstance(part, int):
            value += f"[{part}]"
        else:
            escaped = part.replace("~", "~0").replace("/", "~1")
            value += f"/{escaped}"
    return value


def _walk_strings(
    value: Any, path: tuple[str | int, ...] = ()
) -> Iterable[tuple[tuple[str | int, ...], str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                yield from _walk_strings(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, (*path, index))


def _builtin_matches(path: tuple[str | int, ...], text: str) -> list[_Match]:
    matches: list[_Match] = []
    for pattern in _PATTERNS:
        for regex_match in pattern.expression.finditer(text):
            start, end = regex_match.span(pattern.group)
            matches.append(
                _Match(
                    path=path,
                    category=pattern.category,
                    entity_type=pattern.entity_type,
                    detector="builtin",
                    start=start,
                    end=end,
                    confidence=pattern.confidence,
                    value=text[start:end],
                )
            )
    return matches


def _build_presidio_analyzer() -> Any:
    try:
        from presidio_analyzer import AnalyzerEngine  # pyright: ignore[reportMissingImports]
    except ImportError as error:
        raise PrivacyScanError(
            "Presidio is not installed; run `uv sync --extra privacy` before using --presidio"
        ) from error
    try:
        return AnalyzerEngine()
    except Exception as error:
        raise PrivacyScanError(
            "Presidio could not initialize its NLP engine; install a supported spaCy model "
            "or configure Presidio explicitly"
        ) from error


def _presidio_matches(
    analyzer: Any, path: tuple[str | int, ...], text: str, language: str
) -> list[_Match]:
    results: list[_PresidioResult] = analyzer.analyze(text=text, language=language)
    return [
        _Match(
            path=path,
            category="pii",
            entity_type=result.entity_type,
            detector="presidio",
            start=result.start,
            end=result.end,
            confidence=float(result.score),
            value=text[result.start : result.end],
        )
        for result in results
    ]


def _deduplicate_matches(matches: list[_Match]) -> list[_Match]:
    best: dict[tuple[tuple[str | int, ...], str, int, int], _Match] = {}
    for match in matches:
        key = (match.path, match.category, match.start, match.end)
        current = best.get(key)
        if current is None or match.confidence > current.confidence:
            best[key] = match
    return sorted(
        best.values(), key=lambda item: (item.path, item.start, item.end, item.entity_type)
    )


def _redact_text(text: str, matches: list[_Match]) -> str:
    selected: list[_Match] = []
    occupied_until = -1
    for match in sorted(
        matches,
        key=lambda item: (item.start, -(item.end - item.start), item.category != "secret"),
    ):
        if match.start < occupied_until:
            continue
        selected.append(match)
        occupied_until = match.end

    redacted = text
    for match in reversed(selected):
        placeholder = f"[REDACTED_{match.entity_type}]"
        redacted = redacted[: match.start] + placeholder + redacted[match.end :]
    return redacted


def _redact_value(
    value: Any,
    matches_by_path: dict[tuple[str | int, ...], list[_Match]],
    path: tuple[str | int, ...] = (),
) -> Any:
    if isinstance(value, str):
        return _redact_text(value, matches_by_path.get(path, []))
    if isinstance(value, dict):
        return {
            key: _redact_value(child, matches_by_path, (*path, key)) for key, child in value.items()
        }
    if isinstance(value, list):
        return [
            _redact_value(child, matches_by_path, (*path, index))
            for index, child in enumerate(value)
        ]
    return value


def scan_jsonl(
    input_path: Path,
    *,
    report_path: Path,
    redacted_output: Path | None = None,
    use_presidio: bool = False,
    language: str = "en",
) -> PrivacyReport:
    if redacted_output is not None and redacted_output.resolve() == input_path.resolve():
        raise PrivacyScanError("redacted output must not overwrite the source file")

    analyzer = _build_presidio_analyzer() if use_presidio else None
    records: list[tuple[int, dict[str, Any]]] = []
    all_matches: list[tuple[int, str, _Match]] = []

    with input_path.open(encoding="utf-8") as file_handle:
        for line_number, line in enumerate(file_handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise PrivacyScanError(
                    f"{input_path}:{line_number}: invalid JSON: {error.msg}"
                ) from error
            if not isinstance(record, dict):
                raise PrivacyScanError(f"{input_path}:{line_number}: record must be an object")
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id:
                record_id = f"line-{line_number}"
            records.append((line_number, record))
            for path, text in _walk_strings(record):
                matches = _builtin_matches(path, text)
                if analyzer is not None:
                    matches.extend(_presidio_matches(analyzer, path, text, language))
                for match in _deduplicate_matches(matches):
                    all_matches.append((line_number, record_id, match))

    findings = tuple(
        PrivacyFinding(
            record_id=record_id,
            line_number=line_number,
            field_path=_json_path(match.path),
            category=match.category,
            entity_type=match.entity_type,
            detector=match.detector,
            start=match.start,
            end=match.end,
            confidence=match.confidence,
            value_sha256=hashlib.sha256(match.value.encode("utf-8")).hexdigest(),
        )
        for line_number, record_id, match in all_matches
    )
    scanners = (f"builtin:{BUILTIN_SCANNER_VERSION}",) + (("presidio",) if analyzer else ())
    report = PrivacyReport(
        version=PRIVACY_REPORT_VERSION,
        input_sha256=sha256_file(input_path),
        record_count=len(records),
        scanners=scanners,
        findings=findings,
    )
    atomic_write_json(report_path, report.model_dump(mode="json"))

    if redacted_output is not None:
        matches_by_record: dict[int, dict[tuple[str | int, ...], list[_Match]]] = {}
        for line_number, _record_id, match in all_matches:
            path_matches = matches_by_record.setdefault(line_number, {})
            path_matches.setdefault(match.path, []).append(match)
        redacted_lines = []
        for line_number, record in records:
            redacted = _redact_value(record, matches_by_record.get(line_number, {}))
            redacted_lines.append(canonical_json(redacted))
        payload = (("\n".join(redacted_lines) + "\n") if redacted_lines else "").encode("utf-8")
        atomic_write(redacted_output, payload)

    return report


def load_privacy_report(path: Path) -> PrivacyReport:
    try:
        return PrivacyReport.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PrivacyScanError(f"invalid privacy report {path}: {error}") from error
