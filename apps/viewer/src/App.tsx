import { useMemo, useState } from 'react'
import { alternateTrace, sampleTrace } from './data/sampleTrace'
import { CausalGraphPanel } from './components/CausalGraphPanel'
import { ComparePanel } from './components/ComparePanel'
import { EventDetail } from './components/EventDetail'
import { EventFilterBar } from './components/EventFilterBar'
import { ImportPanel } from './components/ImportPanel'
import { ImportTextarea } from './components/ImportTextarea'
import { IntegrityPanel } from './components/IntegrityPanel'
import { MetricsPanel } from './components/MetricsPanel'
import { PolicyPanel } from './components/PolicyPanel'
import { RedactionPanel } from './components/RedactionPanel'
import { ReplayConsole } from './components/ReplayConsole'
import { SummaryCards } from './components/SummaryCards'
import { Timeline } from './components/Timeline'
import { filterTraceEvents } from './lib/search'
import './App.css'

type View = 'timeline' | 'metrics' | 'replay' | 'policy' | 'integrity' | 'compare' | 'causality' | 'redaction' | 'import'

const views: View[] = ['timeline', 'metrics', 'replay', 'policy', 'integrity', 'compare', 'causality', 'redaction', 'import']

export default function App() {
  const [view, setView] = useState<View>('timeline')
  const [query, setQuery] = useState('')
  const [kind, setKind] = useState('all')
  const [selectedId, setSelectedId] = useState(sampleTrace.events[0].id)
  const filteredEvents = useMemo(() => filterTraceEvents(sampleTrace, query, kind), [query, kind])
  const selectedEvent = useMemo(
    () => sampleTrace.events.find((event) => event.id === selectedId) ?? filteredEvents[0] ?? sampleTrace.events[0],
    [filteredEvents, selectedId],
  )

  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand-mark">A</div>
        <div>
          <strong>Agent Black Box</strong>
          <span>Run recorder</span>
        </div>
      </aside>
      <section className="content">
        <header className="page-header">
          <div>
            <p>AGENT RUNS</p>
            <h1>AI Agent Black Box Recorder</h1>
          </div>
          <nav aria-label="Views">
            {views.map((item) => (
              <button className={item === view ? 'active' : ''} key={item} onClick={() => setView(item)} type="button">
                {item}
              </button>
            ))}
          </nav>
        </header>

        <SummaryCards trace={sampleTrace} />

        {view === 'timeline' && (
          <>
            <EventFilterBar trace={sampleTrace} query={query} kind={kind} onQueryChange={setQuery} onKindChange={setKind} />
            <div className="main-grid">
              <Timeline events={filteredEvents} selectedId={selectedId} onSelect={setSelectedId} />
              <EventDetail event={selectedEvent} />
            </div>
          </>
        )}
        {view === 'metrics' && <MetricsPanel trace={sampleTrace} />}
        {view === 'replay' && (
          <div className="main-grid">
            <ReplayConsole trace={sampleTrace} />
            <ImportPanel trace={sampleTrace} />
          </div>
        )}
        {view === 'policy' && <PolicyPanel trace={sampleTrace} />}
        {view === 'integrity' && <IntegrityPanel trace={sampleTrace} />}
        {view === 'compare' && <ComparePanel left={sampleTrace} right={alternateTrace} />}
        {view === 'causality' && <CausalGraphPanel trace={sampleTrace} />}
        {view === 'redaction' && <RedactionPanel />}
        {view === 'import' && <ImportTextarea />}
      </section>
    </main>
  )
}
