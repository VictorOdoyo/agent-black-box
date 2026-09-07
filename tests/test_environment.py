from agent_black_box.environment import diff_environment


def test_environment_diff_reports_nested_changes():
    changes = diff_environment({"model": {"temperature": 0}, "old": True}, {"model": {"temperature": 1}, "new": True})
    assert {change.operation for change in changes} == {"added", "removed", "changed"}
    assert any(change.path == "model.temperature" for change in changes)
