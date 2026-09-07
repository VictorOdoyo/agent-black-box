import pytest

from agent_black_box import AgentRecorder, EventKind
from agent_black_box.clock import FrozenClock


def test_recorder_captures_successful_tool_call():
    clock = FrozenClock.at("2026-08-18T00:00:00Z")
    with AgentRecorder("demo", clock=clock) as recorder:
        recorder.permission("lookup", True, "read only")
        response = recorder.capture_tool("lookup", {"q": "x"}, lambda: {"ok": True}, requires_permission=True)
    assert response == {"ok": True}
    assert [event.kind for event in recorder.trace.events][0] == EventKind.RUN_STARTED.value
    assert recorder.trace.tools()[0].payload["response"] == {"ok": True}


def test_recorder_redacts_tool_request():
    with AgentRecorder("demo") as recorder:
        recorder.capture_tool("lookup", {"email": "alice@example.com"}, lambda: {"ok": True})
    assert recorder.trace.tools()[0].payload["request"]["email"] == "[redacted-email]"


def test_recorder_logs_tool_errors():
    with pytest.raises(RuntimeError):
        with AgentRecorder("demo") as recorder:
            recorder.capture_tool("explode", {}, lambda: (_ for _ in ()).throw(RuntimeError("bad")))
    assert recorder.trace.tools()[0].payload["status"] == "error"
    assert any(event.kind == "error" for event in recorder.trace.events)
