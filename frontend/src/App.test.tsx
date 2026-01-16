import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from './App'

describe('Frontend Components', () => {
  test('renders main app component', () => {
    render(<App />)
    expect(screen.getByText(/Customer Support and Refund Service/i)).toBeInTheDocument()
  })

  test('renders welcome message', () => {
    render(<App />)
    expect(screen.getByText(/Welcome to the Support and Refund Service/i)).toBeInTheDocument()
  })
})
