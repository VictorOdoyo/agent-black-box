import type { TraceEvent } from '../types'

interface Props {
  event: TraceEvent
}

export function EventDetail({ event }: Props) {
  return (
    <section className="panel detail-panel" aria-label="Selected event detail">
      <div className="panel-heading">
        <h2>Event detail</h2>
        <span>{event.kind}</span>
      </div>
      <dl className="event-metadata">
        <div><dt>Actor</dt><dd>{event.actor}</dd></div>
        <div><dt>Timestamp</dt><dd>{event.timestamp}</dd></div>
        <div><dt>Event id</dt><dd>{event.id}</dd></div>
      </dl>
      <p className="event-summary">{event.summary}</p>
      <pre>{JSON.stringify(event.payload, null, 2)}</pre>
    </section>
  )
}
