from __future__ import annotations

import tarfile
from pathlib import Path


def create_trace_bundle(trace_paths: list[Path], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as archive:
        for path in trace_paths:
            archive.add(path, arcname=path.name)
    return output
