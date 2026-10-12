# Changelog

All notable changes to Venom will be documented in this file.

## 0.1.0 — unreleased

First public alpha of Venom, a vendor-neutral CLI for reproducible AI model comparisons.

### Added

- OpenAI and Anthropic provider adapters
- single-prompt and multi-model comparison commands
- reusable JSON/YAML prompt suites
- JSONL run logging
- provider token-usage capture when available
- opt-in local cost estimation from user-supplied pricing tables
- deterministic `contains`, `exact`, and `regex` scoring
- self-contained HTML comparison reports
- non-interactive benchmark mode with `summary.json` output
- CI test matrix for Python 3.10–3.13

### Notes

- This is an early alpha release.
- Provider pricing is intentionally not bundled because pricing changes over time.
- Venom does not store or manage API credentials.
- A GitHub Release or PyPI package should only be advertised after it is actually published.
