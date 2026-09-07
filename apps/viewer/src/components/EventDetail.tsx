import type { TraceEvent } from '../types'

interface Props {
  event: TraceEvent
}

function readableKey(key: string) {
  return key
    .replaceAll('_', ' ')
    .replaceAll('.', ' / ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatValue(value: unknown): string {
  if (Array.isArray(value)) return value.map(formatValue).join(', ')
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (typeof value === 'number') return value.toLocaleString()
  if (value === null || value === undefined) return 'None'
  if (typeof value === 'object') return Object.entries(value as Record<string, unknown>)
    .map(([key, nested]) => `${readableKey(key)}: ${formatValue(nested)}`)
    .join('; ')
  return String(value)
}

function flattenPayload(payload: Record<string, unknown>, prefix = ''): Array<[string, unknown]> {
  return Object.entries(payload).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key
    if (value && !Array.isArray(value) && typeof value === 'object') {
      return flattenPayload(value as Record<string, unknown>, path)
    }
    return [[path, value]]
  })
}

export function EventDetail({ event }: Props) {
  const payloadRows = flattenPayload(event.payload)

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
      <div className="payload-grid" aria-label="Event payload fields">
        {payloadRows.length === 0 ? (
          <p className="empty-state">No payload fields were recorded for this event.</p>
        ) : (
          payloadRows.map(([key, value]) => (
            <div className="payload-row" key={key}>
              <span>{readableKey(key)}</span>
              <strong>{formatValue(value)}</strong>
            </div>
          ))
        )}
      </div>
    </section>
  )
}
