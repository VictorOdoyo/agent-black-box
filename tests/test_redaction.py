from agent_black_box import RedactionPolicy, redact_value
from agent_black_box.redaction import redaction_preview


def test_redacts_sensitive_keys_and_email_values():
    payload = {"user": "alice@example.com", "authorization": "Bearer abcdefghijklmnopqrstuv", "nested": {"api_key": "sk_live_secretsecretsecret"}}
    redacted, count = redact_value(payload, RedactionPolicy.default())
    assert count >= 3
    assert redacted["authorization"] == "[redacted]"
    assert redacted["nested"]["api_key"] == "[redacted]"
    assert redacted["user"] == "[redacted-email]"


def test_preview_reports_count():
    preview = redaction_preview({"token": "ghp_1234567890abcdefghijklmnop"})
    assert preview["redactions"] == 1
