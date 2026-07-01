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
        {summary ? `你好，${summary.full_name}` : '你好'}
      </h1>
      <p className="text-sm text-slate-400 mb-8">这是你目前的实习记录概览</p>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard label="实习记录" value={summary?.placement_log_count} />
        <StatCard label="Reflection Notes" value={summary?.reflection_note_count} />
        <StatCard label="进行中的 Case" value={summary?.open_case_count} note="功能筹备中" />
      </div>

      <div className="card p-6">
        <h2 className="font-medium text-ink mb-3">待办事项</h2>
        {summary && summary.unread_feedback_count === 0 ? (
          <p className="text-sm text-slate-400">暂时没有待处理的事项。督导给出反馈后会显示在这里。</p>
        ) : (
          <p className="text-sm text-ink">你有 {summary?.unread_feedback_count} 条未读反馈</p>
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
