// src/pages/Dashboard.tsx
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { KPICard, LoadingState, ErrorState, StatusBadge, DataTable, TR, TD } from '../components/ui'
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TrendingUp, DollarSign, AlertTriangle, Package, Zap, Target } from 'lucide-react'

const STATUS_COLORS: Record<string, string> = {
  HEALTHY: '#10b981', REORDER: '#d97706', LOW: '#fbbf24',
  STOCKOUT: '#f43f5e', OVERSTOCK: '#a78bfa'
}

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/analytics/dashboard').then(r => r.data),
    refetchInterval: 60_000,
  })

  if (isLoading) return <LoadingState label="Loading dashboard..." />
  if (error) return <ErrorState message="Failed to load dashboard data" />

  const { kpis, demand_trend, category_breakdown, status_distribution, top_urgent } = data

  return (
    <div className="space-y-6 page-enter">
      {/* KPIs */}
      <div className="grid grid-cols-6 gap-4">
        <KPICard label="Total Products"     value={kpis.n_products}           accent="#38bdf8" icon={<Package size={16}/>} />
        <KPICard label="Stock Value"        value={`$${(kpis.total_stock_value/1000).toFixed(0)}K`} accent="#10b981" icon={<DollarSign size={16}/>} />
        <KPICard label="Annual Savings"     value={`$${(kpis.annual_saving/1000).toFixed(0)}K`}    accent="#10b981" delta="vs naive policy" deltaUp />
        <KPICard label="Forecast MAPE"      value={`${kpis.forecast_mape}%`}  accent="#d97706" delta="23% vs baseline" deltaUp icon={<Target size={16}/>} />
        <KPICard label="Reorder / Stockout" value={kpis.n_stockout_risk}      accent="#f43f5e" sub="need action" icon={<AlertTriangle size={16}/>} />
        <KPICard label="High Anomalies"     value={kpis.n_high_anomalies}     accent="#a78bfa" sub="last 730 days" icon={<Zap size={16}/>} />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-2 gap-5">
        {/* Demand Trend */}
        <div className="card">
          <p className="font-serif font-bold text-sm mb-1">30-Day Demand Trend</p>
          <p className="text-[10px] font-mono text-white/35 mb-4">All products combined · daily total</p>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={demand_trend} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="demGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#d97706" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#d97706" stopOpacity={0}   />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tick={{ fill: '#ffffff40', fontSize: 9, fontFamily: 'JetBrains Mono' }}
                tickFormatter={d => d.slice(5)} interval={4} />
              <YAxis tick={{ fill: '#ffffff40', fontSize: 9, fontFamily: 'JetBrains Mono' }} />
              <Tooltip contentStyle={{ background: '#17171f', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
              <Area type="monotone" dataKey="total" stroke="#d97706" strokeWidth={2} fill="url(#demGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution */}
        <div className="card">
          <p className="font-serif font-bold text-sm mb-1">Inventory Status Distribution</p>
          <p className="text-[10px] font-mono text-white/35 mb-4">All products by health</p>
          <div className="flex items-center gap-4">
            <ResponsiveContainer width="50%" height={160}>
              <PieChart>
                <Pie data={status_distribution} dataKey="count" nameKey="status"
                  cx="50%" cy="50%" innerRadius={40} outerRadius={70} strokeWidth={0}>
                  {status_distribution.map((e: any, i: number) => (
                    <Cell key={i} fill={STATUS_COLORS[e.status] || '#555'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#17171f', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {status_distribution.map((s: any) => (
                <div key={s.status} className="flex items-center gap-2.5 text-xs">
                  <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: STATUS_COLORS[s.status] }} />
                  <span className="text-white/60">{s.status}</span>
                  <span className="font-mono font-semibold ml-auto">{s.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Category Breakdown + Urgent table */}
      <div className="grid grid-cols-5 gap-5">
        <div className="card col-span-2">
          <p className="font-serif font-bold text-sm mb-1">Stock Value by Category</p>
          <p className="text-[10px] font-mono text-white/35 mb-4">Current × cost</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={category_breakdown} layout="vertical" margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
              <XAxis type="number" tick={{ fill: '#ffffff40', fontSize: 9 }} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
              <YAxis type="category" dataKey="category" tick={{ fill: '#ffffff60', fontSize: 10 }} width={90} />
              <Tooltip contentStyle={{ background: '#17171f', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                formatter={(v: any) => [`$${Number(v).toLocaleString()}`, 'Value']} />
              <Bar dataKey="value" fill="#d97706" radius={[0, 3, 3, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card col-span-3">
          <p className="font-serif font-bold text-sm mb-1">Immediate Action Required</p>
          <p className="text-[10px] font-mono text-white/35 mb-3">STOCKOUT + REORDER products</p>
          {top_urgent.filter((r: any) => ['STOCKOUT','REORDER'].includes(r.status)).length === 0
            ? <p className="text-center py-8 text-white/30 text-xs font-mono">✓ All products at healthy levels</p>
            : (
              <DataTable headers={['Product','Stock','Days Left','EOQ Order','Status','Saving']}>
                {top_urgent.filter((r: any) => ['STOCKOUT','REORDER'].includes(r.status)).map((r: any) => (
                  <TR key={r.product_id}>
                    <TD><span className="font-semibold text-sm">{r.name}</span></TD>
                    <TD mono className={r.current_stock === 0 ? 'text-rose-light' : 'text-amber-light'}>{r.current_stock}</TD>
                    <TD mono className="text-white/50">{r.days_of_stock}d</TD>
                    <TD mono className="text-jade-light font-semibold">{r.eoq}</TD>
                    <TD><StatusBadge status={r.status} /></TD>
                    <TD mono className="text-jade-light">{r.pct_saving}%</TD>
                  </TR>
                ))}
              </DataTable>
            )}
        </div>
      </div>
    </div>
  )
}
