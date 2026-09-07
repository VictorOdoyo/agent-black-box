import { describe, expect, it } from 'vitest'
import { alternateTrace, sampleTrace } from '../data/sampleTrace'
import { eventCounts, firstDivergence, timelineWindow, toolEvents } from './traceSelectors'

describe('trace selectors', () => {
  it('uses a substantial synthetic trace', () => {
    expect(sampleTrace.events).toHaveLength(100)
  })

  it('counts event kinds', () => {
    expect(eventCounts(sampleTrace).tool_call).toBe(16)
    expect(eventCounts(sampleTrace).artifact).toBe(15)
  })

  it('finds tool events', () => {
    expect(toolEvents(sampleTrace)[0].payload.name).toBe('search_incidents')
  })

  it('locates first divergence', () => {
    expect(firstDivergence(sampleTrace, alternateTrace)).toBe(23)
  })

  it('returns the visible timeline window', () => {
    expect(timelineWindow(sampleTrace).start).toBe('2026-08-18T11:15:00Z')
  })
})
