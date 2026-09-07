from __future__ import annotations

from .models import TraceEnvelope


def minimize_trace(
    trace: TraceEnvelope,
    *,
    keep_kinds: set[str] | None = None,
    keep_ids: set[str] | None = None,
    keep_tags: set[str] | None = None,
    window: int = 0,
) -> TraceEnvelope:
    keep_indexes: set[int] = set()
    for index, event in enumerate(trace.events):
        matched = False
        matched = matched or (keep_kinds is not None and event.kind in keep_kinds)
        matched = matched or (keep_ids is not None and event.id in keep_ids)
        matched = matched or (keep_tags is not None and not keep_tags.isdisjoint(set(event.tags)))
        if matched:
            for offset in range(-window, window + 1):
                candidate = index + offset
                if 0 <= candidate < len(trace.events):
                    keep_indexes.add(candidate)

    minimized = TraceEnvelope.new(
        app=trace.app,
        run_id=f"{trace.run_id}_minimized",
        metadata={**trace.metadata, "minimized_from": trace.run_id},
    )
    minimized.trace_id = f"{trace.trace_id}_minimized"
    minimized.started_at = trace.started_at
    minimized.events = [event for index, event in enumerate(trace.events) if index in keep_indexes]
    return minimized
