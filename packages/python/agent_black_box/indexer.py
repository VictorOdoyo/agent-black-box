from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable

from .models import TraceEnvelope, TraceEvent


@dataclass
class SearchHit:
    trace_id: str
    run_id: str
    event_id: str
    kind: str
    summary: str
    score: int


def event_text(event: TraceEvent) -> str:
    return " ".join(
        [
            event.kind,
            event.actor,
            event.summary,
            " ".join(event.tags),
            json.dumps(event.payload, sort_keys=True, default=str),
        ]
    ).lower()


class TraceIndex:
    def __init__(self) -> None:
        self._events: list[tuple[TraceEnvelope, TraceEvent, str]] = []

    def add(self, trace: TraceEnvelope) -> None:
        for event in trace.events:
            self._events.append((trace, event, event_text(event)))

    def extend(self, traces: Iterable[TraceEnvelope]) -> None:
        for trace in traces:
            self.add(trace)

    def search(self, query: str, *, kinds: set[str] | None = None, tags: set[str] | None = None) -> list[SearchHit]:
        terms = [term.lower() for term in query.split() if term.strip()]
        hits: list[SearchHit] = []
        for trace, event, text in self._events:
            if kinds and event.kind not in kinds:
                continue
            if tags and tags.isdisjoint(set(event.tags)):
                continue
            score = sum(text.count(term) for term in terms) if terms else 1
            if score:
                hits.append(SearchHit(trace.trace_id, trace.run_id, event.id, event.kind, event.summary, score))
        return sorted(hits, key=lambda hit: (-hit.score, hit.event_id))
