import { useState } from 'react'
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { 
  Shield, 
  LayoutDashboard, 
  FileText, 
  Palette, 
  LogOut, 
  User, 
  Briefcase, 
  CheckCircle2, 
  PenLine, 
  Building2,
  SlidersHorizontal,
  ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/brand-kits', icon: Palette, label: 'Brand Kits' },
  { to: '/drafts', icon: FileText, label: 'Drafts' },
]

const ROLE_PRESETS = [
  { label: 'Admin', role: 'admin', email: 'kaleajay626@gmail.com', name: 'Ajay', icon: Shield },
  { label: 'Manager', role: 'manager', email: 'mahesh@innovex.com', name: 'Mahesh', icon: Briefcase },
  { label: 'Reviewer', role: 'reviewer', email: 'asma@innovex.com', name: 'Asma', icon: CheckCircle2 },
  { label: 'Creator', role: 'creator', email: 'shrushti@innovex.com', name: 'Shrushti', icon: PenLine },
]

export default function Layout() {
  const { user, logout, quickSwitch } = useAuth()
  const [switchingRole, setSwitchingRole] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleSwitchRole = async (targetEmail) => {
    if (user?.email === targetEmail) return
    try {
      setSwitchingRole(true)
      await quickSwitch(targetEmail)
      toast.success(`Active persona: ${targetEmail}`)
    } catch (err) {
      toast.error('Failed to switch persona')
    } finally {
      setSwitchingRole(false)
    }
  }

  const getPageTitle = () => {
    if (location.pathname === '/') return 'Governance Overview'
    if (location.pathname.startsWith('/brand-kits')) return 'Brand Kits & Guidelines'
    if (location.pathname === '/drafts/new') return 'New Content Submission'
    if (location.pathname.startsWith('/drafts/')) return 'Draft Review & Governance'
    if (location.pathname.startsWith('/drafts')) return 'Content Drafts'
    return 'BrandGuard Platform'
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 text-white flex flex-col border-r border-slate-900 select-none">
        {/* Brand Header */}
        <div className="p-5 flex items-center gap-3 border-b border-slate-900">
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white shadow-xs">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight leading-none">BrandGuard AI</h1>
            <p className="text-[11px] text-slate-400 mt-1 font-medium">Innovex Governance</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Workspace
          </div>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-slate-800 text-white shadow-2xs font-semibold'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Demo Role Switcher for Evaluators / Judges */}
        <div className="px-3.5 py-3 border-t border-slate-900 bg-slate-900/40">
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 mb-2">
            <span className="flex items-center gap-1.5">
              <SlidersHorizontal className="w-3 h-3 text-slate-400" />
              <span>Persona Switcher</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono">1-Click</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5 text-xs">
            {ROLE_PRESETS.map((r) => {
              const Icon = r.icon
              const isActive = user?.email === r.email
              return (
                <button
                  key={r.email}
                  type="button"
                  disabled={switchingRole || isActive}
                  onClick={() => handleSwitchRole(r.email)}
                  className={`px-2 py-1.5 rounded-md text-left font-medium transition-all flex items-center justify-between text-[11px] ${
                    isActive
                      ? 'bg-brand-600 text-white font-semibold shadow-xs'
                      : 'bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-white'
                  }`}
                  title={`Switch to ${r.role} (${r.name})`}
                >
                  <span className="inline-flex items-center gap-1 truncate">
                    <Icon className="w-3 h-3 shrink-0" />
                    {r.label}
                  </span>
                  {isActive && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0 ml-1" />}
                </button>
              )
            })}
          </div>
        </div>

        {/* User info + logout */}
        <div className="p-3.5 border-t border-slate-900 bg-slate-950">
          <div className="flex items-center gap-2.5 mb-2.5">
            <div className="w-7 h-7 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center text-slate-300">
              <User className="w-3.5 h-3.5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.full_name}</p>
              <p className="text-[11px] text-slate-400 capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-xs text-slate-400 hover:text-slate-200 transition-colors w-full px-1"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Institutional Context Bar */}
        <header className="h-14 bg-white border-b border-slate-200/80 px-8 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Building2 className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-semibold text-slate-800">Innovex Global</span>
            <ChevronRight className="w-3 h-3 text-slate-400" />
            <span className="text-slate-600 font-medium">{getPageTitle()}</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Policy v2.4 Active
            </span>
          </div>
        </header>

        <main className="flex-1 overflow-auto bg-slate-50/60 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
