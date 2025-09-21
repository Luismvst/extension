import { useState, useEffect } from 'react'
import { jwtDecode } from 'jwt-decode'

interface User {
  id: string
  email: string
  name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
  })

  useEffect(() => {
    // Check for existing token in localStorage
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const decoded = jwtDecode(token) as any
        if (decoded.exp * 1000 > Date.now()) {
          setAuthState({
            user: {
              id: decoded.sub,
              email: decoded.email,
              name: decoded.name || 'Usuario',
            },
            token,
            isAuthenticated: true,
          })
        } else {
          localStorage.removeItem('token')
        }
      } catch (error) {
        localStorage.removeItem('token')
      }
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (response.ok) {
        const data = await response.json()
        const token = data.access_token
        
        localStorage.setItem('token', token)
        
        const decoded = jwtDecode(token) as any
        setAuthState({
          user: {
            id: decoded.sub,
            email: decoded.email,
            name: decoded.name || 'Usuario',
          },
          token,
          isAuthenticated: true,
        })
        
        return { success: true }
      } else {
        const error = await response.json()
        return { success: false, error: error.detail }
      }
    } catch (error) {
      return { success: false, error: 'Error de conexión' }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
    })
  }

  return {
    ...authState,
    login,
    logout,
  }
}
