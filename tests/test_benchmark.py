import json

from venom.benchmark import run_benchmark
from venom.models import RunResult


def _write_suite(path, prompts):
    path.write_text(
        json.dumps({"prompts": [{"name": name, "prompt": prompt} for name, prompt in prompts]}),
        encoding="utf-8",
    )


def test_benchmark_replaces_owned_artifacts_and_writes_summary(tmp_path, monkeypatch):
    suite = tmp_path / "suite.json"
    _write_suite(suite, [("one", "first prompt"), ("two", "second prompt")])

    rules = tmp_path / "rules.json"
    rules.write_text(
        json.dumps({"scorers": [{"name": "has-answer", "type": "contains", "value": "answer"}]}),
        encoding="utf-8",
    )

    def fake_execute(provider, model, prompt, *, pricing=None):
        return RunResult.create(
            provider=provider,
            model=model,
            prompt=prompt,
            response=f"answer for {prompt}",
            latency_ms=10,
            input_tokens=5,
            output_tokens=7,
            estimated_cost_usd=0.001,
        )

    monkeypatch.setattr("venom.benchmark.execute", fake_execute)
    out = tmp_path / "artifacts"
    out.mkdir()
    for name in ("runs.jsonl", "scores.jsonl", "report.html", "summary.json"):
        (out / name).write_text("stale-data", encoding="utf-8")

    summary = run_benchmark(
        suite,
        ["openai:test-model"],
        out,
        scoring_rules=rules,
        report_title="Test report",
    )

    assert summary["planned_runs"] == 2
    assert summary["successful_runs"] == 2
    assert summary["run_failure_count"] == 0
    assert summary["score_checks"] == 2
    assert summary["score_failures"] == 0
    assert summary["priced_runs"] == 2
    assert summary["estimated_cost_usd"] == 0.002
    assert summary["all_passed"] is True

    lines = (out / "runs.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert "stale-data" not in (out / "runs.jsonl").read_text(encoding="utf-8")
    assert (out / "scores.jsonl").exists()
    assert "Test report" in (out / "report.html").read_text(encoding="utf-8")

    saved_summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert saved_summary["successful_runs"] == 2


def test_benchmark_isolates_provider_failures(tmp_path, monkeypatch):
    suite = tmp_path / "suite.json"
    _write_suite(suite, [("good", "good prompt"), ("bad", "bad prompt")])

    def fake_execute(provider, model, prompt, *, pricing=None):
        if prompt == "bad prompt":
            raise RuntimeError("provider unavailable")
        return RunResult.create(
            provider=provider,
            model=model,
            prompt=prompt,
            response="ok",
            latency_ms=5,
        )

    monkeypatch.setattr("venom.benchmark.execute", fake_execute)
    out = tmp_path / "artifacts"

    summary = run_benchmark(suite, ["anthropic:test-model"], out)

    assert summary["planned_runs"] == 2
    assert summary["successful_runs"] == 1
    assert summary["run_failure_count"] == 1
    assert summary["run_failures"][0]["prompt"] == "bad"
    assert "provider unavailable" in summary["run_failures"][0]["error"]
    assert summary["all_passed"] is False
    assert (out / "report.html").exists()
