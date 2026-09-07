import { buildCausalEdges } from '../lib/graph'
import type { TraceEnvelope } from '../types'

interface Props {
  trace: TraceEnvelope
}

export function CausalGraphPanel({ trace }: Props) {
  const edges = buildCausalEdges(trace)
  return (
    <section className="panel" aria-label="Causal graph">
      <div className="panel-heading">
        <h2>Causal graph</h2>
        <span>{edges.length} edges</span>
      </div>
      <ul className="graph-list">
        {edges.map((edge) => (
          <li key={`${edge.source}-${edge.target}-${edge.reason}`}>
            <code>{edge.source}</code>
            <span>{edge.reason}</span>
            <code>{edge.target}</code>
          </li>
        ))}
      </ul>
    </section>
  )
}
