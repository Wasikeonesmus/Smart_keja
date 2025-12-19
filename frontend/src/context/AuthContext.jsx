import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

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
    // Check if user is logged in
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      // You'll need to create a Django endpoint to check auth status
      // For now, check localStorage
      const token = localStorage.getItem('authToken')
      if (token) {
        // Verify token with backend
        // const response = await axios.get('/api/auth/user/')
        // setUser(response.data)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await axios.post('/accounts/login/', {
        username,
        password
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        withCredentials: true
      })
      
      if (response.status === 200) {
        setUser({ username })
        return { success: true }
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      }
    }
  }

  const signup = async (username, email, password1, password2) => {
    try {
      const response = await axios.post('/signup/', {
        username,
        email,
        password1,
        password2
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        withCredentials: true
      })
      
      if (response.status === 200 || response.status === 302) {
        setUser({ username })
        return { success: true }
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Signup failed' 
      }
    }
  }

  const logout = async () => {
    try {
      await axios.post('/accounts/logout/')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      localStorage.removeItem('authToken')
    }
  }

  const value = {
    user,
    loading,
    login,
    signup,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

