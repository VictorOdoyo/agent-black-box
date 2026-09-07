from __future__ import annotations

from typing import Any, Mapping


REQUIRED_TRACE_KEYS = {"schema_version", "trace_id", "run_id", "app", "started_at", "events"}
REQUIRED_EVENT_KEYS = {"id", "kind", "timestamp", "actor", "summary", "payload"}


def validate_trace_dict(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_TRACE_KEYS - set(payload.keys())
    if missing:
        errors.append(f"missing trace keys: {', '.join(sorted(missing))}")
    events = payload.get("events", [])
    if not isinstance(events, list):
        errors.append("events must be a list")
        return errors
    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            errors.append(f"event {index} must be an object")
            continue
        missing_event = REQUIRED_EVENT_KEYS - set(event.keys())
        if missing_event:
            errors.append(f"event {index} missing keys: {', '.join(sorted(missing_event))}")
    return errors
