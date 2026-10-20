import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'

export function HealthCheck() {
  const [status, setStatus] = useState<string>('loading')

  useEffect(() => {
    apiClient.get('/health')
      .then(res => setStatus(JSON.stringify(res.data, null, 2)))
      .catch(err => setStatus(`Error: ${err.message}`))
  }, [])

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Health Check</h1>
      <pre className="bg-gray-100 p-4 rounded">{status}</pre>
    </div>
  )
}