const preview = {
  before: 'operator@example.com used Bearer abcdefghijklmnopqrstuv',
  after: '[redacted-email] used Bearer [redacted-token]',
}

export function RedactionPanel() {
  return (
    <section className="panel" aria-label="Redaction preview">
      <div className="panel-heading">
        <h2>Redaction preview</h2>
        <span>2 replacements</span>
      </div>
      <div className="redaction-grid">
        <article>
          <small>Before</small>
          <code>{preview.before}</code>
        </article>
        <article>
          <small>After</small>
          <code>{preview.after}</code>
        </article>
      </div>
    </section>
  )
}
