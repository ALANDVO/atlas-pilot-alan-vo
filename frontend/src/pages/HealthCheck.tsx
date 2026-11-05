import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { useAuth } from '../context/AuthContext'

export function HealthCheck() {
  const [status, setStatus] = useState<string>('loading')
  const { user } = useAuth()

  useEffect(() => {
    apiClient.get('/health')
      .then(res => setStatus(JSON.stringify(res.data, null, 2)))
      .catch(err => setStatus(`Error: ${err.message}`))
  }, [])

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Health Check</h1>
      {user && (
        <div className="mb-4 p-4 bg-blue-50 rounded text-sm text-blue-800">
          Authenticated as: {user.name || user.preferred_username} ({user.realm_access?.roles.join(', ') || 'viewer'})
        </div>
      )}
      <pre className="bg-gray-100 p-4 rounded">{status}</pre>
    </div>
  )
}