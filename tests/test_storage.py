from agent_black_box import AgentRecorder, TraceFileStore


def test_file_store_round_trips_trace(tmp_path):
    store = TraceFileStore(tmp_path)
    with AgentRecorder("demo", run_id="run_one") as recorder:
        recorder.observation("input")
    saved = store.save(recorder.trace)
    loaded = store.load(saved.name)
    assert loaded.run_id == "run_one"
    assert store.list()[0].event_count == len(loaded.events)
