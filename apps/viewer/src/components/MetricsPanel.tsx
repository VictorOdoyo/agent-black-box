import { eventDuration, toolEvents } from '../lib/traceSelectors'
import type { TraceEnvelope } from '../types'

interface Props {
  trace: TraceEnvelope
}

export function MetricsPanel({ trace }: Props) {
  const tools = toolEvents(trace)
  const totalDuration = tools.reduce((sum, event) => sum + eventDuration(event), 0)
  const maxDuration = Math.max(0, ...tools.map(eventDuration))
  return (
    <section className="panel" aria-label="Trace metrics">
      <div className="panel-heading">
        <h2>Metrics</h2>
        <span>{totalDuration} ms</span>
      </div>
      <div className="comparison-grid">
        <article><small>Total tool duration</small><strong>{totalDuration} ms</strong><span>Across recorded calls</span></article>
        <article><small>Max tool duration</small><strong>{maxDuration} ms</strong><span>Slowest recorded call</span></article>
      </div>
    </section>
  )
}
