"""Deterministic JSON and JSONL helpers."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

JsonRecord = BaseModel | Mapping[str, Any]


class JsonlError(ValueError):
    """A JSONL record could not be parsed or validated."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_jsonl[ModelT: BaseModel](path: Path, model_type: type[ModelT]) -> list[ModelT]:
    records: list[ModelT] = []
    with path.open(encoding="utf-8") as file_handle:
        for line_number, line in enumerate(file_handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise JsonlError(f"{path}:{line_number}: invalid JSON: {error.msg}") from error
            try:
                records.append(model_type.model_validate(value))
            except ValidationError as error:
                raise JsonlError(f"{path}:{line_number}: {error}") from error
    return records


def _json_value(record: JsonRecord) -> Mapping[str, Any]:
    if isinstance(record, BaseModel):
        return record.model_dump(mode="json", exclude_none=True)
    return record


def serialize_jsonl(records: Sequence[JsonRecord]) -> bytes:
    lines = [canonical_json(_json_value(record)) for record in records]
    return ("\n".join(lines) + ("\n" if lines else "")).encode()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as temporary_file:
            temporary_file.write(data)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
