# Venom

**Venom is a tiny, vendor-neutral CLI for comparing AI model responses and saving reproducible runs.**

It is aimed at indie builders, researchers, and vibe coders who want to test the same prompt across providers without building a full evaluation stack.

> Status: **0.1.0 release candidate / early alpha.** The codebase is usable today, but the project has not yet been advertised as a published PyPI package or GitHub Release.

## Why Venom?

AI model comparisons are often done by copying prompts between browser tabs. Venom makes that workflow scriptable and reproducible:

- run one prompt against OpenAI or Anthropic
- compare multiple provider/model pairs from one command
- run reusable prompt suites from JSON or YAML
- record latency, token usage, provider, model, prompt, response, and timestamp
- optionally estimate cost from a pricing table you control
- apply deterministic pass/fail checks without another model call
- turn saved runs into a self-contained HTML comparison report
- run a complete non-interactive benchmark that emits CI-friendly artifacts
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

### Try the report flow without an API key

The repository includes `examples/demo-runs.jsonl`, a clearly labeled **synthetic demo fixture**. It exists only to demonstrate Venom's artifact/report workflow and is not presented as a real OpenAI/Anthropic benchmark.

```bash
venom report \
  --input examples/demo-runs.jsonl \
  --out demo-report.html \
  --title "Venom synthetic demo"
```

Open `demo-report.html` in a browser to see the comparison format without making any API calls.

### Run live models

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

## Deterministic scoring

Score saved runs without paying for an LLM judge. Venom includes three small, reproducible rule types:

- `contains` — response contains expected text
- `exact` — response exactly matches expected text
- `regex` — response matches a regular expression

Rules can be JSON or YAML. Example:

```yaml
scorers:
  - name: mentions-recursion
    type: contains
    value: recursion
    case_sensitive: false

  - name: looks-like-python-function
    type: regex
    value: 'def\s+\w+\s*\('

  - name: exact-yes
    type: exact
    value: yes
    strip: true
```

Apply the rules to an existing run file:

```bash
venom score \
  --input runs.jsonl \
  --rules examples/scorers.yaml \
  --out scores.jsonl
```

Each score is written separately with provider, model, prompt, scorer name, pass/fail, a `0.0` or `1.0` numeric score, and a short explanation. Add `prompt` to a scorer rule to apply it only to one exact prompt string.

For CI, use `--fail-on-miss` so the command exits with status 1 when any applied check fails:

```bash
venom score --input runs.jsonl --rules scorers.yaml --fail-on-miss
```

This first scoring layer intentionally avoids LLM-as-a-judge so results stay deterministic, cheap, and easy to test.

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

## Benchmark mode

`venom benchmark` ties the pieces together for a non-interactive run. It executes a prompt suite against one or more models and writes a fresh set of owned artifacts into one directory:

- `runs.jsonl` with successful model runs
- `scores.jsonl` when deterministic rules are supplied
- `report.html` when at least one run succeeds
- `summary.json` with planned/successful runs, provider failures, score failures, and optional cost totals

Example:

```bash
venom benchmark \
  --suite examples/prompts.yaml \
  --model openai:YOUR_OPENAI_MODEL \
  --model anthropic:YOUR_CLAUDE_MODEL \
  --rules examples/scorers.yaml \
  --pricing pricing.json \
  --out-dir benchmark-results \
  --fail-on-miss
```

A benchmark always returns a nonzero status if any provider/model run fails. With `--fail-on-miss`, deterministic scoring failures also return a nonzero status, which makes the command useful in CI. Venom replaces its own known artifact files on every benchmark run rather than appending stale results. It does **not** add, store, or manage provider API secrets for you.

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

## 0.1.0 release scope

The initial alpha scope is complete:

- [x] OpenAI provider adapter
- [x] Anthropic provider adapter
- [x] JSONL run logging
- [x] multi-model comparison command
- [x] prompt suites from YAML/JSON
- [x] simple deterministic scoring hooks
- [x] cost/token metadata where providers expose it
- [x] HTML comparison report
- [x] CI-friendly non-interactive benchmark mode

See [CHANGELOG.md](CHANGELOG.md) for release notes. A GitHub Release or PyPI package should only be considered published after that publishing step actually happens.

## Project philosophy

Venom should stay understandable. A new contributor should be able to read most of the codebase in one sitting. Provider-specific logic belongs in small adapters; recorded results should use a simple, portable format.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Good first contributions include tests, provider metadata, output formatting, and small evaluation utilities.

## Security

Never commit API keys. Venom reads credentials from provider SDK environment variables. If you accidentally publish a key, revoke it with the provider immediately. See [SECURITY.md](SECURITY.md) for more detail.

## License

MIT — see [LICENSE](LICENSE).
