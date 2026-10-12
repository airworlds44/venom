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
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None

    @classmethod
    def create(
        cls,
        *,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        latency_ms: float,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        estimated_cost_usd: float | None = None,
    ) -> "RunResult":
        return cls(
            provider=provider,
            model=model,
            prompt=prompt,
            response=response,
            latency_ms=round(latency_ms, 2),
            created_at=datetime.now(timezone.utc).isoformat(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost_usd,
        )

    def to_dict(self) -> dict:
        return asdict(self)
