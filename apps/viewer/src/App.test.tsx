import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders the trace workspace', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /ai agent black box recorder/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /timeline/i })).toBeInTheDocument()
  })
})
