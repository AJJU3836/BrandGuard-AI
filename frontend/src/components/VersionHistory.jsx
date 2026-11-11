import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { diffWords } from 'diff'
import {
  X,
  History,
  ChevronRight,
  Clock,
  FileText,
  Loader2,
  GitCompare,
  ArrowLeft,
  Zap,
} from 'lucide-react'
import toast from 'react-hot-toast'

/**
 * VersionHistory — modal component showing all content versions for a draft.
 *
 * Features:
 *  - Lists versions newest-first with timestamps
 *  - Click a version to view its full content
 *  - Select two versions to see a side-by-side word diff
 *  - Inline diff highlights: green = added, red = removed
 */
export default function VersionHistory({ draftId, isOpen, onClose }) {
  const { user } = useAuth()
  const [versions, setVersions] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedVersion, setSelectedVersion] = useState(null)
  const [compareMode, setCompareMode] = useState(false)
  const [compareA, setCompareA] = useState(null) // older
  const [compareB, setCompareB] = useState(null) // newer

  useEffect(() => {
    if (isOpen && draftId) {
      fetchVersions()
    }
  }, [isOpen, draftId])

  const fetchVersions = async () => {
    try {
      setLoading(true)
      const wsId = user?.workspace_id
      if (!wsId) return
      const res = await api.get(`/workspaces/${wsId}/drafts/${draftId}/versions`)
      setVersions(res.data)
      setSelectedVersion(null)
      setCompareA(null)
      setCompareB(null)
    } catch (err) {
      toast.error('Failed to load revision history')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectForCompare = (version) => {
    if (!compareA) {
      setCompareA(version)
    } else if (!compareB && version.id !== compareA.id) {
      // Ensure A is older (lower version_number)
      if (version.version_number < compareA.version_number) {
        setCompareB(compareA)
        setCompareA(version)
      } else {
        setCompareB(version)
      }
    } else {
      // Reset and start fresh
      setCompareA(version)
      setCompareB(null)
    }
  }

  const renderDiff = () => {
    if (!compareA || !compareB) return null

    const changes = diffWords(compareA.content, compareB.content)
    const additionsCount = changes.filter(part => part.added).length
    const deletionsCount = changes.filter(part => part.removed).length

    return (
      <div className="space-y-3 bg-gray-50/70 p-4 rounded-xl border border-gray-200">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
              <GitCompare className="w-4 h-4 text-brand-600" />
              <span>Comparing v{compareA.version_number} → v{compareB.version_number}</span>
            </h4>
            <div className="flex items-center gap-1.5 text-[11px] font-mono">
              <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold border border-emerald-200">
                +{additionsCount}
              </span>
              <span className="px-1.5 py-0.5 rounded bg-rose-100 text-rose-800 font-bold border border-rose-200">
                -{deletionsCount}
              </span>
            </div>
          </div>
          <button
            onClick={() => {
              setCompareA(null)
              setCompareB(null)
              setCompareMode(false)
            }}
            className="text-xs text-gray-500 hover:text-gray-700 underline font-medium"
          >
            Clear comparison
          </button>
        </div>

        <div className="flex gap-3 text-[11px] text-gray-600">
          <span className="flex items-center gap-1">
            <span className="inline-block w-3 h-3 rounded bg-rose-100 border border-rose-300" />
            <span>Removed from v{compareA.version_number}</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-3 h-3 rounded bg-emerald-100 border border-emerald-300" />
            <span>Added in v{compareB.version_number}</span>
          </span>
        </div>

        <div className="bg-white rounded-lg p-4 border border-gray-200 text-sm leading-relaxed whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">
          {changes.map((part, i) => {
            if (part.added) {
              return (
                <span
                  key={i}
                  className="bg-emerald-100 text-emerald-900 border-b-2 border-emerald-400 px-0.5 rounded-sm font-semibold"
                >
                  {part.value}
                </span>
              )
            }
            if (part.removed) {
              return (
                <span
                  key={i}
                  className="bg-rose-100 text-rose-900 line-through border-b-2 border-rose-400 px-0.5 rounded-sm"
                >
                  {part.value}
                </span>
              )
            }
            return <span key={i}>{part.value}</span>
          })}
        </div>
      </div>
    )
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[85vh] flex flex-col overflow-hidden border border-gray-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50/80">
          <div className="flex items-center gap-2.5">
            <History className="w-5 h-5 text-brand-600" />
            <h2 className="text-base font-bold text-gray-900">Revision History</h2>
            <span className="text-xs bg-brand-100 text-brand-700 font-semibold px-2 py-0.5 rounded-full">
              {versions.length} version{versions.length !== 1 ? 's' : ''}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-16 text-gray-400">
              <Loader2 className="w-5 h-5 animate-spin mr-2" />
              Loading revision history…
            </div>
          ) : versions.length === 0 ? (
            <div className="text-center py-16 text-gray-400 text-sm">
              No version history available yet.
            </div>
          ) : (
            <>
              {/* Compare mode toggle & Quick Compare */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs text-gray-500">
                  {compareMode
                    ? 'Select two versions to compare changes'
                    : 'Click a version to view its content'}
                </p>
                <div className="flex items-center gap-2">
                  {versions.length >= 2 && !compareMode && (
                    <button
                      onClick={() => {
                        setCompareMode(true)
                        // versions are newest first (index 0 is newest, index 1 is previous)
                        setCompareB(versions[0])
                        setCompareA(versions[1])
                        setSelectedVersion(null)
                      }}
                      className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100 flex items-center gap-1.5 transition-colors shadow-2xs"
                    >
                      <Zap className="w-3.5 h-3.5 text-amber-500" />
                      <span>Compare Latest vs Previous</span>
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setCompareMode(!compareMode)
                      setCompareA(null)
                      setCompareB(null)
                      setSelectedVersion(null)
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
                      compareMode
                        ? 'bg-brand-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <GitCompare className="w-3.5 h-3.5" />
                    {compareMode ? 'Exit Compare' : 'Compare Versions'}
                  </button>
                </div>
              </div>

              {/* Diff view */}
              {compareMode && compareA && compareB && renderDiff()}

              {/* Version list */}
              <div className="space-y-2">
                {versions.map((v) => {
                  const isSelected = selectedVersion?.id === v.id
                  const isCompareSelected =
                    compareA?.id === v.id || compareB?.id === v.id

                  return (
                    <div key={v.id}>
                      <button
                        onClick={() => {
                          if (compareMode) {
                            handleSelectForCompare(v)
                          } else {
                            setSelectedVersion(isSelected ? null : v)
                          }
                        }}
                        className={`w-full text-left px-4 py-3 rounded-xl border transition-all flex items-center justify-between group ${
                          isSelected || isCompareSelected
                            ? 'bg-brand-50 border-brand-300 shadow-sm'
                            : 'bg-white border-gray-200 hover:border-brand-200 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                              isSelected || isCompareSelected
                                ? 'bg-brand-600 text-white'
                                : 'bg-gray-100 text-gray-600 group-hover:bg-brand-100 group-hover:text-brand-700'
                            }`}
                          >
                            v{v.version_number}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-900">
                              {v.change_summary || `Version ${v.version_number}`}
                            </p>
                            <div className="flex items-center gap-1.5 text-[11px] text-gray-400 mt-0.5">
                              <Clock className="w-3 h-3" />
                              {new Date(v.created_at).toLocaleString()}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {compareMode && isCompareSelected && (
                            <span className="text-[10px] font-bold text-brand-600 bg-brand-100 px-1.5 py-0.5 rounded">
                              {compareA?.id === v.id ? 'A' : 'B'}
                            </span>
                          )}
                          {!compareMode && (
                            <ChevronRight
                              className={`w-4 h-4 text-gray-400 transition-transform ${
                                isSelected ? 'rotate-90' : ''
                              }`}
                            />
                          )}
                        </div>
                      </button>

                      {/* Expanded version content */}
                      {isSelected && !compareMode && (
                        <div className="mt-2 ml-11 bg-gray-50 rounded-lg p-4 border border-gray-200 text-sm text-gray-800 leading-relaxed whitespace-pre-wrap font-sans max-h-64 overflow-y-auto">
                          {v.content}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-gray-200 bg-gray-50/80 flex items-center justify-between">
          <p className="text-[11px] text-gray-400">
            Every draft edit and review creates a version snapshot automatically.
          </p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium hover:bg-gray-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
