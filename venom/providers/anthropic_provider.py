from __future__ import annotations


def run_anthropic(model: str, prompt: str) -> str:
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
    return "\n".join(parts)
