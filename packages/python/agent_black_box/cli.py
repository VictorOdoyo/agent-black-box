from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compare import compare_traces
from .dot import trace_to_dot
from .exporters import findings_junit, trace_markdown
from .filters import filter_events
from .integrity import trace_manifest, verify_manifest
from .metrics import calculate_metrics
from .minimize import minimize_trace
from .models import TraceEnvelope
from .policy import evaluate_trace
from .policy_packs import evaluate_policy_pack, load_policy_pack
from .redaction import redaction_preview, redact_value
from .replay import replay_plan
from .schemas import validate_trace_dict
from .stream import read_jsonl, write_jsonl
from .transcript import render_transcript


def load_trace(path: str | Path) -> TraceEnvelope:
    return TraceEnvelope.from_json(Path(path).read_text(encoding="utf-8"))


def cmd_inspect(args: argparse.Namespace) -> int:
    trace = load_trace(args.trace)
    metrics = calculate_metrics(trace)
    print(f"run_id: {trace.run_id}")
    print(f"app: {trace.app}")
    print(f"events: {metrics.event_count}")
    print(f"tools: {metrics.tool_count}")
    print(f"errors: {metrics.error_count}")
    print(f"tool_duration_ms: {metrics.total_tool_duration_ms}")
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
    trace = load_trace(args.trace)
    findings = evaluate_policy_pack(trace, load_policy_pack(args.pack)) if args.pack else evaluate_trace(trace)
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


def cmd_metrics(args: argparse.Namespace) -> int:
    print(json.dumps(calculate_metrics(load_trace(args.trace)).__dict__, indent=2))
    return 0


def cmd_manifest(args: argparse.Namespace) -> int:
    manifest = trace_manifest(load_trace(args.trace))
    output = json.dumps(manifest, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8", newline="\n")
    else:
        print(output, end="")
    return 0


def cmd_verify_manifest(args: argparse.Namespace) -> int:
    trace = load_trace(args.trace)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    findings = verify_manifest(trace, manifest)
    for finding in findings:
        print(f"{finding.code}: {finding.message}")
    return 1 if findings else 0


def cmd_minimize(args: argparse.Namespace) -> int:
    minimized = minimize_trace(load_trace(args.trace), keep_kinds=set(args.kind), keep_tags=set(args.tag), window=args.window)
    Path(args.output).write_text(minimized.to_json(), encoding="utf-8", newline="\n")
    print(f"events: {len(minimized.events)}")
    return 0


def cmd_jsonl_write(args: argparse.Namespace) -> int:
    write_jsonl(load_trace(args.trace), args.output)
    print(args.output)
    return 0


def cmd_jsonl_read(args: argparse.Namespace) -> int:
    trace = read_jsonl(args.input)
    Path(args.output).write_text(trace.to_json(), encoding="utf-8", newline="\n")
    print(args.output)
    return 0


def cmd_events(args: argparse.Namespace) -> int:
    trace = load_trace(args.trace)
    for event in filter_events(trace, query=args.query, kinds=set(args.kind), tags=set(args.tag), actor=args.actor):
        print(f"{event.id}\t{event.kind}\t{event.summary}")
    return 0


def cmd_dot(args: argparse.Namespace) -> int:
    dot = trace_to_dot(load_trace(args.trace))
    if args.output:
        Path(args.output).write_text(dot, encoding="utf-8", newline="\n")
    else:
        print(dot, end="")
    return 0


def cmd_transcript(args: argparse.Namespace) -> int:
    transcript = render_transcript(load_trace(args.trace))
    if args.output:
        Path(args.output).write_text(transcript, encoding="utf-8", newline="\n")
    else:
        print(transcript, end="")
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
    policy.add_argument("--pack")
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

    metrics = subcommands.add_parser("metrics")
    metrics.add_argument("trace")
    metrics.set_defaults(func=cmd_metrics)

    manifest = subcommands.add_parser("manifest")
    manifest.add_argument("trace")
    manifest.add_argument("--output")
    manifest.set_defaults(func=cmd_manifest)

    verify = subcommands.add_parser("verify-manifest")
    verify.add_argument("trace")
    verify.add_argument("manifest")
    verify.set_defaults(func=cmd_verify_manifest)

    minimize = subcommands.add_parser("minimize")
    minimize.add_argument("trace")
    minimize.add_argument("output")
    minimize.add_argument("--kind", action="append", default=[])
    minimize.add_argument("--tag", action="append", default=[])
    minimize.add_argument("--window", type=int, default=0)
    minimize.set_defaults(func=cmd_minimize)

    write_jsonl_parser = subcommands.add_parser("write-jsonl")
    write_jsonl_parser.add_argument("trace")
    write_jsonl_parser.add_argument("output")
    write_jsonl_parser.set_defaults(func=cmd_jsonl_write)

    read_jsonl_parser = subcommands.add_parser("read-jsonl")
    read_jsonl_parser.add_argument("input")
    read_jsonl_parser.add_argument("output")
    read_jsonl_parser.set_defaults(func=cmd_jsonl_read)

    events = subcommands.add_parser("events")
    events.add_argument("trace")
    events.add_argument("--query", default="")
    events.add_argument("--kind", action="append", default=[])
    events.add_argument("--tag", action="append", default=[])
    events.add_argument("--actor")
    events.set_defaults(func=cmd_events)

    dot = subcommands.add_parser("dot")
    dot.add_argument("trace")
    dot.add_argument("--output")
    dot.set_defaults(func=cmd_dot)

    transcript = subcommands.add_parser("transcript")
    transcript.add_argument("trace")
    transcript.add_argument("--output")
    transcript.set_defaults(func=cmd_transcript)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
