import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Dashboard } from '../pages/Dashboard'

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>)
}

describe('Dashboard', () => {
  it('renders the dashboard with title and navigation cards', () => {
    renderWithRouter(<Dashboard />)
    expect(screen.getByText('atlas-pilot-alan-vo')).toBeInTheDocument()
    expect(screen.getByText('AI Agent Evaluation & Management Platform')).toBeInTheDocument()
    expect(screen.getByText('Agent Catalog')).toBeInTheDocument()
    expect(screen.getByText('Evaluations')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('has links to agents, evaluations, and settings', () => {
    renderWithRouter(<Dashboard />)
    expect(screen.getByText('View Catalog →')).toHaveAttribute('href', '/agents')
    expect(screen.getByText('View Evaluations →')).toHaveAttribute('href', '/evaluations')
    expect(screen.getByText('Open Settings →')).toHaveAttribute('href', '/settings')
  })
})