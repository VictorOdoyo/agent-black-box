import { describe, expect, it } from 'vitest'
import { sampleTrace } from '../data/sampleTrace'
import { buildCausalEdges } from './graph'

describe('graph builder', () => {
  it('links permissions to tool calls', () => {
    expect(buildCausalEdges(sampleTrace).map((edge) => edge.reason)).toContain('permission')
  })
})
