from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PromptCase:
    name: str
    prompt: str


def _normalize_payload(payload: Any) -> list[PromptCase]:
    if isinstance(payload, dict):
        payload = payload.get("prompts")

    if not isinstance(payload, list) or not payload:
        raise ValueError("Prompt suite must contain a non-empty list of prompts.")

    cases: list[PromptCase] = []
    seen: set[str] = set()

    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Prompt #{index} must be an object with name and prompt fields.")

        name = str(item.get("name", "")).strip()
        prompt = str(item.get("prompt", "")).strip()
        if not name or not prompt:
            raise ValueError(f"Prompt #{index} must have non-empty name and prompt fields.")
        if name in seen:
            raise ValueError(f"Duplicate prompt name: {name}")

        seen.add(name)
        cases.append(PromptCase(name=name, prompt=prompt))

    return cases


def load_suite(path: str | Path) -> list[PromptCase]:
    source = Path(path)
    if not source.exists():
        raise ValueError(f"Prompt suite does not exist: {source}")

    suffix = source.suffix.lower()
    text = source.read_text(encoding="utf-8")

    try:
        if suffix == ".json":
            payload = json.loads(text)
        elif suffix in {".yaml", ".yml"}:
            payload = yaml.safe_load(text)
        else:
            raise ValueError("Prompt suite must use .json, .yaml, or .yml.")
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Could not parse prompt suite {source}: {exc}") from exc

    return _normalize_payload(payload)
