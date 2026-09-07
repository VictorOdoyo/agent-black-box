from agent_black_box import AgentRecorder, actor_timeline, run_duration_seconds
from agent_black_box.clock import FrozenClock


def test_duration_uses_event_timestamps():
    clock = FrozenClock.at("2026-08-18T00:00:00Z")
    with AgentRecorder("demo", clock=clock) as recorder:
        clock.tick(5)
        recorder.observation("input")
        clock.tick(4)
    assert run_duration_seconds(recorder.trace) == 9
    assert actor_timeline(recorder.trace)["agent"][1] == "input"
