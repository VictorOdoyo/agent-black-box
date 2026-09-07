import type { EventKind, TraceEnvelope, TraceEvent } from '../types'

type Payload = Record<string, unknown>

interface InvestigationStage {
  observation: string
  decision: string
  capability: string
  toolSummary: string
  request: Payload
  response: Payload
  durationMs: number
  artifactLabel: string
  artifactPath: string
  artifactBytes: number
  environment: string
  tags: string[]
}

const startedAt = '2026-08-18T11:15:00Z'
const startMs = Date.parse(startedAt)

function timestampFor(index: number) {
  return new Date(startMs + index * 5000).toISOString().replace('.000Z', 'Z')
}

function eventId(index: number) {
  return `evt_${String(index + 1).padStart(3, '0')}`
}

function stableValue(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableValue).join(',')}]`
  if (value && typeof value === 'object') {
    return `{${Object.entries(value as Payload)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, nested]) => `${JSON.stringify(key)}:${stableValue(nested)}`)
      .join(',')}}`
  }
  return JSON.stringify(value)
}

function fingerprintFor(event: TraceEvent) {
  const serialized = stableValue({
    actor: event.actor,
    id: event.id,
    kind: event.kind,
    parent_id: event.parent_id,
    payload: event.payload,
    summary: event.summary,
    tags: event.tags,
    timestamp: event.timestamp,
  })
  let hash = 2166136261
  for (const character of serialized) {
    hash ^= character.charCodeAt(0)
    hash = Math.imul(hash, 16777619)
  }
  return `fnv1a-${(hash >>> 0).toString(16).padStart(8, '0')}`
}

function addEvent(
  events: TraceEvent[],
  kind: EventKind,
  actor: string,
  summary: string,
  payload: Payload,
  tags: string[] = [],
  parentId?: string,
) {
  const event: TraceEvent = {
    id: eventId(events.length),
    kind,
    timestamp: timestampFor(events.length),
    actor,
    summary,
    payload,
    parent_id: parentId ?? null,
    tags,
  }
  event.fingerprint = fingerprintFor(event)
  events.push(event)
  return event
}

const stages: InvestigationStage[] = [
  {
    observation: 'Recent release notes mention retry backoff changes in the payment webhook worker.',
    decision: 'Compare webhook worker deploys against the first failure window.',
    capability: 'query_deploys',
    toolSummary: 'Tool call: query_deploys',
    request: { service: 'payment-webhook-worker', window: 'last_4_hours' },
    response: { deploys: ['deploy_480', 'deploy_481'], likely_related: 'deploy_481' },
    durationMs: 164,
    artifactLabel: 'deploy-window',
    artifactPath: 'out/deploy-window.md',
    artifactBytes: 1420,
    environment: 'Pinned deploy_481 as the investigation baseline.',
    tags: ['deploy', 'timeline'],
  },
  {
    observation: 'Webhook delivery latency increased before customer retries began failing.',
    decision: 'Pull metrics for queue depth, retry age, and delivery failure rates.',
    capability: 'query_metrics',
    toolSummary: 'Tool call: query_metrics',
    request: { metrics: ['webhook.failure_rate', 'queue.depth', 'retry.age'], resolution: '1m' },
    response: { failure_rate: '18.4%', queue_depth: 427, retry_age_seconds_p95: 890 },
    durationMs: 231,
    artifactLabel: 'metrics-spike',
    artifactPath: 'out/metrics-spike.json',
    artifactBytes: 2360,
    environment: 'Metrics cache warmed for replay comparison.',
    tags: ['metrics', 'latency'],
  },
  {
    observation: 'The pending retry queue contains more high-priority payment events than normal.',
    decision: 'Inspect queue partitions for starvation or stuck leases.',
    capability: 'inspect_queue_depth',
    toolSummary: 'Tool call: inspect_queue_depth',
    request: { queue: 'payment-webhook-retry', partitions: 12 },
    response: { overloaded_partitions: [3, 4, 7], oldest_visible_age_seconds: 1140 },
    durationMs: 188,
    artifactLabel: 'queue-partitions',
    artifactPath: 'out/queue-partitions.csv',
    artifactBytes: 3180,
    environment: 'Marked partitions 3, 4, and 7 for focused replay.',
    tags: ['queue', 'worker'],
  },
  {
    observation: 'Worker logs show repeated idempotency conflicts after retry lease renewal.',
    decision: 'Collect log samples from affected workers and extract recurring signatures.',
    capability: 'fetch_service_logs',
    toolSummary: 'Tool call: fetch_service_logs',
    request: { service: 'payment-webhook-worker', pattern: 'idempotency conflict', limit: 50 },
    response: { signatures: ['lease_renewal_race', 'duplicate_attempt_window'], sampled_lines: 50 },
    durationMs: 344,
    artifactLabel: 'worker-log-signatures',
    artifactPath: 'out/worker-log-signatures.ndjson',
    artifactBytes: 5210,
    environment: 'Log sample stored with sensitive headers removed.',
    tags: ['logs', 'idempotency'],
  },
  {
    observation: 'Retry policy changed from fixed delay to capped exponential backoff.',
    decision: 'Inspect policy configuration and compare expected retry cadence.',
    capability: 'inspect_retry_policy',
    toolSummary: 'Tool call: inspect_retry_policy',
    request: { policy: 'payment-webhook-default', version: 'deploy_481' },
    response: { max_attempts: 8, max_delay_seconds: 900, jitter: true, regression: 'lease renewal overlaps' },
    durationMs: 276,
    artifactLabel: 'retry-policy-diff',
    artifactPath: 'out/retry-policy-diff.md',
    artifactBytes: 1840,
    environment: 'Policy diff linked to decision trail.',
    tags: ['retry', 'configuration'],
  },
  {
    observation: 'Provider status page has no matching outage in the affected region.',
    decision: 'Verify upstream gateway health before blaming the integration provider.',
    capability: 'check_provider_status',
    toolSummary: 'Tool call: check_provider_status',
    request: { provider: 'stripe-compatible-gateway', region: 'us-east' },
    response: { status: 'operational', incidents: 0, latency_ms_p95: 94 },
    durationMs: 119,
    artifactLabel: 'provider-health',
    artifactPath: 'out/provider-health.md',
    artifactBytes: 980,
    environment: 'Provider outage hypothesis downgraded.',
    tags: ['provider', 'hypothesis'],
  },
  {
    observation: 'Customer impact is concentrated in accounts with high webhook volume.',
    decision: 'Estimate affected customers, failed deliveries, and revenue exposure.',
    capability: 'query_customer_impact',
    toolSummary: 'Tool call: query_customer_impact',
    request: { segment: 'high_volume_merchants', since: '2026-08-18T10:42:00Z' },
    response: { customers: 14, failed_deliveries: 1820, estimated_revenue_exposure_usd: 41600 },
    durationMs: 253,
    artifactLabel: 'customer-impact',
    artifactPath: 'out/customer-impact.csv',
    artifactBytes: 4290,
    environment: 'Customer impact summary attached to status update draft.',
    tags: ['customers', 'impact'],
  },
  {
    observation: 'Rate-limit counters increased after workers retried the same webhook batch.',
    decision: 'Check whether retry amplification is triggering local throttles.',
    capability: 'inspect_rate_limits',
    toolSummary: 'Tool call: inspect_rate_limits',
    request: { limiter: 'webhook-delivery', keys: ['customer', 'endpoint', 'tenant'] },
    response: { throttled_keys: 23, reset_seconds_p50: 42, reset_seconds_p95: 180 },
    durationMs: 201,
    artifactLabel: 'rate-limit-sample',
    artifactPath: 'out/rate-limit-sample.json',
    artifactBytes: 2675,
    environment: 'Rate-limit evidence associated with retry amplification.',
    tags: ['rate-limit', 'throttle'],
  },
  {
    observation: 'Duplicate webhook attempts appear for the same event identifiers.',
    decision: 'Scan delivery records for duplicate attempts and missing acknowledgements.',
    capability: 'scan_duplicate_deliveries',
    toolSummary: 'Tool call: scan_duplicate_deliveries',
    request: { dataset: 'webhook_deliveries', lookback_minutes: 90 },
    response: { duplicate_groups: 37, missing_acknowledgements: 19, worst_endpoint: 'orders.created' },
    durationMs: 413,
    artifactLabel: 'duplicate-deliveries',
    artifactPath: 'out/duplicate-deliveries.csv',
    artifactBytes: 5520,
    environment: 'Duplicate-delivery sample prepared for replay.',
    tags: ['duplicates', 'acknowledgements'],
  },
  {
    observation: 'A controlled replay can reproduce the failure without customer credentials.',
    decision: 'Build a replay plan using sanitized events from overloaded partitions.',
    capability: 'simulate_replay_plan',
    toolSummary: 'Tool call: simulate_replay_plan',
    request: { partitions: [3, 4, 7], anonymized: true, max_events: 25 },
    response: { replay_events: 25, reproduced: true, failing_step: 'lease_renewal_after_retry' },
    durationMs: 635,
    artifactLabel: 'sanitized-replay-plan',
    artifactPath: 'out/sanitized-replay-plan.json',
    artifactBytes: 7160,
    environment: 'Replay data marked synthetic-safe for public demonstration.',
    tags: ['replay', 'sanitized'],
  },
  {
    observation: 'Rollback simulation reduces queue age without dropping idempotency protection.',
    decision: 'Compare rollback impact against a smaller retry-policy patch.',
    capability: 'simulate_rollback',
    toolSummary: 'Tool call: simulate_rollback',
    request: { candidate: 'rollback_retry_policy_to_480', horizon_minutes: 45 },
    response: { projected_recovery_minutes: 18, customer_risk: 'low', engineering_risk: 'medium' },
    durationMs: 721,
    artifactLabel: 'rollback-simulation',
    artifactPath: 'out/rollback-simulation.md',
    artifactBytes: 3370,
    environment: 'Rollback option retained as backup remediation.',
    tags: ['rollback', 'remediation'],
  },
  {
    observation: 'The incident channel needs a concise update for support and account teams.',
    decision: 'Draft a status update with impact, mitigation, and next check-in time.',
    capability: 'draft_status_update',
    toolSummary: 'Tool call: draft_status_update',
    request: { audience: ['support', 'account-management'], tone: 'operational' },
    response: { draft_id: 'status_update_001', sections: ['impact', 'mitigation', 'next_update'] },
    durationMs: 154,
    artifactLabel: 'status-update-draft',
    artifactPath: 'out/status-update-draft.md',
    artifactBytes: 1920,
    environment: 'Status update queued for human approval.',
    tags: ['comms', 'status'],
  },
  {
    observation: 'Ownership metadata points to two services and one shared retry library.',
    decision: 'Resolve the service owner and escalation path before recommending changes.',
    capability: 'resolve_service_owner',
    toolSummary: 'Tool call: resolve_service_owner',
    request: { services: ['payment-webhook-worker', 'retry-core'] },
    response: { owner: 'payments-platform', escalation: 'platform-oncall', confidence: 0.92 },
    durationMs: 138,
    artifactLabel: 'ownership-map',
    artifactPath: 'out/ownership-map.md',
    artifactBytes: 1260,
    environment: 'Owner assignment attached to remediation recommendation.',
    tags: ['ownership', 'escalation'],
  },
  {
    observation: 'The trace contains personal contacts, customer identifiers, and request secrets.',
    decision: 'Preview redactions before generating a reviewer-shareable trace.',
    capability: 'preview_trace_redaction',
    toolSummary: 'Tool call: preview_trace_redaction',
    request: { trace: 'trc_webhook_recovery_481', policy: 'default-sharing-policy-v1' },
    response: { replacements: 4, blocked_fields: ['email', 'authorization', 'account_id', 'phone'] },
    durationMs: 177,
    artifactLabel: 'redaction-report',
    artifactPath: 'out/redaction-report.md',
    artifactBytes: 2110,
    environment: 'Shared trace preview contains no raw credentials.',
    tags: ['redaction', 'privacy'],
  },
  {
    observation: 'Post-incident actions need owners, verification steps, and due dates.',
    decision: 'Generate a postmortem outline from the evidence trail.',
    capability: 'generate_postmortem_outline',
    toolSummary: 'Tool call: generate_postmortem_outline',
    request: { incident: 'payment-webhook-recovery', include_actions: true },
    response: { action_items: 6, owners_assigned: 5, unresolved_questions: 2 },
    durationMs: 289,
    artifactLabel: 'postmortem-outline',
    artifactPath: 'out/postmortem-outline.md',
    artifactBytes: 4080,
    environment: 'Postmortem outline prepared from synthetic evidence.',
    tags: ['postmortem', 'follow-up'],
  },
]

function buildSampleEvents(): TraceEvent[] {
  const events: TraceEvent[] = []
  const runStarted = addEvent(events, 'run_started', 'agent', 'Agent run started', {
    model: 'incident-triage-agent-v2',
    run_mode: 'synthetic-demo',
    trigger: 'payment-webhook-outage',
  })
  const runtime = addEvent(events, 'environment', 'runtime', 'Runtime and policy context loaded', {
    sdk: 'agent-black-box',
    viewer: 'react',
    python: '3.13',
    node: '20',
  }, ['environment'], runStarted.id)
  const policy = addEvent(events, 'environment', 'policy-engine', 'Default trace sharing policy loaded', {
    policy: 'default-sharing-policy-v1',
    redaction_rules: ['email', 'bearer_token', 'customer_identifier', 'phone'],
  }, ['policy'], runtime.id)
  const report = addEvent(events, 'observation', 'operator', 'User reported a payment webhook outage', {
    channel: 'incident-bridge',
    severity: 'high',
    affected_area: 'payment webhooks',
  }, ['input', 'incident'], policy.id)
  const impact = addEvent(events, 'observation', 'agent', 'Initial symptoms suggest delayed retries and duplicate delivery attempts', {
    affected_customers_estimate: 12,
    failure_window: '2026-08-18T10:42:00Z/2026-08-18T11:15:00Z',
    confidence: 0.72,
  }, ['triage'], report.id)
  const classification = addEvent(events, 'decision', 'agent', 'Classify incident as integration failure with retry amplification risk', {
    rationale: 'Failures cluster around webhook retry behavior after the newest worker deploy.',
    alternatives: ['provider outage', 'database latency', 'customer endpoint failure'],
  }, ['triage', 'decision'], impact.id)
  const permission = addEvent(events, 'permission', 'policy-engine', 'Permission allowed: search_incidents', {
    capability: 'search_incidents',
    allowed: true,
    reason: 'Read-only incident search with no customer secrets returned.',
  }, ['permission'], classification.id)
  addEvent(events, 'tool_call', 'agent', 'Tool call: search_incidents', {
    name: 'search_incidents',
    request: { query: 'payment webhook retry failure', limit: 5 },
    response: { matches: ['INC-421', 'INC-422', 'INC-437'], similar_open_incidents: 1 },
    status: 'ok',
    duration_ms: 112,
    requires_permission: true,
  }, ['tool', 'triage'], permission.id)

  stages.forEach((stage) => {
    const observation = addEvent(events, 'observation', 'agent', stage.observation, {
      phase: stage.tags[0],
      confidence: 0.78,
      evidence_source: stage.capability,
    }, stage.tags)
    const decision = addEvent(events, 'decision', 'agent', stage.decision, {
      rationale: `The ${stage.tags[0]} evidence changes the investigation priority.`,
      expected_outcome: stage.artifactLabel,
      next_capability: stage.capability,
    }, [...stage.tags, 'decision'], observation.id)
    const permissionEvent = addEvent(events, 'permission', 'policy-engine', `Permission allowed: ${stage.capability}`, {
      capability: stage.capability,
      allowed: true,
      reason: 'Synthetic demo trace permits read-only diagnostic access.',
    }, ['permission', ...stage.tags], decision.id)
    const tool = addEvent(events, 'tool_call', 'agent', stage.toolSummary, {
      name: stage.capability,
      request: stage.request,
      response: stage.response,
      status: 'ok',
      duration_ms: stage.durationMs,
      requires_permission: true,
    }, ['tool', ...stage.tags], permissionEvent.id)
    const artifact = addEvent(events, 'artifact', 'agent', `Artifact captured: ${stage.artifactLabel}`, {
      path: stage.artifactPath,
      label: stage.artifactLabel,
      exists: true,
      bytes: stage.artifactBytes,
      derived_from: tool.id,
    }, ['artifact', ...stage.tags], tool.id)
    addEvent(events, 'environment', 'runtime', stage.environment, {
      phase: stage.tags[0],
      checkpoint: stage.artifactLabel,
      replay_safe: true,
    }, ['checkpoint', ...stage.tags], artifact.id)
  })

  const finalDecision = addEvent(events, 'decision', 'agent', 'Recommend retry-policy patch with rollback plan held in reserve', {
    recommendation: 'Patch retry lease renewal and keep rollback candidate ready for immediate use.',
    validation: ['sanitized replay reproduced failure', 'provider outage ruled out', 'redaction preview clean'],
    residual_risk: 'medium',
  }, ['resolution', 'decision'])
  addEvent(events, 'run_finished', 'agent', 'Agent run finished with reviewer-safe incident packet', {
    status: 'completed',
    events_recorded: 100,
    artifacts_created: 15,
    policy_findings: 0,
  }, ['resolution'], finalDecision.id)

  return events
}

export const sampleTrace: TraceEnvelope = {
  schema_version: 'abb.trace.v1',
  trace_id: 'trc_webhook_recovery_481',
  run_id: 'run_payment_webhook_recovery',
  app: 'incident-triage-agent',
  started_at: startedAt,
  metadata: {
    model: 'incident-triage-agent-v2',
    environment: 'synthetic-demo',
    domain: 'payment-webhook-incident-response',
    generated_events: 100,
  },
  events: buildSampleEvents(),
}

export const alternateTrace: TraceEnvelope = {
  ...sampleTrace,
  trace_id: 'trc_webhook_recovery_481_alt',
  run_id: 'run_payment_webhook_recovery_alt',
  events: sampleTrace.events.map((event, index) => {
    if (index !== 23) return event
    return {
      ...event,
      id: 'evt_alt_024',
      summary: 'Tool call: query_metrics with five-minute rollup',
      payload: {
        ...event.payload,
        request: { metrics: ['webhook.failure_rate', 'queue.depth'], resolution: '5m' },
        response: { failure_rate: '16.9%', queue_depth: 388, retry_age_seconds_p95: 812 },
      },
    }
  }),
}
