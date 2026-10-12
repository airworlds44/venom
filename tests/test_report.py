import json

import pytest

from venom.report import build_html, generate_html_report, load_jsonl


def test_build_html_groups_prompts_and_escapes_content():
    rows = [
        {
            "provider": "openai",
            "model": "model-a",
            "prompt": "Compare <one> & two",
            "response": "<script>alert('x')</script>",
            "latency_ms": 12.3,
        },
        {
            "provider": "anthropic",
            "model": "model-b",
            "prompt": "Compare <one> & two",
            "response": "safe & sound",
            "latency_ms": 15.0,
        },
    ]

    html = build_html(rows)

    assert "2 run(s) across 1 prompt(s)" in html
    assert "Compare &lt;one&gt; &amp; two" in html
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in html
    assert "<script>alert('x')</script>" not in html


def test_generate_html_report_supports_older_run_files(tmp_path):
    runs = tmp_path / "runs.jsonl"
    runs.write_text(
        json.dumps(
            {
                "provider": "openai",
                "model": "model-a",
                "prompt": "hello",
                "response": "world",
                "latency_ms": 10,
                "created_at": "2026-10-12T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "report.html"

    count = generate_html_report(runs, output)

    assert count == 1
    text = output.read_text(encoding="utf-8")
    assert "world" in text
    assert "Tokens in/out" in text


def test_load_jsonl_reports_line_number_for_invalid_json(tmp_path):
    runs = tmp_path / "runs.jsonl"
    runs.write_text('{"provider": "openai"}\nnot-json\n', encoding="utf-8")

    with pytest.raises(ValueError, match="missing required field"):
        load_jsonl(runs)


def test_load_jsonl_rejects_empty_file(tmp_path):
    runs = tmp_path / "runs.jsonl"
    runs.write_text("\n", encoding="utf-8")

    with pytest.raises(ValueError, match="no results"):
        load_jsonl(runs)
