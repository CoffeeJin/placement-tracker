import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import client from '../api/client'

export default function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('verifying')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const token = searchParams.get('token')
    if (!token) {
      setStatus('error')
      setMessage('Missing verification token')
      return
    }
    client
      .post('/auth/verify-email', { token })
      .then((res) => {
        setStatus('success')
        setMessage(res.data.message)
      })
      .catch((err) => {
        setStatus('error')
        setMessage(err.response?.data?.detail || 'Verification failed')
      })
  }, [searchParams])

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm text-center">
        <p className="font-display text-2xl text-moss-700 font-semibold mb-2">Placement Journal</p>
        <p className="text-sm text-slate-600">
          {status === 'verifying' ? 'Verifying your email…' : message}
        </p>
        {status !== 'verifying' && (
          <Link to="/login" className="text-sm text-moss-600 hover:underline mt-4 inline-block">
            Go to Log In
          </Link>
        )}
      </div>
    </div>
  )
}
