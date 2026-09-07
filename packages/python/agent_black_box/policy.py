from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .models import EventKind, TraceEnvelope


SECRET_LEAK_PATTERN = re.compile(r"(gh[pous]_[A-Za-z0-9_]{16,}|Bearer\s+[A-Za-z0-9._~+/=-]{16,})")


@dataclass
class PolicyFinding:
    code: str
    severity: str
    message: str
    event_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "event_id": self.event_id,
        }


@dataclass
class PolicyConfig:
    max_tool_duration_ms: int = 30000
    max_error_events: int = 0


def evaluate_trace(trace: TraceEnvelope, config: PolicyConfig | None = None) -> list[PolicyFinding]:
    active = config or PolicyConfig()
    findings: list[PolicyFinding] = []
    ids: set[str] = set()
    permissions_seen: set[str] = set()

    if not trace.events:
        findings.append(PolicyFinding("empty_trace", "high", "Trace has no events."))
        return findings

    if trace.events[0].kind != EventKind.RUN_STARTED.value:
        findings.append(PolicyFinding("missing_run_start", "medium", "First event is not run_started.", trace.events[0].id))

    if trace.events[-1].kind != EventKind.RUN_FINISHED.value:
        findings.append(PolicyFinding("missing_run_finish", "medium", "Last event is not run_finished.", trace.events[-1].id))

    error_count = 0
    for event in trace.events:
        if event.id in ids:
            findings.append(PolicyFinding("duplicate_event_id", "high", f"Duplicate event id {event.id}.", event.id))
        ids.add(event.id)

        raw_payload = json.dumps(event.payload, sort_keys=True, default=str)
        if SECRET_LEAK_PATTERN.search(raw_payload):
            findings.append(PolicyFinding("secret_leak", "critical", "Payload appears to contain an unredacted token.", event.id))

        if event.kind == EventKind.PERMISSION.value and event.payload.get("allowed"):
            permissions_seen.add(str(event.payload.get("capability")))

        if event.kind == EventKind.ERROR.value:
            error_count += 1

        if event.kind == EventKind.TOOL_CALL.value:
            duration = int(event.payload.get("duration_ms", 0) or 0)
            if duration > active.max_tool_duration_ms:
                findings.append(PolicyFinding("slow_tool_call", "medium", f"Tool call exceeded {active.max_tool_duration_ms} ms.", event.id))
            if event.payload.get("requires_permission") and str(event.payload.get("name")) not in permissions_seen:
                findings.append(PolicyFinding("missing_permission", "high", "Tool call required permission before execution.", event.id))
            if event.payload.get("status") == "error":
                findings.append(PolicyFinding("tool_error", "medium", "Recorded tool call ended in error.", event.id))

    if error_count > active.max_error_events:
        findings.append(PolicyFinding("error_budget_exceeded", "high", f"{error_count} errors exceeded budget {active.max_error_events}."))

    return findings
