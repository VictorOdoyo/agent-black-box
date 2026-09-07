import pytest

from agent_black_box import AgentRecorder, ReplaySession, fork_trace, replay_plan
from agent_black_box.replay import ReplayMismatch


def build_trace():
    with AgentRecorder("demo") as recorder:
        recorder.capture_tool("lookup", {"q": "x"}, lambda: {"result": 1})
    return recorder.trace


def test_replay_returns_recorded_response():
    replay = ReplaySession(build_trace())
    assert replay.next("lookup") == {"result": 1}


def test_replay_detects_wrong_tool():
    replay = ReplaySession(build_trace())
    with pytest.raises(ReplayMismatch):
        replay.next("other")


def test_fork_trace_keeps_prefix():
    trace = build_trace()
    fork = fork_trace(trace, until_event_id=trace.events[1].id)
    assert len(fork.events) == 2
    assert replay_plan(trace)[0].endswith("lookup -> ok")
