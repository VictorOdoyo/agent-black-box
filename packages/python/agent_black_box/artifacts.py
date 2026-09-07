from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .models import EventKind, TraceEnvelope


@dataclass(frozen=True)
class ArtifactRecord:
    path: str
    label: str
    exists: bool
    sha256: str | None = None
    bytes: int | None = None


def artifact_manifest(trace: TraceEnvelope) -> list[ArtifactRecord]:
    records: list[ArtifactRecord] = []
    for event in trace.events:
        if event.kind != EventKind.ARTIFACT.value:
            continue
        payload = event.payload
        records.append(
            ArtifactRecord(
                path=str(payload.get("path", "")),
                label=str(payload.get("label", "")),
                exists=bool(payload.get("exists")),
                sha256=payload.get("sha256"),
                bytes=int(payload["bytes"]) if "bytes" in payload else None,
            )
        )
    return records


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_artifact_files(base_path: Path, records: list[ArtifactRecord]) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for record in records:
        path = base_path / record.path
        if not path.exists():
            results[record.path] = False
        elif record.sha256 is None:
            results[record.path] = True
        else:
            results[record.path] = sha256_file(path) == record.sha256
    return results
