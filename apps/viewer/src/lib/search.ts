import type { TraceEnvelope, TraceEvent } from '../types'

export function eventMatchesQuery(event: TraceEvent, query: string): boolean {
  const normalized = query.trim().toLowerCase()
  if (!normalized) return true
  const body = `${event.kind} ${event.actor} ${event.summary} ${event.tags.join(' ')} ${JSON.stringify(event.payload)}`.toLowerCase()
  return normalized.split(/\s+/).every((term) => body.includes(term))
}

export function filterTraceEvents(trace: TraceEnvelope, query: string, kind: string): TraceEvent[] {
  return trace.events.filter((event) => {
    const kindMatches = kind === 'all' || event.kind === kind
    return kindMatches && eventMatchesQuery(event, query)
  })
}

export function eventKinds(trace: TraceEnvelope): string[] {
  return Array.from(new Set(trace.events.map((event) => event.kind))).sort()
}
