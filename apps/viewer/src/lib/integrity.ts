import type { TraceEnvelope } from '../types'

export interface IntegrityFinding {
  code: string
  message: string
}

export function evaluateIntegrity(trace: TraceEnvelope): IntegrityFinding[] {
  const findings: IntegrityFinding[] = []
  const ids = new Set<string>()
  trace.events.forEach((event) => {
    if (ids.has(event.id)) {
      findings.push({ code: 'duplicate_event_id', message: `Duplicate event id ${event.id}` })
    }
    ids.add(event.id)
    if (!event.fingerprint) {
      findings.push({ code: 'missing_fingerprint', message: `Event ${event.id} has no fingerprint` })
    }
  })
  return findings
}
