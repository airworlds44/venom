from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from .models import RunResult
from .providers import run_anthropic, run_openai

ProviderFn = Callable[[str, str], str]

PROVIDERS: dict[str, ProviderFn] = {
    "openai": run_openai,
    "anthropic": run_anthropic,
}


def execute(provider: str, model: str, prompt: str) -> RunResult:
    provider = provider.lower().strip()
    if provider not in PROVIDERS:
        supported = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Unsupported provider '{provider}'. Supported: {supported}")

    started = time.perf_counter()
    response = PROVIDERS[provider](model, prompt)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return RunResult.create(
        provider=provider,
        model=model,
        prompt=prompt,
        response=response,
        latency_ms=elapsed_ms,
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
