// src/pages/Anomalies.tsx
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { KPICard, LoadingState, ErrorState, StatusBadge, DataTable, TR, TD } from '../components/ui'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AnomaliesPage() {
  const [severity, setSeverity] = useState('')
  const qc = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['anomalies', severity],
    queryFn: () => api.get('/anomalies/', { params: severity ? { severity } : {} }).then(r => r.data),
  })

  const reviewMut = useMutation({
    mutationFn: (id: number) => api.patch(`/anomalies/${id}/review`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['anomalies'] }); toast.success('Marked as reviewed') }
  })

  if (isLoading) return <LoadingState label="Analysing anomalies..." />
  if (error)     return <ErrorState message="Failed to load anomaly data" />

  const { anomalies, summary } = data
  const sevCols = { high: '#f43f5e', medium: '#d97706', low: '#10b981' }
  const pieData = [
    { name: 'High',   value: summary.high,   fill: '#f43f5e' },
    { name: 'Medium', value: summary.medium, fill: '#d97706' },
    { name: 'Low',    value: summary.low,    fill: '#10b981' },
  ]

  // By-product count
  const byProd: Record<string, Record<string, number>> = {}
  anomalies.forEach((a: any) => {
    const k = a.name || a.sku
    if (!byProd[k]) byProd[k] = { high:0, medium:0, low:0 }
    byProd[k][a.severity]++
  })
  const prodChart = Object.entries(byProd).slice(0,8).map(([name, v]) => ({ name: name.split(' ').slice(0,2).join(' '), ...v }))

  return (
    <div className="space-y-5 page-enter">
      <div className="grid grid-cols-5 gap-4">
        <KPICard label="Total Anomalies"  value={summary.total}  accent="#d97706" />
        <KPICard label="High Severity"    value={summary.high}   accent="#f43f5e" />
        <KPICard label="Medium Severity"  value={summary.medium} accent="#d97706" />
        <KPICard label="Low Severity"     value={summary.low}    accent="#10b981" />
        <KPICard label="Unreviewed"       value={anomalies.filter((a:any)=>!a.is_reviewed).length} accent="#a78bfa" />
      </div>

      <div className="grid grid-cols-2 gap-5">
        <div className="card">
          <p className="font-serif font-bold text-sm mb-4">Anomalies by Product</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={prodChart}>
              <XAxis dataKey="name" tick={{ fill:'#ffffff40', fontSize:8 }} />
              <YAxis tick={{ fill:'#ffffff40', fontSize:9 }} />
              <Tooltip contentStyle={{ background:'#17171f', border:'1px solid rgba(255,255,255,0.1)', borderRadius:8, fontSize:12 }} />
              <Bar dataKey="high"   fill="#f43f5e" stackId="a" radius={[0,0,0,0]} />
              <Bar dataKey="medium" fill="#d97706" stackId="a" />
              <Bar dataKey="low"    fill="#10b981" stackId="a" radius={[2,2,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card flex items-center gap-8">
          <ResponsiveContainer width="50%" height={180}>
            <PieChart>
              <Pie data={pieData} dataKey="value" innerRadius={45} outerRadius={75} strokeWidth={0}>
                {pieData.map((e,i) => <Cell key={i} fill={e.fill} />)}
              </Pie>
              <Tooltip contentStyle={{ background:'#17171f', border:'1px solid rgba(255,255,255,0.1)', borderRadius:8, fontSize:12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-3">
            {pieData.map(e => (
              <div key={e.name} className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: e.fill }} />
                <span className="text-sm text-white/60">{e.name}</span>
                <span className="font-mono font-bold ml-auto text-sm">{e.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="font-serif font-bold text-sm">Anomaly Alert Log</p>
            <p className="text-[10px] font-mono text-white/35 mt-0.5">Isolation Forest · z-score severity</p>
          </div>
          <div className="flex gap-2">
            {['','high','medium','low'].map(s => (
              <button key={s} onClick={() => setSeverity(s)}
                className={`text-[10px] font-mono uppercase px-3 py-1.5 rounded transition-all ${severity===s ? 'bg-amber text-black font-bold' : 'bg-white/5 text-white/40 hover:text-white/70'}`}>
                {s || 'All'}
              </button>
            ))}
          </div>
        </div>
        <DataTable headers={['Date','Product','Demand','Average','Z-Score','Type','Severity','Reviewed']}>
          {anomalies.slice(0,60).map((a: any) => (
            <TR key={a.id}>
              <TD mono className="text-white/40">{a.date}</TD>
              <TD>{a.name}</TD>
              <TD mono className="text-amber-light">{a.demand}</TD>
              <TD mono className="text-white/40">{a.avg_demand}</TD>
              <TD mono className={Math.abs(a.z_score)>3.5?'text-rose-light':Math.abs(a.z_score)>3?'text-amber-light':'text-jade-light'}>{a.z_score}</TD>
              <TD mono className="text-white/60">{a.type}</TD>
              <TD><StatusBadge status={a.severity} /></TD>
              <TD>
                {a.is_reviewed
                  ? <span className="text-jade-light text-xs font-mono">✓</span>
                  : <button onClick={() => reviewMut.mutate(a.id)} className="text-white/30 hover:text-jade-light transition-colors">
                      <CheckCircle size={14} />
                    </button>
                }
              </TD>
            </TR>
          ))}
        </DataTable>
      </div>
    </div>
  )
}
