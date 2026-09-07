import { firstDivergence, toolEvents } from '../lib/traceSelectors'
import type { TraceEnvelope } from '../types'

interface Props {
  left: TraceEnvelope
  right: TraceEnvelope
}

export function ComparePanel({ left, right }: Props) {
  const divergence = firstDivergence(left, right)
  return (
    <section className="panel" aria-label="Trace comparison">
      <div className="panel-heading">
        <h2>Comparison</h2>
        <span>{divergence === null ? 'aligned' : `diverges at ${divergence}`}</span>
      </div>
      <div className="comparison-grid">
        <article>
          <small>Baseline</small>
          <strong>{left.run_id}</strong>
          <span>{toolEvents(left).map((event) => String(event.payload.name)).join(', ')}</span>
        </article>
        <article>
          <small>Variant</small>
          <strong>{right.run_id}</strong>
          <span>{toolEvents(right).map((event) => String(event.payload.name)).join(', ')}</span>
        </article>
      </div>
    </section>
  )
}
