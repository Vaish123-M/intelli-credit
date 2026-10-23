import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

vi.mock('./pages/Home', () => ({
  default: () => <div>home stub</div>,
}))

vi.mock('./pages/CreditDashboard', () => ({
  default: () => <div>credit stub</div>,
}))

vi.mock('./pages/PortfolioDashboard', () => ({
  default: () => <div>portfolio stub</div>,
}))

import App from './App'

describe('App navigation', () => {
  it('switches between the main views', async () => {
    render(<App />)

    expect(await screen.findByText('home stub')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /credit dashboard/i }))
    await waitFor(() => expect(screen.getByText('credit stub')).toBeInTheDocument())
    expect(screen.queryByText('home stub')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /portfolio monitor/i }))
    await waitFor(() => expect(screen.getByText('portfolio stub')).toBeInTheDocument())
  })
})