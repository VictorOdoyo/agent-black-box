from agent_black_box import AgentRecorder, TraceFileStore
from agent_black_box.cli import main


def test_cli_inspect_prints_summary(tmp_path, capsys):
    store = TraceFileStore(tmp_path)
    with AgentRecorder("demo", run_id="run_cli") as recorder:
        recorder.capture_tool("lookup", {}, lambda: {"ok": True})
    path = store.save(recorder.trace)
    assert main(["inspect", str(path)]) == 0
    output = capsys.readouterr().out
    assert "run_cli" in output
    assert "tools: 1" in output


def test_cli_validate_rejects_bad_trace(tmp_path, capsys):
    path = tmp_path / "bad.json"
    path.write_text("{}", encoding="utf-8")
    assert main(["validate", str(path)]) == 1
    assert "missing trace keys" in capsys.readouterr().out
