from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .models import TraceEnvelope, TraceEvent


HEADER_RECORD = "trace_header"
EVENT_RECORD = "trace_event"


def envelope_to_records(trace: TraceEnvelope) -> Iterable[dict[str, Any]]:
    yield {
        "record_type": HEADER_RECORD,
        "schema_version": trace.schema_version,
        "trace_id": trace.trace_id,
        "run_id": trace.run_id,
        "app": trace.app,
        "started_at": trace.started_at,
        "metadata": trace.metadata,
    }
    for event in trace.events:
        yield {"record_type": EVENT_RECORD, "event": event.to_dict()}


def write_jsonl(trace: TraceEnvelope, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in envelope_to_records(trace):
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    return output


def read_jsonl(path: str | Path) -> TraceEnvelope:
    header: dict[str, Any] | None = None
    events: list[TraceEvent] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            record = json.loads(line)
            record_type = record.get("record_type")
            if record_type == HEADER_RECORD:
                header = record
            elif record_type == EVENT_RECORD:
                events.append(TraceEvent.from_dict(record["event"]))
            else:
                raise ValueError(f"Unknown JSONL record at line {line_number}: {record_type!r}")
    if header is None:
        raise ValueError("JSONL trace is missing a trace_header record.")
    trace = TraceEnvelope(
        schema_version=str(header["schema_version"]),
        trace_id=str(header["trace_id"]),
        run_id=str(header["run_id"]),
        app=str(header["app"]),
        started_at=str(header["started_at"]),
        metadata=dict(header.get("metadata", {})),
        events=events,
    )
    return trace
