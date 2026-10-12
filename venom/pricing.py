from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelPrice:
    input_per_million: float
    output_per_million: float


PricingTable = dict[str, ModelPrice]


def load_pricing(path: str | Path) -> PricingTable:
    target = Path(path)
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid pricing JSON: {exc.msg}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Pricing file must contain a JSON object keyed by provider:model.")

    table: PricingTable = {}
    for key, value in raw.items():
        if not isinstance(key, str) or ":" not in key:
            raise ValueError("Each pricing key must look like provider:model.")
        if not isinstance(value, dict):
            raise ValueError(f"Pricing entry '{key}' must be an object.")

        input_rate = value.get("input_per_million")
        output_rate = value.get("output_per_million")
        if not isinstance(input_rate, (int, float)) or input_rate < 0:
            raise ValueError(f"Pricing entry '{key}' needs a non-negative input_per_million.")
        if not isinstance(output_rate, (int, float)) or output_rate < 0:
            raise ValueError(f"Pricing entry '{key}' needs a non-negative output_per_million.")

        provider, model = key.split(":", 1)
        normalized = f"{provider.strip().lower()}:{model.strip()}"
        if not provider.strip() or not model.strip():
            raise ValueError("Each pricing key must look like provider:model.")
        table[normalized] = ModelPrice(float(input_rate), float(output_rate))

    return table


def estimate_cost_usd(
    provider: str,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
    pricing: PricingTable | None,
) -> float | None:
    if pricing is None or input_tokens is None or output_tokens is None:
        return None

    price = pricing.get(f"{provider.strip().lower()}:{model.strip()}")
    if price is None:
        return None

    cost = (
        input_tokens * price.input_per_million
        + output_tokens * price.output_per_million
    ) / 1_000_000
    return round(cost, 8)
