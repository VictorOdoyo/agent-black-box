from agent_black_box import AgentRecorder, evaluate_trace
from agent_black_box.models import EventKind, TraceEnvelope, TraceEvent
from agent_black_box.policy import PolicyConfig


def test_policy_requires_run_lifecycle():
    trace = TraceEnvelope.new(app="demo")
    trace.append(TraceEvent.create(EventKind.OBSERVATION, actor="agent", summary="input"))
    findings = evaluate_trace(trace)
    assert {finding.code for finding in findings} >= {"missing_run_start", "missing_run_finish"}


def test_policy_flags_permission_missing():
    with AgentRecorder("demo") as recorder:
        recorder.capture_tool("delete_file", {}, lambda: {"ok": True}, requires_permission=True)
    findings = evaluate_trace(recorder.trace)
    assert "missing_permission" in {finding.code for finding in findings}


def test_policy_flags_slow_tools():
    with AgentRecorder("demo") as recorder:
        recorder.tool_call("lookup", {}, {"ok": True}, duration_ms=40)
    findings = evaluate_trace(recorder.trace, PolicyConfig(max_tool_duration_ms=10))
    assert "slow_tool_call" in {finding.code for finding in findings}
