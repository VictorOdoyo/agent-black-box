from agent_black_box import AgentRecorder, capability_ledger, unauthorized_tool_calls


def test_permission_ledger_tracks_outcomes():
    with AgentRecorder("demo") as recorder:
        recorder.permission("lookup", True, "read")
    assert capability_ledger(recorder.trace)["lookup"].allowed is True


def test_unauthorized_tool_call_reports_event_id():
    with AgentRecorder("demo") as recorder:
        recorder.capture_tool("lookup", {}, lambda: {"ok": True}, requires_permission=True)
    assert unauthorized_tool_calls(recorder.trace) == [recorder.trace.tools()[0].id]
