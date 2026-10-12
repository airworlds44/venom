from __future__ import annotations

import argparse
import json
import sys

from .core import append_jsonl, execute, parse_model_spec
from .pricing import PricingTable, load_pricing
from .suites import load_suite


def _load_optional_pricing(path: str | None) -> PricingTable | None:
    return load_pricing(path) if path else None


def _usage_summary(result) -> str:
    parts: list[str] = []
    if result.input_tokens is not None and result.output_tokens is not None:
        parts.append(f"tokens in/out: {result.input_tokens}/{result.output_tokens}")
    if result.estimated_cost_usd is not None:
        parts.append(f"estimated cost: ${result.estimated_cost_usd:.8f}")
    return " | ".join(parts)


def _cmd_run(args: argparse.Namespace) -> int:
    pricing = _load_optional_pricing(args.pricing)
    result = execute(args.provider, args.model, args.prompt, pricing=pricing)
    if args.out:
        append_jsonl(args.out, result)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    pricing = _load_optional_pricing(args.pricing)
    had_error = False
    for spec in args.models:
        try:
            provider, model = parse_model_spec(spec)
            result = execute(provider, model, args.prompt, pricing=pricing)
            append_jsonl(args.out, result)
            summary = _usage_summary(result)
            suffix = f"\n{summary}" if summary else ""
            print(f"\n=== {provider}:{model} ==={suffix}\n{result.response}\n")
        except Exception as exc:  # CLI boundary: report provider failures independently
            had_error = True
            print(f"ERROR {spec}: {exc}", file=sys.stderr)
    return 1 if had_error else 0


def _cmd_suite(args: argparse.Namespace) -> int:
    pricing = _load_optional_pricing(args.pricing)
    cases = load_suite(args.file)
    had_error = False

    for case in cases:
        for spec in args.models:
            try:
                provider, model = parse_model_spec(spec)
                result = execute(provider, model, case.prompt, pricing=pricing)
                append_jsonl(args.out, result)
                summary = _usage_summary(result)
                suffix = f"\n{summary}" if summary else ""
                print(f"\n=== {case.name} | {provider}:{model} ==={suffix}\n{result.response}\n")
            except Exception as exc:  # keep independent runs from blocking the rest of a suite
                had_error = True
                print(f"ERROR {case.name} | {spec}: {exc}", file=sys.stderr)

    return 1 if had_error else 0


def _add_pricing_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--pricing",
        help="Optional JSON pricing table keyed by provider:model. Unknown models are never priced.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="venom", description="Compare AI model responses reproducibly.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run one prompt against one model.")
    run.add_argument("--provider", required=True, choices=["openai", "anthropic"])
    run.add_argument("--model", required=True)
    run.add_argument("--prompt", required=True)
    run.add_argument("--out", help="Optional JSONL output path.")
    _add_pricing_argument(run)
    run.set_defaults(func=_cmd_run)

    compare = sub.add_parser("compare", help="Run one prompt against multiple provider:model pairs.")
    compare.add_argument(
        "--model",
        dest="models",
        action="append",
        required=True,
        help="Repeatable provider:model value, e.g. openai:YOUR_MODEL",
    )
    compare.add_argument("--prompt", required=True)
    compare.add_argument("--out", default="runs.jsonl")
    _add_pricing_argument(compare)
    compare.set_defaults(func=_cmd_compare)

    suite = sub.add_parser("suite", help="Run a JSON/YAML prompt suite against one or more models.")
    suite.add_argument("--file", required=True, help="Path to a .json, .yaml, or .yml prompt suite.")
    suite.add_argument(
        "--model",
        dest="models",
        action="append",
        required=True,
        help="Repeatable provider:model value, e.g. openai:YOUR_MODEL",
    )
    suite.add_argument("--out", default="runs.jsonl")
    _add_pricing_argument(suite)
    suite.set_defaults(func=_cmd_suite)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        raise SystemExit(args.func(args))
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
