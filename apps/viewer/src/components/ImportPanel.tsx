import type { TraceEnvelope } from '../types'

interface Props {
  trace: TraceEnvelope
}

export function ImportPanel({ trace }: Props) {
  return (
    <section className="panel" aria-label="Trace import">
      <div className="panel-heading">
        <h2>Trace metadata</h2>
        <span>{trace.schema_version}</span>
      </div>
      <dl className="event-metadata">
        <div><dt>Trace id</dt><dd>{trace.trace_id}</dd></div>
        <div><dt>Run id</dt><dd>{trace.run_id}</dd></div>
        <div><dt>Application</dt><dd>{trace.app}</dd></div>
      </dl>
    </section>
  )
}
