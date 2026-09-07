from agent_black_box import AgentRecorder
from agent_black_box.minimize import minimize_trace


def test_minimize_keeps_kind_with_context_window():
    with AgentRecorder("demo") as recorder:
        recorder.observation("input")
        recorder.decision("choose path", "because")
        recorder.capture_tool("lookup", {}, lambda: {"ok": True})
    minimized = minimize_trace(recorder.trace, keep_kinds={"decision"}, window=1)
    assert [event.summary for event in minimized.events] == ["input", "choose path", "Tool call: lookup"]
