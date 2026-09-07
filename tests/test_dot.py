from agent_black_box import AgentRecorder
from agent_black_box.dot import trace_to_dot


def test_dot_export_contains_event_nodes():
    with AgentRecorder("demo") as recorder:
        recorder.observation("input")
    dot = trace_to_dot(recorder.trace)
    assert "digraph trace" in dot
    assert "input" in dot
