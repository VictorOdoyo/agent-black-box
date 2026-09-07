import { describe, expect, it } from 'vitest'
import { sampleTrace } from '../data/sampleTrace'
import { evaluateTrace } from './policy'

describe('policy evaluation', () => {
  it('accepts the synthetic trace', () => {
    expect(evaluateTrace(sampleTrace)).toEqual([])
  })

  it('flags missing permission', () => {
    const trace = {
      ...sampleTrace,
      events: sampleTrace.events.filter((event) => event.kind !== 'permission'),
    }
    expect(evaluateTrace(trace).map((finding) => finding.code)).toContain('missing_permission')
  })
})
