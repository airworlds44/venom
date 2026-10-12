from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

_REQUIRED_FIELDS = ("provider", "model", "prompt", "response")


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(target.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"Line {line_number} must contain a JSON object.")
        missing = [field for field in _REQUIRED_FIELDS if field not in row]
        if missing:
            raise ValueError(
                f"Line {line_number} is missing required field(s): {', '.join(missing)}"
            )
        rows.append(row)
    if not rows:
        raise ValueError("Run file contains no results.")
    return rows


def _format_optional(value: Any, *, suffix: str = "") -> str:
    if value is None:
        return "—"
    return escape(f"{value}{suffix}")


def build_html(rows: list[dict[str, Any]], *, title: str = "Venom comparison report") -> str:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["prompt"]), []).append(row)

    sections: list[str] = []
    for prompt, results in grouped.items():
        cards: list[str] = []
        for row in results:
            provider = escape(str(row["provider"]))
            model = escape(str(row["model"]))
            response = escape(str(row["response"]))
            latency = _format_optional(row.get("latency_ms"), suffix=" ms")
            input_tokens = _format_optional(row.get("input_tokens"))
            output_tokens = _format_optional(row.get("output_tokens"))
            created_at = _format_optional(row.get("created_at"))
            cost = row.get("estimated_cost_usd")
            cost_text = "—" if cost is None else escape(f"${cost}")
            cards.append(
                f"""
                <article class="card">
                  <h3>{provider}<span>:</span>{model}</h3>
                  <dl>
                    <div><dt>Latency</dt><dd>{latency}</dd></div>
                    <div><dt>Tokens in/out</dt><dd>{input_tokens} / {output_tokens}</dd></div>
                    <div><dt>Estimated cost</dt><dd>{cost_text}</dd></div>
                    <div><dt>Created</dt><dd>{created_at}</dd></div>
                  </dl>
                  <pre>{response}</pre>
                </article>
                """
            )
        sections.append(
            f"""
            <section>
              <h2>Prompt</h2>
              <pre class="prompt">{escape(prompt)}</pre>
              <div class="grid">{''.join(cards)}</div>
            </section>
            """
        )

    safe_title = escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    :root {{ color-scheme: light dark; font-family: ui-sans-serif, system-ui, sans-serif; }}
    body {{ max-width: 1200px; margin: 0 auto; padding: 2rem; line-height: 1.5; }}
    header {{ margin-bottom: 2rem; }}
    section {{ margin: 2rem 0 3rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; }}
    .card {{ border: 1px solid color-mix(in srgb, currentColor 22%, transparent); border-radius: 12px; padding: 1rem; }}
    h1, h2, h3 {{ line-height: 1.2; }}
    h3 span {{ opacity: .55; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; padding: 1rem; border-radius: 8px; background: color-mix(in srgb, currentColor 7%, transparent); }}
    .prompt {{ font-weight: 600; }}
    dl {{ margin: .5rem 0 1rem; }}
    dl div {{ display: flex; justify-content: space-between; gap: 1rem; border-bottom: 1px solid color-mix(in srgb, currentColor 12%, transparent); padding: .25rem 0; }}
    dt {{ opacity: .7; }}
    dd {{ margin: 0; text-align: right; }}
  </style>
</head>
<body>
  <header>
    <h1>{safe_title}</h1>
    <p>{len(rows)} run(s) across {len(grouped)} prompt(s). Generated from saved Venom JSONL; no model calls were made.</p>
  </header>
  {''.join(sections)}
</body>
</html>
"""


def generate_html_report(
    input_path: str | Path,
    output_path: str | Path,
    *,
    title: str = "Venom comparison report",
) -> int:
    rows = load_jsonl(input_path)
    html = build_html(rows, title=title)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return len(rows)
