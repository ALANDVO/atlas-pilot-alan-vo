import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

export function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">atlas-pilot-alan-vo</h1>
          <p className="text-gray-600 mt-1">AI Agent Evaluation & Management Platform</p>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-2">Agent Catalog</h2>
            <p className="text-gray-600 mb-4">Browse, search, and manage AI agents</p>
            <Link href="/agents" className="text-blue-600 hover:underline">View Catalog →</Link>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-2">Evaluations</h2>
            <p className="text-gray-600 mb-4">Run and compare agent evaluations</p>
            <Link href="/evaluations" className="text-blue-600 hover:underline">View Evaluations →</Link>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-2">Settings</h2>
            <p className="text-gray-600 mb-4">Configure LLM providers and integrations</p>
            <Link href="/settings" className="text-blue-600 hover:underline">Open Settings →</Link>
          </div>
        </div>
      </main>
    </div>
  )
}