import { eventCounts, timelineWindow, toolEvents } from '../lib/traceSelectors'
import type { TraceEnvelope } from '../types'

interface Props {
  trace: TraceEnvelope
}

export function SummaryCards({ trace }: Props) {
  const counts = eventCounts(trace)
  const window = timelineWindow(trace)
  return (
    <section className="summary-grid" aria-label="Trace summary">
      <article className="metric-card">
        <span>Events</span>
        <strong>{trace.events.length}</strong>
        <small>{window.start} to {window.end}</small>
      </article>
      <article className="metric-card">
        <span>Tool calls</span>
        <strong>{toolEvents(trace).length}</strong>
        <small>{counts.tool_call ?? 0} recorded interactions</small>
      </article>
      <article className="metric-card">
        <span>Decisions</span>
        <strong>{counts.decision ?? 0}</strong>
        <small>Inspectable rationale events</small>
      </article>
      <article className="metric-card">
        <span>Artifacts</span>
        <strong>{counts.artifact ?? 0}</strong>
        <small>Outputs linked to the run</small>
      </article>
    </section>
  )
}
