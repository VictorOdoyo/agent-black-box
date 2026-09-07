import { useMemo, useState } from 'react'

export function ImportTextarea() {
  const [value, setValue] = useState('')
  const validation = useMemo(() => {
    if (!value.trim()) return 'Waiting for trace JSON'
    try {
      const parsed = JSON.parse(value)
      return Array.isArray(parsed.events) ? `${parsed.events.length} events detected` : 'Trace JSON must include events'
    } catch {
      return 'Trace JSON is invalid'
    }
  }, [value])

  return (
    <section className="panel" aria-label="Trace JSON import">
      <div className="panel-heading">
        <h2>Import trace</h2>
        <span>{validation}</span>
      </div>
      <textarea value={value} onChange={(event) => setValue(event.target.value)} placeholder="Paste an Agent Black Box trace JSON document" />
    </section>
  )
}
