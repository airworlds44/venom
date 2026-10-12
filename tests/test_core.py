import json

import pytest

from venom.core import PROVIDERS, append_jsonl, execute, parse_model_spec
from venom.models import RunResult
from venom.pricing import ModelPrice
from venom.providers import ProviderResponse


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
    assert saved["input_tokens"] is None
    assert saved["estimated_cost_usd"] is None


def test_execute_captures_usage_and_estimated_cost(monkeypatch):
    def fake_provider(model: str, prompt: str) -> ProviderResponse:
        assert model == "test-model"
        assert prompt == "hello"
        return ProviderResponse(text="world", input_tokens=1_000, output_tokens=500)

    monkeypatch.setitem(PROVIDERS, "openai", fake_provider)
    result = execute(
        "openai",
        "test-model",
        "hello",
        pricing={"openai:test-model": ModelPrice(2.0, 8.0)},
    )

    assert result.response == "world"
    assert result.input_tokens == 1_000
    assert result.output_tokens == 500
    assert result.estimated_cost_usd == 0.006
