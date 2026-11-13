import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  FileText, 
  Plus, 
  Search, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight,
  Sparkles,
  ShieldAlert,
  ShieldCheck
} from 'lucide-react'

export default function Drafts() {
  const { user } = useAuth()
  const [drafts, setDrafts] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterStatus, setFilterStatus] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchDrafts()
  }, [user, filterStatus])

  const fetchDrafts = async () => {
    try {
      setLoading(true)
      let wsId = user?.workspace_id
      if (!wsId) {
        const wsRes = await api.get('/workspaces/')
        if (wsRes.data && wsRes.data.length > 0) {
          wsId = wsRes.data[0].id
        }
      }
      if (wsId) {
        const url = filterStatus === 'all' 
          ? `/workspaces/${wsId}/drafts/`
          : `/workspaces/${wsId}/drafts/?status=${filterStatus}`
        const res = await api.get(url)
        setDrafts(res.data)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" /> Approved
          </span>
        )
      case 'changes_requested':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
            <AlertCircle className="w-3.5 h-3.5" /> Changes Needed
          </span>
        )
      case 'in_review':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
            <Clock className="w-3.5 h-3.5" /> In Review
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
            Draft
          </span>
        )
    }
  }

  const filtered = drafts.filter(d => 
    d.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.content.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="w-7 h-7 text-brand-600" />
            Content Drafts & Reviews
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Pre-publication review queue for social posts, blogs, emails, and ads.
          </p>
        </div>
        <Link
          to="/drafts/new"
          className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors shadow-sm flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Create New Draft
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="flex items-center gap-2 w-full sm:w-72 border border-gray-200 rounded-lg px-3 py-2 bg-white focus-within:ring-2 focus-within:ring-brand-500 shadow-xs">
          <Search className="w-3.5 h-3.5 text-gray-400 shrink-0" />
          <input
            type="text"
            placeholder="Search drafts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full text-xs outline-none bg-transparent text-gray-700 placeholder-gray-400"
          />
        </div>

        <div className="flex gap-1.5 flex-wrap">
          {['all', 'draft', 'in_review', 'changes_requested', 'approved'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-2.5 py-1.5 rounded-lg text-[11px] font-semibold capitalize whitespace-nowrap transition-colors ${
                filterStatus === st
                  ? 'bg-brand-600 text-white shadow-xs'
                  : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              {st.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Drafts List */}
      {loading ? (
        <div className="py-12 text-center text-gray-400">Loading drafts...</div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center border border-dashed border-gray-300 max-w-xl mx-auto space-y-4">
          <FileText className="w-12 h-12 text-gray-400 mx-auto" />
          <h3 className="text-lg font-medium text-gray-900">No drafts found</h3>
          <p className="text-sm text-gray-500">
            Submit copy, ad headlines, or social snippets to verify brand tone and claim accuracy.
          </p>
          <Link
            to="/drafts/new"
            className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors inline-flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Check Your First Draft
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((draft) => (
            <Link
              key={draft.id}
              to={`/drafts/${draft.id}`}
              className="bg-white border border-gray-200 rounded-xl p-4 hover:border-brand-300 hover:shadow-xs flex items-start justify-between transition-all group block"
            >
              <div className="space-y-2 flex-1 pr-4 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-sm font-semibold text-gray-900 group-hover:text-brand-600 transition-colors truncate">
                    {draft.title}
                  </h3>
                  {getStatusBadge(draft.status)}
                  <span className="capitalize px-2 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-500 border border-gray-200 shrink-0">
                    {draft.content_type?.replace('_', ' ')}
                  </span>
                  {draft.findings_count > 0 ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 shrink-0">
                      <ShieldAlert className="w-3 h-3" />
                      {draft.findings_count} violation{draft.findings_count !== 1 ? 's' : ''}
                    </span>
                  ) : draft.findings_count === 0 && draft.status !== 'draft' ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
                      <ShieldCheck className="w-3 h-3" />
                      Clean
                    </span>
                  ) : null}
                </div>
                <p className="text-xs text-gray-400 leading-relaxed line-clamp-1">
                  {draft.content?.slice(0, 130)}{draft.content?.length > 130 ? '…' : ''}
                </p>
                <div className="flex items-center gap-3 text-[11px] text-gray-400">
                  <span className="tabular-nums">{draft.content?.split(/\s+/).filter(Boolean).length || 0} words</span>
                  <span>·</span>
                  <span>Updated {new Date(draft.updated_at).toLocaleString()}</span>
                </div>
              </div>
              <div className="flex items-center gap-1 text-xs font-medium text-gray-400 group-hover:text-brand-600 transition-colors shrink-0 mt-0.5">
                <span className="hidden sm:block">Review</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
