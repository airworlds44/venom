from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from .models import RunResult
from .pricing import PricingTable, estimate_cost_usd
from .providers import ProviderResponse, run_anthropic, run_openai

ProviderFn = Callable[[str, str], ProviderResponse]

PROVIDERS: dict[str, ProviderFn] = {
    "openai": run_openai,
    "anthropic": run_anthropic,
}


def execute(
    provider: str,
    model: str,
    prompt: str,
    *,
    pricing: PricingTable | None = None,
) -> RunResult:
    provider = provider.lower().strip()
    if provider not in PROVIDERS:
        supported = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Unsupported provider '{provider}'. Supported: {supported}")

    started = time.perf_counter()
    provider_result = PROVIDERS[provider](model, prompt)
    elapsed_ms = (time.perf_counter() - started) * 1000
    estimated_cost = estimate_cost_usd(
        provider,
        model,
        provider_result.input_tokens,
        provider_result.output_tokens,
        pricing,
    )
    return RunResult.create(
        provider=provider,
        model=model,
        prompt=prompt,
        response=provider_result.text,
        latency_ms=elapsed_ms,
        input_tokens=provider_result.input_tokens,
        output_tokens=provider_result.output_tokens,
        estimated_cost_usd=estimated_cost,
    )


def append_jsonl(path: str | Path, result: RunResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")


def parse_model_spec(value: str) -> tuple[str, str]:
    provider, sep, model = value.partition(":")
    if not sep or not provider.strip() or not model.strip():
        raise ValueError("Model must look like provider:model, e.g. openai:YOUR_MODEL")
    return provider.strip(), model.strip()
