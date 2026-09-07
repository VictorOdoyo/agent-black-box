import type { TraceEnvelope, TraceEvent } from '../types'

export function eventCounts(trace: TraceEnvelope): Record<string, number> {
  return trace.events.reduce<Record<string, number>>((counts, event) => {
    counts[event.kind] = (counts[event.kind] ?? 0) + 1
    return counts
  }, {})
}

export function toolEvents(trace: TraceEnvelope): TraceEvent[] {
  return trace.events.filter((event) => event.kind === 'tool_call')
}

export function firstDivergence(left: TraceEnvelope, right: TraceEnvelope): number | null {
  const max = Math.max(left.events.length, right.events.length)
  for (let index = 0; index < max; index += 1) {
    const leftEvent = left.events[index]
    const rightEvent = right.events[index]
    if (!leftEvent || !rightEvent) return index
    if (leftEvent.kind !== rightEvent.kind || leftEvent.summary !== rightEvent.summary) return index
  }
  return null
}

export function eventDuration(event: TraceEvent): number {
  const duration = event.payload.duration_ms
  return typeof duration === 'number' ? duration : 0
}

export function timelineWindow(trace: TraceEnvelope): { start: string; end: string } {
  const start = trace.events[0]?.timestamp ?? trace.started_at
  const end = trace.events.at(-1)?.timestamp ?? trace.started_at
  return { start, end }
}
