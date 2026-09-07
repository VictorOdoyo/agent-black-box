from agent_black_box import AgentRecorder
from agent_black_box.metrics import calculate_metrics


def test_calculate_metrics_from_tool_events():
    with AgentRecorder("demo") as recorder:
        recorder.tool_call("lookup", {}, {"ok": True}, duration_ms=25)
    metrics = calculate_metrics(recorder.trace)
    assert metrics.tool_count == 1
    assert metrics.total_tool_duration_ms == 25
