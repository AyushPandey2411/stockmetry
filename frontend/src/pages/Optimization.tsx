// src/pages/Optimization.tsx
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { KPICard, LoadingState, ErrorState, StatusBadge, DataTable, TR, TD } from '../components/ui'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function OptimizationPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['optimization'],
    queryFn: () => api.get('/optimize/').then(r => r.data),
  })

  if (isLoading) return <LoadingState label="Computing EOQ recommendations..." />
  if (error)     return <ErrorState message="Failed to load optimization data" />

  const { recommendations: recs, summary } = data
  const chartData = recs.slice(0, 8).map((r: any) => ({
    name: r.name.split(' ').slice(0, 2).join(' '),
    'Naive Cost': r.naive_annual_cost,
    'EOQ Cost':   r.eoq_annual_cost,
  }))
  const savingsData = [...recs].sort((a: any, b: any) => b.pct_saving - a.pct_saving)
    .slice(0, 10).map((r: any) => ({ name: r.name.split(' ').slice(0, 2).join(' '), saving: r.pct_saving }))

  return (
    <div className="space-y-5 page-enter">
      <div className="grid grid-cols-5 gap-4">
        <KPICard label="Total Annual Saving" value={`$${(summary.total_annual_saving/1000).toFixed(1)}K`} accent="#10b981" delta="vs naive ordering" deltaUp />
        <KPICard label="Avg Saving %" value={`${summary.avg_pct_saving}%`} accent="#d97706" />
        <KPICard label="Stockout Risk"  value={summary.status_counts?.STOCKOUT  || 0} accent="#f43f5e" />
        <KPICard label="Reorder Now"    value={summary.status_counts?.REORDER   || 0} accent="#d97706" />
        <KPICard label="Healthy Stock"  value={summary.status_counts?.HEALTHY   || 0} accent="#10b981" />
      </div>

      <div className="grid grid-cols-2 gap-5">
        <div className="card">
          <p className="font-serif font-bold text-sm mb-1">Naive vs EOQ Annual Cost</p>
          <p className="text-[10px] font-mono text-white/35 mb-4">Top 8 products · ordering + holding costs</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fill: '#ffffff40', fontSize: 9 }} />
              <YAxis tick={{ fill: '#ffffff40', fontSize: 9 }} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
              <Tooltip contentStyle={{ background: '#17171f', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                formatter={(v: any) => [`$${Number(v).toLocaleString()}`, '']} />
              <Legend wrapperStyle={{ fontSize: 10, fontFamily: 'JetBrains Mono', color: '#ffffff60' }} />
              <Bar dataKey="Naive Cost" fill="#f43f5e" opacity={0.7} radius={[2,2,0,0]} />
              <Bar dataKey="EOQ Cost"   fill="#10b981" radius={[2,2,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <p className="font-serif font-bold text-sm mb-1">Savings by Product</p>
          <p className="text-[10px] font-mono text-white/35 mb-4">% cost reduction via EOQ</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={savingsData} layout="vertical">
              <XAxis type="number" tick={{ fill: '#ffffff40', fontSize: 9 }} tickFormatter={v => `${v}%`} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#ffffff60', fontSize: 9 }} width={90} />
              <Tooltip contentStyle={{ background: '#17171f', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                formatter={(v: any) => [`${v}%`, 'Saving']} />
              <Bar dataKey="saving" fill="#d97706" radius={[0,3,3,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <p className="font-serif font-bold text-sm mb-1">Full Optimization Recommendations</p>
        <p className="text-[10px] font-mono text-white/35 mb-3">All products · sorted by urgency</p>
        <DataTable headers={['Product','Category','Stock','Avg/Day','ROP','Safety Stk','EOQ','Days Left','Annual Save','Save %','Status']}>
          {recs.map((r: any) => (
            <TR key={r.product_id}>
              <TD><span className="font-semibold">{r.name}</span></TD>
              <TD mono className="text-white/50">{r.category}</TD>
              <TD mono className={r.current_stock === 0 ? 'text-rose-light' : r.current_stock <= r.reorder_point ? 'text-amber-light' : 'text-jade-light'}>
                {r.current_stock}
              </TD>
              <TD mono className="text-white/50">{r.avg_daily_demand}</TD>
              <TD mono className="text-white/50">{r.reorder_point}</TD>
              <TD mono className="text-white/50">{r.safety_stock}</TD>
              <TD mono className="text-jade-light font-semibold">{r.eoq}</TD>
              <TD mono className={r.days_of_stock < r.lead_time_days ? 'text-rose-light' : 'text-white/50'}>{r.days_of_stock}d</TD>
              <TD mono className="text-jade-light">${r.annual_saving.toLocaleString()}</TD>
              <TD mono className="text-amber-light">{r.pct_saving}%</TD>
              <TD><StatusBadge status={r.status} /></TD>
            </TR>
          ))}
        </DataTable>
      </div>
    </div>
  )
}
