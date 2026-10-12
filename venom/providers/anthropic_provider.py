from __future__ import annotations

from .types import ProviderResponse


def _token_count(value: object) -> int | None:
    return value if isinstance(value, int) and value >= 0 else None


def run_anthropic(model: str, prompt: str) -> ProviderResponse:
    """Run a prompt with Anthropic Messages.

    Authentication is read by the Anthropic SDK from ANTHROPIC_API_KEY.
    """
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise RuntimeError("Install the anthropic package to use the Anthropic provider.") from exc

    client = Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    parts: list[str] = []
    for block in getattr(message, "content", []):
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    if not parts:
        raise RuntimeError("Anthropic returned no text content.")

    usage = getattr(message, "usage", None)
    return ProviderResponse(
        text="\n".join(parts),
        input_tokens=_token_count(getattr(usage, "input_tokens", None)),
        output_tokens=_token_count(getattr(usage, "output_tokens", None)),
    )
