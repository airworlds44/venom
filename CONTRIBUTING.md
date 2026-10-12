# Contributing to Venom

Thanks for considering a contribution. Venom is intentionally small, so focused changes with clear tests are preferred over broad framework rewrites.

If you are trying Venom rather than changing code, start with [TESTING.md](TESTING.md). First-user feedback is useful even when you do not plan to submit a pull request.

## Useful contribution areas

Current contribution areas include:

- improve error messages and CLI ergonomics
- expand tests for malformed JSONL, YAML, pricing, and scorer configuration
- improve Windows installation and shell examples
- improve accessibility/readability of generated HTML reports
- improve provider usage-metadata handling while preserving backwards-compatible JSONL output
- add small deterministic evaluation utilities with clear, reproducible behavior
- improve packaging, documentation, and examples

Before starting a larger feature, open an issue so the scope can stay aligned with the project's deliberately small design.

## Development

Requires Python 3.10+.

```bash
git clone https://github.com/airworlds44/venom.git
cd venom
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

The GitHub Actions test matrix currently covers Python 3.10 through 3.13. Pull requests should keep that matrix green.

## Pull requests

Please keep pull requests focused and explain the user-facing reason for the change. Add or update tests when behavior changes. Documentation-only fixes do not need artificial code changes.

Do not commit API keys, provider credentials, PyPI tokens, generated secrets, private prompts, or sensitive benchmark results. If a credential is exposed, revoke/rotate it rather than relying on deletion from Git history.

## Project boundaries

Venom aims to stay understandable and reproducible. In particular:

- deterministic scoring is preferred over adding an LLM judge by default
- provider pricing should not be hardcoded as if it were permanent
- provider failures should remain isolated where practical
- saved result formats should remain simple and portable
- activity should represent real maintenance or product work, not filler commits/issues
