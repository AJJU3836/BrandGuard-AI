import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import VersionHistory from '../components/VersionHistory'
import { 
  ArrowLeft, 
  Sparkles, 
  ShieldAlert, 
  ShieldCheck,
  Check, 
  X, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  MessageSquare, 
  Send,
  BookOpen,
  Info,
  RefreshCw,
  History,
  Download,
  Image as ImageIcon,
  UploadCloud,
  Filter,
  Search,
  FileSpreadsheet,
  FileCode,
  Eye,
  SlidersHorizontal
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
  const [showHistory, setShowHistory] = useState(false)

  // Filtering states
  const [severityFilter, setSeverityFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Image audit states
  const [selectedImageFile, setSelectedImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [altText, setAltText] = useState('')
  const [isAuditingImage, setIsAuditingImage] = useState(false)
  const [showImageAuditBox, setShowImageAuditBox] = useState(false)
  const [lastAuditedAsset, setLastAuditedAsset] = useState(null)

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
      toast.success(`Suggestion marked as ${newStatus}`)
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
      toast.success(`Draft status updated to ${newStatus.replace('_', ' ')}`)
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

  // Image Selection Handler
  const handleImageFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedImageFile(file)
      setImagePreview(URL.createObjectURL(file))
    }
  }

  // Run Image Compliance Audit
  const handleRunImageAudit = async (e) => {
    e.preventDefault()
    if (!selectedImageFile && !altText) {
      toast.error('Please select an image file or enter an asset name & alt-text.')
      return
    }

    try {
      setIsAuditingImage(true)
      const formData = new FormData()
      if (selectedImageFile) {
        formData.append('file', selectedImageFile)
      }
      formData.append('image_name', selectedImageFile ? selectedImageFile.name : 'Visual-Asset.png')
      formData.append('alt_text', altText)

      const res = await api.post(
        `/workspaces/${user.workspace_id}/drafts/${draftId}/review/image`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      )

      toast.success(`Image audit generated ${res.data.length} visual findings`)
      // Refresh findings list to include new visual & accessibility checks
      const updatedFindings = await api.get(`/workspaces/${user.workspace_id}/drafts/${draftId}/review/findings`)
      setFindings(updatedFindings.data)

      // Retain audited asset summary for user visibility
      setLastAuditedAsset({
        preview: imagePreview,
        name: selectedImageFile ? selectedImageFile.name : 'Visual-Asset.png',
        size: selectedImageFile ? (selectedImageFile.size / 1024).toFixed(1) : null,
        altText: altText,
        findingsCount: res.data.length,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      })

      setShowImageAuditBox(false)
      setSelectedImageFile(null)
      setImagePreview(null)
      setAltText('')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Image audit failed')
      console.error(err)
    } finally {
      setIsAuditingImage(false)
    }
  }

  // Export Findings as CSV or JSON
  const handleExport = async (format) => {
    try {
      const res = await api.get(
        `/workspaces/${user.workspace_id}/drafts/${draftId}/review/export?format=${format}`,
        { responseType: format === 'csv' ? 'blob' : 'json' }
      )

      if (format === 'csv') {
        const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `brandguard_audit_${draft.title.replace(/\s+/g, '_')}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        toast.success('CSV Audit Report downloaded')
      } else {
        const jsonStr = JSON.stringify(res.data, null, 2)
        const blob = new Blob([jsonStr], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `brandguard_audit_${draft.title.replace(/\s+/g, '_')}.json`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        toast.success('JSON Audit Report downloaded')
      }
    } catch (err) {
      toast.error('Failed to export report')
      console.error(err)
    }
  }

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'error':
        return 'bg-rose-50 text-rose-700 border-rose-200'
      case 'warning':
        return 'bg-amber-50 text-amber-700 border-amber-200'
      default:
        return 'bg-sky-50 text-sky-700 border-sky-200'
    }
  }

  if (loading) {
    return (
      <div className="py-24 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-brand-500 border-t-transparent mb-3" />
        <p className="text-gray-500 font-medium text-sm">Analyzing draft against brand governance guidelines...</p>
      </div>
    )
  }

  if (!draft) {
    return <div className="py-24 text-center text-gray-500">Draft not found.</div>
  }

  // Filtered Findings Calculation
  const filteredFindings = findings.filter((f) => {
    if (severityFilter !== 'all' && f.severity !== severityFilter) return false
    if (categoryFilter !== 'all' && f.category !== categoryFilter) return false
    if (statusFilter !== 'all' && f.status !== statusFilter) return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const textMatch = f.text_highlight?.toLowerCase().includes(q)
      const explMatch = f.explanation?.toLowerCase().includes(q)
      const sourceMatch = f.guideline_source?.toLowerCase().includes(q)
      const suggMatch = f.suggestion?.toLowerCase().includes(q)
      if (!textMatch && !explMatch && !sourceMatch && !suggMatch) return false
    }
    return true
  })

  const openFindingsCount = findings.filter(f => f.status === 'open').length
  const aiFindingsCount = findings.filter(f => f.is_ai_generated).length
  const ruleFindingsCount = findings.filter(f => !f.is_ai_generated).length

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto px-2 sm:px-4">
      {/* Top Header & Workflow Bar */}
      <div className="bg-white rounded-2xl p-4 sm:p-6 border border-gray-200/80 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-start gap-3">
            <button
              onClick={() => navigate('/drafts')}
              className="p-2 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors text-gray-600 mt-0.5"
              title="Back to drafts"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-lg sm:text-xl font-bold text-gray-900 tracking-tight">{draft.title}</h1>
                <span className={`capitalize px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                  draft.status === 'approved' 
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                    : draft.status === 'changes_requested'
                    ? 'bg-rose-50 text-rose-700 border-rose-200'
                    : 'bg-amber-50 text-amber-700 border-amber-200'
                }`}>
                  {draft.status.replace('_', ' ')}
                </span>
                <span className="capitalize px-2 py-0.5 rounded text-[11px] font-medium bg-gray-100 text-gray-600 border border-gray-200">
                  {draft.content_type?.replace('_', ' ')}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Last reviewed • {draft.content.split(/\s+/).filter(Boolean).length} words • {findings.length} total governance observations
              </p>
            </div>
          </div>

          {/* Action Toolbar */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Revision History Modal Trigger */}
            <button
              onClick={() => setShowHistory(true)}
              className="px-3 py-2 border border-gray-200 rounded-xl text-xs font-semibold text-gray-700 bg-white hover:bg-gray-50 transition-colors flex items-center gap-1.5 shadow-2xs"
            >
              <History className="w-3.5 h-3.5 text-brand-600" />
              <span>Versions</span>
            </button>

            {/* Export Dropdown / Buttons */}
            <div className="flex items-center rounded-xl border border-gray-200 bg-white p-0.5 shadow-2xs">
              <button
                onClick={() => handleExport('csv')}
                className="px-2.5 py-1.5 text-xs font-medium text-gray-700 hover:text-brand-600 hover:bg-gray-50 rounded-lg flex items-center gap-1 transition-colors"
                title="Download CSV Audit Report"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600" />
                <span>CSV</span>
              </button>
              <div className="h-4 w-px bg-gray-200" />
              <button
                onClick={() => handleExport('json')}
                className="px-2.5 py-1.5 text-xs font-medium text-gray-700 hover:text-brand-600 hover:bg-gray-50 rounded-lg flex items-center gap-1 transition-colors"
                title="Download JSON Audit Report"
              >
                <FileCode className="w-3.5 h-3.5 text-sky-600" />
                <span>JSON</span>
              </button>
            </div>

            {/* Re-Audit Button */}
            <button
              onClick={handleReReview}
              disabled={reReviewing}
              className="px-3.5 py-2 border border-brand-200 rounded-xl text-xs font-semibold text-brand-700 bg-brand-50/60 hover:bg-brand-100/70 transition-colors flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reReviewing ? 'animate-spin text-brand-600' : ''}`} />
              <span>{reReviewing ? 'Auditing...' : 'Re-Run Check'}</span>
            </button>

            {/* Reviewer Workflow Actions */}
            {user?.role !== 'creator' && (
              <>
                <button
                  onClick={() => handleUpdateDraftStatus('changes_requested')}
                  className="px-3.5 py-2 bg-rose-50 text-rose-700 border border-rose-200 rounded-xl text-xs font-semibold hover:bg-rose-100 transition-colors"
                >
                  Request Changes
                </button>
                <button
                  onClick={() => handleUpdateDraftStatus('approved')}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-semibold hover:bg-emerald-700 transition-colors shadow-xs flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Approve</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* AI & Rule Transparency Summary Banner */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-3 border-t border-gray-100 text-xs">
          <div className="bg-gray-50 rounded-xl p-2.5 border border-gray-100 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-500" />
            <div>
              <span className="text-gray-400 block text-[10px] font-bold uppercase">Open Issues</span>
              <span className="font-bold text-gray-800">{openFindingsCount}</span>
            </div>
          </div>
          <div className="bg-purple-50/60 rounded-xl p-2.5 border border-purple-100 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-600" />
            <div>
              <span className="text-purple-700 block text-[10px] font-bold uppercase">AI Evaluated</span>
              <span className="font-bold text-purple-900">{aiFindingsCount} flags</span>
            </div>
          </div>
          <div className="bg-emerald-50/60 rounded-xl p-2.5 border border-emerald-100 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <div>
              <span className="text-emerald-700 block text-[10px] font-bold uppercase">Rule Engine</span>
              <span className="font-bold text-emerald-900">{ruleFindingsCount} flags</span>
            </div>
          </div>
          <div className="bg-blue-50/60 rounded-xl p-2.5 border border-blue-100 flex items-center gap-2">
            <Check className="w-4 h-4 text-blue-600" />
            <div>
              <span className="text-blue-700 block text-[10px] font-bold uppercase">Accepted Fixes</span>
              <span className="font-bold text-blue-900">{findings.filter(f => f.status === 'accepted').length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Review Workspace: Two Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (Content, Visual Asset Audit, Comments) */}
        <div className="lg:col-span-6 space-y-6">
          {/* Submitted Content Display */}
          <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-200/80 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b pb-2.5">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                Submitted Content Body
              </span>
              <span className="text-xs text-gray-400 font-mono">
                {draft.content.length} characters
              </span>
            </div>

            <div className="bg-gray-50/80 rounded-xl p-4 sm:p-5 border border-gray-100 text-gray-800 text-sm leading-relaxed whitespace-pre-wrap font-sans selection:bg-brand-100">
              {draft.content}
            </div>
          </div>

          {/* Image & Visual Asset Compliance Module */}
          <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-purple-50 text-purple-600 border border-purple-100">
                  <ImageIcon className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-gray-900">Visual & Image Governance</h3>
                  <p className="text-[11px] text-gray-400">WCAG AA Alt-Text, Logo Isolation, Color Palette</p>
                </div>
              </div>
              <button
                onClick={() => setShowImageAuditBox(!showImageAuditBox)}
                className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-700 transition-colors"
              >
                {showImageAuditBox ? 'Hide Panel' : '+ Audit Visual Asset'}
              </button>
            </div>

            {/* Audited Asset Review Card */}
            {lastAuditedAsset && (
              <div className="p-3.5 bg-gradient-to-br from-purple-50/80 to-blue-50/60 border border-purple-200/90 rounded-xl space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3 h-3 text-purple-600" />
                    Last Audited Visual Asset
                  </span>
                  <span className="text-[10px] text-gray-400 font-mono">{lastAuditedAsset.timestamp}</span>
                </div>

                <div className="flex items-center gap-3 bg-white p-2.5 rounded-lg border border-purple-100">
                  {lastAuditedAsset.preview ? (
                    <img
                      src={lastAuditedAsset.preview}
                      alt={lastAuditedAsset.altText || 'Audited asset'}
                      className="w-16 h-16 object-cover rounded-lg border border-gray-200 flex-shrink-0 shadow-2xs"
                    />
                  ) : (
                    <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <ImageIcon className="w-6 h-6 text-purple-600" />
                    </div>
                  )}
                  <div className="min-w-0 flex-1 text-xs space-y-1">
                    <p className="font-bold text-gray-900 truncate">{lastAuditedAsset.name}</p>
                    <p className="text-[11px] text-gray-500">
                      {lastAuditedAsset.size ? `${lastAuditedAsset.size} KB • ` : ''}
                      <span className="font-semibold text-purple-700">{lastAuditedAsset.findingsCount} findings generated</span>
                    </p>
                    <p className="text-[11px] text-gray-600 truncate">
                      <strong>Alt-Text:</strong> {lastAuditedAsset.altText ? `"${lastAuditedAsset.altText}"` : <span className="text-rose-500 italic">None provided (WCAG error)</span>}
                    </p>
                  </div>
                </div>

                {/* Quick-filter buttons */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="text-[10px] text-gray-400 font-semibold uppercase">Filter Findings:</span>
                  <button
                    type="button"
                    onClick={() => setCategoryFilter('visual')}
                    className={`px-2 py-0.5 text-[11px] rounded-md border font-medium transition-colors ${
                      categoryFilter === 'visual'
                        ? 'bg-purple-600 text-white border-purple-600'
                        : 'bg-white text-purple-800 border-purple-200 hover:bg-purple-50'
                    }`}
                  >
                    Visual Rules
                  </button>
                  <button
                    type="button"
                    onClick={() => setCategoryFilter('accessibility')}
                    className={`px-2 py-0.5 text-[11px] rounded-md border font-medium transition-colors ${
                      categoryFilter === 'accessibility'
                        ? 'bg-amber-600 text-white border-amber-600'
                        : 'bg-white text-amber-800 border-amber-200 hover:bg-amber-50'
                    }`}
                  >
                    WCAG Accessibility
                  </button>
                  {categoryFilter !== 'all' && (
                    <button
                      type="button"
                      onClick={() => setCategoryFilter('all')}
                      className="text-[11px] text-gray-400 hover:text-gray-700 underline ml-auto"
                    >
                      Clear Filter
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Expandable Image Upload & Audit Box */}
            {showImageAuditBox && (
              <form onSubmit={handleRunImageAudit} className="mt-3 p-4 bg-gray-50/80 rounded-xl border border-gray-200 space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Upload Graphic or Campaign Image</label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageFileChange}
                    className="block w-full text-xs text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100 border border-gray-200 rounded-lg p-1 bg-white"
                  />
                </div>

                {imagePreview && (
                  <div className="flex items-center gap-3 p-2 bg-white rounded-lg border border-gray-200">
                    <img src={imagePreview} alt="Preview" className="w-16 h-16 object-cover rounded-md border" />
                    <div className="text-xs">
                      <p className="font-semibold text-gray-800">{selectedImageFile?.name}</p>
                      <p className="text-gray-400 text-[11px]">{(selectedImageFile?.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                )}

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-semibold text-gray-700">Alternative Text (Alt-Text)</label>
                    <span className={`text-[10px] font-mono ${altText.length >= 10 ? 'text-emerald-600 font-bold' : 'text-amber-600'}`}>
                      {altText.length}/10 chars min (WCAG AA)
                    </span>
                  </div>
                  <input
                    type="text"
                    value={altText}
                    onChange={(e) => setAltText(e.target.value)}
                    placeholder="e.g. BrandGuard AI dashboard showcasing verified real-time claim flags"
                    className="w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-2 focus:ring-brand-500 bg-white"
                  />
                </div>

                <div className="flex justify-end pt-1">
                  <button
                    type="submit"
                    disabled={isAuditingImage}
                    className="px-4 py-2 bg-brand-600 text-white rounded-lg text-xs font-semibold hover:bg-brand-700 disabled:opacity-50 flex items-center gap-1.5 transition-colors shadow-2xs"
                  >
                    {isAuditingImage ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <UploadCloud className="w-3.5 h-3.5" />}
                    <span>{isAuditingImage ? 'Auditing Visual Asset...' : 'Run Visual Compliance Audit'}</span>
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Collaborative Discussion & Audit Log feed */}
          <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-200/80 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-brand-600" />
              <span>Reviewer Discussion & Change Requests</span>
            </h3>

            {comments.length === 0 ? (
              <p className="text-xs text-gray-400 py-3 italic">
                No discussion comments on this draft yet.
              </p>
            ) : (
              <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                {comments.map((c) => (
                  <div key={c.id} className="bg-gray-50/80 rounded-xl p-3 text-xs border border-gray-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-gray-800">Team Note</span>
                      <span className="text-gray-400 text-[10px]">{new Date(c.created_at).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed">{c.content}</p>
                  </div>
                ))}
              </div>
            )}

            <form onSubmit={handleAddComment} className="flex gap-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add reviewer notes or requested revisions..."
                className="flex-1 px-3 py-2 border rounded-xl text-xs outline-none focus:ring-2 focus:ring-brand-500 bg-gray-50/50"
              />
              <button
                type="submit"
                disabled={commentSubmitting}
                className="px-3.5 py-2 bg-brand-600 text-white rounded-xl text-xs font-semibold hover:bg-brand-700 disabled:opacity-50 flex items-center gap-1 shadow-2xs"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Post</span>
              </button>
            </form>
          </div>
        </div>

        {/* Right Column (Explained Findings with Interactive Filtering & Transparency) */}
        <div className="lg:col-span-6 space-y-4">
          {/* Findings Filter Bar */}
          <div className="bg-white rounded-2xl p-4 border border-gray-200/80 shadow-xs space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <h2 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-brand-600" />
                <span>Explained Findings ({filteredFindings.length} of {findings.length})</span>
              </h2>
              <div className="flex items-center gap-1.5 text-[11px] text-gray-500">
                <span className="inline-block w-2 h-2 rounded-full bg-rose-500" />
                <span>{openFindingsCount} Open</span>
              </div>
            </div>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Filter findings by keyword, rule, or explanation..."
                className="w-full pl-8 pr-3 py-1.5 border border-gray-200 rounded-xl text-xs outline-none focus:ring-2 focus:ring-brand-500 bg-gray-50/50"
              />
            </div>

            {/* Filter Pills */}
            <div className="grid grid-cols-3 gap-2 text-xs">
              {/* Severity Filter */}
              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase block mb-1">Severity</label>
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-xs bg-white text-gray-700 outline-none"
                >
                  <option value="all">All Severities</option>
                  <option value="error">Error</option>
                  <option value="warning">Warning</option>
                  <option value="info">Info</option>
                </select>
              </div>

              {/* Category Filter */}
              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase block mb-1">Category</label>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-xs bg-white text-gray-700 outline-none"
                >
                  <option value="all">All Categories</option>
                  <option value="terminology">Terminology</option>
                  <option value="claim">Claims</option>
                  <option value="tone">Tone</option>
                  <option value="visual">Visual</option>
                  <option value="accessibility">Accessibility</option>
                </select>
              </div>

              {/* Status Filter */}
              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase block mb-1">Status</label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-xs bg-white text-gray-700 outline-none"
                >
                  <option value="all">All Statuses</option>
                  <option value="open">Open</option>
                  <option value="accepted">Accepted</option>
                  <option value="rejected">Dismissed</option>
                </select>
              </div>
            </div>
          </div>

          {/* Findings List */}
          {filteredFindings.length === 0 ? (
            <div className="bg-emerald-50/80 border border-emerald-200 rounded-2xl p-8 text-center space-y-2">
              <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
              <h3 className="text-sm font-bold text-emerald-900">No issues match current filters!</h3>
              <p className="text-xs text-emerald-700">
                All content in this view meets enterprise brand guidelines.
              </p>
            </div>
          ) : (
            <div className="space-y-3.5">
              {filteredFindings.map((f) => {
                const isResolved = f.status !== 'open'
                return (
                  <div
                    key={f.id}
                    className={`bg-white rounded-2xl p-5 border shadow-xs transition-all ${
                      isResolved
                        ? 'opacity-65 border-gray-200 bg-gray-50/60'
                        : 'border-gray-200/90 hover:border-brand-300'
                    }`}
                  >
                    {/* Header Row: Severity + Category + AI Transparency Badge */}
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
                      <div className="flex flex-wrap items-center gap-1.5">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${getSeverityStyle(
                            f.severity
                          )}`}
                        >
                          {f.severity}
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-100 text-gray-700 capitalize">
                          {f.category}
                        </span>

                        {/* AI-use Disclosure Badge with Visual Indicator */}
                        {f.is_ai_generated ? (
                          <span
                            className="px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-50 text-purple-700 border border-purple-200 flex items-center gap-1"
                            title="Detected via AI LLM & semantic reasoning against retrieved brand guidelines"
                          >
                            <Sparkles className="w-3 h-3 text-purple-600" />
                            <span>AI Evaluated</span>
                          </span>
                        ) : (
                          <span
                            className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1"
                            title="Deterministic rule match against approved brand kit parameters"
                          >
                            <ShieldCheck className="w-3 h-3 text-emerald-600" />
                            <span>Deterministic Rule</span>
                          </span>
                        )}
                      </div>

                      {f.status !== 'open' && (
                        <span className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                          f.status === 'accepted' ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-200 text-gray-700'
                        }`}>
                          {f.status}
                        </span>
                      )}
                    </div>

                    {/* Flagged Snippet */}
                    {f.text_highlight && (
                      <div className="mb-2">
                        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Flagged Context: </span>
                        <code className="text-xs bg-rose-50 text-rose-800 px-1.5 py-0.5 rounded font-mono border border-rose-100 font-medium">
                          "{f.text_highlight}"
                        </code>
                      </div>
                    )}

                    {/* Explanation */}
                    <p className="text-xs text-gray-800 leading-relaxed mb-3">
                      {f.explanation}
                    </p>

                    {/* Grounded Guideline Citation */}
                    {f.guideline_source && (
                      <div className="mb-3 bg-brand-50/60 border border-brand-100 rounded-xl p-2.5 flex items-start gap-2 text-xs text-brand-900">
                        <BookOpen className="w-4 h-4 text-brand-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold block text-[10px] text-brand-700 uppercase tracking-wider">
                            Cited Guideline Source
                          </span>
                          <span className="text-xs text-brand-800 font-medium">
                            {f.guideline_source}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Suggestion Fix */}
                    {f.suggestion && (
                      <div className="mb-3 bg-emerald-50/60 border border-emerald-200 rounded-xl p-2.5 text-xs text-emerald-950 space-y-1">
                        <span className="font-bold block text-[10px] text-emerald-800 uppercase tracking-wider">
                          Proposed Fix (Creator Control)
                        </span>
                        <p className="font-sans text-emerald-900 font-medium leading-relaxed">
                          {f.suggestion}
                        </p>
                      </div>
                    )}

                    {/* Action buttons (Accept/Dismiss) */}
                    {f.status === 'open' && f.suggestion && (
                      <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-100">
                        <button
                          onClick={() => handleUpdateFindingStatus(f.id, 'rejected')}
                          className="px-2.5 py-1 text-xs font-semibold text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg flex items-center gap-1 transition-colors"
                        >
                          <X className="w-3.5 h-3.5 text-gray-400" />
                          <span>Dismiss</span>
                        </button>
                        <button
                          onClick={() => handleUpdateFindingStatus(f.id, 'accepted')}
                          className="px-3 py-1 text-xs font-semibold bg-brand-600 text-white rounded-lg hover:bg-brand-700 flex items-center gap-1 shadow-2xs transition-colors"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>Accept Fix</span>
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

      {/* Revision History Modal */}
      <VersionHistory
        draftId={draftId}
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
      />
    </div>
  )
}
