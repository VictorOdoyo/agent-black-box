from agent_black_box import AgentRecorder
from agent_black_box.transcript import decision_table, render_transcript


def test_transcript_and_decision_table():
    with AgentRecorder("demo") as recorder:
        recorder.decision("use cache", "faster")
    assert "use cache" in render_transcript(recorder.trace)
    assert decision_table(recorder.trace)[0]["rationale"] == "faster"
