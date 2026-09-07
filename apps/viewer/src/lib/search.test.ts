import { describe, expect, it } from 'vitest'
import { sampleTrace } from '../data/sampleTrace'
import { eventKinds, eventMatchesQuery, filterTraceEvents } from './search'

describe('search helpers', () => {
  it('matches event payload text', () => {
    const incidentReport = sampleTrace.events.find((event) => event.summary.includes('payment webhook outage'))
    expect(incidentReport).toBeDefined()
    expect(eventMatchesQuery(incidentReport!, 'payment webhook')).toBe(true)
  })

  it('filters by kind', () => {
    expect(filterTraceEvents(sampleTrace, '', 'tool_call')).toHaveLength(16)
  })

  it('lists event kinds', () => {
    expect(eventKinds(sampleTrace)).toContain('decision')
  })
})
