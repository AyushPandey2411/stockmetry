// src/components/layout/TopBar.tsx
import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const PAGE_TITLES: Record<string, string> = {
  '/':             'Dashboard',
  '/forecasting':  'Demand Forecasting',
  '/optimization': 'Inventory Optimization',
  '/anomalies':    'Anomaly Detection',
  '/products':     'Products',
  '/upload':       'Upload Data',
  '/ai':           'AI Assistant',
  '/about':        'About Stockmetry',
}

export default function TopBar() {
  const { pathname } = useLocation()
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <header className="h-16 bg-[#111118] border-b border-white/7 flex items-center justify-between px-6 flex-shrink-0">
      <h1 className="font-serif font-bold text-xl text-white">
        {PAGE_TITLES[pathname] || 'Stockmetry'}
      </h1>
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2 text-[11px] font-mono text-jade-light">
          <span className="w-1.5 h-1.5 rounded-full bg-jade-light animate-pulse-dot" />
          LIVE
        </div>
        <span className="text-[11px] font-mono text-white/40">
          {time.toLocaleTimeString()}
        </span>
      </div>
    </header>
  )
}
