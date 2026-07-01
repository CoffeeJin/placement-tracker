import { useEffect, useState } from 'react'
import client from '../api/client'
import Layout from '../components/Layout.jsx'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    client.get('/dashboard/summary').then((res) => setSummary(res.data))
  }, [])

  return (
    <Layout>
      <h1 className="font-display text-2xl text-ink font-semibold mb-1">
        {summary ? `Hello, ${summary.full_name}` : 'Hello'}
      </h1>
      <p className="text-sm text-slate-400 mb-8">Here's an overview of your current placement records</p>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard label="Placement Logs" value={summary?.placement_log_count} />
        <StatCard label="Reflection Notes" value={summary?.reflection_note_count} />
        <StatCard label="Open Cases" value={summary?.open_case_count} note="Coming soon" />
      </div>

      <div className="card p-6">
        <h2 className="font-medium text-ink mb-3">To-Do</h2>
        {summary && summary.unread_feedback_count === 0 ? (
          <p className="text-sm text-slate-400">Nothing pending right now. Supervisor feedback will appear here.</p>
        ) : (
          <p className="text-sm text-ink">You have {summary?.unread_feedback_count} unread feedback item(s)</p>
        )}
      </div>
    </Layout>
  )
}

function StatCard({ label, value, note }) {
  return (
    <div className="card p-5">
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className="font-display text-3xl text-moss-700 font-semibold">
        {value ?? '–'}
      </p>
      {note && <p className="text-xs text-slate-400 mt-1">{note}</p>}
    </div>
  )
}
