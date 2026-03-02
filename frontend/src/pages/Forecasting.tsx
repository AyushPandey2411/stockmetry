// src/pages/Forecasting.tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { KPICard, LoadingState, ErrorState, DataTable, TR, TD } from '../components/ui'
import { ComposedChart, Area, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function ForecastingPage() {
  const [productId, setProductId] = useState<number | null>(null)
  const [horizon, setHorizon] = useState(30)

  const { data, isLoading, error } = useQuery({
    queryKey: ['forecasts', productId, horizon],
    queryFn: () => api.get('/forecasts/', { params: { product_id: productId, horizon } }).then(r => r.data),
  })

  if (isLoading) return <LoadingState label="Loading forecasts..." />
  if (error)     return <ErrorState message="Failed to load forecast data" />

  const products  = data?.products || []
  const historical = (data?.historical || []).filter((r: any) => !productId || r.product_id === productId).slice(-60)
  const forecasts  = (data?.forecasts  || []).filter((r: any) => !productId || r.product_id === productId).slice(0, horizon)

  const chartData = [
    ...historical.map((h: any) => ({ date: h.date.slice(5), actual: h.demand, type: 'hist' })),
    ...forecasts.map((f: any)  => ({ date: f.date.slice(5), forecast: f.forecast, ci_lower: f.ci_lower, ci_upper: f.ci_upper, type: 'fc' })),
  ]

  return (
    <div className="space-y-5 page-enter">
      {/* Controls */}
      <div className="flex gap-4 items-end">
        <div>
          <label className="text-[10px] font-mono text-white/40 uppercase tracking-wider block mb-1.5">Product</label>
          <select className="input w-60" value={productId || ''} onChange={e => setProductId(e.target.value ? +e.target.value : null)}>
            <option value="">All Products</option>
            {products.map((p: any) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-[10px] font-mono text-white/40 uppercase tracking-wider block mb-1.5">Horizon</label>
          <select className="input w-32" value={horizon} onChange={e => setHorizon(+e.target.value)}>
            {[7,14,30,60,90].map(h => <option key={h} value={h}>{h} days</option>)}
          </select>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard label="Model Type"       value="XGBoost"    accent="#38bdf8" />
        <KPICard label="MAPE"             value="19.2%"      accent="#10b981" delta="23% vs naive" deltaUp />
        <KPICard label="Forecast Points"  value={forecasts.length} accent="#d97706" />
        <KPICard label="Historical Days"  value={historical.length} accent="#a78bfa" />
      </div>

      {/* Chart */}
      <div className="card">
        <p className="font-serif font-bold text-sm mb-1">Demand Forecast with 95% Confidence Interval</p>
        <p className="text-[10px] font-mono text-white/35 mb-4">60-day historical + {horizon}-day forecast</p>
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={chartData}>
            <defs>
              <linearGradient id="ciGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#d97706" stopOpacity={0.15} />
                <stop offset="100%" stopColor="#d97706" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <XAxis dataKey="date" tick={{ fill: '#ffffff40', fontSize: 9, fontFamily: 'JetBrains Mono' }} interval={6} />
            <YAxis tick={{ fill: '#ffffff40', fontSize: 9, fontFamily: 'JetBrains Mono' }} />
            <Tooltip contentStyle={{ background: '#17171f', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: '#ffffff60' }} />
            <Area type="monotone" dataKey="ci_upper"   fill="url(#ciGrad)" stroke="transparent" name="CI Upper" legendType="none" />
            <Area type="monotone" dataKey="ci_lower"   fill="#0a0a0f" stroke="transparent" name="CI Lower" legendType="none" />
            <Line type="monotone" dataKey="actual"     stroke="#38bdf8" strokeWidth={1.5} dot={false} name="Historical" />
            <Line type="monotone" dataKey="forecast"   stroke="#d97706" strokeWidth={2} strokeDasharray="5 3" dot={false} name="Forecast" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Forecast table */}
      <div className="card">
        <p className="font-serif font-bold text-sm mb-3">Forecast Detail — Next {Math.min(horizon, 14)} Days</p>
        <DataTable headers={['Date','Product','Forecast','Lower 95%','Upper 95%']}>
          {forecasts.slice(0,14).map((f: any, i: number) => (
            <TR key={i}>
              <TD mono className="text-white/50">{f.date}</TD>
              <TD>{f.name}</TD>
              <TD mono className="text-amber-light font-semibold">{f.forecast}</TD>
              <TD mono className="text-white/40">{f.ci_lower}</TD>
              <TD mono className="text-white/40">{f.ci_upper}</TD>
            </TR>
          ))}
        </DataTable>
      </div>
    </div>
  )
}
