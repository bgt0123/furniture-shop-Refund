import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import SupportCaseForm from '../../../src/components/support/SupportCaseForm'

describe('SupportCaseForm', () => {
  it('renders support case form with required fields', () => {
    // This test should fail initially since the component doesn't exist
    const mockOnSubmit = vi.fn()
    
    render(<SupportCaseForm onSubmit={mockOnSubmit} />)
    
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/order id/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create support case/i })).toBeInTheDocument()
  })

  it('submits form with correct data', () => {
    // This test should fail initially since the component doesn't exist
    const mockOnSubmit = vi.fn()
    
    render(<SupportCaseForm onSubmit={mockOnSubmit} />)
    
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Test Case' } })
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'Test Description' } })
    fireEvent.change(screen.getByLabelText(/order id/i), { target: { value: '123e4567-e89b-12d3-a456-426614174000' } })
    fireEvent.click(screen.getByRole('button', { name: /create support case/i }))
    
    expect(mockOnSubmit).toHaveBeenCalledWith({
      title: 'Test Case',
      description: 'Test Description',
      orderId: '123e4567-e89b-12d3-a456-426614174000'
    })
  })

  it('shows validation errors for required fields', () => {
    // This test should fail initially since the component doesn't exist
    const mockOnSubmit = vi.fn()
    
    render(<SupportCaseForm onSubmit={mockOnSubmit} />)
    
    fireEvent.click(screen.getByRole('button', { name: /create support case/i }))
    
    expect(screen.getByText(/title is required/i)).toBeInTheDocument()
    expect(screen.getByText(/description is required/i)).toBeInTheDocument()
  })
})