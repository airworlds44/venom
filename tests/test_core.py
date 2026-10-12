import json

import pytest

from venom.core import append_jsonl, parse_model_spec
from venom.models import RunResult


def test_parse_model_spec():
    assert parse_model_spec("openai:example-model") == ("openai", "example-model")


def test_parse_model_spec_rejects_invalid_value():
    with pytest.raises(ValueError):
        parse_model_spec("missing-separator")


def test_append_jsonl(tmp_path):
    result = RunResult.create(
        provider="openai",
        model="example-model",
        prompt="hello",
        response="world",
        latency_ms=12.345,
    )
    path = tmp_path / "runs.jsonl"
    append_jsonl(path, result)
    saved = json.loads(path.read_text().strip())
    assert saved["provider"] == "openai"
    assert saved["latency_ms"] == 12.35
