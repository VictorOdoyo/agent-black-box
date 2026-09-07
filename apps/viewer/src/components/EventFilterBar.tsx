import { eventKinds } from '../lib/search'
import type { TraceEnvelope } from '../types'

interface Props {
  trace: TraceEnvelope
  query: string
  kind: string
  onQueryChange: (value: string) => void
  onKindChange: (value: string) => void
}

export function EventFilterBar({ trace, query, kind, onQueryChange, onKindChange }: Props) {
  return (
    <section className="filter-bar" aria-label="Filter events">
      <label>
        Search
        <input value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Search events, payloads, or tags" />
      </label>
      <label>
        Kind
        <select value={kind} onChange={(event) => onKindChange(event.target.value)}>
          <option value="all">All</option>
          {eventKinds(trace).map((eventKind) => (
            <option key={eventKind} value={eventKind}>{eventKind}</option>
          ))}
        </select>
      </label>
    </section>
  )
}
