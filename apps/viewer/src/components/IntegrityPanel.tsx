import { evaluateIntegrity } from '../lib/integrity'
import type { TraceEnvelope } from '../types'

interface Props {
  trace: TraceEnvelope
}

export function IntegrityPanel({ trace }: Props) {
  const findings = evaluateIntegrity(trace)
  return (
    <section className="panel" aria-label="Integrity findings">
      <div className="panel-heading">
        <h2>Integrity</h2>
        <span>{findings.length || 'clean'}</span>
      </div>
      {findings.length === 0 ? (
        <p className="empty-state">All event identifiers and fingerprints are present.</p>
      ) : (
        <ul className="finding-list">
          {findings.map((finding) => (
            <li key={finding.code}><strong>{finding.code}</strong><span>{finding.message}</span></li>
          ))}
        </ul>
      )}
    </section>
  )
}
