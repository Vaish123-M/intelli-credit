import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import EntityOnboarding from './EntityOnboarding'

function fillCompanyDetails() {
  fireEvent.change(screen.getByPlaceholderText('Enter legal company name'), { target: { value: 'Acme Infra Ltd' } })
  fireEvent.change(screen.getByPlaceholderText('Enter CIN'), { target: { value: 'L12345' } })
  fireEvent.change(screen.getByPlaceholderText('Enter PAN'), { target: { value: 'ABCDE1234F' } })
  fireEvent.change(screen.getByPlaceholderText('Enter sector'), { target: { value: 'Infrastructure' } })
  fireEvent.change(screen.getByPlaceholderText('Enter annual turnover'), { target: { value: '125000000' } })
}

function fillLoanDetails() {
  fireEvent.change(screen.getByPlaceholderText('Enter requested loan amount'), { target: { value: '25000000' } })
  fireEvent.change(screen.getByPlaceholderText('Example: 36 months'), { target: { value: '36 months' } })
  fireEvent.change(screen.getByPlaceholderText('Example: 11.5'), { target: { value: '12.5' } })
}

describe('EntityOnboarding', () => {
  it('shows required field errors before advancing', () => {
    render(<EntityOnboarding onSubmit={vi.fn()} />)

    fireEvent.click(screen.getByRole('button', { name: 'Next' }))

    expect(screen.getByText('Company name is required.')).toBeInTheDocument()
    expect(screen.getByText('CIN is required.')).toBeInTheDocument()
    expect(screen.getByText('PAN is required.')).toBeInTheDocument()
  })

  it('submits normalized numeric values and shows completion', async () => {
    const onSubmit = vi.fn().mockResolvedValue({ entity_id: 'ent_test123' })
    const onCompleted = vi.fn()
    render(<EntityOnboarding onSubmit={onSubmit} onCompleted={onCompleted} />)

    fillCompanyDetails()
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    fillLoanDetails()
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    fireEvent.click(screen.getByRole('button', { name: /Continue to Document Upload/i }))

    await waitFor(() => expect(onSubmit).toHaveBeenCalledOnce())
    expect(onSubmit).toHaveBeenCalledWith({
      company_name: 'Acme Infra Ltd',
      cin: 'L12345',
      pan: 'ABCDE1234F',
      sector: 'Infrastructure',
      annual_turnover: 125000000,
      loan_type: 'Working Capital',
      loan_amount: 25000000,
      loan_tenure: '36 months',
      interest_rate: 12.5,
    })
    expect(onCompleted).toHaveBeenCalledOnce()
    expect(screen.getByText('Entity Onboarding Complete')).toBeInTheDocument()
    expect(screen.getByText('Entity ID: ent_test123')).toBeInTheDocument()
  })

  it('renders server errors and allows retry', async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error('Unable to save entity'))
    render(<EntityOnboarding onSubmit={onSubmit} />)

    fillCompanyDetails()
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    fillLoanDetails()
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    fireEvent.click(screen.getByRole('button', { name: /Continue to Document Upload/i }))

    expect(await screen.findByText('Unable to save entity')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Continue to Document Upload/i })).toBeEnabled()
  })
})
