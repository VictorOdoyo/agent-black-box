from __future__ import annotations

from .models import EventKind, TraceEnvelope


def render_transcript(trace: TraceEnvelope) -> str:
    lines = [f"Transcript for {trace.run_id}"]
    for event in trace.events:
        lines.append(f"[{event.timestamp}] {event.actor} {event.kind}: {event.summary}")
    return "\n".join(lines) + "\n"


def decision_table(trace: TraceEnvelope) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for event in trace.events:
        if event.kind == EventKind.DECISION.value:
            rows.append(
                {
                    "event_id": event.id,
                    "summary": event.summary,
                    "rationale": str(event.payload.get("rationale", "")),
                }
            )
    return rows
