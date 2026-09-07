from agent_black_box import AgentRecorder, compare_traces


def make_trace(tool_name):
    with AgentRecorder("demo") as recorder:
        recorder.capture_tool(tool_name, {}, lambda: {"ok": True})
    return recorder.trace


def test_compare_finds_changed_tool_summary():
    left = make_trace("search")
    right = make_trace("query")
    comparison = compare_traces(left, right)
    assert comparison.first_divergence_index == 1
    assert comparison.added_tool_calls == ["query"]
    assert comparison.removed_tool_calls == ["search"]
