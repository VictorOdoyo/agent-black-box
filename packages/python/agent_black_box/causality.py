from __future__ import annotations

from dataclasses import dataclass

from .models import EventKind, TraceEnvelope


@dataclass(frozen=True)
class CausalEdge:
    source: str
    target: str
    reason: str


def build_causal_edges(trace: TraceEnvelope) -> list[CausalEdge]:
    edges: list[CausalEdge] = []
    latest_permission_by_capability: dict[str, str] = {}
    latest_decision_id: str | None = None

    for event in trace.events:
        if event.parent_id:
            edges.append(CausalEdge(event.parent_id, event.id, "parent"))
        if event.kind == EventKind.DECISION.value:
            latest_decision_id = event.id
        if event.kind == EventKind.PERMISSION.value and event.payload.get("allowed"):
            latest_permission_by_capability[str(event.payload.get("capability"))] = event.id
        if event.kind == EventKind.TOOL_CALL.value:
            tool_name = str(event.payload.get("name"))
            permission_id = latest_permission_by_capability.get(tool_name)
            if permission_id:
                edges.append(CausalEdge(permission_id, event.id, "permission"))
            elif latest_decision_id:
                edges.append(CausalEdge(latest_decision_id, event.id, "decision"))
    return edges


def ancestors(trace: TraceEnvelope, event_id: str) -> list[str]:
    reverse: dict[str, list[str]] = {}
    for edge in build_causal_edges(trace):
        reverse.setdefault(edge.target, []).append(edge.source)

    found: list[str] = []
    stack = list(reverse.get(event_id, []))
    while stack:
        current = stack.pop()
        if current in found:
            continue
        found.append(current)
        stack.extend(reverse.get(current, []))
    return found


def explain_event(trace: TraceEnvelope, event_id: str) -> list[str]:
    events = {event.id: event for event in trace.events}
    return [events[ancestor].summary for ancestor in ancestors(trace, event_id) if ancestor in events]
