from __future__ import annotations

import argparse
import json
import sys

from .core import append_jsonl, execute, parse_model_spec


def _cmd_run(args: argparse.Namespace) -> int:
    result = execute(args.provider, args.model, args.prompt)
    if args.out:
        append_jsonl(args.out, result)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    had_error = False
    for spec in args.models:
        try:
            provider, model = parse_model_spec(spec)
            result = execute(provider, model, args.prompt)
            append_jsonl(args.out, result)
            print(f"\n=== {provider}:{model} ===\n{result.response}\n")
        except Exception as exc:  # CLI boundary: report provider failures independently
            had_error = True
            print(f"ERROR {spec}: {exc}", file=sys.stderr)
    return 1 if had_error else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="venom", description="Compare AI model responses reproducibly.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run one prompt against one model.")
    run.add_argument("--provider", required=True, choices=["openai", "anthropic"])
    run.add_argument("--model", required=True)
    run.add_argument("--prompt", required=True)
    run.add_argument("--out", help="Optional JSONL output path.")
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
    compare.set_defaults(func=_cmd_compare)

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
