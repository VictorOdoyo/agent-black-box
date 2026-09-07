from agent_black_box import AgentRecorder, build_causal_edges, explain_event


def test_permission_links_to_tool_call():
    with AgentRecorder("demo") as recorder:
        recorder.permission("lookup", True, "read")
        recorder.capture_tool("lookup", {}, lambda: {"ok": True}, requires_permission=True)
    edges = build_causal_edges(recorder.trace)
    assert any(edge.reason == "permission" for edge in edges)
    assert "Permission allowed: lookup" in explain_event(recorder.trace, recorder.trace.tools()[0].id)
