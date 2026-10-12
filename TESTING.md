# Try Venom in five minutes

This guide is for people trying Venom for the first time. You can complete the basic path without an OpenAI or Anthropic API key.

Please do **not** post API keys, private prompts, customer data, or sensitive benchmark output in issues or screenshots.

## 1. Clone and install

Venom requires Python 3.10 or newer.

### macOS / Linux

```bash
git clone https://github.com/airworlds44/venom.git
cd venom
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

### Windows PowerShell

```powershell
git clone https://github.com/airworlds44/venom.git
cd venom
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

If PowerShell blocks activation, you can also call the virtual environment's Python directly instead of changing your execution policy.

## 2. Run the no-API demo

The committed input file is synthetic fixture data, not a live OpenAI/Anthropic benchmark.

```bash
venom report --input examples/demo-runs.jsonl --out demo-report.html --title "Venom synthetic demo"
```

Open `demo-report.html` in a browser. You should see two example model cards for one recursion prompt.

Also check the CLI entry point:

```bash
venom --help
```

At this point you have tested installation, the command-line entry point, JSONL parsing, and HTML report generation without spending API credits.

## 3. Optional: try your own provider account

Only do this if you are comfortable using your own API account and its normal provider charges/limits.

### macOS / Linux

```bash
export OPENAI_API_KEY="your-key-here"
# or: export ANTHROPIC_API_KEY="your-key-here"
```

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="your-key-here"
# or: $env:ANTHROPIC_API_KEY="your-key-here"
```

Then use a model ID available to your account:

```bash
venom run --provider openai --model YOUR_OPENAI_MODEL --prompt "Explain recursion in one sentence."
```

or:

```bash
venom run --provider anthropic --model YOUR_CLAUDE_MODEL --prompt "Explain recursion in one sentence."
```

For a fuller comparison, see the prompt-suite and benchmark examples in the main README.

## 4. Tell us what happened

Useful feedback is concrete and reproducible. Please include:

- operating system and Python version
- which path you tried (demo, live run, suite, scoring, benchmark)
- the command that was confusing or failed
- the error message with secrets/private data removed
- whether Venom would solve a real problem for you and what is missing

Use the repository's **Usability feedback** issue form, or add a comment to [issue #13](https://github.com/airworlds44/venom/issues/13) if you are participating in the first-user validation round.

A star is appreciated if you genuinely find the project useful, but feedback is more valuable than a vanity metric.
