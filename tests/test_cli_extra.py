import json

from agent_black_box import AgentRecorder, TraceFileStore
from agent_black_box.cli import main


def save_trace(tmp_path):
    store = TraceFileStore(tmp_path)
    with AgentRecorder("demo", run_id="run_cli_extra") as recorder:
        recorder.observation("payment webhook failed", tags=["incident"])
        recorder.capture_tool("lookup", {}, lambda: {"ok": True})
    return store.save(recorder.trace)


def test_cli_metrics_outputs_json(tmp_path, capsys):
    path = save_trace(tmp_path)
    assert main(["metrics", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["tool_count"] == 1


def test_cli_manifest_and_verify(tmp_path):
    path = save_trace(tmp_path)
    manifest = tmp_path / "manifest.json"
    assert main(["manifest", str(path), "--output", str(manifest)]) == 0
    assert main(["verify-manifest", str(path), str(manifest)]) == 0


def test_cli_events_filters_output(tmp_path, capsys):
    path = save_trace(tmp_path)
    assert main(["events", str(path), "--query", "webhook", "--kind", "observation"]) == 0
    assert "payment webhook failed" in capsys.readouterr().out


def test_cli_jsonl_round_trip(tmp_path):
    path = save_trace(tmp_path)
    jsonl = tmp_path / "trace.jsonl"
    restored = tmp_path / "restored.json"
    assert main(["write-jsonl", str(path), str(jsonl)]) == 0
    assert main(["read-jsonl", str(jsonl), str(restored)]) == 0
    assert restored.exists()
