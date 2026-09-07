import type { PolicyFinding, TraceEnvelope } from '../types'

export function evaluateTrace(trace: TraceEnvelope): PolicyFinding[] {
  const findings: PolicyFinding[] = []
  const seenPermissions = new Set<string>()
  const ids = new Set<string>()

  trace.events.forEach((event, index) => {
    if (ids.has(event.id)) {
      findings.push({ code: 'duplicate_event_id', severity: 'high', message: `Duplicate event id ${event.id}`, eventId: event.id })
    }
    ids.add(event.id)

    if (index === 0 && event.kind !== 'run_started') {
      findings.push({ code: 'missing_run_start', severity: 'medium', message: 'First event is not run_started.', eventId: event.id })
    }

    if (event.kind === 'permission' && event.payload.allowed === true) {
      seenPermissions.add(String(event.payload.capability))
    }

    if (event.kind === 'tool_call') {
      if (event.payload.requires_permission && !seenPermissions.has(String(event.payload.name))) {
        findings.push({ code: 'missing_permission', severity: 'high', message: 'Tool call required permission before execution.', eventId: event.id })
      }
      if (Number(event.payload.duration_ms ?? 0) > 30000) {
        findings.push({ code: 'slow_tool_call', severity: 'medium', message: 'Tool call exceeded 30000 ms.', eventId: event.id })
      }
    }
  })

  const last = trace.events.at(-1)
  if (last && last.kind !== 'run_finished') {
    findings.push({ code: 'missing_run_finish', severity: 'medium', message: 'Last event is not run_finished.', eventId: last.id })
  }

  return findings
}
