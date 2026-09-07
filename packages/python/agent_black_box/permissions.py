from __future__ import annotations

from dataclasses import dataclass, field

from .models import EventKind, TraceEnvelope


@dataclass
class CapabilityRecord:
    capability: str
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    event_ids: list[str] = field(default_factory=list)


def capability_ledger(trace: TraceEnvelope) -> dict[str, CapabilityRecord]:
    ledger: dict[str, CapabilityRecord] = {}
    for event in trace.events:
        if event.kind != EventKind.PERMISSION.value:
            continue
        capability = str(event.payload.get("capability"))
        record = ledger.setdefault(capability, CapabilityRecord(capability, False))
        record.allowed = bool(event.payload.get("allowed"))
        record.reasons.append(str(event.payload.get("reason", "")))
        record.event_ids.append(event.id)
    return ledger


def unauthorized_tool_calls(trace: TraceEnvelope) -> list[str]:
    ledger = capability_ledger(trace)
    unauthorized: list[str] = []
    for event in trace.tools():
        if not event.payload.get("requires_permission"):
            continue
        tool_name = str(event.payload.get("name"))
        if tool_name not in ledger or not ledger[tool_name].allowed:
            unauthorized.append(event.id)
    return unauthorized
