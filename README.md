# Agent Black Box

Agent Black Box is a portable run recorder for AI agent systems. It captures observations, decisions, permission checks, tool calls, environment changes, artifacts, and errors in a versioned JSON trace that can be inspected, redacted, replayed, compared, and evaluated by policy checks.

The repository includes a Python SDK and CLI, a React trace viewer, JSON schemas, fixtures, examples, tests, Docker support, and CI.

## What it solves

Modern agents can fail because of stale observations, missing permissions, unsafe tool calls, leaking payloads, or environment changes that are hard to reconstruct after the fact. Agent Black Box gives each run a durable record that can be shared without live credentials.

## Capabilities

- Record agent events with a small Python SDK
- Redact emails, bearer tokens, API keys, passwords, and secret-like keys
- Replay recorded tool responses with deterministic mocks
- Fork a trace at a known event for controlled experiments
- Compare two runs and locate the first behavioral divergence
- Evaluate traces for lifecycle, permission, slow tool, secret leak, and error-budget findings
- Export trace summaries as Markdown and policy findings as JUnit XML
- Inspect traces in a local React dashboard

## Repository layout

```text
packages/python/agent_black_box/  Python SDK and CLI
apps/viewer/                      React trace viewer
schemas/                          JSON schemas for traces and policies
fixtures/traces/                  Demo traces used by examples and tests
examples/                         Minimal recording and replay examples
docs/                             Architecture and workflow documentation
```

## Requirements

- Python 3.11+
- Node.js 20+
- pnpm 9+

## Install

```bash
python -m pip install -e ".[dev]"
pnpm install
```

## Run checks

```bash
python -m pytest
pnpm --dir apps/viewer test -- --run
pnpm --dir apps/viewer build
```

## Use the CLI

```bash
abb inspect fixtures/traces/incident_triage.json
abb validate fixtures/traces/incident_triage.json
abb replay fixtures/traces/incident_triage.json
abb policy fixtures/traces/incident_triage.json
abb compare fixtures/traces/incident_triage.json fixtures/traces/incident_triage_alt.json
abb export fixtures/traces/incident_triage.json out/trace.md
```

## Run the viewer

```bash
pnpm dev
```

Open the local Vite URL and inspect the bundled demo trace.
