import { Routes, Route } from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { HealthCheck } from './pages/HealthCheck'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/health" element={<HealthCheck />} />
    </Routes>
  )
}

export default App