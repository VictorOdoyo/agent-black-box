import tarfile

from agent_black_box.bundles import create_trace_bundle


def test_create_trace_bundle(tmp_path):
    trace = tmp_path / "trace.json"
    trace.write_text("{}", encoding="utf-8")
    bundle = create_trace_bundle([trace], tmp_path / "bundle.tgz")
    with tarfile.open(bundle, "r:gz") as archive:
        assert archive.getnames() == ["trace.json"]
