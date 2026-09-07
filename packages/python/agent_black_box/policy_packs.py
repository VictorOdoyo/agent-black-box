from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .models import TraceEnvelope
from .policy import PolicyConfig, PolicyFinding, evaluate_trace


@dataclass
class PolicyPack:
    name: str
    max_tool_duration_ms: int = 30000
    max_error_events: int = 0
    denied_tools: set[str] = field(default_factory=set)
    required_tags: set[str] = field(default_factory=set)


def load_policy_pack(path: str | Path) -> PolicyPack:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return PolicyPack(
        name=str(payload["name"]),
        max_tool_duration_ms=int(payload.get("max_tool_duration_ms", 30000)),
        max_error_events=int(payload.get("max_error_events", 0)),
        denied_tools=set(payload.get("denied_tools", [])),
        required_tags=set(payload.get("required_tags", [])),
    )


def evaluate_policy_pack(trace: TraceEnvelope, pack: PolicyPack) -> list[PolicyFinding]:
    findings = evaluate_trace(trace, PolicyConfig(pack.max_tool_duration_ms, pack.max_error_events))
    for event in trace.tools():
        tool_name = str(event.payload.get("name"))
        if tool_name in pack.denied_tools:
            findings.append(PolicyFinding("denied_tool", "critical", f"Tool {tool_name} is denied by policy pack.", event.id))
    present_tags = {tag for event in trace.events for tag in event.tags}
    missing_tags = pack.required_tags - present_tags
    for tag in sorted(missing_tags):
        findings.append(PolicyFinding("missing_required_tag", "medium", f"Required tag {tag!r} was not present."))
    return findings
