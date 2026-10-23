
import {
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react'

import api, { setCsrfToken } from '../api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [authenticated, setAuthenticated] = useState(false)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    let active = true

    async function restoreSession() {
      try {
        const { data } = await api.get('/auth/me')

        if (!active) return

        setCsrfToken(data.csrf_token)
        setAuthenticated(true)
      } catch {
        if (!active) return

        setCsrfToken(null)
        setAuthenticated(false)
      } finally {
        if (active) setChecking(false)
      }
    }

    restoreSession()

    return () => {
      active = false
    }
  }, [])

  async function login(password) {
    const { data } = await api.post('/auth/login', {
      password,
    })

    setCsrfToken(data.csrf_token)
    setAuthenticated(true)
  }

  async function logout() {
    await api.post('/auth/logout')

    setCsrfToken(null)
    setAuthenticated(false)
  }

  return (
    <AuthContext.Provider
      value={{
        authenticated,
        checking,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }

  return context
}
