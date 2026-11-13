import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { ArrowLeft, AlertTriangle, CheckCircle2, Zap } from 'lucide-react'
import toast from 'react-hot-toast'

const CONTENT_TYPES = [
  { value: 'social_post', label: 'Social Post', hint: 'LinkedIn, X, Instagram' },
  { value: 'ad', label: 'Ad Copy', hint: 'Banner, Display, PPC' },
  { value: 'email', label: 'Email', hint: 'Newsletter, Nurture' },
  { value: 'blog', label: 'Blog / Article', hint: 'Editorial, Thought leadership' },
  { value: 'press_release', label: 'Press Release', hint: 'Media & investor comms' },
  { value: 'other', label: 'Other', hint: 'Landing page, misc copy' },
]

export default function CreateDraft() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [contentType, setContentType] = useState('social_post')
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)

  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0

  const handleQuickSample = () => {
    setTitle('Q4 Platform Launch — Social Copy')
    setContentType('social_post')
    setContent(
      "Introducing Brand Guard. We are recognized as the #1 in India brand protection solution. " +
      "Our software is 100% safe, completely guaranteed, and unbeatable across the sector. " +
      "Don't waste money on overpriced legacy alternatives when you can get cheap software right here. " +
      "Brand accent styled in #FF0055."
    )
    toast('Loaded flagged copy — 6 violations expected', { icon: '⚠️' })
  }

  const handleCompliantSample = () => {
    setTitle('Enterprise Governance Announcement')
    setContentType('social_post')
    setContent(
      "We are proud to present BrandGuard AI by Innovex. " +
      "Engineered for enterprise marketing and communications teams to maintain brand integrity, tone consistency, and ASCI regulatory compliance. " +
      "With over 500+ enterprise clients onboarded worldwide, our platform offers proven governance at scale. " +
      "Verified primary palette: #1E40AF and #2563EB. " +
      "Schedule a consultation with our compliance specialists today."
    )
    toast.success('Loaded compliant copy — passes all checks')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!content.trim()) {
      toast.error('Content cannot be empty')
      return
    }
    try {
      setLoading(true)
      let workspaceId = user?.workspace_id
      if (!workspaceId) {
        const wsRes = await api.get('/workspaces/')
        if (wsRes.data?.length > 0) {
          workspaceId = wsRes.data[0].id
        } else {
          const newWs = await api.post('/workspaces/', {
            name: `${user.full_name}'s Workspace`,
            description: 'Brand governance workspace',
          })
          workspaceId = newWs.data.id
        }
      }
      const draftRes = await api.post(`/workspaces/${workspaceId}/drafts/`, {
        title, content, content_type: contentType,
      })
      const draftId = draftRes.data.id
      try {
        await api.post(`/workspaces/${workspaceId}/drafts/${draftId}/review/`)
        toast.success('Audit running — findings loading')
      } catch {
        toast.error('Review triggered with warnings')
      }
      navigate(`/drafts/${draftId}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create draft')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-5">

      {/* Top bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/drafts')}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 transition-colors font-medium"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Drafts
        </button>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleQuickSample}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-amber-700 bg-amber-50 border border-amber-200 rounded-lg hover:bg-amber-100 transition-colors"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            Load Flagged
          </button>
          <button
            type="button"
            onClick={handleCompliantSample}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            Load Compliant
          </button>
        </div>
      </div>

      {/* Main card */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
        <div className="px-7 pt-6 pb-5 border-b border-slate-100">
          <h1 className="text-base font-semibold text-slate-900">New compliance audit</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Rules engine + semantic AI check claims, terminology, and palette — before publication.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="px-7 py-6 space-y-5">

          {/* Title */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700 block">
              Title <span className="text-slate-400 font-normal">— internal reference</span>
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Diwali Sale — Instagram caption v2"
              className="w-full px-3.5 py-2.5 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-300 focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none transition-all"
            />
          </div>

          {/* Content type — pill selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700 block">Content format</label>
            <div className="flex flex-wrap gap-2">
              {CONTENT_TYPES.map((ct) => (
                <button
                  key={ct.value}
                  type="button"
                  onClick={() => setContentType(ct.value)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    contentType === ct.value
                      ? 'bg-brand-600 text-white border-brand-600 shadow-xs'
                      : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                  title={ct.hint}
                >
                  {ct.label}
                </button>
              ))}
            </div>
            <p className="text-[11px] text-slate-400">
              {CONTENT_TYPES.find(c => c.value === contentType)?.hint}
            </p>
          </div>

          {/* Content body */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-700 block">Content</label>
              <span className={`text-[11px] font-mono tabular-nums ${wordCount > 500 ? 'text-amber-600' : 'text-slate-400'}`}>
                {wordCount} {wordCount === 1 ? 'word' : 'words'}
              </span>
            </div>
            <textarea
              required
              rows={9}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste the copy here — ad headline, social caption, email body, press release..."
              className="w-full px-3.5 py-3 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-300 focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none transition-all resize-none leading-relaxed"
            />
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between pt-2 border-t border-slate-100">
            <p className="text-[11px] text-slate-400 max-w-xs leading-relaxed">
              Findings are suggestions only. No changes are made without your explicit approval.
            </p>
            <div className="flex items-center gap-2.5">
              <button
                type="button"
                onClick={() => navigate('/drafts')}
                className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !content.trim()}
                className="flex items-center gap-2 px-5 py-2 bg-brand-600 text-white rounded-lg text-xs font-semibold hover:bg-brand-700 transition-colors disabled:opacity-40 shadow-xs"
              >
                <Zap className="w-3.5 h-3.5" />
                {loading ? 'Running audit…' : 'Run audit'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
