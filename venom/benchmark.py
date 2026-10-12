from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .core import append_jsonl, execute, parse_model_spec
from .pricing import PricingTable
from .report import generate_html_report, load_jsonl
from .scoring import load_scorers, score_rows, write_scores_jsonl
from .suites import load_suite


def run_benchmark(
    suite_path: str | Path,
    models: list[str],
    out_dir: str | Path,
    *,
    pricing: PricingTable | None = None,
    scoring_rules: str | Path | None = None,
    report_title: str = "Venom benchmark report",
) -> dict[str, Any]:
    """Run a prompt suite and write reproducible benchmark artifacts.

    The command owns four artifact names inside ``out_dir`` and replaces those
    files on every invocation so previous benchmark data is never appended.
    """
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)

    runs_path = target / "runs.jsonl"
    scores_path = target / "scores.jsonl"
    report_path = target / "report.html"
    summary_path = target / "summary.json"

    for owned_path in (runs_path, scores_path, report_path, summary_path):
        if owned_path.exists():
            owned_path.unlink()

    cases = load_suite(suite_path)
    failures: list[dict[str, str]] = []
    successful_runs = 0
    estimated_cost_total = 0.0
    priced_runs = 0

    for case in cases:
        for spec in models:
            try:
                provider, model = parse_model_spec(spec)
                result = execute(provider, model, case.prompt, pricing=pricing)
                append_jsonl(runs_path, result)
                successful_runs += 1
                if result.estimated_cost_usd is not None:
                    estimated_cost_total += result.estimated_cost_usd
                    priced_runs += 1
            except Exception as exc:
                failures.append(
                    {
                        "prompt": case.name,
                        "model": spec,
                        "error": str(exc),
                    }
                )

    score_checks = 0
    score_failures = 0
    if successful_runs:
        generate_html_report(runs_path, report_path, title=report_title)

        if scoring_rules is not None:
            rows = load_jsonl(runs_path)
            specs = load_scorers(scoring_rules)
            score_results = score_rows(rows, specs)
            if not score_results:
                raise ValueError("No scorers applied to the benchmark runs.")
            write_scores_jsonl(scores_path, score_results)
            score_checks = len(score_results)
            score_failures = sum(not result.passed for result in score_results)

    summary: dict[str, Any] = {
        "suite": str(suite_path),
        "models": list(models),
        "planned_runs": len(cases) * len(models),
        "successful_runs": successful_runs,
        "run_failure_count": len(failures),
        "run_failures": failures,
        "score_checks": score_checks,
        "score_failures": score_failures,
        "priced_runs": priced_runs,
        "estimated_cost_usd": round(estimated_cost_total, 10) if priced_runs else None,
        "artifacts": {
            "runs": str(runs_path) if successful_runs else None,
            "scores": str(scores_path) if score_checks else None,
            "report": str(report_path) if successful_runs else None,
            "summary": str(summary_path),
        },
    }
    summary["all_passed"] = not failures and score_failures == 0

    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary
