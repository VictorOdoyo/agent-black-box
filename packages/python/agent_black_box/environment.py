from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class EnvironmentChange:
    path: str
    before: Any
    after: Any
    operation: str


def diff_environment(before: Mapping[str, Any], after: Mapping[str, Any], *, prefix: str = "") -> list[EnvironmentChange]:
    changes: list[EnvironmentChange] = []
    keys = set(before) | set(after)
    for key in sorted(keys):
        path = f"{prefix}.{key}" if prefix else str(key)
        if key not in before:
            changes.append(EnvironmentChange(path, None, after[key], "added"))
        elif key not in after:
            changes.append(EnvironmentChange(path, before[key], None, "removed"))
        elif isinstance(before[key], Mapping) and isinstance(after[key], Mapping):
            changes.extend(diff_environment(before[key], after[key], prefix=path))
        elif before[key] != after[key]:
            changes.append(EnvironmentChange(path, before[key], after[key], "changed"))
    return changes
