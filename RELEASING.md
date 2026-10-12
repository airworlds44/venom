# Releasing Venom

This checklist is for maintainers preparing a public Venom release. It is intentionally conservative: do not mark a distribution channel as published until the corresponding artifact is actually available there.

## Before tagging

1. Confirm `pyproject.toml` has the intended version.
2. Update `CHANGELOG.md` with user-visible changes.
3. Run the full test suite on supported Python versions.
4. Build both source and wheel distributions and validate them with `twine check`.
5. Install the built wheel in a clean environment and confirm `venom --help` works.
6. Review the synthetic demo and documentation for accidental credentials or private prompts.

## GitHub release

Create an annotated `vX.Y.Z` tag from the tested commit, then create a GitHub Release using the matching changelog section. Attach the built wheel and source distribution if desired.

## PyPI

PyPI publication should use a dedicated trusted-publishing configuration or narrowly scoped publishing credential. Do not store PyPI tokens in the repository. After publishing, verify the package page and test installation in a clean environment before updating README text to claim PyPI availability.

## After release

- verify the GitHub Release points to the expected commit
- verify installation instructions against the released artifact
- open follow-up issues for any discovered packaging or documentation problems
- keep provider API keys, benchmark prompts, and private benchmark results out of public release artifacts
