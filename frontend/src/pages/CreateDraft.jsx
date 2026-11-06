import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { Sparkles, FileText, ArrowLeft, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function CreateDraft() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [contentType, setContentType] = useState('social_post')
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)

  const handleQuickSample = () => {
    setTitle('Launch Campaign Social Announcement')
    setContentType('social_post')
    setContent(
      "🚀 Introducing Brand Guard! We are the #1 in India brand protection tool. " +
      "Our software is 100% safe, completely guaranteed, and unbeatable. " +
      "Don't waste money on overpriced alternatives when you can get cheap software right here. " +
      "Brand theme updated to #FF0055."
    )
    toast.success('Sample draft loaded with typical ASCI & brand guideline violations!')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!content.trim()) {
      toast.error('Draft content cannot be empty')
      return
    }

    try {
      setLoading(true)

      // Ensure user has a workspace
      let workspaceId = user?.workspace_id
      if (!workspaceId) {
        const wsRes = await api.get('/workspaces/')
        if (wsRes.data && wsRes.data.length > 0) {
          workspaceId = wsRes.data[0].id
        } else {
          const newWs = await api.post('/workspaces/', {
            name: `${user.full_name}'s Workspace`,
            description: 'Brand governance workspace',
          })
          workspaceId = newWs.data.id
        }
      }

      // 1. Create draft
      const draftRes = await api.post(`/workspaces/${workspaceId}/drafts/`, {
        title,
        content,
        content_type: contentType,
      })
      const draftId = draftRes.data.id

      // 2. Automatically trigger review
      try {
        await api.post(`/workspaces/${workspaceId}/drafts/${draftId}/review/`)
        toast.success('Draft created and brand compliance review initiated!')
      } catch (revErr) {
        // If no brand kit, warn user
        toast.error(revErr.response?.data?.detail || 'Review triggered with warnings.')
      }

      navigate(`/drafts/${draftId}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create draft')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/drafts')}
          className="text-sm font-medium text-gray-500 hover:text-gray-700 flex items-center gap-1.5"
        >
          <ArrowLeft className="w-4 h-4" /> Back to drafts
        </button>
        <button
          type="button"
          onClick={handleQuickSample}
          className="px-3 py-1.5 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg text-xs font-semibold hover:bg-amber-100 transition-colors flex items-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5" /> Load Violative Sample (Demo)
        </button>
      </div>

      <div className="bg-white rounded-xl p-8 border border-gray-200 shadow-sm space-y-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="w-6 h-6 text-brand-600" />
            Submit Draft for Pre-Publication Governance
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Our multi-engine pipeline verifies claims, terminology, tone rules, and brand colors in real-time.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Draft Title / Campaign
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Diwali Flash Sale - Ad Headline Copy"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Content Format
            </label>
            <select
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-brand-500 bg-white"
            >
              <option value="social_post">Social Media Post (LinkedIn / X / Instagram)</option>
              <option value="ad">Ad Copy / Banner Text</option>
              <option value="blog">Blog Post / Article</option>
              <option value="email">Marketing Email / Newsletter</option>
              <option value="other">General Website Copy / Landing Page</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-sm font-medium text-gray-700">
                Content Body
              </label>
              <span className="text-xs text-gray-400">
                {content.length} characters
              </span>
            </div>
            <textarea
              required
              rows={8}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste or write the draft content to evaluate against brand guidelines..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-brand-500 font-mono"
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-xs text-blue-800 space-y-1">
            <p className="font-semibold flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-blue-600" />
              Responsible AI Guarantee
            </p>
            <p>
              BrandGuard AI will flag discrepancies and propose corrections, but will <strong>never auto-apply changes</strong> without your explicit acceptance.
            </p>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={() => navigate('/drafts')}
              className="px-5 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {loading ? 'Evaluating Brand Safety...' : 'Run Governance Check'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
