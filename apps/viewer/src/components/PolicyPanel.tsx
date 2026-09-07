import { evaluateTrace } from '../lib/policy'
import type { TraceEnvelope } from '../types'

interface Props {
  trace: TraceEnvelope
}

export function PolicyPanel({ trace }: Props) {
  const findings = evaluateTrace(trace)
  return (
    <section className="panel" aria-label="Policy findings">
      <div className="panel-heading">
        <h2>Policy findings</h2>
        <span>{findings.length || 'clean'}</span>
      </div>
      {findings.length === 0 ? (
        <p className="empty-state">No policy findings for this trace.</p>
      ) : (
        <ul className="finding-list">
          {findings.map((finding) => (
            <li key={`${finding.code}-${finding.eventId}`} className={finding.severity}>
              <strong>{finding.code}</strong>
              <span>{finding.message}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
