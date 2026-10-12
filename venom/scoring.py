from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

ScorerType = Literal["contains", "exact", "regex"]
_SUPPORTED_TYPES: set[str] = {"contains", "exact", "regex"}


@dataclass(frozen=True)
class ScorerSpec:
    name: str
    type: ScorerType
    value: str
    case_sensitive: bool = True
    strip: bool = False
    prompt: str | None = None


@dataclass(frozen=True)
class ScoreResult:
    provider: str
    model: str
    prompt: str
    scorer: str
    scorer_type: str
    passed: bool
    score: float
    details: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_config(path: Path) -> Any:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON scorer config: {exc.msg}") from exc
    if suffix in {".yaml", ".yml"}:
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML scorer config: {exc}") from exc
    raise ValueError("Scorer config must be .json, .yaml, or .yml.")


def load_scorers(path: str | Path) -> list[ScorerSpec]:
    target = Path(path)
    data = _load_config(target)
    if not isinstance(data, dict) or not isinstance(data.get("scorers"), list):
        raise ValueError("Scorer config must contain a 'scorers' list.")

    specs: list[ScorerSpec] = []
    seen: set[str] = set()
    for index, raw in enumerate(data["scorers"], start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Scorer #{index} must be an object.")

        name = raw.get("name")
        scorer_type = raw.get("type")
        value = raw.get("value")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Scorer #{index} requires a non-empty string name.")
        name = name.strip()
        if name in seen:
            raise ValueError(f"Duplicate scorer name: {name}")
        seen.add(name)

        if scorer_type not in _SUPPORTED_TYPES:
            supported = ", ".join(sorted(_SUPPORTED_TYPES))
            raise ValueError(f"Scorer '{name}' has unsupported type '{scorer_type}'. Supported: {supported}")
        if not isinstance(value, str):
            raise ValueError(f"Scorer '{name}' requires a string value.")

        case_sensitive = raw.get("case_sensitive", True)
        strip = raw.get("strip", False)
        prompt = raw.get("prompt")
        if not isinstance(case_sensitive, bool):
            raise ValueError(f"Scorer '{name}' case_sensitive must be boolean.")
        if not isinstance(strip, bool):
            raise ValueError(f"Scorer '{name}' strip must be boolean.")
        if prompt is not None and not isinstance(prompt, str):
            raise ValueError(f"Scorer '{name}' prompt must be a string when provided.")

        if scorer_type == "regex":
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                re.compile(value, flags)
            except re.error as exc:
                raise ValueError(f"Scorer '{name}' has invalid regex: {exc}") from exc

        specs.append(
            ScorerSpec(
                name=name,
                type=scorer_type,
                value=value,
                case_sensitive=case_sensitive,
                strip=strip,
                prompt=prompt,
            )
        )

    if not specs:
        raise ValueError("Scorer config contains no scorers.")
    return specs


def _normalize(text: str, spec: ScorerSpec) -> str:
    if spec.strip:
        text = text.strip()
    if not spec.case_sensitive:
        text = text.casefold()
    return text


def evaluate(response: str, spec: ScorerSpec) -> tuple[bool, str]:
    if spec.type == "contains":
        haystack = _normalize(response, spec)
        needle = _normalize(spec.value, spec)
        passed = needle in haystack
        return passed, f"response {'contains' if passed else 'does not contain'} expected text"

    if spec.type == "exact":
        actual = _normalize(response, spec)
        expected = _normalize(spec.value, spec)
        passed = actual == expected
        return passed, f"response {'matches' if passed else 'does not match'} expected text exactly"

    flags = 0 if spec.case_sensitive else re.IGNORECASE
    candidate = response.strip() if spec.strip else response
    passed = re.search(spec.value, candidate, flags) is not None
    return passed, f"regex {'matched' if passed else 'did not match'} response"


def score_rows(rows: list[dict[str, Any]], specs: list[ScorerSpec]) -> list[ScoreResult]:
    results: list[ScoreResult] = []
    for row in rows:
        prompt = str(row["prompt"])
        response = str(row["response"])
        for spec in specs:
            if spec.prompt is not None and spec.prompt != prompt:
                continue
            passed, details = evaluate(response, spec)
            results.append(
                ScoreResult(
                    provider=str(row["provider"]),
                    model=str(row["model"]),
                    prompt=prompt,
                    scorer=spec.name,
                    scorer_type=spec.type,
                    passed=passed,
                    score=1.0 if passed else 0.0,
                    details=details,
                )
            )
    return results


def write_scores_jsonl(path: str | Path, results: list[ScoreResult]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
