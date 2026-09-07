import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { RedactionPanel } from './RedactionPanel'

describe('RedactionPanel', () => {
  it('renders a reviewer-safe redaction report from synthetic trace data', () => {
    render(<RedactionPanel />)

    expect(screen.getByRole('heading', { name: /redaction report/i })).toBeInTheDocument()
    expect(screen.getByText('trc_webhook_recovery_481')).toBeInTheDocument()
    expect(screen.getByText('Ready to share')).toBeInTheDocument()

    const table = screen.getByLabelText(/sensitive fields replaced/i)
    expect(within(table).getByText('Authorization header')).toBeInTheDocument()
    expect(within(table).getByText('authorization-token-redacted')).toBeInTheDocument()
    expect(within(table).getByText('Credential material')).toBeInTheDocument()
  })
})
