# Trace Format

The trace format is JSON and versioned by `schema_version`.

Required top-level fields:

- `schema_version`
- `trace_id`
- `run_id`
- `app`
- `started_at`
- `events`

Events represent observations, decisions, permissions, tool calls, environment changes, artifacts, errors, and lifecycle markers. Tool-call payloads contain `name`, `request`, `response`, `status`, `duration_ms`, and `requires_permission`.
