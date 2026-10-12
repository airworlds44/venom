# Venom architecture

Venom is intentionally a small Python CLI. The architecture keeps provider-specific API code at the edges and moves saved results through simple, portable data structures and files.

## High-level data flow

```text
CLI
 ├─ run / compare / suite
 │    └─ core.execute
 │         └─ provider adapter
 │              └─ ProviderResponse
 │         └─ RunResult
 │              └─ JSONL
 │
 ├─ score
 │    └─ saved JSONL + scorer config
 │         └─ ScoreResult JSONL
 │
 ├─ report
 │    └─ saved JSONL
 │         └─ self-contained HTML
 │
 └─ benchmark
      └─ suite × provider:model targets
           ├─ runs.jsonl
           ├─ optional scores.jsonl
           ├─ report.html
           └─ summary.json
```

## CLI boundary

`venom/cli.py` owns argument parsing and user-facing command behavior. The CLI should stay thin: parsing flags, loading optional configuration, calling library functions, printing summaries, and choosing exit codes.

The primary commands are:

- `venom run` — one provider/model and one prompt
- `venom compare` — one prompt across multiple `provider:model` targets
- `venom suite` — a JSON/YAML prompt suite across one or more models
- `venom score` — deterministic checks against already-saved runs
- `venom report` — an HTML report from already-saved runs
- `venom benchmark` — orchestration of suite execution, optional pricing/scoring, reporting, and a machine-readable summary

Keeping orchestration functions outside the argument parser makes them testable without shelling out to the CLI or making live API calls.

## Provider boundary

`venom/core.py` contains the small provider registry and `execute()` function. A provider function has the conceptual shape:

```python
(model: str, prompt: str) -> ProviderResponse
```

`ProviderResponse` normalizes provider output into:

- response text
- optional input-token count
- optional output-token count

The OpenAI adapter uses the OpenAI Responses API, while the Anthropic adapter uses Anthropic Messages. Their SDKs read `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` from the environment respectively. Venom does not introduce its own credential database.

This boundary is the main extension point for future providers: provider-specific SDK details should stay in a small adapter and return the same normalized response structure.

## Run results

`core.execute()` measures elapsed request time, calls the selected provider adapter, optionally estimates cost, and creates a `RunResult`.

A saved run is deliberately plain data: provider, model, prompt, response, latency, creation time, optional token usage, and optional estimated cost. `append_jsonl()` writes one JSON object per line so runs can be streamed, diffed, processed with standard tools, or consumed by notebooks without a database.

## Pricing

Pricing is external configuration rather than built-in model knowledge.

A pricing table is keyed by exact `provider:model` values. Cost estimation is only performed when both token usage and a matching price are available. Unknown models are left unpriced rather than assigned a guessed or stale rate.

This is a deliberate stability choice: provider prices change independently of Venom releases.

## Prompt suites

Prompt suites are loaded from JSON or YAML and normalized into named prompt cases. Suite execution is a Cartesian product of prompt cases and requested model targets.

Failures are handled per run where practical. One provider/model failure should not erase successful results from other prompt/model pairs.

## Deterministic scoring

`venom/scoring.py` treats scoring as a separate pass over saved result data. The first scoring layer is intentionally deterministic and local:

- `contains`
- `exact`
- `regex`

A scorer may optionally target one exact prompt. Each applied scorer produces a separate `ScoreResult` containing the provider, model, prompt, scorer name/type, pass/fail value, numeric `0.0` or `1.0` score, and short details.

This design keeps scoring reproducible and cheap. LLM-as-a-judge is not part of the default architecture because it introduces another model call, cost, nondeterminism, and judge-model configuration.

## Reports

`venom/report.py` reads saved run JSONL and generates one self-contained HTML file. Prompt and response content is escaped before insertion into HTML.

Reporting performs no provider calls. That separation allows old or synthetic run files to be rendered repeatedly without API credentials or additional cost.

## Benchmark orchestration

`venom/benchmark.py` composes the smaller parts rather than reimplementing them.

For each benchmark it:

1. creates/uses an output directory;
2. removes Venom-owned artifacts from a previous benchmark in that directory;
3. loads the prompt suite;
4. executes each prompt/model pair independently;
5. appends successful runs to `runs.jsonl`;
6. generates `report.html` when at least one run succeeded;
7. optionally scores successful runs and writes `scores.jsonl`;
8. writes `summary.json` with planned/successful runs, failures, scoring totals, optional cost totals, and artifact paths.

The summary is designed for automation while the HTML report is designed for humans.

## Testing and release boundaries

Tests use fake provider functions for orchestration logic so CI does not require provider API keys or spend model credits. The committed demo fixture is synthetic and has a regression test proving it remains parseable and renderable.

The CI workflow tests Python 3.10–3.13. A separate package job builds source/wheel distributions, validates metadata with `twine check`, installs the wheel into a clean virtual environment, runs `pip check`, smoke-tests the CLI, and retains the built distributions as a workflow artifact.

The `Release` workflow is separate from normal CI. It only runs for version tags matching `v*.*.*`, checks that the tag matches `project.version`, rebuilds and validates distributions, and creates a GitHub Release only after those checks pass.

## Security boundaries

Venom is designed not to become a secret-management system.

- provider SDKs obtain credentials from their normal environment variables;
- API keys should never be written into prompt suites, pricing files, examples, issues, or benchmark artifacts;
- reports may contain model responses and prompts, so users should treat real benchmark artifacts according to the sensitivity of their input data;
- generated model text is HTML-escaped before report rendering;
- publishing a benchmark directory is an explicit user decision, not an automatic Venom action.

See [SECURITY.md](SECURITY.md) for reporting guidance.

## Deliberate non-goals for the current alpha

The current architecture does not try to provide:

- a hosted evaluation service or multi-tenant backend
- a credential vault
- a permanent built-in provider pricing database
- a default LLM-as-a-judge pipeline
- a database or proprietary result format
- automatic publication of private prompts/results
- fabricated usage or contribution metrics

These limits keep the project understandable while its core workflow is being validated with real users.

## Extension principles

A proposed change fits the architecture best when it preserves the following properties:

1. provider-specific behavior remains isolated behind small adapters;
2. saved artifacts remain simple and portable;
3. offline scoring/reporting can operate without live model calls;
4. multi-run failures are isolated rather than all-or-nothing when practical;
5. changing external facts such as provider pricing are explicit user configuration;
6. new behavior can be tested without storing real API credentials in CI.
