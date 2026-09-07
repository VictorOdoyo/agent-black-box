from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
BEARER_PATTERN = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b")
TOKEN_PATTERN = re.compile(r"\b(?:sk|ghp|gho|xoxb|api)[A-Za-z0-9_\-]{16,}\b")


@dataclass(frozen=True)
class RedactionRule:
    name: str
    pattern: re.Pattern[str]
    replacement: str

    def apply(self, text: str) -> tuple[str, int]:
        return self.pattern.subn(self.replacement, text)


@dataclass
class RedactionPolicy:
    sensitive_keys: set[str] = field(default_factory=set)
    rules: list[RedactionRule] = field(default_factory=list)

    @classmethod
    def default(cls) -> "RedactionPolicy":
        return cls(
            sensitive_keys={
                "authorization",
                "api_key",
                "apikey",
                "access_token",
                "refresh_token",
                "password",
                "secret",
                "client_secret",
                "private_key",
            },
            rules=[
                RedactionRule("email", EMAIL_PATTERN, "[redacted-email]"),
                RedactionRule("bearer", BEARER_PATTERN, "Bearer [redacted-token]"),
                RedactionRule("token", TOKEN_PATTERN, "[redacted-token]"),
            ],
        )


def _key_is_sensitive(key: str, policy: RedactionPolicy) -> bool:
    lowered = key.lower().replace("-", "_")
    return lowered in policy.sensitive_keys or any(part in lowered for part in ("secret", "token", "password"))


def redact_text(value: str, policy: RedactionPolicy | None = None) -> tuple[str, int]:
    active = policy or RedactionPolicy.default()
    count = 0
    redacted = value
    for rule in active.rules:
        redacted, changed = rule.apply(redacted)
        count += changed
    return redacted, count


def redact_value(value: Any, policy: RedactionPolicy | None = None, *, key_path: tuple[str, ...] = ()) -> tuple[Any, int]:
    active = policy or RedactionPolicy.default()
    if isinstance(value, Mapping):
        redactions = 0
        result: dict[str, Any] = {}
        for key, nested in value.items():
            string_key = str(key)
            if _key_is_sensitive(string_key, active):
                result[string_key] = "[redacted]"
                redactions += 1
            else:
                result[string_key], changed = redact_value(nested, active, key_path=key_path + (string_key,))
                redactions += changed
        return result, redactions
    if isinstance(value, list):
        result = []
        redactions = 0
        for item in value:
            redacted_item, changed = redact_value(item, active, key_path=key_path)
            result.append(redacted_item)
            redactions += changed
        return result, redactions
    if isinstance(value, tuple):
        result = []
        redactions = 0
        for item in value:
            redacted_item, changed = redact_value(item, active, key_path=key_path)
            result.append(redacted_item)
            redactions += changed
        return tuple(result), redactions
    if isinstance(value, str):
        return redact_text(value, active)
    return value, 0


def redaction_preview(payload: Mapping[str, Any], policy: RedactionPolicy | None = None) -> dict[str, Any]:
    redacted, count = redact_value(payload, policy)
    return {"redactions": count, "payload": redacted}
