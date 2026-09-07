import type { TraceEnvelope } from '../types'

export const sampleTrace: TraceEnvelope = {
  schema_version: 'abb.trace.v1',
  trace_id: 'trc_demo_dispatch',
  run_id: 'run_demo_incident_triage',
  app: 'incident-triage-agent',
  started_at: '2026-08-18T11:15:00Z',
  metadata: { model: 'example-agent', environment: 'local-demo' },
  events: [
    { id: 'evt_001', kind: 'run_started', timestamp: '2026-08-18T11:15:00Z', actor: 'agent', summary: 'Agent run started', payload: { metadata: { model: 'example-agent' } }, tags: [] },
    { id: 'evt_002', kind: 'observation', timestamp: '2026-08-18T11:15:03Z', actor: 'agent', summary: 'User reported a payment webhook outage', payload: { channel: 'ops', severity: 'high' }, tags: ['input'] },
    { id: 'evt_003', kind: 'decision', timestamp: '2026-08-18T11:15:08Z', actor: 'agent', summary: 'Classify incident as integration failure', payload: { rationale: 'Recent deploy touched webhook retry logic.', alternatives: ['provider outage', 'database latency'] }, tags: ['triage'] },
    { id: 'evt_004', kind: 'permission', timestamp: '2026-08-18T11:15:10Z', actor: 'agent', summary: 'Permission allowed: search_incidents', payload: { capability: 'search_incidents', allowed: true, reason: 'Read-only diagnostic search.' }, tags: [] },
    { id: 'evt_005', kind: 'tool_call', timestamp: '2026-08-18T11:15:11Z', actor: 'agent', summary: 'Tool call: search_incidents', payload: { name: 'search_incidents', request: { query: 'webhook retry failure' }, response: { matches: ['INC-421', 'INC-422'] }, status: 'ok', duration_ms: 112, requires_permission: true }, tags: ['tool'] },
    { id: 'evt_006', kind: 'artifact', timestamp: '2026-08-18T11:15:22Z', actor: 'agent', summary: 'Artifact captured: incident-summary', payload: { path: 'out/incident-summary.md', label: 'incident-summary', exists: true, bytes: 820 }, tags: ['artifact'] },
    { id: 'evt_007', kind: 'run_finished', timestamp: '2026-08-18T11:15:29Z', actor: 'agent', summary: 'Agent run finished', payload: { status: 'completed' }, tags: [] },
  ],
}

export const alternateTrace: TraceEnvelope = {
  ...sampleTrace,
  trace_id: 'trc_demo_dispatch_alt',
  run_id: 'run_demo_incident_triage_alt',
  events: [
    ...sampleTrace.events.slice(0, 3),
    { id: 'evt_alt_004', kind: 'tool_call', timestamp: '2026-08-18T11:15:10Z', actor: 'agent', summary: 'Tool call: query_metrics', payload: { name: 'query_metrics', request: { metric: 'webhook.failures' }, response: { spike: true }, status: 'ok', duration_ms: 89, requires_permission: false }, tags: ['tool'] },
    ...sampleTrace.events.slice(-2),
  ],
}
