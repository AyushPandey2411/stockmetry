// src/components/ui/index.tsx — All shared UI primitives
import React from 'react'
import clsx from 'clsx'
import { Loader2 } from 'lucide-react'

// ── KPI Card ────────────────────────────────────────────────
interface KPIProps {
  label: string; value: string | number
  accent?: string; sub?: string; delta?: string; deltaUp?: boolean
  icon?: React.ReactNode
}
export function KPICard({ label, value, accent = '#d97706', sub, delta, deltaUp, icon }: KPIProps) {
  return (
    <div className="card relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-0.5" style={{ background: accent }} />
      <div className="flex items-start justify-between mb-3">
        <p className="text-[9px] font-mono text-white/40 uppercase tracking-widest">{label}</p>
        {icon && <span className="text-white/20">{icon}</span>}
      </div>
      <p className="font-serif font-black text-3xl leading-none" style={{ color: accent }}>{value}</p>
      {sub   && <p className="text-[11px] text-white/30 mt-1.5">{sub}</p>}
      {delta && (
        <p className={clsx('text-[11px] font-mono mt-2', deltaUp ? 'text-jade-light' : 'text-rose-light')}>
          {deltaUp ? '↑' : '↓'} {delta}
        </p>
      )}
    </div>
  )
}

// ── Status Badge ────────────────────────────────────────────
export function StatusBadge({ status }: { status: string }) {
  const cls: Record<string, string> = {
    STOCKOUT: 'badge-stockout', REORDER: 'badge-reorder',
    LOW: 'badge-low', HEALTHY: 'badge-healthy', OVERSTOCK: 'badge-overstock',
    high: 'badge-high', medium: 'badge-medium', low: 'badge-low-sev',
  }
  return <span className={cls[status] || 'badge-healthy'}>{status}</span>
}

// ── Spinner ─────────────────────────────────────────────────
export function Spinner({ size = 20 }: { size?: number }) {
  return <Loader2 size={size} className="animate-spin text-amber" />
}

// ── Loading overlay ─────────────────────────────────────────
export function LoadingState({ label = 'Loading...' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center py-20 gap-3 text-white/40 text-sm font-mono">
      <Spinner /> {label}
    </div>
  )
}

// ── Error state ─────────────────────────────────────────────
export function ErrorState({ message }: { message: string }) {
  return (
    <div className="card border-rose/20 bg-rose/5 text-rose-light text-sm p-6 text-center font-mono">
      ⚠ {message}
    </div>
  )
}

// ── Empty state ─────────────────────────────────────────────
export function EmptyState({ label }: { label: string }) {
  return <p className="text-center py-12 text-white/30 text-sm font-mono">{label}</p>
}

// ── Callout ─────────────────────────────────────────────────
type CalloutVariant = 'warn' | 'danger' | 'success' | 'info'
export function Callout({ title, body, variant = 'warn' }: { title: string; body: string; variant?: CalloutVariant }) {
  const styles: Record<CalloutVariant, string> = {
    warn:    'bg-amber/8 border-l-amber text-amber-light',
    danger:  'bg-rose/8 border-l-rose text-rose-light',
    success: 'bg-jade/8 border-l-jade text-jade-light',
    info:    'bg-sky/8 border-l-sky text-sky-light',
  }
  return (
    <div className={clsx('rounded-lg p-4 border border-white/5 border-l-2 mb-4', styles[variant])}>
      <p className="font-semibold text-sm mb-1">{title}</p>
      <p className="text-sm text-white/70">{body}</p>
    </div>
  )
}

// ── Data Table ───────────────────────────────────────────────
interface TableProps { headers: string[]; children: React.ReactNode }
export function DataTable({ headers, children }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/7">
            {headers.map(h => (
              <th key={h} className="text-left py-2.5 px-3 text-[9px] font-mono text-white/35 uppercase tracking-widest">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  )
}

export function TR({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <tr className={clsx('border-b border-white/4 hover:bg-white/2 transition-colors', className)}>
      {children}
    </tr>
  )
}

export function TD({ children, mono = false, className }: { children: React.ReactNode; mono?: boolean; className?: string }) {
  return (
    <td className={clsx('py-2.5 px-3', mono && 'font-mono text-xs', className)}>
      {children}
    </td>
  )
}
