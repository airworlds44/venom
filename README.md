# Venom

**Venom is a tiny, vendor-neutral CLI for comparing AI model responses and saving reproducible runs.**

It is aimed at indie builders, researchers, and vibe coders who want to test the same prompt across providers without building a full evaluation stack.

> Status: early alpha. The project is intentionally small and welcomes contributors.

## Why Venom?

AI model comparisons are often done by copying prompts between browser tabs. Venom makes that workflow scriptable and reproducible:

- run one prompt against OpenAI or Anthropic
- compare multiple provider/model pairs from one command
- record latency, provider, model, prompt, response, and timestamp
- save results as JSONL so they are easy to diff, analyze, or feed into notebooks
- keep API keys in environment variables rather than source code

Venom is not affiliated with OpenAI or Anthropic.

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/airworlds44/venom.git
cd venom
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

Set the API key for the provider you want to use:

```bash
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

Run a prompt:

```bash
venom run --provider openai --model gpt-6-luna --prompt "Explain recursion in one paragraph."
```

Or compare providers/models:

```bash
venom compare \
  --model openai:gpt-6-luna \
  --model anthropic:YOUR_CLAUDE_MODEL \
  --prompt "Write a Python function that validates an email address." \
  --out runs.jsonl
```

Use model IDs that are available in your own provider account.

## Output

Each run is written as a JSON object, for example:

```json
{
  "provider": "openai",
  "model": "gpt-6-luna",
  "prompt": "Explain recursion in one paragraph.",
  "response": "...",
  "latency_ms": 842.31,
  "created_at": "2026-10-12T17:30:00+00:00"
}
```

## Roadmap

- [ ] OpenAI provider adapter
- [ ] Anthropic provider adapter
- [ ] JSONL run logging
- [ ] multi-model comparison command
- [ ] prompt suites from YAML/JSON
- [ ] simple scoring hooks
- [ ] cost/token metadata where providers expose it
- [ ] HTML comparison report
- [ ] CI-friendly non-interactive benchmark mode

## Project philosophy

Venom should stay understandable. A new contributor should be able to read most of the codebase in one sitting. Provider-specific logic belongs in small adapters; recorded results should use a simple, portable format.

## Contributing

Issues and pull requests are welcome. Good first contributions include tests, provider metadata, output formatting, and small evaluation utilities.

## Security

Never commit API keys. Venom should read credentials from provider SDK environment variables. If you accidentally publish a key, revoke it with the provider immediately.

## License

Planned license: MIT.
