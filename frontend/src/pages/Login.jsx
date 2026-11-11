import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Shield, Sparkles, Server } from 'lucide-react'
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
      toast.success('Signed in successfully!')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (demoEmail) => {
    setEmail(demoEmail)
    setPassword('password123')
  }

  const demoAccounts = [
    {
      role: 'Admin',
      name: 'Ajay Kale',
      email: 'kaleajay626@gmail.com',
      badge: '👑 Admin',
      desc: 'Full Governance & System Audit',
      color: 'border-purple-200 hover:border-purple-400 bg-purple-50/40 text-purple-900',
    },
    {
      role: 'Manager',
      name: 'Mahesh Gadekar',
      email: 'mahesh@innovex.com',
      badge: '👔 Manager',
      desc: 'Audit Logs & Guideline Gaps',
      color: 'border-blue-200 hover:border-blue-400 bg-blue-50/40 text-blue-900',
    },
    {
      role: 'Reviewer',
      name: 'Asma Inamdar',
      email: 'asma@innovex.com',
      badge: '🔍 Reviewer',
      desc: 'Draft Approval & Verification',
      color: 'border-emerald-200 hover:border-emerald-400 bg-emerald-50/40 text-emerald-900',
    },
    {
      role: 'Creator',
      name: 'Shrushti Kharadkar',
      email: 'shrushti@innovex.com',
      badge: '✍️ Creator',
      desc: 'Submit Drafts & 1-Click Fixes',
      color: 'border-amber-200 hover:border-amber-400 bg-amber-50/40 text-amber-900',
    },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-900 via-brand-800 to-blue-900 px-4 py-8">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-lg border border-gray-100">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="w-11 h-11 bg-brand-600 rounded-xl flex items-center justify-center text-white shadow-md shadow-brand-500/30">
            <Shield className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">BrandGuard AI</h1>
            <p className="text-xs text-gray-500">Pre-Publication Governance Platform</p>
          </div>
        </div>

        {/* Demo Quick-Fill Bar for Examiners/Judges */}
        <div className="mb-6 p-4 bg-slate-50 border border-slate-200 rounded-xl">
          <div className="flex items-center justify-between mb-2.5">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
              <Sparkles className="w-4 h-4 text-brand-600" />
              <span>Judge / Examiner Demo Accounts</span>
            </div>
            <span className="text-[11px] font-mono font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
              Password: password123
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mb-3">
            Click any role below to <strong>1-Click Instant Sign-In</strong> without typing:
          </p>
          <div className="grid grid-cols-2 gap-2">
            {demoAccounts.map((acc) => (
              <button
                key={acc.email}
                type="button"
                disabled={loading}
                onClick={() => handleDirectLogin(acc.email)}
                className={`text-left p-2.5 rounded-xl border transition-all text-xs group hover:shadow-sm ${acc.color} ${
                  email === acc.email ? 'ring-2 ring-brand-500 shadow-sm' : ''
                }`}
                title={`Sign in as ${acc.role} (${acc.email})`}
              >
                <div className="flex items-center justify-between font-semibold">
                  <span>{acc.badge}</span>
                  <span className="text-[10px] opacity-70 group-hover:opacity-100 font-normal">Instant ➔</span>
                </div>
                <div className="text-[11px] font-medium text-slate-700 mt-1 truncate">{acc.name}</div>
                <div className="text-[10px] text-slate-400 truncate font-mono">{acc.email}</div>
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none"
              placeholder="••••••••"
            />
          </div>

          {/* Cold-Start Informative Alert */}
          {slowServerHint && (
            <div className="flex items-start gap-2.5 p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 animate-pulse">
              <Server className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <span>
                <strong>Cloud server waking up...</strong> Render free tier spins up from sleep on first request (~20–30s). Please hold on!
              </span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 text-white py-2.5 rounded-lg font-medium hover:bg-brand-700 transition-colors disabled:opacity-50 shadow-md shadow-brand-500/20"
          >
            {loading ? 'Connecting & Signing In...' : 'Sign In'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-brand-600 hover:underline font-medium">
            Create one
          </Link>
        </p>
      </div>
    </div>
  )
}
