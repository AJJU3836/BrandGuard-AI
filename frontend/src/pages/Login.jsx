import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Shield, Server, Briefcase, CheckCircle2, PenLine, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../services/api'

export default function Login() {
  const [email, setEmail] = useState('kaleajay626@gmail.com')
  const [password, setPassword] = useState('password123')
  const [loading, setLoading] = useState(false)
  const [slowServerHint, setSlowServerHint] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  // Pre-warm backend on page load so cold-start starts early
  useEffect(() => {
    api.get('/').catch(() => {})
  }, [])

  // Timer to show cold-start message if request takes > 3s
  useEffect(() => {
    let timer
    if (loading) {
      timer = setTimeout(() => {
        setSlowServerHint(true)
      }, 3000)
    } else {
      setSlowServerHint(false)
    }
    return () => clearTimeout(timer)
  }, [loading])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setSlowServerHint(false)
    try {
      await login(email, password)
      toast.success('Welcome back!')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDirectLogin = async (demoEmail) => {
    setEmail(demoEmail)
    setPassword('password123')
    setLoading(true)
    setSlowServerHint(false)
    try {
      await login(demoEmail, 'password123')
      toast.success('Authenticated successfully')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const demoAccounts = [
    {
      role: 'Admin',
      name: 'Ajay Kale',
      email: 'kaleajay626@gmail.com',
      title: 'System Administrator',
      desc: 'Full workspace & audit control',
      icon: Shield,
      badgeClass: 'bg-purple-50 text-purple-700 border-purple-200',
    },
    {
      role: 'Manager',
      name: 'Mahesh Gadekar',
      email: 'mahesh@innovex.com',
      title: 'Compliance Manager',
      desc: 'Policy rules & gap analytics',
      icon: Briefcase,
      badgeClass: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    {
      role: 'Reviewer',
      name: 'Asma Inamdar',
      email: 'asma@innovex.com',
      title: 'Editorial Reviewer',
      desc: 'Verification & approvals',
      icon: CheckCircle2,
      badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    {
      role: 'Creator',
      name: 'Shrushti Kharadkar',
      email: 'shrushti@innovex.com',
      title: 'Content Author',
      desc: 'Drafting & 1-click suggestion fixes',
      icon: PenLine,
      badgeClass: 'bg-slate-100 text-slate-700 border-slate-200',
    },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4 py-8 relative overflow-hidden">
      {/* Subtle enterprise background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-brand-600/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-lg border border-slate-200/80 relative z-10">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-brand-600 rounded-xl flex items-center justify-center text-white shadow-sm">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">BrandGuard AI</h1>
            <p className="text-xs text-slate-500">Enterprise Pre-Publication Governance</p>
          </div>
        </div>

        {/* Demo Personas Quick-Access Panel */}
        <div className="mb-6 p-4 bg-slate-50/80 border border-slate-200 rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-800">
              Evaluation Personas
            </span>
            <span className="text-[11px] font-mono font-medium text-slate-600 bg-white border border-slate-200 px-2 py-0.5 rounded-md">
              Password: password123
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mb-3">
            Select a pre-configured team account to evaluate role permissions:
          </p>
          <div className="grid grid-cols-2 gap-2">
            {demoAccounts.map((acc) => {
              const Icon = acc.icon
              const isSelected = email === acc.email
              return (
                <button
                  key={acc.email}
                  type="button"
                  disabled={loading}
                  onClick={() => handleDirectLogin(acc.email)}
                  className={`text-left p-2.5 rounded-xl border transition-all text-xs group bg-white ${
                    isSelected
                      ? 'border-brand-600 ring-1 ring-brand-500 shadow-xs'
                      : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/60'
                  }`}
                  title={`Sign in as ${acc.title} (${acc.email})`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold border ${acc.badgeClass}`}>
                      <Icon className="w-3 h-3" />
                      {acc.role}
                    </span>
                    <ArrowRight className="w-3 h-3 text-slate-300 group-hover:text-slate-600 transition-colors" />
                  </div>
                  <div className="text-[11px] font-medium text-slate-800 truncate">{acc.name}</div>
                  <div className="text-[10px] text-slate-400 truncate">{acc.desc}</div>
                </button>
              )
            })}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Work Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3.5 py-2 border border-slate-200 rounded-lg text-sm text-slate-900 focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none bg-white transition-all"
              placeholder="name@company.com"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3.5 py-2 border border-slate-200 rounded-lg text-sm text-slate-900 focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none bg-white transition-all"
              placeholder="••••••••"
            />
          </div>

          {/* Cold-Start Informative Alert */}
          {slowServerHint && (
            <div className="flex items-start gap-2.5 p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 animate-pulse">
              <Server className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <span>
                <strong>Starting application instance...</strong> The cloud service is initializing (~20-30s). Your request will complete automatically.
              </span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-brand-700 transition-colors disabled:opacity-50 shadow-sm"
          >
            {loading ? 'Authenticating...' : 'Sign In to Workspace'}
          </button>
        </form>

        <p className="text-center text-xs text-slate-500 mt-6">
          Need a separate workspace?{' '}
          <Link to="/register" className="text-brand-600 hover:text-brand-700 font-medium">
            Create an organization
          </Link>
        </p>
      </div>
    </div>
  )
}
