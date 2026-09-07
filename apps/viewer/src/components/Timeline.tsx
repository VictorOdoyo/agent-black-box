import type { TraceEvent } from '../types'

interface Props {
  events: TraceEvent[]
  selectedId: string
  onSelect: (id: string) => void
}

export function Timeline({ events, selectedId, onSelect }: Props) {
  return (
    <section className="panel timeline-panel" aria-label="Event timeline">
      <div className="panel-heading">
        <h2>Event timeline</h2>
        <span>{events.length} events</span>
      </div>
      <ol className="timeline-list">
        {events.map((event) => (
          <li key={event.id}>
            <button
              className={event.id === selectedId ? 'timeline-event active' : 'timeline-event'}
              onClick={() => onSelect(event.id)}
              type="button"
            >
              <span className={`kind ${event.kind}`}>{event.kind.replace('_', ' ')}</span>
              <strong>{event.summary}</strong>
              <small>{event.timestamp}</small>
            </button>
          </li>
        ))}
      </ol>
    </section>
  )
}
