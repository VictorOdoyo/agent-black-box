import { describe, expect, it } from 'vitest'
import { sampleTrace } from '../data/sampleTrace'
import { evaluateIntegrity } from './integrity'

describe('integrity evaluator', () => {
  it('accepts the fingerprinted synthetic trace', () => {
    expect(evaluateIntegrity(sampleTrace)).toEqual([])
  })

  it('flags duplicate identifiers and missing fingerprints', () => {
    const trace = {
      ...sampleTrace,
      events: [
        sampleTrace.events[0],
        { ...sampleTrace.events[0], fingerprint: undefined },
      ],
    }

    expect(evaluateIntegrity(trace).map((finding) => finding.code)).toEqual([
      'duplicate_event_id',
      'missing_fingerprint',
    ])
  })
})
