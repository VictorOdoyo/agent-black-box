import { toolEvents } from '../lib/traceSelectors'
import type { TraceEnvelope } from '../types'

interface Props {
  trace: TraceEnvelope
}

export function ReplayConsole({ trace }: Props) {
  const tools = toolEvents(trace)
  return (
    <section className="panel" aria-label="Replay console">
      <div className="panel-heading">
        <h2>Replay plan</h2>
        <span>{tools.length} mocks</span>
      </div>
      <div className="tool-stack">
        {tools.map((event, index) => (
          <article className="tool-card" key={event.id}>
            <small>Step {index + 1}</small>
            <strong>{String(event.payload.name)}</strong>
            <code>{String(event.payload.status)}</code>
          </article>
        ))}
      </div>
    </section>
  )
}
