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

  const fillDemo = (demoEmail) => {
    setEmail(demoEmail)
    setPassword('password123')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-900 via-brand-800 to-blue-900 px-4 py-8">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-6">
          <Shield className="w-10 h-10 text-brand-600" />
          <h1 className="text-2xl font-bold text-gray-900">BrandGuard AI</h1>
        </div>

        <h2 className="text-xl font-semibold text-center mb-4">Sign In</h2>

        {/* Demo Quick-Fill Bar for Examiners/Judges */}
        <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-blue-900 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>Judge / Examiner Demo Accounts (1-Click Fill):</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            <button
              type="button"
              onClick={() => fillDemo('kaleajay626@gmail.com')}
              className={`text-xs px-2.5 py-1.5 rounded-lg border font-medium text-left transition-all ${
                email === 'kaleajay626@gmail.com'
                  ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-brand-300'
              }`}
            >
              👑 Admin (Ajay)
            </button>
            <button
              type="button"
              onClick={() => fillDemo('mahesh@innovex.com')}
              className={`text-xs px-2.5 py-1.5 rounded-lg border font-medium text-left transition-all ${
                email === 'mahesh@innovex.com'
                  ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-brand-300'
              }`}
            >
              👔 Manager (Mahesh)
            </button>
            <button
              type="button"
              onClick={() => fillDemo('asma@innovex.com')}
              className={`text-xs px-2.5 py-1.5 rounded-lg border font-medium text-left transition-all ${
                email === 'asma@innovex.com'
                  ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-brand-300'
              }`}
            >
              🔍 Reviewer (Asma)
            </button>
            <button
              type="button"
              onClick={() => fillDemo('shrushti@innovex.com')}
              className={`text-xs px-2.5 py-1.5 rounded-lg border font-medium text-left transition-all ${
                email === 'shrushti@innovex.com'
                  ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-brand-300'
              }`}
            >
              ✍️ Creator (Shrushti)
            </button>
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
