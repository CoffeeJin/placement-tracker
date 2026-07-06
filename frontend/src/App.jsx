import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import VerifyEmail from './pages/VerifyEmail.jsx'
import Dashboard from './pages/Dashboard.jsx'
import PlacementLogs from './pages/PlacementLogs.jsx'
import ReflectionNotes from './pages/ReflectionNotes.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/placement-logs" element={<ProtectedRoute><PlacementLogs /></ProtectedRoute>} />
      <Route path="/reflection-notes" element={<ProtectedRoute><ReflectionNotes /></ProtectedRoute>} />
    </Routes>
  )
}
