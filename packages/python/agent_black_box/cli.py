from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compare import compare_traces
from .exporters import findings_junit, trace_markdown
from .models import TraceEnvelope
from .policy import evaluate_trace
from .redaction import redaction_preview, redact_value
from .replay import replay_plan
from .schemas import validate_trace_dict


def load_trace(path: str | Path) -> TraceEnvelope:
    return TraceEnvelope.from_json(Path(path).read_text(encoding="utf-8"))


def cmd_inspect(args: argparse.Namespace) -> int:
    trace = load_trace(args.trace)
    print(f"run_id: {trace.run_id}")
    print(f"app: {trace.app}")
    print(f"events: {len(trace.events)}")
    print(f"tools: {len(trace.tools())}")
    for kind, count in sorted(trace.event_counts().items()):
        print(f"{kind}: {count}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.trace).read_text(encoding="utf-8"))
    errors = validate_trace_dict(payload)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("trace is valid")
    return 0


def cmd_policy(args: argparse.Namespace) -> int:
    findings = evaluate_trace(load_trace(args.trace))
    if args.junit:
        Path(args.junit).write_text(findings_junit(findings), encoding="utf-8", newline="\n")
    for finding in findings:
        print(f"{finding.severity.upper()} {finding.code}: {finding.message}")
    return 1 if any(finding.severity in {"critical", "high"} for finding in findings) else 0


def cmd_replay(args: argparse.Namespace) -> int:
    for line in replay_plan(load_trace(args.trace)):
        print(line)
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    comparison = compare_traces(load_trace(args.left), load_trace(args.right))
    print(comparison.to_markdown())
    return 0 if comparison.first_divergence_index is None else 1


def cmd_redact(args: argparse.Namespace) -> int:
    trace = load_trace(args.trace)
    payload, count = redact_value(trace.to_dict())
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"redactions: {count}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    trace = load_trace(args.trace)
    Path(args.output).write_text(trace_markdown(trace), encoding="utf-8", newline="\n")
    print(args.output)
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    print(json.dumps(redaction_preview(payload), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="abb", description="Inspect, redact, replay, and compare AI agent traces.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    inspect = subcommands.add_parser("inspect")
    inspect.add_argument("trace")
    inspect.set_defaults(func=cmd_inspect)

    validate = subcommands.add_parser("validate")
    validate.add_argument("trace")
    validate.set_defaults(func=cmd_validate)

    policy = subcommands.add_parser("policy")
    policy.add_argument("trace")
    policy.add_argument("--junit")
    policy.set_defaults(func=cmd_policy)

    replay = subcommands.add_parser("replay")
    replay.add_argument("trace")
    replay.set_defaults(func=cmd_replay)

    compare = subcommands.add_parser("compare")
    compare.add_argument("left")
    compare.add_argument("right")
    compare.set_defaults(func=cmd_compare)

    redact = subcommands.add_parser("redact")
    redact.add_argument("trace")
    redact.add_argument("output")
    redact.set_defaults(func=cmd_redact)

    export = subcommands.add_parser("export")
    export.add_argument("trace")
    export.add_argument("output")
    export.set_defaults(func=cmd_export)

    preview = subcommands.add_parser("preview-redaction")
    preview.add_argument("payload")
    preview.set_defaults(func=cmd_preview)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
