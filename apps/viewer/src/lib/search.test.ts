import { describe, expect, it } from 'vitest'
import { sampleTrace } from '../data/sampleTrace'
import { eventKinds, eventMatchesQuery, filterTraceEvents } from './search'

describe('search helpers', () => {
  it('matches event payload text', () => {
    expect(eventMatchesQuery(sampleTrace.events[1], 'payment webhook')).toBe(true)
  })

  it('filters by kind', () => {
    expect(filterTraceEvents(sampleTrace, '', 'tool_call')).toHaveLength(1)
  })

  it('lists event kinds', () => {
    expect(eventKinds(sampleTrace)).toContain('decision')
  })
})
