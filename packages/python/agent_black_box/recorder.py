from __future__ import annotations

import hashlib
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Mapping

from .clock import UtcClock
from .models import EventKind, TraceEnvelope, TraceEvent
from .redaction import RedactionPolicy, redact_value


class AgentRecorder:
    def __init__(
        self,
        app: str,
        *,
        actor: str = "agent",
        run_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        redaction_policy: RedactionPolicy | None = None,
        clock: UtcClock | None = None,
    ) -> None:
        self.actor = actor
        self.clock = clock or UtcClock()
        self.redaction_policy = redaction_policy or RedactionPolicy.default()
        self.trace = TraceEnvelope.new(app=app, run_id=run_id, metadata=metadata)

    def __enter__(self) -> "AgentRecorder":
        self.record(EventKind.RUN_STARTED, "Agent run started", {"metadata": self.trace.metadata})
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: object) -> bool:
        if exc is not None:
            self.error(exc, stage="run")
            self.record(EventKind.RUN_FINISHED, "Agent run failed", {"status": "failed"})
            return False
        self.record(EventKind.RUN_FINISHED, "Agent run finished", {"status": "completed"})
        return False

    def _sanitize(self, payload: Mapping[str, Any] | None) -> dict[str, Any]:
        redacted, count = redact_value(dict(payload or {}), self.redaction_policy)
        body = dict(redacted)
        if count:
            body["_redactions"] = count
        return body

    def record(
        self,
        kind: str | EventKind,
        summary: str,
        payload: Mapping[str, Any] | None = None,
        *,
        parent_id: str | None = None,
        tags: list[str] | None = None,
    ) -> TraceEvent:
        return self.trace.append(
            TraceEvent.create(
                kind,
                actor=self.actor,
                summary=summary,
                payload=self._sanitize(payload),
                timestamp=self.clock.now(),
                parent_id=parent_id,
                tags=tags or [],
            )
        )

    def observation(self, summary: str, payload: Mapping[str, Any] | None = None) -> TraceEvent:
        return self.record(EventKind.OBSERVATION, summary, payload)

    def decision(self, summary: str, rationale: str, alternatives: list[str] | None = None) -> TraceEvent:
        return self.record(EventKind.DECISION, summary, {"rationale": rationale, "alternatives": alternatives or []})

    def permission(self, capability: str, allowed: bool, reason: str) -> TraceEvent:
        return self.record(EventKind.PERMISSION, f"Permission {'allowed' if allowed else 'denied'}: {capability}", {
            "capability": capability,
            "allowed": allowed,
            "reason": reason,
        })

    def environment(self, summary: str, before: Mapping[str, Any], after: Mapping[str, Any]) -> TraceEvent:
        return self.record(EventKind.ENVIRONMENT, summary, {"before": before, "after": after})

    def artifact(self, path: str | Path, label: str) -> TraceEvent:
        artifact_path = Path(path)
        payload: dict[str, Any] = {"path": str(artifact_path), "label": label, "exists": artifact_path.exists()}
        if artifact_path.exists() and artifact_path.is_file():
            digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            payload.update({"sha256": digest, "bytes": artifact_path.stat().st_size})
        return self.record(EventKind.ARTIFACT, f"Artifact captured: {label}", payload)

    def tool_call(
        self,
        name: str,
        request: Mapping[str, Any],
        response: Mapping[str, Any],
        *,
        status: str = "ok",
        duration_ms: int = 0,
        requires_permission: bool = False,
    ) -> TraceEvent:
        return self.record(EventKind.TOOL_CALL, f"Tool call: {name}", {
            "name": name,
            "request": request,
            "response": response,
            "status": status,
            "duration_ms": duration_ms,
            "requires_permission": requires_permission,
        })

    def capture_tool(
        self,
        name: str,
        request: Mapping[str, Any],
        func: Callable[[], Mapping[str, Any]],
        *,
        requires_permission: bool = False,
    ) -> Mapping[str, Any]:
        started = time.perf_counter()
        try:
            response = func()
        except Exception as exc:
            duration_ms = int((time.perf_counter() - started) * 1000)
            self.tool_call(
                name,
                request,
                {"error_type": type(exc).__name__, "message": str(exc)},
                status="error",
                duration_ms=duration_ms,
                requires_permission=requires_permission,
            )
            raise
        duration_ms = int((time.perf_counter() - started) * 1000)
        self.tool_call(
            name,
            request,
            dict(response),
            status="ok",
            duration_ms=duration_ms,
            requires_permission=requires_permission,
        )
        return response

    def error(self, exc: BaseException, *, stage: str) -> TraceEvent:
        return self.record(EventKind.ERROR, f"{type(exc).__name__} during {stage}", {
            "type": type(exc).__name__,
            "message": str(exc),
            "stage": stage,
            "traceback": traceback.format_exception_only(type(exc), exc),
        })
