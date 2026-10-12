# Venom

**Venom is a tiny, vendor-neutral CLI for comparing AI model responses and saving reproducible runs.**

It is aimed at indie builders, researchers, and vibe coders who want to test the same prompt across providers without building a full evaluation stack.

> Status: early alpha. The project is intentionally small and welcomes contributors.

## Why Venom?

AI model comparisons are often done by copying prompts between browser tabs. Venom makes that workflow scriptable and reproducible:

- run one prompt against OpenAI or Anthropic
- compare multiple provider/model pairs from one command
- run reusable prompt suites from JSON or YAML
- record latency, token usage, provider, model, prompt, response, and timestamp
- optionally estimate cost from a pricing table you control
- turn saved runs into a self-contained HTML comparison report
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
venom run --provider openai --model YOUR_OPENAI_MODEL --prompt "Explain recursion in one paragraph."
```

Or compare providers/models:

```bash
venom compare \
  --model openai:YOUR_OPENAI_MODEL \
  --model anthropic:YOUR_CLAUDE_MODEL \
  --prompt "Write a Python function that validates an email address." \
  --out runs.jsonl
```

Use model IDs that are available in your own provider account.

## Prompt suites

A prompt suite is a JSON or YAML file with named prompts. For example:

```yaml
prompts:
  - name: explain-recursion
    prompt: Explain recursion in one concise paragraph.
  - name: write-validator
    prompt: Write a small Python function that validates a non-empty email-like string.
```

Run the suite against one or more models:

```bash
venom suite \
  --file examples/prompts.yaml \
  --model openai:YOUR_OPENAI_MODEL \
  --model anthropic:YOUR_CLAUDE_MODEL \
  --out runs.jsonl
```

Each prompt/model pair runs independently, so one provider failure does not stop the rest of the suite.

## Token usage and cost estimates

When the provider SDK exposes usage metadata, Venom records input and output token counts automatically.

Cost estimates are deliberately **opt-in**. Venom does not ship a model pricing table because provider prices can change. Instead, create a local JSON file with the prices you want Venom to use:

```json
{
  "openai:YOUR_OPENAI_MODEL": {
    "input_per_million": 0.0,
    "output_per_million": 0.0
  },
  "anthropic:YOUR_CLAUDE_MODEL": {
    "input_per_million": 0.0,
    "output_per_million": 0.0
  }
}
```

Replace the zeroes with current prices from the provider, then pass the file with `--pricing`:

```bash
venom compare \
  --model openai:YOUR_OPENAI_MODEL \
  --model anthropic:YOUR_CLAUDE_MODEL \
  --prompt "Summarize this idea in three bullets." \
  --pricing pricing.json \
  --out runs.jsonl
```

Pricing lookup is exact by `provider:model`. If a model is missing from the file, Venom leaves `estimated_cost_usd` as `null` rather than guessing.

## HTML reports

Turn an existing JSONL run file into a portable report without making any additional model calls:

```bash
venom report --input runs.jsonl --out venom-report.html
```

The report groups results by prompt and shows each provider/model response alongside latency, token usage, estimated cost, and timestamp. It is one self-contained HTML file with no external assets, and model output is HTML-escaped before rendering.

You can also set a report title:

```bash
venom report \
  --input runs.jsonl \
  --out benchmark.html \
  --title "Model benchmark — checkout support prompts"
```

## Output

Each run is written as a JSON object, for example:

```json
{
  "provider": "openai",
  "model": "YOUR_OPENAI_MODEL",
  "prompt": "Explain recursion in one paragraph.",
  "response": "...",
  "latency_ms": 842.31,
  "created_at": "2026-10-12T17:30:00+00:00",
  "input_tokens": 24,
  "output_tokens": 73,
  "estimated_cost_usd": null
}
```

## Roadmap

- [x] OpenAI provider adapter
- [x] Anthropic provider adapter
- [x] JSONL run logging
- [x] multi-model comparison command
- [x] prompt suites from YAML/JSON
- [ ] simple scoring hooks
- [x] cost/token metadata where providers expose it
- [x] HTML comparison report
- [ ] CI-friendly non-interactive benchmark mode

## Project philosophy

Venom should stay understandable. A new contributor should be able to read most of the codebase in one sitting. Provider-specific logic belongs in small adapters; recorded results should use a simple, portable format.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Good first contributions include tests, provider metadata, output formatting, and small evaluation utilities.

## Security

Never commit API keys. Venom reads credentials from provider SDK environment variables. If you accidentally publish a key, revoke it with the provider immediately.

## License

MIT — see [LICENSE](LICENSE).
