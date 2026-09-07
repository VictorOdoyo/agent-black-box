# Architecture

Agent Black Box separates capture, storage, replay, policy evaluation, and presentation.

## SDK

The Python SDK records events into a `TraceEnvelope`. Each event has a stable fingerprint, timestamp, actor, summary, payload, tags, and parent reference.

## Redaction

Payloads are sanitized before they enter the trace. The default policy redacts common secret keys and text patterns such as emails and bearer tokens.

## Replay

Replay turns recorded tool calls into deterministic mocks. The target agent can consume the same tool names while responses come from the trace instead of live systems.

## Viewer

The React viewer provides local inspection for timelines, selected event payloads, policy findings, replay plans, redaction previews, and run comparison.
