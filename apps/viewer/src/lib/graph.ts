import type { TraceEnvelope } from '../types'

export interface CausalEdge {
  source: string
  target: string
  reason: string
}

export function buildCausalEdges(trace: TraceEnvelope): CausalEdge[] {
  const edges: CausalEdge[] = []
  let latestDecision: string | null = null
  const permissions = new Map<string, string>()
  trace.events.forEach((event) => {
    if (event.parent_id) edges.push({ source: event.parent_id, target: event.id, reason: 'parent' })
    if (event.kind === 'decision') latestDecision = event.id
    if (event.kind === 'permission' && event.payload.allowed === true) {
      permissions.set(String(event.payload.capability), event.id)
    }
    if (event.kind === 'tool_call') {
      const permission = permissions.get(String(event.payload.name))
      if (permission) edges.push({ source: permission, target: event.id, reason: 'permission' })
      else if (latestDecision) edges.push({ source: latestDecision, target: event.id, reason: 'decision' })
    }
  })
  return edges
}
