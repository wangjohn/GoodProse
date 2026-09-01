from __future__ import annotations

from pathlib import Path

import pytest

from goodprose.jsonl import JsonlError, load_jsonl
from goodprose.models import ModelOutput


def test_reports_invalid_json_line(tmp_path: Path) -> None:
    path = tmp_path / "broken.jsonl"
    path.write_text('{"id":"one","output":"ok"}\nnot-json\n', encoding="utf-8")

    with pytest.raises(JsonlError, match=r"broken\.jsonl:2: invalid JSON"):
        load_jsonl(path, ModelOutput)
