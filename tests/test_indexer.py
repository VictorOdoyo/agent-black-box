from agent_black_box import AgentRecorder
from agent_black_box.indexer import TraceIndex


def test_index_searches_payload_and_summary():
    with AgentRecorder("demo") as recorder:
        recorder.observation("payment webhook failed", {"ticket": "INC-421"})
    index = TraceIndex()
    index.add(recorder.trace)
    hits = index.search("INC-421")
    assert hits[0].summary == "payment webhook failed"
