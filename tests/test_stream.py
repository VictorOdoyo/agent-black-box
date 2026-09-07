from agent_black_box import AgentRecorder, read_jsonl, write_jsonl


def test_jsonl_round_trip(tmp_path):
    with AgentRecorder("demo", run_id="run_jsonl") as recorder:
        recorder.observation("input")
    path = write_jsonl(recorder.trace, tmp_path / "trace.jsonl")
    loaded = read_jsonl(path)
    assert loaded.run_id == "run_jsonl"
    assert loaded.events[1].summary == "input"
