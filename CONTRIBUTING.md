# Contributing to Venom

Thanks for considering a contribution.

## Good first contributions

- add tests for parsing and output behavior
- improve error messages
- add token/cost metadata without breaking the output format
- add a prompt-suite loader
- improve Windows setup instructions

## Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e . pytest
pytest
```

Please keep pull requests focused. Avoid committing API keys, generated secrets, or provider credentials.
