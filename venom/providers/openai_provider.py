from __future__ import annotations

from .types import ProviderResponse


def _token_count(value: object) -> int | None:
    return value if isinstance(value, int) and value >= 0 else None


def run_openai(model: str, prompt: str) -> ProviderResponse:
    """Run a prompt with the OpenAI Responses API.

    Authentication is read by the OpenAI SDK from OPENAI_API_KEY.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the openai package to use the OpenAI provider.") from exc

    client = OpenAI()
    response = client.responses.create(model=model, input=prompt)
    text = getattr(response, "output_text", None)
    if not text:
        raise RuntimeError("OpenAI returned no output_text.")

    usage = getattr(response, "usage", None)
    return ProviderResponse(
        text=text,
        input_tokens=_token_count(getattr(usage, "input_tokens", None)),
        output_tokens=_token_count(getattr(usage, "output_tokens", None)),
    )
