import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Shield, LayoutDashboard, FileText, Palette, LogOut, User, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/brand-kits', icon: Palette, label: 'Brand Kits' },
  { to: '/drafts', icon: FileText, label: 'Drafts' },
]

const ROLE_PRESETS = [
  { label: '👑 Admin', role: 'admin', email: 'kaleajay626@gmail.com', name: 'Ajay' },
  { label: '👔 Manager', role: 'manager', email: 'mahesh@innovex.com', name: 'Mahesh' },
  { label: '🔍 Reviewer', role: 'reviewer', email: 'asma@innovex.com', name: 'Asma' },
  { label: '✍️ Creator', role: 'creator', email: 'shrushti@innovex.com', name: 'Shrushti' },
]

export default function Layout() {
  const { user, logout, quickSwitch } = useAuth()
  const [switchingRole, setSwitchingRole] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleSwitchRole = async (targetEmail) => {
    if (user?.email === targetEmail) return
    try {
      setSwitchingRole(true)
      await quickSwitch(targetEmail)
      toast.success(`Switched active persona to ${targetEmail}`)
    } catch (err) {
      toast.error('Failed to switch persona')
    } finally {
      setSwitchingRole(false)
    }
  }

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-brand-900 text-white flex flex-col">
        {/* Logo */}
        <div className="p-6 flex items-center gap-3 border-b border-brand-800">
          <Shield className="w-8 h-8 text-brand-300" />
          <div>
            <h1 className="text-lg font-bold">BrandGuard AI</h1>
            <p className="text-xs text-brand-400">Brand Governance</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-brand-700 text-white'
                    : 'text-brand-300 hover:bg-brand-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Demo Role Switcher for Evaluators / Judges */}
        <div className="px-3.5 py-3 border-t border-brand-800/70 bg-brand-950/30">
          <div className="flex items-center justify-between text-[11px] font-semibold text-brand-300 mb-2">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Role Switcher</span>
            </span>
            <span className="text-[10px] text-brand-400 font-mono">1-Click</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5 text-xs">
            {ROLE_PRESETS.map((r) => {
              const isActive = user?.email === r.email
              return (
                <button
                  key={r.email}
                  type="button"
                  disabled={switchingRole || isActive}
                  onClick={() => handleSwitchRole(r.email)}
                  className={`px-2 py-1.5 rounded-lg text-left font-medium transition-all flex items-center justify-between ${
                    isActive
                      ? 'bg-brand-600 text-white font-semibold shadow-xs ring-1 ring-white/20'
                      : 'bg-brand-800/50 text-brand-200 hover:bg-brand-800 hover:text-white'
                  }`}
                  title={`Switch to ${r.role} (${r.name})`}
                >
                  <span className="truncate">{r.label}</span>
                  {isActive && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0 ml-1" />}
                </button>
              )
            })}
          </div>
        </div>

        {/* User info + logout */}
        <div className="p-4 border-t border-brand-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-brand-700 rounded-full flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name}</p>
              <p className="text-xs text-brand-400 capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-brand-400 hover:text-white transition-colors w-full"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
