import { createContext, useContext, useEffect, useState } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const expiresAt = localStorage.getItem('token_expires_at')

    if (!token || (expiresAt && new Date(expiresAt) < new Date())) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('token_expires_at')
      setLoading(false)
      return
    }

    client
      .get('/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('token_expires_at')
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (username, password) => {
    const res = await client.post('/auth/login', { username, password })
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('token_expires_at', res.data.expires_at)
    const me = await client.get('/auth/me')
    setUser(me.data)
    return me.data
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('token_expires_at')
    setUser(null)
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
