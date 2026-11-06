import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import BrandKits from './pages/BrandKits'
import Drafts from './pages/Drafts'
import DraftReview from './pages/DraftReview'
import CreateDraft from './pages/CreateDraft'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>
  if (!user) return <Navigate to="/login" />
  return children
}

function App() {
  return (
    <AuthProvider>
      <Toaster position="top-right" />
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="brand-kits" element={<BrandKits />} />
          <Route path="drafts" element={<Drafts />} />
          <Route path="drafts/new" element={<CreateDraft />} />
          <Route path="drafts/:draftId" element={<DraftReview />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
