from __future__ import annotations

from datetime import datetime, timezone

from .models import TraceEnvelope, TraceEvent


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def sorted_events(trace: TraceEnvelope) -> list[TraceEvent]:
    return sorted(trace.events, key=lambda event: parse_timestamp(event.timestamp))


def run_duration_seconds(trace: TraceEnvelope) -> float:
    if not trace.events:
        return 0.0
    ordered = sorted_events(trace)
    return (parse_timestamp(ordered[-1].timestamp) - parse_timestamp(ordered[0].timestamp)).total_seconds()


def events_between(trace: TraceEnvelope, start: str, end: str) -> list[TraceEvent]:
    start_dt = parse_timestamp(start)
    end_dt = parse_timestamp(end)
    return [event for event in trace.events if start_dt <= parse_timestamp(event.timestamp) <= end_dt]


def actor_timeline(trace: TraceEnvelope) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for event in sorted_events(trace):
        grouped.setdefault(event.actor, []).append(event.summary)
    return grouped
