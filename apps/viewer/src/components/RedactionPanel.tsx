const report = {
  traceId: 'trc_webhook_recovery_481',
  incident: 'Webhook recovery investigation',
  policy: 'default-sharing-policy-v1',
  status: 'Ready to share',
  replacements: [
    {
      field: 'Operator email',
      source: 'incident intake note',
      detected: 'maya.chen@northstar.example',
      replacement: 'operator-contact-01',
      reason: 'Personal contact detail',
    },
    {
      field: 'Authorization header',
      source: 'tool request metadata',
      detected: 'Bearer sk_live_demo_4812c2b6f0',
      replacement: 'authorization-token-redacted',
      reason: 'Credential material',
    },
    {
      field: 'Customer account',
      source: 'search_incidents response',
      detected: 'acct_northstar_77841',
      replacement: 'customer-account-ref',
      reason: 'Customer identifier',
    },
    {
      field: 'Escalation phone',
      source: 'follow-up recommendation',
      detected: '+1-415-555-0138',
      replacement: 'escalation-phone-redacted',
      reason: 'Contact routing data',
    },
  ],
  before:
    'Maya Chen reported that Northstar production webhooks were failing after retry policy deploy 481. The diagnostic request used a bearer token and returned customer account acct_northstar_77841 with an escalation phone number for the incident bridge.',
  after:
    'An operator reported that a customer production webhook was failing after retry policy deploy 481. The diagnostic request was authorized, and the shared trace keeps only the customer reference, failure pattern, and follow-up action.',
}

export function RedactionPanel() {
  return (
    <section className="panel" aria-label="Redaction preview">
      <div className="panel-heading">
        <h2>Redaction report</h2>
        <span>{report.replacements.length} replacements</span>
      </div>
      <div className="redaction-summary" aria-label="Redaction report summary">
        <article>
          <small>Trace</small>
          <strong>{report.traceId}</strong>
        </article>
        <article>
          <small>Scenario</small>
          <strong>{report.incident}</strong>
        </article>
        <article>
          <small>Policy</small>
          <strong>{report.policy}</strong>
        </article>
        <article>
          <small>Share status</small>
          <strong>{report.status}</strong>
        </article>
      </div>
      <div className="redaction-document-grid">
        <article>
          <small>Original captured note</small>
          <p>{report.before}</p>
        </article>
        <article>
          <small>Reviewer-safe version</small>
          <p>{report.after}</p>
        </article>
      </div>
      <div className="redaction-table" aria-label="Sensitive fields replaced">
        <div className="redaction-table-header">
          <span>Field</span>
          <span>Source</span>
          <span>Replacement</span>
          <span>Reason</span>
        </div>
        {report.replacements.map((item) => (
          <div className="redaction-table-row" key={item.field}>
            <strong>
              {item.field}
              <small>{item.detected}</small>
            </strong>
            <span>{item.source}</span>
            <span>{item.replacement}</span>
            <span>{item.reason}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
