// Login page - redirects to Keycloak
import { useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'

export function Login() {
  const { login, loading } = useAuth()

  useEffect(() => {
    if (!loading) {
      login()
    }
  }, [login, loading])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
        <p className="text-gray-600">Redirecting to sign in...</p>
      </div>
    </div>
  )
}
