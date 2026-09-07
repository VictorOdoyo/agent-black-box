# Policies

Policy checks are local quality gates for recorded runs.

Implemented findings:

- Missing lifecycle events
- Duplicate event ids
- Secret-like tokens in payloads
- Tool calls that required permission without a prior permission event
- Slow tool calls
- Tool-call errors
- Error-budget violations
