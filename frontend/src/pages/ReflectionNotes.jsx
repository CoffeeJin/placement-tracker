import { useEffect, useState } from 'react'
import client from '../api/client'
import Layout from '../components/Layout.jsx'

const PLACEMENT_TYPES = ['Direct Practice', 'Group Work', 'Community Outreach', 'Administrative', 'Supervision', 'Training', 'Other']

const emptyForm = { date: '', location: '', topic: '', placement_type: PLACEMENT_TYPES[0], content: '' }

export default function ReflectionNotes() {
  const [notes, setNotes] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [selected, setSelected] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const loadNotes = () => client.get('/reflection-notes').then((res) => setNotes(res.data))

  useEffect(() => {
    loadNotes()
  }, [])

  const openCreate = () => {
    setForm(emptyForm)
    setEditingId(null)
    setShowForm(true)
  }

  const openEdit = (note) => {
    setForm({
      date: note.date,
      location: note.location,
      topic: note.topic,
      placement_type: note.placement_type,
      content: note.content || '',
    })
    setEditingId(note.id)
    setShowForm(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      if (editingId) {
        await client.put(`/reflection-notes/${editingId}`, form)
      } else {
        await client.post('/reflection-notes', form)
      }
      setShowForm(false)
      await loadNotes()
    } catch (err) {
      setError(err.response?.data?.detail || 'Save failed')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this record?')) return
    await client.delete(`/reflection-notes/${id}`)
    if (selected?.id === id) setSelected(null)
    await loadNotes()
  }

  const openDetail = async (id) => {
    const res = await client.get(`/reflection-notes/${id}`)
    setSelected(res.data)
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file || !selected) return
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    try {
      await client.post(`/reflection-notes/${selected.id}/attachments`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      await openDetail(selected.id)
    } catch (err) {
      alert(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-2xl text-ink font-semibold">Reflection Notes</h1>
        <button className="btn-primary" onClick={openCreate}>+ New Entry</button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-3">
          {notes.length === 0 && (
            <p className="text-sm text-slate-400">No records yet. Click the button above to add one.</p>
          )}
          {notes.map((note) => (
            <div
              key={note.id}
              className={`card p-4 cursor-pointer hover:border-moss-300 transition-colors ${selected?.id === note.id ? 'border-moss-500' : ''}`}
              onClick={() => openDetail(note.id)}
            >
              <div className="flex items-center justify-between">
                <p className="font-medium text-ink">{note.topic}</p>
                <span className="status-pill bg-moss-50 text-moss-700">{note.placement_type}</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">{note.date} · {note.location}</p>
            </div>
          ))}
        </div>

        <div>
          {showForm ? (
            <form onSubmit={handleSubmit} className="card p-5 space-y-4">
              <h2 className="font-medium text-ink">{editingId ? 'Edit Entry' : 'New Entry'}</h2>
              <div>
                <label className="label-text">Date</label>
                <input type="date" required className="input-field"
                  value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
              </div>
              <div>
                <label className="label-text">Location</label>
                <input required className="input-field"
                  value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
              </div>
              <div>
                <label className="label-text">Topic</label>
                <input required className="input-field"
                  value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} />
              </div>
              <div>
                <label className="label-text">Placement Type</label>
                <select className="input-field" value={form.placement_type}
                  onChange={(e) => setForm({ ...form, placement_type: e.target.value })}>
                  {PLACEMENT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="label-text">Reflection Content</label>
                <textarea rows={5} className="input-field"
                  value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
              </div>
              {error && <p className="text-sm text-red-600">{error}</p>}
              <div className="flex gap-2">
                <button type="submit" className="btn-primary">Save</button>
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          ) : selected ? (
            <div className="card p-5 space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="font-medium text-ink">{selected.topic}</h2>
                  <p className="text-xs text-slate-400 mt-1">
                    {selected.date} · {selected.location} · {selected.placement_type}
                  </p>
                </div>
                <span className="status-pill bg-moss-50 text-moss-700">{statusLabel(selected.status)}</span>
              </div>
              <p className="text-sm text-ink whitespace-pre-wrap">{selected.content || '(No content)'}</p>

              <div>
                <p className="label-text">Attachments</p>
                {selected.attachments.length === 0 ? (
                  <p className="text-sm text-slate-400">No attachments yet</p>
                ) : (
                  <ul className="space-y-1">
                    {selected.attachments.map((a) => (
                      <li key={a.id}>
                        <a
                          className="text-sm text-moss-600 hover:underline"
                          href="#"
                          onClick={(e) => downloadWithAuth(e, a.id, a.original_filename)}
                        >
                          {a.original_filename}
                        </a>
                      </li>
                    ))}
                  </ul>
                )}
                <label className="btn-secondary inline-block mt-3 cursor-pointer">
                  {uploading ? 'Uploading…' : 'Upload Attachment/Image'}
                  <input type="file" className="hidden" onChange={handleFileUpload} disabled={uploading} />
                </label>
              </div>

              <div className="flex gap-2 pt-2 border-t border-moss-100">
                <button className="btn-secondary" onClick={() => openEdit(selected)}>Edit</button>
                <button className="text-sm text-red-600 hover:underline" onClick={() => handleDelete(selected.id)}>Delete</button>
              </div>
            </div>
          ) : (
            <div className="card p-5 text-sm text-slate-400">Select a record on the left to view details</div>
          )}
        </div>
      </div>
    </Layout>
  )
}

function statusLabel(status) {
  return { draft: 'Draft', submitted: 'Submitted', reviewed: 'Reviewed' }[status] || status
}

async function downloadWithAuth(e, id, filename) {
  e.preventDefault()
  const res = await client.get(`/attachments/${id}/download`, { responseType: 'blob' })
  const url = window.URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}
