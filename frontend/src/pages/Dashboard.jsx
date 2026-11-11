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
  Activity,
  Layers,
  Target,
  Check,
  ShieldCheck,
  Zap,
  BookOpen,
  BarChart3,
  HelpCircle,
  Lightbulb,
  ExternalLink
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [auditLogs, setAuditLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCategoryTab, setSelectedCategoryTab] = useState('all')

  useEffect(() => {
    fetchDashboardData()
  }, [user])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      if (user?.workspace_id) {
        const [statsRes, auditRes] = await Promise.all([
          api.get(`/workspaces/${user.workspace_id}/dashboard/stats`),
          api.get(`/workspaces/${user.workspace_id}/dashboard/audit-log?limit=10`),
        ])
        setStats(statsRes.data)
        setAuditLogs(auditRes.data)
      } else {
        setStats({
          total_drafts: 0,
          drafts_by_status: {},
          findings_by_category: {},
          findings_by_severity: {},
          top_recurring_issues: [],
          health_score: 100,
          acceptance_rate: 100,
          open_issues_count: 0,
          resolved_issues_count: 0,
          engine_breakdown: { ai_count: 0, rule_count: 0 },
          content_type_matrix: [],
          guideline_gaps: [],
        })
        setAuditLogs([])
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  const healthScore = stats?.health_score ?? 100
  const getHealthBadge = (score) => {
    if (score >= 85) {
      return {
        label: 'Optimal Compliance',
        color: 'bg-emerald-50 text-emerald-800 border-emerald-200',
        dot: 'bg-emerald-500'
      }
    }
    if (score >= 65) {
      return {
        label: 'Moderate Risk',
        color: 'bg-amber-50 text-amber-800 border-amber-200',
        dot: 'bg-amber-500'
      }
    }
    return {
      label: 'High Friction',
      color: 'bg-rose-50 text-rose-800 border-rose-200',
      dot: 'bg-rose-500'
    }
  }
  const healthBadge = getHealthBadge(healthScore)

  const statCards = [
    {
      title: 'Total Drafts Audited',
      value: stats?.total_drafts || 0,
      subtitle: `${stats?.drafts_by_status?.approved || 0} approved for release`,
      icon: FileText,
      color: 'bg-blue-50 text-blue-600 border-blue-200',
    },
    {
      title: 'Active Open Issues',
      value: stats?.open_issues_count ?? (stats?.findings_by_severity?.error || 0),
      subtitle: 'Requiring creator revision',
      icon: AlertTriangle,
      color: 'bg-rose-50 text-rose-600 border-rose-200',
    },
    {
      title: 'Fix Adoption Rate',
      value: `${stats?.acceptance_rate ?? 100}%`,
      subtitle: `${stats?.resolved_issues_count || 0} suggestions resolved`,
      icon: CheckCircle2,
      color: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    },
    {
      title: 'Multi-Engine Protection',
      value: `${(stats?.engine_breakdown?.ai_count || 0) + (stats?.engine_breakdown?.rule_count || 0)} flags`,
      subtitle: `${stats?.engine_breakdown?.ai_count || 0} AI + ${stats?.engine_breakdown?.rule_count || 0} Deterministic`,
      icon: Zap,
      color: 'bg-purple-50 text-purple-600 border-purple-200',
    },
  ]

  const filteredGaps = (stats?.guideline_gaps || []).filter(gap => {
    if (selectedCategoryTab === 'all') return true
    return gap.category === selectedCategoryTab
  })

  return (
    <div className="space-y-8">
      {/* Welcome & Governance Health Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white p-6 rounded-2xl border border-gray-200/80 shadow-xs">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">
              Governance Intelligence Hub
            </h1>
            <span className={`px-2.5 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${healthBadge.color}`}>
              <span className={`w-2 h-2 rounded-full ${healthBadge.dot} animate-pulse`} />
              <span>{healthScore}% • {healthBadge.label}</span>
            </span>
          </div>
          <p className="text-xs sm:text-sm text-gray-500 mt-1.5">
            Pre-publication governance telemetry: root-cause diagnosis, guideline friction, and format risk analysis.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2.5">
          <Link
            to="/brand-kits"
            className="px-3.5 py-2 border border-gray-300 rounded-xl text-xs font-semibold text-gray-700 bg-white hover:bg-gray-50 transition-colors shadow-2xs flex items-center gap-1.5"
          >
            <BookOpen className="w-3.5 h-3.5 text-brand-600" />
            <span>Brand Kit Rules</span>
          </Link>
          <Link
            to="/drafts/new"
            className="px-4 py-2 bg-brand-600 text-white rounded-xl text-xs font-semibold hover:bg-brand-700 transition-colors shadow-2xs flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Audit New Draft</span>
          </Link>
        </div>
      </div>

      {/* High-level telemetry metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon
          return (
            <div
              key={i}
              className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-xs flex items-center justify-between"
            >
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                  {card.title}
                </p>
                <p className="text-2xl font-extrabold text-gray-900 mt-1">
                  {loading ? '...' : card.value}
                </p>
                <p className="text-[11px] text-gray-500 mt-0.5 font-medium">
                  {card.subtitle}
                </p>
              </div>
              <div className={`p-3 rounded-xl border ${card.color}`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>
          )
        })}
      </div>

      {/* Guideline-Gap Intelligence & Root-Cause Diagnosis (Round 3 Improvement 3) */}
      <div className="bg-white rounded-2xl p-6 border border-gray-200/80 shadow-xs space-y-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 border-b border-gray-100 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
                <TrendingUp className="w-4 h-4" />
              </div>
              <h2 className="text-base font-bold text-gray-900">
                Guideline-Gap Intelligence & Root-Cause Analytics
              </h2>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Autonomous clustering of repeated mistakes: explains <strong>why</strong> creators struggle and recommends specific Brand Kit updates.
            </p>
          </div>

          {/* Category Tabs */}
          <div className="flex flex-wrap items-center gap-1 bg-gray-100 p-1 rounded-xl text-xs font-semibold">
            {['all', 'terminology', 'claim', 'tone', 'accessibility'].map((tab) => (
              <button
                key={tab}
                onClick={() => setSelectedCategoryTab(tab)}
                className={`px-3 py-1 rounded-lg capitalize transition-colors ${
                  selectedCategoryTab === tab
                    ? 'bg-white text-gray-900 shadow-2xs'
                    : 'text-gray-500 hover:text-gray-900'
                }`}
              >
                {tab === 'all' ? 'All Gaps' : tab}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center text-gray-400 text-sm">
            Diagnosing guideline friction points across drafts...
          </div>
        ) : filteredGaps.length === 0 ? (
          <div className="py-12 text-center bg-gray-50/80 rounded-2xl border border-dashed border-gray-200 space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
            <h3 className="text-sm font-bold text-gray-800">No active guideline friction detected!</h3>
            <p className="text-xs text-gray-500 max-w-md mx-auto">
              Drafts in this workspace are adhering smoothly to established tone rules, terminology, and claim policies.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredGaps.map((gap, idx) => (
              <div
                key={idx}
                className="bg-gray-50/60 rounded-2xl p-5 border border-gray-200/90 space-y-3 hover:border-brand-300 transition-all shadow-2xs"
              >
                {/* Header: Guideline source + Friction badge */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-brand-100 text-brand-800 border border-brand-200">
                      {gap.category}
                    </span>
                    <span className="text-xs font-bold text-gray-900">
                      {gap.guideline_source}
                    </span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    gap.friction_severity === 'High'
                      ? 'bg-rose-100 text-rose-800 border border-rose-200'
                      : 'bg-amber-100 text-amber-800 border border-amber-200'
                  }`}>
                    {gap.violation_count} Recurrences ({gap.friction_severity} Friction)
                  </span>
                </div>

                {/* Sample flagged excerpt */}
                {gap.sample_highlight && (
                  <div className="text-xs bg-white p-2.5 rounded-xl border border-gray-200">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-0.5">
                      Frequent Trigger:
                    </span>
                    <code className="text-xs text-rose-700 font-mono font-medium">
                      "{gap.sample_highlight}"
                    </code>
                  </div>
                )}

                {/* Root Cause Diagnosis */}
                <div className="bg-white p-3 rounded-xl border border-gray-200 text-xs space-y-1">
                  <div className="flex items-center gap-1.5 text-indigo-700 font-bold">
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span className="text-[10px] uppercase tracking-wider">Root-Cause Analysis</span>
                  </div>
                  <p className="text-gray-700 leading-relaxed font-sans">
                    {gap.root_cause}
                  </p>
                </div>

                {/* Actionable Recommendation */}
                <div className="bg-emerald-50/70 p-3 rounded-xl border border-emerald-200 text-xs space-y-1.5">
                  <div className="flex items-center gap-1.5 text-emerald-800 font-bold">
                    <Lightbulb className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-[10px] uppercase tracking-wider">Recommended Brand Kit Update</span>
                  </div>
                  <p className="text-emerald-950 leading-relaxed font-medium">
                    {gap.ai_recommendation}
                  </p>
                  <div className="pt-1 flex justify-end">
                    <Link
                      to="/brand-kits"
                      className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 hover:text-emerald-900 underline"
                    >
                      <span>Update Brand Kit</span>
                      <ExternalLink className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dual Insights Grid: Content-Type Risk Heatmap & Dual Engine Synergy */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Format / Content-Type Risk Breakdown (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-6 border border-gray-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-xl border border-blue-100">
                <BarChart3 className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-gray-900">Format Risk Matrix</h3>
                <p className="text-[11px] text-gray-400">Violation density across content publishing formats</p>
              </div>
            </div>
          </div>

          {(stats?.content_type_matrix || []).length === 0 ? (
            <p className="text-xs text-gray-400 py-6 text-center">
              No content drafts available to compute format risk matrix.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead>
                  <tr className="border-b border-gray-100 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                    <th className="pb-2">Content Format</th>
                    <th className="pb-2">Drafts</th>
                    <th className="pb-2">Violations</th>
                    <th className="pb-2">Issues / Draft</th>
                    <th className="pb-2">Primary Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 font-medium text-gray-700">
                  {stats.content_type_matrix.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50/60 transition-colors">
                      <td className="py-2.5 font-bold capitalize text-gray-900 flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-gray-400" />
                        <span>{row.content_type.replace('_', ' ')}</span>
                      </td>
                      <td className="py-2.5">{row.drafts_count}</td>
                      <td className="py-2.5 font-bold text-rose-600">{row.findings_count}</td>
                      <td className="py-2.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          row.density > 2
                            ? 'bg-rose-100 text-rose-800'
                            : row.density > 0
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-emerald-100 text-emerald-800'
                        }`}>
                          {row.density} avg
                        </span>
                      </td>
                      <td className="py-2.5">
                        <span className="capitalize px-2 py-0.5 bg-gray-100 rounded text-gray-700 text-[10px] font-semibold">
                          {row.primary_risk}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Dual Engine Synergy & Category Distribution (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-6 border border-gray-200/80 shadow-xs space-y-5">
          <div className="border-b border-gray-100 pb-3">
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-brand-600" />
              <span>Multi-Engine Audit Breakdown</span>
            </h3>
            <p className="text-[11px] text-gray-400 mt-0.5">
              Deterministic rule speed + Gemini Multimodal semantic coverage
            </p>
          </div>

          {/* Engine Ratio Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-purple-700 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Gemini AI ({stats?.engine_breakdown?.ai_count || 0})
              </span>
              <span className="text-emerald-700 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" />
                Rule Engine ({stats?.engine_breakdown?.rule_count || 0})
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden flex">
              <div
                className="bg-purple-500 h-full transition-all"
                style={{
                  width: `${
                    (stats?.engine_breakdown?.ai_count || 0) + (stats?.engine_breakdown?.rule_count || 0) === 0
                      ? 50
                      : Math.round(
                          ((stats?.engine_breakdown?.ai_count || 0) /
                            ((stats?.engine_breakdown?.ai_count || 0) + (stats?.engine_breakdown?.rule_count || 1))) *
                            100
                        )
                  }%`,
                }}
              />
              <div
                className="bg-emerald-500 h-full transition-all flex-1"
              />
            </div>
          </div>

          {/* Violations by Category Progress */}
          <div className="space-y-3 pt-2">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">
              Violations by Category
            </span>
            {Object.keys(stats?.findings_by_category || {}).length === 0 ? (
              <p className="text-xs text-gray-400 py-3 italic">No violations recorded yet.</p>
            ) : (
              Object.entries(stats.findings_by_category).map(([cat, count]) => (
                <div key={cat} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="capitalize text-gray-700">{cat}</span>
                    <span className="text-gray-500">{count} flags</span>
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
              ))
            )}
          </div>
        </div>
      </div>

      {/* Immutable Governance & Audit Trail */}
      <div className="bg-white rounded-2xl p-6 border border-gray-200/80 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-gray-100 pb-3">
          <div>
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-600" />
              <span>Immutable Governance Audit Log</span>
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Tamper-evident log of reviews, approvals, AI service invocations, and 1-click suggestion applications.
            </p>
          </div>
        </div>

        {auditLogs.length === 0 ? (
          <div className="py-8 text-center text-gray-400 text-xs">
            No audit logs available yet in this workspace.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 text-xs">
              <thead>
                <tr className="text-left text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Entity</th>
                  <th className="py-2.5 px-3">Audit Details</th>
                  <th className="py-2.5 px-3">AI / Engine</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 text-gray-700">
                {auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50/70 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-gray-900 capitalize">
                      {log.action.replace(/_/g, ' ')}
                    </td>
                    <td className="py-2.5 px-3 capitalize text-gray-500">
                      {log.entity_type}
                    </td>
                    <td className="py-2.5 px-3 text-gray-600 max-w-xs truncate font-mono text-[11px]">
                      {log.details ? JSON.stringify(log.details) : '—'}
                    </td>
                    <td className="py-2.5 px-3">
                      {log.ai_service_used ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-50 text-purple-700 border border-purple-200">
                          {log.ai_service_used}
                        </span>
                      ) : (
                        <span className="text-[11px] text-gray-400">Deterministic Rule</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-gray-500 text-[11px]">
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
