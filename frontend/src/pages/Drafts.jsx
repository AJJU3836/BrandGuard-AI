import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  FileText, 
  Plus, 
  Search, 
  Filter, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight,
  Sparkles
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
      if (user?.workspace_id) {
        const url = filterStatus === 'all' 
          ? `/workspaces/${user.workspace_id}/drafts/`
          : `/workspaces/${user.workspace_id}/drafts/?status=${filterStatus}`
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
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="flex items-center gap-2 w-full sm:w-80 border border-gray-300 rounded-lg px-3 py-1.5 focus-within:ring-2 focus-within:ring-brand-500">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search drafts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full text-sm outline-none bg-transparent"
          />
        </div>

        <div className="flex gap-2 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          {['all', 'draft', 'in_review', 'changes_requested', 'approved'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize whitespace-nowrap transition-colors ${
                filterStatus === st
                  ? 'bg-brand-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
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
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden divide-y divide-gray-100">
          {filtered.map((draft) => (
            <Link
              key={draft.id}
              to={`/drafts/${draft.id}`}
              className="p-5 hover:bg-gray-50 flex items-center justify-between transition-colors block"
            >
              <div className="space-y-1.5 flex-1 pr-6">
                <div className="flex items-center gap-2.5">
                  <h3 className="text-base font-semibold text-gray-900 hover:text-brand-600">
                    {draft.title}
                  </h3>
                  {getStatusBadge(draft.status)}
                  <span className="capitalize px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200">
                    {draft.content_type?.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-sm text-gray-500 line-clamp-1 font-mono text-xs">
                  {draft.content}
                </p>
                <p className="text-xs text-gray-400">
                  Last updated {new Date(draft.updated_at).toLocaleString()}
                </p>
              </div>

              <div className="flex items-center gap-2 text-brand-600 font-medium text-sm">
                <span>Inspect Review</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
