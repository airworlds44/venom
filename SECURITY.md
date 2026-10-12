# Security Policy

Venom is an early-stage developer tool that makes requests to third-party AI providers using credentials supplied through their normal SDK environment variables.

## Reporting a vulnerability

Please do **not** post sensitive vulnerability details, API keys, tokens, or private provider responses in a public GitHub issue.

For non-sensitive security hardening ideas, open a normal GitHub issue and describe the affected component and expected behavior without including secrets.

If a report requires sharing sensitive details, contact the maintainer privately through a GitHub-supported private channel when one is available. Until a dedicated security contact is published, avoid sending secrets through public repository discussions.

## API keys

Venom does not intentionally persist provider API keys. Credentials are read by provider SDKs from environment variables such as `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.

If a credential is accidentally committed, pasted into an issue, included in logs, or otherwise exposed:

1. revoke or rotate it with the provider immediately;
2. remove it from the public location;
3. do not rely on deleting a Git commit as the only remediation, because copied credentials may already have been observed.

## Output sensitivity

`runs.jsonl`, `scores.jsonl`, HTML reports, and benchmark summaries can contain prompts and model responses. Treat those artifacts according to the sensitivity of the data you send to providers. Do not publish benchmark artifacts that contain confidential or personal information.

## Supported versions

Security fixes currently target the latest code on `main` while Venom is in early alpha. A formal supported-version policy will be added if stable releases are published.
