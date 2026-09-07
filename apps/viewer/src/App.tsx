import { useMemo, useState } from 'react'
import { alternateTrace, sampleTrace } from './data/sampleTrace'
import { ComparePanel } from './components/ComparePanel'
import { EventDetail } from './components/EventDetail'
import { ImportPanel } from './components/ImportPanel'
import { PolicyPanel } from './components/PolicyPanel'
import { RedactionPanel } from './components/RedactionPanel'
import { ReplayConsole } from './components/ReplayConsole'
import { SummaryCards } from './components/SummaryCards'
import { Timeline } from './components/Timeline'
import './App.css'

type View = 'timeline' | 'replay' | 'policy' | 'compare' | 'redaction'

export default function App() {
  const [view, setView] = useState<View>('timeline')
  const [selectedId, setSelectedId] = useState(sampleTrace.events[0].id)
  const selectedEvent = useMemo(
    () => sampleTrace.events.find((event) => event.id === selectedId) ?? sampleTrace.events[0],
    [selectedId],
  )

  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand-mark">A</div>
        <div>
          <strong>Agent Black Box</strong>
          <span>Trace laboratory</span>
        </div>
      </aside>
      <section className="content">
        <header className="page-header">
          <div>
            <p>AGENT OBSERVABILITY</p>
            <h1>Portable agent run recorder</h1>
          </div>
          <nav aria-label="Views">
            {(['timeline', 'replay', 'policy', 'compare', 'redaction'] as View[]).map((item) => (
              <button className={item === view ? 'active' : ''} key={item} onClick={() => setView(item)} type="button">
                {item}
              </button>
            ))}
          </nav>
        </header>

        <SummaryCards trace={sampleTrace} />

        {view === 'timeline' && (
          <div className="main-grid">
            <Timeline events={sampleTrace.events} selectedId={selectedId} onSelect={setSelectedId} />
            <EventDetail event={selectedEvent} />
          </div>
        )}
        {view === 'replay' && (
          <div className="main-grid">
            <ReplayConsole trace={sampleTrace} />
            <ImportPanel trace={sampleTrace} />
          </div>
        )}
        {view === 'policy' && <PolicyPanel trace={sampleTrace} />}
        {view === 'compare' && <ComparePanel left={sampleTrace} right={alternateTrace} />}
        {view === 'redaction' && <RedactionPanel />}
      </section>
    </main>
  )
}
