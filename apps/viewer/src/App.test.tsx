import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders the trace workspace', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /portable agent run recorder/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /timeline/i })).toBeInTheDocument()
  })
})
