# Integrity

Trace integrity is based on event fingerprints and a trace-level hash chain.

Use:

```bash
abb manifest fixtures/traces/incident_triage.json --output out/manifest.json
abb verify-manifest fixtures/traces/incident_triage.json out/manifest.json
```

The manifest records the trace id, run id, event count, event fingerprints, and chain hash.
