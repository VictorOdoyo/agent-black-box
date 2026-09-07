import { describe, expect, it } from 'vitest'
import { sampleTrace } from '../data/sampleTrace'
import { evaluateIntegrity } from './integrity'

describe('integrity evaluator', () => {
  it('requires fingerprints', () => {
    expect(evaluateIntegrity(sampleTrace).map((finding) => finding.code)).toContain('missing_fingerprint')
  })
})
