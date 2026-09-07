# Minimization

Trace minimization extracts the smallest useful trace around matching events.

Use:

```bash
abb minimize fixtures/traces/incident_triage.json out/minimized.json --kind tool_call --window 1
```

This keeps the selected events plus nearby context.
