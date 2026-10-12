from pathlib import Path

from venom.report import generate_html_report, load_jsonl


ROOT = Path(__file__).resolve().parents[1]


def test_committed_demo_fixture_is_valid_and_renderable(tmp_path):
    fixture = ROOT / "examples" / "demo-runs.jsonl"
    rows = load_jsonl(fixture)

    assert len(rows) == 2
    assert {row["provider"] for row in rows} == {"demo-openai", "demo-anthropic"}
    assert all(str(row["provider"]).startswith("demo-") for row in rows)

    output = tmp_path / "demo-report.html"
    count = generate_html_report(fixture, output, title="Venom synthetic demo")

    assert count == 2
    html = output.read_text(encoding="utf-8")
    assert "Venom synthetic demo" in html
    assert "Explain recursion in one sentence." in html
    assert "demo-openai" in html
    assert "demo-anthropic" in html
