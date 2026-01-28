/**
 * Authentication Context
 * Manages user authentication state across the application
 */

import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    const storedUser = localStorage.getItem('user')
    const accessToken = localStorage.getItem('accessToken')

    if (storedUser && accessToken) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (error) {
        console.error('Error parsing stored user:', error)
        localStorage.removeItem('user')
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
      }
    }

    setLoading(false)
  }, [])

  const login = async (username, password) => {
    try {
      const response = await authAPI.login({ username, password })

      if (response.data.success) {
        const { user, tokens } = response.data.data

        // Store user and tokens
        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('accessToken', tokens.access)
        localStorage.setItem('refreshToken', tokens.refresh)

        setUser(user)
        toast.success('Login successful!')
        return { success: true }
      } else {
        throw new Error(response.data.error?.message || 'Login failed')
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || error.message || 'Login failed'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    }
  }

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)

      if (response.data.success) {
        const { user, tokens } = response.data.data

        // Store user and tokens
        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('accessToken', tokens.access)
        localStorage.setItem('refreshToken', tokens.refresh)

        setUser(user)
        toast.success('Registration successful!')
        return { success: true }
      } else {
        throw new Error(response.data.error?.message || 'Registration failed')
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || error.message || 'Registration failed'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local storage regardless of API call success
      localStorage.removeItem('user')
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      setUser(null)
      toast.success('Logged out successfully')
    }
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
