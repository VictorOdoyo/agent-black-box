from __future__ import annotations

from dataclasses import dataclass

from .models import TraceEnvelope


@dataclass
class TraceMetrics:
    event_count: int
    tool_count: int
    error_count: int
    total_tool_duration_ms: int
    max_tool_duration_ms: int


def calculate_metrics(trace: TraceEnvelope) -> TraceMetrics:
    durations = [int(event.payload.get("duration_ms", 0) or 0) for event in trace.tools()]
    return TraceMetrics(
        event_count=len(trace.events),
        tool_count=len(durations),
        error_count=sum(1 for event in trace.events if event.kind == "error"),
        total_tool_duration_ms=sum(durations),
        max_tool_duration_ms=max(durations, default=0),
    )
