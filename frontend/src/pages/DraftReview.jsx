import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  ArrowLeft, 
  Sparkles, 
  ShieldAlert, 
  Check, 
  X, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  MessageSquare, 
  Send,
  BookOpen,
  Info,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function DraftReview() {
  const { draftId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [draft, setDraft] = useState(null)
  const [findings, setFindings] = useState([])
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(true)
  const [reReviewing, setReReviewing] = useState(false)
  const [commentSubmitting, setCommentSubmitting] = useState(false)

  useEffect(() => {
    fetchDraftData()
  }, [draftId])

  const fetchDraftData = async () => {
    try {
      setLoading(true)
      const wsId = user?.workspace_id
      if (!wsId) return

      const [draftRes, findingsRes, commentsRes] = await Promise.all([
        api.get(`/workspaces/${wsId}/drafts/${draftId}`),
        api.get(`/workspaces/${wsId}/drafts/${draftId}/review/findings`),
        api.get(`/workspaces/${wsId}/drafts/${draftId}/comments`),
      ])

      setDraft(draftRes.data)
      setFindings(findingsRes.data)
      setComments(commentsRes.data)
    } catch (err) {
      toast.error('Failed to load draft review data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleReReview = async () => {
    try {
      setReReviewing(true)
      const res = await api.post(`/workspaces/${user.workspace_id}/drafts/${draftId}/review/`)
      toast.success(res.data.message || 'Review completed!')
      fetchDraftData()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Review failed')
    } finally {
      setReReviewing(false)
    }
  }

  const handleUpdateFindingStatus = async (findingId, newStatus) => {
    try {
      await api.put(
        `/workspaces/${user.workspace_id}/drafts/${draftId}/review/findings/${findingId}`,
        { status: newStatus }
      )
      toast.success(`Suggestion ${newStatus}`)
      setFindings(findings.map(f => f.id === findingId ? { ...f, status: newStatus } : f))
    } catch (err) {
      toast.error('Failed to update suggestion status')
    }
  }

  const handleUpdateDraftStatus = async (newStatus) => {
    try {
      await api.put(`/workspaces/${user.workspace_id}/drafts/${draftId}/status`, {
        status: newStatus,
      })
      toast.success(`Draft marked as ${newStatus.replace('_', ' ')}`)
      setDraft({ ...draft, status: newStatus })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update draft status')
    }
  }

  const handleAddComment = async (e) => {
    e.preventDefault()
    if (!newComment.trim()) return

    try {
      setCommentSubmitting(true)
      const res = await api.post(`/workspaces/${user.workspace_id}/drafts/${draftId}/comments`, {
        content: newComment,
      })
      setComments([...comments, res.data])
      setNewComment('')
      toast.success('Comment added')
    } catch (err) {
      toast.error('Failed to add comment')
    } finally {
      setCommentSubmitting(false)
    }
  }

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'error':
        return 'bg-rose-50 text-rose-700 border-rose-200'
      case 'warning':
        return 'bg-amber-50 text-amber-700 border-amber-200'
      default:
        return 'bg-blue-50 text-blue-700 border-blue-200'
    }
  }

  if (loading) {
    return <div className="py-24 text-center text-gray-400 font-medium">Analyzing draft governance...</div>
  }

  if (!draft) {
    return <div className="py-24 text-center text-gray-500">Draft not found.</div>
  }

  const openFindings = findings.filter(f => f.status === 'open')
  const resolvedFindings = findings.filter(f => f.status !== 'open')

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/drafts')}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 text-gray-600" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-gray-900">{draft.title}</h1>
              <span className="capitalize px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-700 border">
                {draft.status.replace('_', ' ')}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Format: <span className="capitalize font-medium text-gray-600">{draft.content_type?.replace('_', ' ')}</span>
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleReReview}
            disabled={reReviewing}
            className="px-3.5 py-2 border border-gray-300 rounded-lg text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reReviewing ? 'animate-spin text-brand-600' : ''}`} />
            {reReviewing ? 'Auditing...' : 'Re-Run Check'}
          </button>

          {/* Workflow approval buttons for Managers/Reviewers */}
          {user?.role !== 'creator' && (
            <>
              <button
                onClick={() => handleUpdateDraftStatus('changes_requested')}
                className="px-3.5 py-2 bg-rose-50 text-rose-700 border border-rose-200 rounded-lg text-xs font-medium hover:bg-rose-100 transition-colors"
              >
                Request Changes
              </button>
              <button
                onClick={() => handleUpdateDraftStatus('approved')}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 transition-colors shadow-xs flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                Approve for Publishing
              </button>
            </>
          )}
        </div>
      </div>

      {/* Main Review Workspace: Two Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (Content & Comments) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Draft text display */}
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                Submitted Content Draft
              </span>
              <span className="text-xs text-gray-400">
                {draft.content.split(/\s+/).filter(Boolean).length} words
              </span>
            </div>

            <div className="bg-gray-50 rounded-lg p-5 border border-gray-100 text-gray-800 text-sm leading-relaxed whitespace-pre-wrap font-sans">
              {draft.content}
            </div>
          </div>

          {/* Collaborative reviewer notes & comments */}
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-brand-600" />
              Reviewer Discussion & Audit Notes
            </h3>

            {comments.length === 0 ? (
              <p className="text-xs text-gray-400 py-3 italic">
                No discussion comments on this draft yet.
              </p>
            ) : (
              <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
                {comments.map((c) => (
                  <div key={c.id} className="bg-gray-50 rounded-lg p-3 text-xs border border-gray-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-gray-700">Reviewer Note</span>
                      <span className="text-gray-400">{new Date(c.created_at).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-gray-800">{c.content}</p>
                  </div>
                ))}
              </div>
            )}

            <form onSubmit={handleAddComment} className="flex gap-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add compliance notes or feedback for creator..."
                className="flex-1 px-3 py-2 border rounded-lg text-xs outline-none focus:ring-2 focus:ring-brand-500"
              />
              <button
                type="submit"
                disabled={commentSubmitting}
                className="px-3.5 py-2 bg-brand-600 text-white rounded-lg text-xs font-medium hover:bg-brand-700 disabled:opacity-50 flex items-center gap-1"
              >
                <Send className="w-3.5 h-3.5" />
                Post
              </button>
            </form>
          </div>
        </div>

        {/* Right Column (Explained Findings with Source Citation) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-brand-600" />
              Explained Findings ({findings.length})
            </h2>
            <span className="text-xs text-gray-500">
              {openFindings.length} open issues
            </span>
          </div>

          {findings.length === 0 ? (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-8 text-center space-y-2">
              <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
              <h3 className="text-sm font-bold text-emerald-900">100% Brand Compliant!</h3>
              <p className="text-xs text-emerald-700">
                No banned terms, unsupported claims, or unapproved colors detected.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {findings.map((f) => {
                const isResolved = f.status !== 'open'
                return (
                  <div
                    key={f.id}
                    className={`bg-white rounded-xl p-5 border shadow-xs transition-all ${
                      isResolved
                        ? 'opacity-60 border-gray-200 bg-gray-50/50'
                        : 'border-gray-200 hover:border-brand-300'
                    }`}
                  >
                    {/* Header badge row */}
                    <div className="flex items-center justify-between gap-2 mb-2.5">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${getSeverityStyle(
                            f.severity
                          )}`}
                        >
                          {f.severity}
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-700 capitalize">
                          {f.category}
                        </span>
                      </div>

                      {f.status !== 'open' && (
                        <span className="text-[11px] font-semibold text-gray-500 capitalize">
                          [{f.status}]
                        </span>
                      )}
                    </div>

                    {/* Flagged snippet */}
                    {f.text_highlight && (
                      <div className="mb-2">
                        <span className="text-[11px] font-bold text-gray-400 uppercase">Flagged: </span>
                        <code className="text-xs bg-rose-50 text-rose-800 px-1.5 py-0.5 rounded font-mono border border-rose-100">
                          "{f.text_highlight}"
                        </code>
                      </div>
                    )}

                    {/* Explanation */}
                    <p className="text-xs text-gray-800 leading-relaxed mb-3">
                      {f.explanation}
                    </p>

                    {/* Grounded Citation */}
                    {f.guideline_source && (
                      <div className="mb-3 bg-brand-50/60 border border-brand-100 rounded-lg p-2.5 flex items-start gap-2 text-xs text-brand-900">
                        <BookOpen className="w-4 h-4 text-brand-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold block text-[11px] text-brand-700">
                            Cited Guideline Source:
                          </span>
                          <span className="font-mono text-[11px] text-brand-800">
                            {f.guideline_source}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Suggestion & Diff */}
                    {f.suggestion && (
                      <div className="mb-3 bg-emerald-50/50 border border-emerald-100 rounded-lg p-2.5 text-xs text-emerald-950 space-y-1">
                        <span className="font-semibold block text-[11px] text-emerald-800">
                          Proposed Fix (Never auto-applied):
                        </span>
                        <p className="font-sans text-emerald-900 font-medium">
                          {f.suggestion}
                        </p>
                      </div>
                    )}

                    {/* Action buttons (Accept/Reject) */}
                    {f.status === 'open' && f.suggestion && (
                      <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-100">
                        <button
                          onClick={() => handleUpdateFindingStatus(f.id, 'rejected')}
                          className="px-2.5 py-1 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded flex items-center gap-1 transition-colors"
                        >
                          <X className="w-3.5 h-3.5 text-gray-500" />
                          Dismiss
                        </button>
                        <button
                          onClick={() => handleUpdateFindingStatus(f.id, 'accepted')}
                          className="px-3 py-1 text-xs font-semibold bg-brand-600 text-white rounded hover:bg-brand-700 flex items-center gap-1 shadow-2xs transition-colors"
                        >
                          <Check className="w-3.5 h-3.5" />
                          Accept Fix
                        </button>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
