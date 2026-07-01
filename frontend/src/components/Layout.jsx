import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const navItems = [
  { to: '/', label: '主页', end: true },
  { to: '/placement-logs', label: '实习记录' },
  { to: '/reflection-notes', label: 'Reflection Notes' },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 border-r border-moss-100 bg-white flex flex-col">
        <div className="px-6 py-6 border-b border-moss-100">
          <p className="font-display text-lg text-moss-700 font-semibold">Placement Journal</p>
          <p className="text-xs text-slate-400 mt-0.5">实习记录与督导系统</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-moss-50 text-moss-700'
                    : 'text-slate-600 hover:bg-moss-50 hover:text-moss-700'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-4 py-4 border-t border-moss-100">
          <p className="text-sm font-medium text-ink">{user?.full_name}</p>
          <p className="text-xs text-slate-400 mb-3">
            {user?.role === 'student' ? '实习生' : user?.role === 'supervisor' ? '督导' : '管理员'}
          </p>
          <button onClick={logout} className="text-xs text-moss-600 hover:underline">
            退出登录
          </button>
        </div>
      </aside>
      <main className="flex-1 px-8 py-8 max-w-5xl">{children}</main>
    </div>
  )
}
