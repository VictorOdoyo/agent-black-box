from agent_black_box import AgentRecorder, artifact_manifest, verify_artifact_files


def test_artifact_manifest_verifies_file_hash(tmp_path):
    output = tmp_path / "report.md"
    output.write_text("hello", encoding="utf-8")
    with AgentRecorder("demo") as recorder:
        recorder.artifact(output, "report")
    records = artifact_manifest(recorder.trace)
    assert records[0].label == "report"
    assert verify_artifact_files(tmp_path, records) == {str(output): True}
