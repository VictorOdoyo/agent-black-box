import json

from agent_black_box import AgentRecorder, evaluate_policy_pack, load_policy_pack


def test_policy_pack_flags_denied_tools(tmp_path):
    policy = tmp_path / "pack.json"
    policy.write_text(json.dumps({"name": "strict", "denied_tools": ["shell"]}), encoding="utf-8")
    with AgentRecorder("demo") as recorder:
        recorder.capture_tool("shell", {}, lambda: {"ok": True})
    findings = evaluate_policy_pack(recorder.trace, load_policy_pack(policy))
    assert "denied_tool" in {finding.code for finding in findings}
