from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .models import EventKind, TraceEnvelope


class ReplayMismatch(Exception):
    pass


@dataclass
class ReplayStep:
    index: int
    tool: str
    request: Mapping[str, Any]
    response: Mapping[str, Any]
    status: str


class ReplaySession:
    def __init__(self, trace: TraceEnvelope) -> None:
        self.trace = trace
        self.steps = [
            ReplayStep(
                index=index,
                tool=str(event.payload.get("name")),
                request=event.payload.get("request", {}),
                response=event.payload.get("response", {}),
                status=str(event.payload.get("status", "ok")),
            )
            for index, event in enumerate(trace.events)
            if event.kind == EventKind.TOOL_CALL.value
        ]
        self.cursor = 0

    def next(self, expected_tool: str | None = None) -> Mapping[str, Any]:
        if self.cursor >= len(self.steps):
            raise ReplayMismatch("No recorded tool calls remain.")
        step = self.steps[self.cursor]
        if expected_tool is not None and step.tool != expected_tool:
            raise ReplayMismatch(f"Expected tool {expected_tool!r}, got {step.tool!r}.")
        self.cursor += 1
        if step.status != "ok":
            raise ReplayMismatch(f"Recorded tool {step.tool!r} failed with status {step.status!r}.")
        return step.response

    def mock(self, tool_name: str) -> Callable[[Mapping[str, Any]], Mapping[str, Any]]:
        def _call(_request: Mapping[str, Any]) -> Mapping[str, Any]:
            return self.next(tool_name)

        return _call


def fork_trace(trace: TraceEnvelope, *, until_event_id: str, app_suffix: str = "fork") -> TraceEnvelope:
    fork = TraceEnvelope.new(app=f"{trace.app}:{app_suffix}", metadata=dict(trace.metadata))
    fork.run_id = f"run_{uuid.uuid4().hex[:16]}"
    for event in trace.events:
        fork.events.append(event)
        if event.id == until_event_id:
            return fork
    raise ReplayMismatch(f"Event {until_event_id!r} was not found.")


def replay_plan(trace: TraceEnvelope) -> list[str]:
    return [f"{step.index}: {step.tool} -> {step.status}" for step in ReplaySession(trace).steps]
