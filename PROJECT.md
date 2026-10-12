# Venom project overview

Venom is an open-source, vendor-neutral Python CLI for making AI model comparisons reproducible instead of relying on copy/paste between chat tabs.

## The problem

Indie builders and small teams often want to answer practical questions such as:

- How did two models respond to the same prompt?
- Which response satisfied a deterministic requirement?
- How long did each request take?
- How many input/output tokens were reported?
- What would the run cost under a pricing table I control?
- Can I save the evidence and inspect it later or in CI?

Large evaluation platforms can solve parts of this problem, but they may be more infrastructure than a small project needs. Venom deliberately focuses on a local, inspectable workflow built from plain files and small commands.

## Who it is for

Venom is currently aimed at:

- indie developers and solo builders comparing models during product development
- open-source maintainers who want simple repeatable model checks
- researchers or students who need lightweight saved comparison artifacts
- small teams that want deterministic checks in CI without adopting a hosted evaluation platform

The project is early alpha. These are target users, not claims about current adoption.

## What works today

The current codebase includes:

- OpenAI and Anthropic provider adapters
- single-model runs and multi-model comparisons
- reusable prompt suites from JSON or YAML
- JSONL run records with response, latency, timestamp, and provider/model metadata
- input/output token capture when the provider SDK exposes it
- opt-in cost estimation from a user-supplied pricing table
- deterministic `contains`, `exact`, and `regex` scoring
- self-contained HTML comparison reports
- a non-interactive benchmark command that writes run, score, report, and summary artifacts
- provider-failure isolation in multi-run workflows
- Python 3.10–3.13 CI coverage
- source/wheel build validation and clean-environment CLI smoke tests in CI
- a tag-triggered GitHub Release workflow that validates artifacts before publication
- a no-API synthetic demo path for first-time testers

See [README.md](README.md) for commands and [ARCHITECTURE.md](ARCHITECTURE.md) for the implementation model.

## Design position

Venom tries to stay small enough that a contributor can understand the core data flow without learning a framework-specific evaluation system.

The project favors:

- portable JSON/JSONL/YAML/HTML artifacts
- explicit provider adapters instead of provider-specific behavior leaking through the codebase
- deterministic scoring before LLM-as-a-judge
- user-controlled pricing rather than bundled prices that silently become stale
- environment-variable credentials handled by provider SDKs rather than a Venom credential store
- independent failures during comparisons and suites where practical

## Current status

`pyproject.toml` declares version `0.1.0`. The repository is being treated as an early-alpha release candidate until an actual version tag/GitHub Release is published and verified.

The feature foundation is substantially implemented and tested. The most important remaining product question is no longer “can more features be added?” but “does this workflow help people who did not build it?”

The active validation goal is tracked in [issue #13](https://github.com/airworlds44/venom/issues/13): get concrete feedback from at least three independent external testers and fix a repeated usability problem before expanding the major feature set.

No user-count, revenue, funding, production-usage, or adoption claim should be inferred from this document. Those should only be added when there is real evidence.

## Near-term priorities

1. Complete external-user validation and capture reproducible feedback.
2. Fix repeated onboarding or usability problems discovered by testers.
3. Publish and verify a real `v0.1.0` GitHub Release when the maintainer is ready to make that explicit publication step.
4. Enable the static `docs/` site through GitHub Pages or another static host if a public landing-page URL is useful.
5. Consider PyPI trusted publishing separately after the release/install workflow is proven.

## Open-source direction

Venom should grow based on real usage rather than commit volume. Useful future work is expected to come from concrete needs: additional provider metadata, report accessibility, deterministic evaluation utilities, packaging improvements, or ergonomics discovered through user feedback.

The repository welcomes focused issues and pull requests; see [CONTRIBUTING.md](CONTRIBUTING.md) and [TESTING.md](TESTING.md).
