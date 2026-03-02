// src/pages/Login.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Boxes, Eye, EyeOff } from 'lucide-react'
import { api } from '../services/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [showPw,   setShowPw]   = useState(false)
  const [loading,  setLoading]  = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) { toast.error('Please enter email and password'); return }
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { email, password })
      setAuth(data.access_token, data.refresh_token, data.user)
      toast.success(`Welcome back, ${data.user.full_name || data.user.username}!`)
      navigate('/')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Invalid credentials')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Grid background */}
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{
          backgroundImage: `linear-gradient(rgba(217,119,6,0.08) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(217,119,6,0.08) 1px, transparent 1px)`,
          backgroundSize: '48px 48px',
          maskImage: 'radial-gradient(ellipse 70% 70% at 50% 50%, black, transparent)',
        }}
      />
      {/* Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-amber/5 rounded-full blur-3xl pointer-events-none" />

      {/* Logo */}
      <div className="flex items-center gap-3 mb-10 animate-fade-up">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-amber to-amber-light flex items-center justify-center shadow-lg shadow-amber/20">
          <Boxes size={20} className="text-black" />
        </div>
        <h1 className="font-serif font-black text-3xl">
          Stock<span className="text-amber">metry</span>
        </h1>
      </div>

      {/* Card */}
      <div className="w-full max-w-md bg-[#111118] border border-white/8 rounded-2xl p-8 shadow-2xl shadow-black/60 animate-fade-up" style={{ animationDelay: '0.1s' }}>
        <h2 className="font-serif font-bold text-xl mb-1">Sign in to your account</h2>
        <p className="text-sm text-white/40 mb-7">AI-powered inventory intelligence platform</p>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="text-[10px] font-mono text-white/40 uppercase tracking-wider block mb-1.5">Email or Username</label>
            <input
              className="input"
              placeholder="admin@stockmetry.io"
              value={email} onChange={e => setEmail(e.target.value)}
              autoComplete="username"
            />
          </div>
          <div>
            <label className="text-[10px] font-mono text-white/40 uppercase tracking-wider block mb-1.5">Password</label>
            <div className="relative">
              <input
                className="input pr-10"
                type={showPw ? 'text' : 'password'}
                placeholder="••••••••"
                value={password} onChange={e => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button type="button" onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors">
                {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading}
            className="btn-primary w-full justify-center mt-2 py-3 text-base">
            {loading ? 'Signing in...' : 'Sign In →'}
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-white/7">
          <p className="text-[10px] font-mono text-white/30 mb-3">DEMO ACCOUNTS — contact your admin for credentials</p>
          <div className="grid grid-cols-3 gap-2">
            {[
              { role: 'Admin',   color: '#6366f1', desc: 'Full access' },
              { role: 'Manager', color: '#10b981', desc: 'Analytics + Products' },
              { role: 'Analyst', color: '#f59e0b', desc: 'Read-only analytics' },
            ].map(r => (
              <div key={r.role} className="bg-[#17171f] rounded-lg p-2.5 text-center border border-white/5">
                <div className="w-7 h-7 rounded-full mx-auto mb-1.5 flex items-center justify-center text-xs font-bold text-black" style={{ background: r.color }}>
                  {r.role[0]}
                </div>
                <p className="text-xs font-semibold">{r.role}</p>
                <p className="text-[9px] text-white/35 mt-0.5">{r.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="mt-6 text-[10px] font-mono text-white/20 animate-fade-up" style={{ animationDelay: '0.2s' }}>
        Stockmetry v1.0 · FastAPI · PostgreSQL · XGBoost · Claude AI
      </p>
    </div>
  )
}
