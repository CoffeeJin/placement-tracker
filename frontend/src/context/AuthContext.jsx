import { createContext, useContext, useEffect, useRef, useState } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const logoutTimer = useRef(null)

  const logout = () => {
    if (logoutTimer.current) {
      clearTimeout(logoutTimer.current)
      logoutTimer.current = null
    }
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('token_expires_at')
    setUser(null)
  }

  const scheduleAutoLogout = (expiresAt) => {
    if (logoutTimer.current) clearTimeout(logoutTimer.current)
    const delay = new Date(expiresAt).getTime() - Date.now()
    if (delay <= 0) {
      logout()
      return
    }
    logoutTimer.current = setTimeout(logout, delay)
  }

  useEffect(() => {
    const token = sessionStorage.getItem('access_token')
    const expiresAt = sessionStorage.getItem('token_expires_at')

    if (!token || (expiresAt && new Date(expiresAt) < new Date())) {
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('token_expires_at')
      setLoading(false)
      return
    }

    client
      .get('/auth/me')
      .then((res) => {
        setUser(res.data)
        scheduleAutoLogout(expiresAt)
      })
      .catch(() => {
        sessionStorage.removeItem('access_token')
        sessionStorage.removeItem('token_expires_at')
      })
      .finally(() => setLoading(false))

    return () => {
      if (logoutTimer.current) clearTimeout(logoutTimer.current)
    }
  }, [])

  const login = async (username, password) => {
    const res = await client.post('/auth/login', { username, password })
    sessionStorage.setItem('access_token', res.data.access_token)
    sessionStorage.setItem('token_expires_at', res.data.expires_at)
    const me = await client.get('/auth/me')
    setUser(me.data)
    scheduleAutoLogout(res.data.expires_at)
    return me.data
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
