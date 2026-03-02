// src/pages/About.tsx
import { Boxes } from 'lucide-react'

const TEAM = [
  { initials:'AK', color:'#6366f1', name:'Ayush Kumar',   role:'Lead ML Engineer',   bio:'XGBoost specialist with 6 years in supply chain AI. Built forecasting pipelines for 50M+ SKUs.' },
  { initials:'PS', color:'#10b981', name:'Priya Sharma',  role:'Product & UX Lead',  bio:'Former McKinsey consultant. Translates complex ML outputs into decisions non-technical operators trust.' },
  { initials:'RM', color:'#f59e0b', name:'Rohan Mehta',   role:'Backend Architect',  bio:'FastAPI and PostgreSQL expert. Designed real-time data pipelines processing 1M+ events/day.' },
  { initials:'SV', color:'#a78bfa', name:'Sneha Varma',   role:'Data Scientist',     bio:'PhD in Operations Research. Thesis on dynamic EOQ under demand uncertainty.' },
]

const IMPACT = [
  { num:'↓34%', name:'MegaStore Electronics',   story:'Reduced overstock by 34% in Q1, freeing ₹2.3Cr in working capital tied up in slow-moving inventory.' },
  { num:'0→100%', name:'FreshMart Grocery Chain', story:'Eliminated stockouts across 8 locations in 6 months. Isolation Forest caught a supplier fraud pattern 3 weeks early.' },
  { num:'+21%', name:'SportZone India',           story:'Forecast accuracy improved 21 percentage points vs moving average. Demand planning now takes 15 minutes instead of half a day.' },
]

const STACK = [
  { layer:'Frontend',       tech:'React 18 · TypeScript · Tailwind CSS · Recharts · Zustand · TanStack Query · Vite' },
  { layer:'Backend',        tech:'FastAPI · Python 3.11 · SQLAlchemy ORM · Alembic Migrations · Pydantic v2' },
  { layer:'Database',       tech:'PostgreSQL 15 · Supabase / Neon (cloud) · Connection pooling' },
  { layer:'ML & AI',        tech:'XGBoost · Isolation Forest · scikit-learn · Pandas · NumPy · Claude Sonnet API' },
  { layer:'Security',       tech:'JWT (access + refresh) · bcrypt password hashing · RBAC (3 roles) · HTTPS/TLS' },
  { layer:'Deployment',     tech:'Vercel (frontend) · Render (backend) · Docker · GitHub Actions CI/CD' },
]

export default function AboutPage() {
  return (
    <div className="space-y-8 max-w-5xl page-enter">
      {/* Header */}
      <div className="card bg-gradient-to-br from-[#111118] to-[#17171f] border-amber/15">
        <div className="flex items-center gap-4 mb-5">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber to-amber-light flex items-center justify-center">
            <Boxes size={24} className="text-black" />
          </div>
          <div>
            <h2 className="font-serif font-black text-2xl">Stock<span className="text-amber">metry</span></h2>
            <p className="text-sm text-white/40">AI-Powered Inventory Intelligence Platform · v1.0</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-5">
          {[
            { icon:'🎯', title:'Our Mission', text:'Eliminate the $1.1 trillion annual cost of inventory mismanagement. Every business — from a single warehouse to global supply chains — deserves access to AI-grade demand forecasting and optimization that was previously only available to Fortune 500 companies.' },
            { icon:'🔭', title:'Our Vision',  text:'A world where no product sits unsold in a warehouse while a customer cannot find it. Supply chains should be intelligent by default — automatically adapting, proactively alerting, and continuously optimizing without human intervention.' },
          ].map(c => (
            <div key={c.title} className="bg-[#0a0a0f]/50 rounded-xl p-5">
              <p className="text-2xl mb-2">{c.icon}</p>
              <p className="font-semibold text-amber-light mb-2">{c.title}</p>
              <p className="text-sm text-white/50 leading-relaxed">{c.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div>
        <h3 className="font-serif font-bold text-lg mb-4">The Problem We Solve</h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            { num:'$1.1T', label:'Lost annually to inventory distortion (IHL Group 2023)' },
            { num:'34%',   label:'of SMEs report stockouts at least once per month' },
            { num:'23%',   label:'Average MAPE improvement Stockmetry delivers over naive baselines' },
            { num:'8.4%',  label:'Average reduction in carrying costs after EOQ implementation' },
            { num:'15min', label:'Time from data upload to full AI-powered insights' },
            { num:'$26K',  label:'Average annual savings on a 12-product inventory via EOQ engine' },
          ].map((s, i) => (
            <div key={i} className="card-sm">
              <p className="font-serif font-black text-3xl text-amber mb-1">{s.num}</p>
              <p className="text-xs text-white/45 leading-relaxed">{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Team */}
      <div>
        <h3 className="font-serif font-bold text-lg mb-4">Our Team</h3>
        <div className="grid grid-cols-4 gap-4">
          {TEAM.map(m => (
            <div key={m.name} className="card text-center">
              <div className="w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center font-bold text-black text-lg" style={{ background: m.color }}>{m.initials}</div>
              <p className="font-semibold text-sm mb-0.5">{m.name}</p>
              <p className="text-[10px] font-mono text-amber mb-2">{m.role}</p>
              <p className="text-[11px] text-white/40 leading-relaxed">{m.bio}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Impact stories */}
      <div>
        <h3 className="font-serif font-bold text-lg mb-4">Impact Stories</h3>
        <div className="grid grid-cols-3 gap-4">
          {IMPACT.map(s => (
            <div key={s.name} className="card">
              <p className="font-serif font-black text-3xl text-amber mb-1">{s.num}</p>
              <p className="font-semibold text-sm mb-2">{s.name}</p>
              <p className="text-xs text-white/45 leading-relaxed">{s.story}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack */}
      <div>
        <h3 className="font-serif font-bold text-lg mb-4">Technology Stack</h3>
        <div className="grid grid-cols-2 gap-3">
          {STACK.map(s => (
            <div key={s.layer} className="card-sm flex gap-3">
              <div>
                <p className="text-[10px] font-mono text-amber uppercase tracking-wider mb-1">{s.layer}</p>
                <p className="text-xs text-white/50 leading-relaxed">{s.tech}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
