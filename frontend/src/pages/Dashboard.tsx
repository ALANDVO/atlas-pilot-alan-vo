import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Dashboard() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">atlas-pilot-alan-vo</h1>
            <p className="text-gray-600 mt-1">AI Agent Evaluation & Management Platform</p>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-700">
                  {user.name || user.preferred_username}
                  {user.email && <span className="ml-2 text-gray-400">({user.email})</span>}
                </span>
                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                  {user.realm_access?.roles.join(', ') || 'viewer'}
                </span>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm text-white bg-red-600 rounded hover:bg-red-700"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-2">Agent Catalog</h2>
            <p className="text-gray-600 mb-4">Browse, search, and manage AI agents</p>
            <Link to="/agents" className="text-blue-600 hover:underline">View Catalog →</Link>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-2">Evaluations</h2>
            <p className="text-gray-600 mb-4">Run and compare agent evaluations</p>
            <Link to="/evaluations" className="text-blue-600 hover:underline">View Evaluations →</Link>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-2">Settings</h2>
            <p className="text-gray-600 mb-4">Configure LLM providers and integrations</p>
            <Link to="/settings" className="text-blue-600 hover:underline">Open Settings →</Link>
          </div>
        </div>
      </main>
    </div>
  )
}