# Releasing Venom

This checklist is for maintainers preparing a public Venom release. It is intentionally conservative: do not mark a distribution channel as published until the corresponding artifact is actually available there.

## Before tagging

1. Confirm `pyproject.toml` has the intended version.
2. Update `CHANGELOG.md` with user-visible changes.
3. Run the full test suite on supported Python versions.
4. Confirm the `package` CI job builds both source and wheel distributions, passes `twine check`, and smoke-tests the wheel.
5. Review the synthetic demo and documentation for accidental credentials or private prompts.
6. Merge all intended release changes into `main` and make sure `main` CI is green.

## GitHub release

The repository's `Release` workflow is triggered only by version tags matching `v*.*.*`. It verifies that the tag version exactly matches `project.version` in `pyproject.toml`, rebuilds and validates the distributions, smoke-tests the wheel, and then creates a GitHub Release with the source and wheel artifacts.

For example, after verifying that `pyproject.toml` says `0.1.0`:

```bash
git checkout main
git pull --ff-only
git tag -a v0.1.0 -m "Venom 0.1.0"
git push origin v0.1.0
```

Pushing the tag is the explicit publication action. If the version does not match `pyproject.toml`, or if build/package validation fails, the workflow stops before creating a release.

After the workflow succeeds, inspect the GitHub Release and only then change documentation from "release candidate" / "unreleased" wording to published-release wording.

## PyPI

PyPI publication is intentionally separate from the GitHub Release workflow. Configure PyPI trusted publishing (preferred) or another narrowly scoped publishing credential before adding any PyPI upload step. Do not store PyPI tokens in the repository.

After publishing to PyPI, verify the package page and test installation in a clean environment before updating README text to claim PyPI availability.

## After release

- verify the GitHub Release points to the expected tag and commit
- verify the attached wheel and source distribution are present
- verify installation instructions against the released artifact
- change the matching changelog heading from `unreleased` to the actual release date
- open follow-up issues for any discovered packaging or documentation problems
- keep provider API keys, benchmark prompts, and private benchmark results out of public release artifacts
