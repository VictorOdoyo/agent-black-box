from __future__ import annotations

import hashlib
import json
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "abb.trace.v1"


class EventKind(str, Enum):
    RUN_STARTED = "run_started"
    RUN_FINISHED = "run_finished"
    OBSERVATION = "observation"
    DECISION = "decision"
    PERMISSION = "permission"
    TOOL_CALL = "tool_call"
    ENVIRONMENT = "environment"
    ARTIFACT = "artifact"
    ERROR = "error"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


@dataclass
class TraceEvent:
    id: str
    kind: str
    timestamp: str
    actor: str
    summary: str
    payload: dict[str, Any] = field(default_factory=dict)
    parent_id: str | None = None
    tags: list[str] = field(default_factory=list)
    fingerprint: str | None = None

    @classmethod
    def create(
        cls,
        kind: str | EventKind,
        *,
        actor: str,
        summary: str,
        payload: Mapping[str, Any] | None = None,
        timestamp: str | None = None,
        parent_id: str | None = None,
        tags: Iterable[str] | None = None,
    ) -> "TraceEvent":
        event = cls(
            id=f"evt_{uuid.uuid4().hex[:16]}",
            kind=kind.value if isinstance(kind, EventKind) else kind,
            timestamp=timestamp or utc_now(),
            actor=actor,
            summary=summary,
            payload=dict(payload or {}),
            parent_id=parent_id,
            tags=list(tags or []),
        )
        event.fingerprint = event.compute_fingerprint()
        return event

    def compute_fingerprint(self) -> str:
        body = self.to_dict(include_fingerprint=False)
        return stable_hash(body)

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        body: dict[str, Any] = {
            "id": self.id,
            "kind": self.kind,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "summary": self.summary,
            "payload": self.payload,
            "parent_id": self.parent_id,
            "tags": self.tags,
        }
        if include_fingerprint:
            body["fingerprint"] = self.fingerprint or self.compute_fingerprint()
        return body

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "TraceEvent":
        event = cls(
            id=str(payload["id"]),
            kind=str(payload["kind"]),
            timestamp=str(payload["timestamp"]),
            actor=str(payload["actor"]),
            summary=str(payload["summary"]),
            payload=dict(payload.get("payload", {})),
            parent_id=payload.get("parent_id"),
            tags=list(payload.get("tags", [])),
            fingerprint=payload.get("fingerprint"),
        )
        if event.fingerprint is None:
            event.fingerprint = event.compute_fingerprint()
        return event


@dataclass
class TraceEnvelope:
    trace_id: str
    run_id: str
    app: str
    started_at: str
    schema_version: str = SCHEMA_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)
    events: list[TraceEvent] = field(default_factory=list)

    @classmethod
    def new(cls, *, app: str, run_id: str | None = None, metadata: Mapping[str, Any] | None = None) -> "TraceEnvelope":
        return cls(
            trace_id=f"trc_{uuid.uuid4().hex[:16]}",
            run_id=run_id or f"run_{uuid.uuid4().hex[:16]}",
            app=app,
            started_at=utc_now(),
            metadata=dict(metadata or {}),
        )

    def append(self, event: TraceEvent) -> TraceEvent:
        self.events.append(event)
        return event

    def find(self, event_id: str) -> TraceEvent | None:
        return next((event for event in self.events if event.id == event_id), None)

    def event_counts(self) -> dict[str, int]:
        return dict(Counter(event.kind for event in self.events))

    def tools(self) -> list[TraceEvent]:
        return [event for event in self.events if event.kind == EventKind.TOOL_CALL.value]

    def decisions(self) -> list[TraceEvent]:
        return [event for event in self.events if event.kind == EventKind.DECISION.value]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "app": self.app,
            "started_at": self.started_at,
            "metadata": self.metadata,
            "events": [event.to_dict() for event in self.events],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "TraceEnvelope":
        return cls(
            schema_version=str(payload.get("schema_version", SCHEMA_VERSION)),
            trace_id=str(payload["trace_id"]),
            run_id=str(payload["run_id"]),
            app=str(payload["app"]),
            started_at=str(payload["started_at"]),
            metadata=dict(payload.get("metadata", {})),
            events=[TraceEvent.from_dict(event) for event in payload.get("events", [])],
        )

    @classmethod
    def from_json(cls, text: str) -> "TraceEnvelope":
        return cls.from_dict(json.loads(text))
