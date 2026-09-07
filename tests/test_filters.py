from agent_black_box import AgentRecorder, filter_events


def test_filter_events_by_query_kind_and_tag():
    with AgentRecorder("demo") as recorder:
        recorder.observation("payment webhook failed", tags=["incident"])
        recorder.decision("ignore unrelated", "not needed")
    matches = filter_events(recorder.trace, query="payment", kinds={"observation"}, tags={"incident"})
    assert len(matches) == 1
