from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .models import TraceEnvelope, stable_hash


@dataclass
class IntegrityFinding:
    code: str
    message: str
    event_id: str | None = None


def verify_event_fingerprints(trace: TraceEnvelope) -> list[IntegrityFinding]:
    findings: list[IntegrityFinding] = []
    for event in trace.events:
        expected = event.compute_fingerprint()
        if event.fingerprint and event.fingerprint != expected:
            findings.append(
                IntegrityFinding(
                    code="fingerprint_mismatch",
                    message=f"Event {event.id} fingerprint does not match its contents.",
                    event_id=event.id,
                )
            )
    return findings


def chain_hash(trace: TraceEnvelope) -> str:
    cursor = "abb.chain.v1"
    for event in trace.events:
        cursor = stable_hash({"previous": cursor, "event": event.fingerprint or event.compute_fingerprint()})
    return stable_hash({"trace_id": trace.trace_id, "run_id": trace.run_id, "chain": cursor})


def trace_manifest(trace: TraceEnvelope) -> dict[str, Any]:
    return {
        "schema_version": "abb.manifest.v1",
        "trace_id": trace.trace_id,
        "run_id": trace.run_id,
        "event_count": len(trace.events),
        "chain_hash": chain_hash(trace),
        "event_fingerprints": [event.fingerprint or event.compute_fingerprint() for event in trace.events],
    }


def verify_manifest(trace: TraceEnvelope, manifest: Mapping[str, Any]) -> list[IntegrityFinding]:
    findings = verify_event_fingerprints(trace)
    if manifest.get("trace_id") != trace.trace_id:
        findings.append(IntegrityFinding("trace_id_mismatch", "Manifest trace_id does not match trace."))
    if manifest.get("run_id") != trace.run_id:
        findings.append(IntegrityFinding("run_id_mismatch", "Manifest run_id does not match trace."))
    if manifest.get("event_count") != len(trace.events):
        findings.append(IntegrityFinding("event_count_mismatch", "Manifest event count does not match trace."))
    if manifest.get("chain_hash") != chain_hash(trace):
        findings.append(IntegrityFinding("chain_hash_mismatch", "Manifest chain hash does not match trace."))
    return findings
