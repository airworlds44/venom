from __future__ import annotations


def run_openai(model: str, prompt: str) -> str:
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
    return text
