export type EventKind =
  | 'run_started'
  | 'run_finished'
  | 'observation'
  | 'decision'
  | 'permission'
  | 'tool_call'
  | 'environment'
  | 'artifact'
  | 'error'

export interface TraceEvent {
  id: string
  kind: EventKind
  timestamp: string
  actor: string
  summary: string
  payload: Record<string, unknown>
  parent_id?: string | null
  tags: string[]
  fingerprint?: string
}

export interface TraceEnvelope {
  schema_version: string
  trace_id: string
  run_id: string
  app: string
  started_at: string
  metadata: Record<string, unknown>
  events: TraceEvent[]
}

export interface PolicyFinding {
  code: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  message: string
  eventId?: string
}
