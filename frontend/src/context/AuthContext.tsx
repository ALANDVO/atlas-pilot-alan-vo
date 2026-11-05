// Authentication context for React frontend
import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react'
import { apiClient } from '../api/client'

interface User {
  sub: string
  preferred_username: string
  email?: string
  name?: string
  given_name?: string
  family_name?: string
  realm_access?: {
    roles: string[]
  }
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: () => void
  logout: () => Promise<void>
  refreshToken: () => Promise<boolean>
  hasRole: (role: string) => boolean
  hasAnyRole: (roles: string[]) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    try {
      const response = await apiClient.get('/auth/me')
      setUser(response.data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = () => {
    // Redirect to backend login endpoint which will redirect to Keycloak
    window.location.href = '/api/v1/auth/login'
  }

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // Ignore errors
    }
    setUser(null)
    // Redirect to Keycloak logout
    window.location.href = '/api/v1/auth/logout'
  }

  const refreshToken = async (): Promise<boolean> => {
    try {
      await apiClient.post('/auth/refresh')
      await fetchUser()
      return true
    } catch {
      setUser(null)
      return false
    }
  }

  const hasRole = (role: string): boolean => {
    return user?.realm_access?.roles.includes(role) ?? false
  }

  const hasAnyRole = (roles: string[]): boolean => {
    return roles.some(role => hasRole(role))
  }

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      logout,
      refreshToken,
      hasRole,
      hasAnyRole,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
