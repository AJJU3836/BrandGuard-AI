import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  TrendingUp, 
  ArrowRight,
  Sparkles,
  Activity
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [auditLogs, setAuditLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [user])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      // Check if user has workspace
      if (user?.workspace_id) {
        const [statsRes, auditRes] = await Promise.all([
          api.get(`/workspaces/${user.workspace_id}/dashboard/stats`),
          api.get(`/workspaces/${user.workspace_id}/dashboard/audit-log?limit=8`),
        ])
        setStats(statsRes.data)
        setAuditLogs(auditRes.data)
      } else {
        // Fallback or demo empty state
        setStats({
          total_drafts: 0,
          drafts_by_status: {},
          findings_by_category: {},
          findings_by_severity: {},
          top_recurring_issues: []
        })
        setAuditLogs([])
      }
    } catch (err) {
      console.error(err)
      // Non-blocking toast if workspace isn't fully configured yet
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: 'Total Drafts',
      value: stats?.total_drafts || 0,
      icon: FileText,
      color: 'bg-blue-50 text-blue-600 border-blue-200',
    },
    {
      title: 'Pending Review',
      value: stats?.drafts_by_status?.in_review || 0,
      icon: Clock,
      color: 'bg-amber-50 text-amber-600 border-amber-200',
    },
    {
      title: 'Changes Requested',
      value: stats?.drafts_by_status?.changes_requested || 0,
      icon: AlertTriangle,
      color: 'bg-rose-50 text-rose-600 border-rose-200',
    },
    {
      title: 'Approved Content',
      value: stats?.drafts_by_status?.approved || 0,
      icon: CheckCircle2,
      color: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Welcome header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name} 👋
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Pre-publication governance dashboard — catch brand issues before they go live.
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/brand-kits"
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors shadow-sm"
          >
            Manage Brand Kit
          </Link>
          <Link
            to="/drafts/new"
            className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors shadow-sm flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Check New Draft
          </Link>
        </div>
      </div>

      {/* High-level metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {statCards.map((card, i) => {
          const Icon = card.icon
          return (
            <div
              key={i}
              className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm flex items-center justify-between"
            >
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {card.title}
                </p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {loading ? '...' : card.value}
                </p>
              </div>
              <div className={`p-3 rounded-lg border ${card.color}`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
          )
        })}
      </div>

      {/* Main insights grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Categories of detected issues */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-brand-600" />
              Violations by Category
            </h2>
          </div>
          {loading ? (
            <div className="py-8 text-center text-gray-400 text-sm">Loading insights...</div>
          ) : Object.keys(stats?.findings_by_category || {}).length === 0 ? (
            <div className="py-8 text-center text-gray-400 text-sm">
              No brand findings recorded yet.
            </div>
          ) : (
            <div className="space-y-3">
              {Object.entries(stats.findings_by_category).map(([cat, count]) => (
                <div key={cat} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="capitalize text-gray-700">{cat}</span>
                    <span className="text-gray-500">{count} flagged</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-brand-500 h-2 rounded-full"
                      style={{
                        width: `${Math.min(100, (count / (stats.total_drafts || 1)) * 100)}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Guideline Gap Insights (Top Recurring Issues) */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-indigo-600" />
                Guideline Gap Insights
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Repeated mistakes indicate ambiguous guidelines that need clarification.
              </p>
            </div>
          </div>

          {loading ? (
            <div className="py-8 text-center text-gray-400 text-sm">Analyzing gaps...</div>
          ) : (stats?.top_recurring_issues || []).length === 0 ? (
            <div className="py-8 text-center text-gray-400 text-sm">
              All guidelines are currently adhered to smoothly!
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {stats.top_recurring_issues.map((issue, idx) => (
                <div key={idx} className="py-3 flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold flex items-center justify-center mt-0.5">
                      #{idx + 1}
                    </span>
                    <p className="text-sm text-gray-700 leading-snug">
                      {issue.explanation}
                    </p>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 flex-shrink-0">
                    {issue.count} occurrences
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Governance & Audit Log section */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <Activity className="w-5 h-5 text-emerald-600" />
              Recent Governance Audit Trail
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Immutable log of every draft review, status change, and AI evaluation.
            </p>
          </div>
        </div>

        {auditLogs.length === 0 ? (
          <div className="py-6 text-center text-gray-400 text-sm">
            No audit logs available yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Entity</th>
                  <th className="py-3 px-4">AI Service</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700">
                {auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4 font-medium text-gray-900 capitalize">
                      {log.action.replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 px-4 capitalize text-xs text-gray-500">
                      {log.entity_type}
                    </td>
                    <td className="py-3 px-4">
                      {log.ai_service_used ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200">
                          {log.ai_service_used}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">Manual / Rule</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-xs text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
