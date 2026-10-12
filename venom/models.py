from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class RunResult:
    provider: str
    model: str
    prompt: str
    response: str
    latency_ms: float
    created_at: str

    @classmethod
    def create(
        cls,
        *,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        latency_ms: float,
    ) -> "RunResult":
        return cls(
            provider=provider,
            model=model,
            prompt=prompt,
            response=response,
            latency_ms=round(latency_ms, 2),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict:
        return asdict(self)
