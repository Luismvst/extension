import { useState, useEffect } from 'react'
import { jwtDecode } from 'jwt-decode'
import { api, createTimeoutController, handleApiError } from '../lib/api'

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
      console.log('Attempting login for:', email)
      const controller = createTimeoutController(10000) // 10 second timeout
      const response = await api.auth.login(email, password, controller.signal)
      
      console.log('Login response:', response)
      
      if (response.data) {
        const token = response.data.access_token
        console.log('Token received:', token ? 'Yes' : 'No')
        
        localStorage.setItem('token', token)
        
        const decoded = jwtDecode(token) as any
        console.log('Decoded token:', decoded)
        
        const newAuthState = {
          user: {
            id: decoded.sub,
            email: decoded.email,
            name: decoded.name || 'Usuario',
          },
          token,
          isAuthenticated: true,
        }
        
        console.log('Setting auth state:', newAuthState)
        setAuthState(newAuthState)
        
        // Store token in a way that can be accessed by other components
        if (typeof window !== 'undefined') {
          (window as any).__authToken = token
        }
        
        return { success: true }
      } else {
        console.log('No data in response')
        return { success: false, error: 'No se recibió token de autenticación' }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: handleApiError(error) }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    
    // Clear window token
    if (typeof window !== 'undefined') {
      delete (window as any).__authToken
    }
    
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
    })
    
    // Force a small delay to ensure state is updated before any redirects
    setTimeout(() => {
      // This ensures the login screen renders properly
      window.location.reload()
    }, 100)
  }

  return {
    ...authState,
    login,
    logout,
  }
}
