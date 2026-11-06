import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  Palette, 
  Plus, 
  BookOpen, 
  CheckCircle, 
  XCircle, 
  Cpu, 
  Sparkles,
  HelpCircle,
  FileCheck
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function BrandKits() {
  const { user } = useAuth()
  const [brandKits, setBrandKits] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [indexingKitId, setIndexingKitId] = useState(null)

  // Form state
  const [name, setName] = useState('Acme Corp Brand Kit')
  const [guidelinesRaw, setGuidelinesRaw] = useState('')
  const [approvedTerms, setApprovedTerms] = useState('BrandGuard, AI-powered, NextGen')
  const [bannedTerms, setBannedTerms] = useState('cheap, 100% safe, #1 in India, guaranteed')
  const [toneRules, setToneRules] = useState('Professional, Empathetic, Clear, Honest, No hyperbole')
  const [approvedFacts, setApprovedFacts] = useState('Over 500+ enterprise clients, Founded in 2024, ISO-27001 certified')
  const [colorPalette, setColorPalette] = useState('#1E40AF, #2563EB, #F59E0B, #10B981')

  useEffect(() => {
    fetchBrandKits()
  }, [user])

  const fetchBrandKits = async () => {
    try {
      setLoading(true)
      if (user?.workspace_id) {
        const res = await api.get(`/workspaces/${user.workspace_id}/brand-kits/`)
        setBrandKits(res.data)
      } else {
        // Automatically ensure or prompt workspace
        const wsRes = await api.get('/workspaces/')
        if (wsRes.data && wsRes.data.length > 0) {
          const ws = wsRes.data[0]
          await api.post(`/workspaces/${ws.id}/join`)
          const kitsRes = await api.get(`/workspaces/${ws.id}/brand-kits/`)
          setBrandKits(kitsRes.data)
        }
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      if (!user?.workspace_id) {
        // create workspace first if none
        const ws = await api.post('/workspaces/', {
          name: `${user.full_name}'s Workspace`,
          description: 'Default brand governance workspace'
        })
        user.workspace_id = ws.data.id
      }

      const payload = {
        name,
        guidelines_raw: guidelinesRaw,
        terminology_approved: approvedTerms.split(',').map(s => s.trim()).filter(Boolean),
        terminology_banned: bannedTerms.split(',').map(s => s.trim()).filter(Boolean),
        tone_rules: toneRules.split(',').map(s => s.trim()).filter(Boolean),
        approved_facts: approvedFacts.split(',').map(s => s.trim()).filter(Boolean),
        color_palette: colorPalette.split(',').map(s => s.trim()).filter(Boolean),
      }

      await api.post(`/workspaces/${user.workspace_id}/brand-kits/`, payload)
      toast.success('Brand Kit created successfully!')
      setShowModal(false)
      fetchBrandKits()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create brand kit')
    }
  }

  const handleIndex = async (kitId) => {
    try {
      setIndexingKitId(kitId)
      const res = await api.post(`/workspaces/${user.workspace_id}/brand-kits/${kitId}/index`)
      toast.success(res.data.message || 'Guidelines indexed successfully!')
      fetchBrandKits()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Indexing failed')
    } finally {
      setIndexingKitId(null)
    }
  }

  const loadDemoKit = () => {
    setName('Innovex / Inkloom Official Brand Kit')
    setGuidelinesRaw(
      "1. TONE AND VOICE\n" +
      "We communicate with clarity, empathy, and technical authority. Never use hype words or exaggerated claims. Avoid informal slang.\n\n" +
      "2. TERMINOLOGY\n" +
      "Always write 'BrandGuard AI' with camel-casing and a space before AI. Never refer to ourselves as 'cheap software'. Use 'enterprise-grade' instead.\n\n" +
      "3. CLAIM REGULATION (ASCI Compliance)\n" +
      "Do not state '#1 in India' or claim '100% error-free' without third-party audited proof. Every performance claim must be verifiable against our certified facts.\n\n" +
      "4. VISUAL IDENTITY\n" +
      "Our primary brand color is Deep Blue (#1E40AF) with vibrant accent blue (#2563EB). Do not use unapproved neon hues."
    )
    setApprovedTerms('BrandGuard AI, Inkloom, Innovex, enterprise-grade, explainable AI')
    setBannedTerms('cheap, #1 in India, 100% safe, guaranteed, unbeatable, miraculous')
    setToneRules('Authoritative, Empathic, Transparent, Modest, Accurate')
    setApprovedFacts('Founded in 2024, Reviewed over 10,000 drafts, ASCI guideline compliant, ISO 27001 certified')
    setColorPalette('#1E40AF, #2563EB, #10B981, #F59E0B')
    toast.success('Sample enterprise brand kit populated!')
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Palette className="w-7 h-7 text-brand-600" />
            Brand Kits & Guidelines
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Centralized source of truth: terminology, claims, tone rules, and color palettes.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors shadow-sm flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Create Brand Kit
        </button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-gray-400">Loading brand kits...</div>
      ) : brandKits.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center border border-dashed border-gray-300 max-w-xl mx-auto space-y-4">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto" />
          <h3 className="text-lg font-medium text-gray-900">No brand kit defined yet</h3>
          <p className="text-sm text-gray-500">
            A Brand Kit is required to run compliance checks. Upload rules, banned words, and approved facts.
          </p>
          <button
            onClick={() => {
              loadDemoKit()
              setShowModal(true)
            }}
            className="px-4 py-2 bg-brand-50 text-brand-700 border border-brand-200 rounded-lg text-sm font-medium hover:bg-brand-100 transition-colors inline-flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Load Sample Brand Kit
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {brandKits.map((kit) => (
            <div key={kit.id} className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm space-y-5">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{kit.name}</h3>
                  <p className="text-xs text-gray-400 mt-0.5">
                    Updated {new Date(kit.updated_at).toLocaleDateString()}
                  </p>
                </div>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    kit.is_indexed
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}
                >
                  {kit.is_indexed ? '✓ RAG Indexed' : 'Needs Indexing'}
                </span>
              </div>

              {/* Rules summary chips */}
              <div className="space-y-3 text-xs">
                <div>
                  <span className="font-semibold text-gray-600 block mb-1">Approved Terms:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {kit.terminology_approved?.map((t, idx) => (
                      <span key={idx} className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="font-semibold text-gray-600 block mb-1">Banned Terms (Flags):</span>
                  <div className="flex flex-wrap gap-1.5">
                    {kit.terminology_banned?.map((t, idx) => (
                      <span key={idx} className="bg-rose-50 text-rose-700 px-2 py-0.5 rounded">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="font-semibold text-gray-600 block mb-1">Approved Facts:</span>
                  <div className="text-gray-600 italic">
                    {kit.approved_facts?.length || 0} claims verified in repository
                  </div>
                </div>

                <div>
                  <span className="font-semibold text-gray-600 block mb-1">Brand Colors:</span>
                  <div className="flex gap-2 items-center">
                    {kit.color_palette?.map((hex, idx) => (
                      <div
                        key={idx}
                        className="w-6 h-6 rounded border border-gray-300 shadow-xs"
                        style={{ backgroundColor: hex }}
                        title={hex}
                      />
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-100 flex items-center justify-between">
                <button
                  onClick={() => handleIndex(kit.id)}
                  disabled={indexingKitId === kit.id}
                  className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5"
                >
                  <Cpu className="w-3.5 h-3.5 text-brand-600" />
                  {indexingKitId === kit.id ? 'Indexing Clauses...' : 'Re-index Guidelines'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Creation Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl my-8 space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h2 className="text-lg font-bold text-gray-900">Define Brand Governance Kit</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600 text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                onClick={loadDemoKit}
                className="text-xs text-brand-600 hover:text-brand-800 font-medium flex items-center gap-1"
              >
                <Sparkles className="w-3.5 h-3.5" /> Auto-fill Sample Brand Kit
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-sm">
              <div>
                <label className="block font-medium text-gray-700 mb-1">Brand Kit Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div>
                <label className="block font-medium text-gray-700 mb-1">
                  Full Brand Guidelines (Clauses / PDF text)
                </label>
                <textarea
                  rows={4}
                  value={guidelinesRaw}
                  onChange={(e) => setGuidelinesRaw(e.target.value)}
                  placeholder="Paste rules regarding voice, tone, legal claims, and positioning..."
                  className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-brand-500 font-mono text-xs"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Approved Terms (comma-separated)</label>
                  <input
                    type="text"
                    value={approvedTerms}
                    onChange={(e) => setApprovedTerms(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-brand-500 text-xs"
                  />
                </div>

                <div>
                  <label className="block font-medium text-gray-700 mb-1">Banned Terms (comma-separated)</label>
                  <input
                    type="text"
                    value={bannedTerms}
                    onChange={(e) => setBannedTerms(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-brand-500 text-xs text-rose-600"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-gray-700 mb-1">
                  Approved Factual Claims (For ASCI / claim verification)
                </label>
                <input
                  type="text"
                  value={approvedFacts}
                  onChange={(e) => setApprovedFacts(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-brand-500 text-xs"
                  placeholder="e.g. Over 500+ clients, Founded in 2024"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Tone Rules (comma-separated)</label>
                  <input
                    type="text"
                    value={toneRules}
                    onChange={(e) => setToneRules(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-brand-500 text-xs"
                  />
                </div>

                <div>
                  <label className="block font-medium text-gray-700 mb-1">Color Palette (Hex Codes)</label>
                  <input
                    type="text"
                    value={colorPalette}
                    onChange={(e) => setColorPalette(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-brand-500 text-xs"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border rounded-lg text-gray-600 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700"
                >
                  Save Brand Kit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
