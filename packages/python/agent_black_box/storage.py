from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .models import TraceEnvelope


@dataclass
class TraceSummary:
    path: Path
    trace_id: str
    run_id: str
    app: str
    event_count: int


class TraceFileStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, trace: TraceEnvelope, *, name: str | None = None) -> Path:
        filename = name or f"{trace.run_id}.json"
        path = self.root / filename
        path.write_text(trace.to_json(), encoding="utf-8", newline="\n")
        return path

    def load(self, name: str | Path) -> TraceEnvelope:
        path = Path(name)
        if not path.is_absolute():
            path = self.root / path
        return TraceEnvelope.from_json(path.read_text(encoding="utf-8"))

    def list(self) -> list[TraceSummary]:
        summaries: list[TraceSummary] = []
        for path in sorted(self.root.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            summaries.append(
                TraceSummary(
                    path=path,
                    trace_id=str(payload["trace_id"]),
                    run_id=str(payload["run_id"]),
                    app=str(payload["app"]),
                    event_count=len(payload.get("events", [])),
                )
            )
        return summaries
