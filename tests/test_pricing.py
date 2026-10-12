import json

import pytest

from venom.pricing import estimate_cost_usd, load_pricing


def test_load_pricing_and_estimate_cost(tmp_path):
    path = tmp_path / "pricing.json"
    path.write_text(
        json.dumps(
            {
                "openai:test-model": {
                    "input_per_million": 2.0,
                    "output_per_million": 8.0,
                }
            }
        )
    )

    pricing = load_pricing(path)
    cost = estimate_cost_usd("OpenAI", "test-model", 1_000, 500, pricing)

    assert cost == 0.006


def test_unknown_model_is_not_silently_priced(tmp_path):
    path = tmp_path / "pricing.json"
    path.write_text(
        json.dumps(
            {
                "openai:test-model": {
                    "input_per_million": 2.0,
                    "output_per_million": 8.0,
                }
            }
        )
    )

    pricing = load_pricing(path)
    assert estimate_cost_usd("openai", "other-model", 100, 100, pricing) is None


def test_missing_usage_is_not_priced(tmp_path):
    path = tmp_path / "pricing.json"
    path.write_text(
        json.dumps(
            {
                "openai:test-model": {
                    "input_per_million": 2.0,
                    "output_per_million": 8.0,
                }
            }
        )
    )

    pricing = load_pricing(path)
    assert estimate_cost_usd("openai", "test-model", None, 100, pricing) is None


def test_load_pricing_rejects_negative_rates(tmp_path):
    path = tmp_path / "pricing.json"
    path.write_text(
        json.dumps(
            {
                "openai:test-model": {
                    "input_per_million": -1,
                    "output_per_million": 8.0,
                }
            }
        )
    )

    with pytest.raises(ValueError, match="non-negative"):
        load_pricing(path)
