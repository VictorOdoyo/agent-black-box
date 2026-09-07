from agent_black_box import EventKind, TraceEnvelope, TraceEvent


def test_trace_event_fingerprint_is_stable():
    event = TraceEvent.create(EventKind.OBSERVATION, actor="agent", summary="Saw input", payload={"b": 2, "a": 1})
    assert event.fingerprint == event.compute_fingerprint()
    assert event.to_dict()["kind"] == "observation"


def test_trace_envelope_counts_events():
    trace = TraceEnvelope.new(app="demo", run_id="run_demo")
    trace.append(TraceEvent.create(EventKind.RUN_STARTED, actor="agent", summary="start"))
    trace.append(TraceEvent.create(EventKind.TOOL_CALL, actor="agent", summary="tool", payload={"name": "search"}))
    assert trace.event_counts() == {"run_started": 1, "tool_call": 1}
    assert trace.tools()[0].payload["name"] == "search"
