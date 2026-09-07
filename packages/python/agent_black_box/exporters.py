from __future__ import annotations

from xml.sax.saxutils import escape

from .models import TraceEnvelope
from .policy import PolicyFinding


def trace_markdown(trace: TraceEnvelope) -> str:
    lines = [
        f"# Agent trace {trace.run_id}",
        "",
        f"- Application: {trace.app}",
        f"- Events: {len(trace.events)}",
        f"- Tool calls: {len(trace.tools())}",
        "",
        "## Timeline",
    ]
    for event in trace.events:
        lines.append(f"- `{event.kind}` {event.timestamp}: {event.summary}")
    return "\n".join(lines) + "\n"


def findings_junit(findings: list[PolicyFinding], *, suite_name: str = "agent-black-box-policy") -> str:
    failures = len(findings)
    lines = [f'<testsuite name="{escape(suite_name)}" tests="{max(failures, 1)}" failures="{failures}">']
    if not findings:
        lines.append('<testcase name="policy-clean" />')
    for finding in findings:
        lines.append(f'<testcase name="{escape(finding.code)}">')
        lines.append(f'<failure type="{escape(finding.severity)}">{escape(finding.message)}</failure>')
        lines.append("</testcase>")
    lines.append("</testsuite>")
    return "\n".join(lines) + "\n"
