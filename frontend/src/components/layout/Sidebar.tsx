// src/components/layout/Sidebar.tsx
import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, TrendingUp, Package, AlertTriangle, Upload, Cpu, BarChart3, Info, LogOut, Boxes, FileText } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import clsx from 'clsx'

const NAV = [
  { to: '/',            icon: LayoutDashboard, label: 'Dashboard'    },
  { to: '/forecasting', icon: TrendingUp,       label: 'Forecasting'  },
  { to: '/optimization',icon: BarChart3,        label: 'Optimization' },
  { to: '/anomalies',   icon: AlertTriangle,    label: 'Anomalies'    },
  { to: '/products',    icon: Package,          label: 'Products'     },
  { to: '/upload',      icon: Upload,           label: 'Upload Data'  },
  { to: '/ai',          icon: Cpu,              label: 'AI Assistant' },
   { to: '/summary',     icon: FileText,         label: 'Exec Summary'      },
  { to: '/about',       icon: Info,             label: 'About'        },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <aside className="w-56 bg-[#111118] border-r border-white/7 flex flex-col flex-shrink-0">
      {/* Logo */}
      <div className="h-16 flex items-center gap-2.5 px-5 border-b border-white/7">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber to-amber-light flex items-center justify-center">
          <Boxes size={16} className="text-black" />
        </div>
        <span className="font-serif font-bold text-lg">
          Stock<span className="text-amber">metry</span>
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 overflow-y-auto">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg text-sm font-medium transition-all',
              isActive
                ? 'bg-amber/10 text-amber border-l-2 border-amber pl-3.5'
                : 'text-white/50 hover:text-white/80 hover:bg-white/3'
            )}
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User section */}
      <div className="p-3 border-t border-white/7">
        <div className="flex items-center gap-2.5 px-2 py-2 rounded-lg mb-1">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-black text-sm font-bold flex-shrink-0"
            style={{ background: user?.avatar_color || '#6366f1' }}
          >
            {user?.full_name?.[0] || user?.username?.[0] || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate">{user?.full_name || user?.username}</p>
            <p className="text-[10px] font-mono text-amber">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-white/40 hover:text-rose-light hover:bg-rose/8 text-sm transition-all"
        >
          <LogOut size={14} /> Sign out
        </button>
      </div>
    </aside>
  )
}
