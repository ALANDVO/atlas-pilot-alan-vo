// OIDC callback page for handling Keycloak redirect
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export function Callback() {
  const navigate = useNavigate()
  const { refreshToken } = useAuth()

  useEffect(() => {
    // The backend sets cookies via the callback redirect
    // We just need to fetch user info and redirect to dashboard
    const initializeAuth = async () => {
      const success = await refreshToken()
      if (success) {
        navigate('/')
      } else {
        navigate('/login')
      }
    }
    initializeAuth()
  }, [navigate, refreshToken])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
        <p className="text-gray-600">Completing sign in...</p>
      </div>
    </div>
  )
}
