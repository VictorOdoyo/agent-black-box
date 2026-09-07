from __future__ import annotations

import json

from .models import TraceEnvelope, TraceEvent


def filter_events(
    trace: TraceEnvelope,
    *,
    query: str = "",
    kinds: set[str] | None = None,
    tags: set[str] | None = None,
    actor: str | None = None,
) -> list[TraceEvent]:
    terms = [term.lower() for term in query.split() if term.strip()]
    results: list[TraceEvent] = []
    for event in trace.events:
        if kinds and event.kind not in kinds:
            continue
        if tags and tags.isdisjoint(set(event.tags)):
            continue
        if actor and event.actor != actor:
            continue
        text = f"{event.summary} {event.kind} {event.actor} {' '.join(event.tags)} {json.dumps(event.payload, default=str)}".lower()
        if all(term in text for term in terms):
            results.append(event)
    return results
