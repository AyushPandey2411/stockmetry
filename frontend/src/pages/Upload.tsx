// src/pages/Upload.tsx
import { useState, useCallback } from 'react'
import { api } from '../services/api'
import { Upload, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'

export default function UploadPage() {
  const [dragging, setDragging] = useState(false)
  const [status, setStatus] = useState<'idle'|'uploading'|'done'|'error'>('idle')
  const [result, setResult] = useState<any>(null)
  const [progress, setProgress] = useState(0)

  const handleFile = async (file: File) => {
    if (!['csv','xlsx'].includes(file.name.split('.').pop()?.toLowerCase() || '')) {
      toast.error('Only CSV and XLSX files supported'); return
    }
    setStatus('uploading'); setProgress(0)
    const interval = setInterval(() => setProgress(p => Math.min(p + 8, 92)), 150)
    const fd = new FormData(); fd.append('file', file)
    try {
      const { data } = await api.post('/upload/demand', fd, { headers: {'Content-Type':'multipart/form-data'} })
      clearInterval(interval); setProgress(100); setStatus('done'); setResult(data)
      toast.success(`Uploaded! ${data.inserted} rows inserted`)
    } catch(e: any) {
      clearInterval(interval); setStatus('error')
      toast.error(e.response?.data?.detail || 'Upload failed')
    }
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDragging(false)
    const file = e.dataTransfer.files[0]; if (file) handleFile(file)
  }, [])

  return (
    <div className="max-w-3xl space-y-6 page-enter">
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => document.getElementById('file-inp')?.click()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition-all',
          dragging ? 'border-amber bg-amber/5' : 'border-white/10 hover:border-white/20 bg-white/2'
        )}
      >
        <Upload size={40} className={clsx('mx-auto mb-4', dragging ? 'text-amber' : 'text-white/20')} />
        <p className="font-serif font-bold text-lg mb-1">Drop your inventory file here</p>
        <p className="text-sm text-white/40 mb-4">or click to browse · CSV and XLSX supported</p>
        <div className="flex justify-center gap-2">
          {['.csv','.xlsx'].map(f => (
            <span key={f} className="px-3 py-1 border border-white/10 rounded text-[10px] font-mono text-white/40">{f}</span>
          ))}
        </div>
        <input id="file-inp" type="file" accept=".csv,.xlsx" className="hidden" onChange={e => { if(e.target.files?.[0]) handleFile(e.target.files[0]) }} />
      </div>

      {status === 'uploading' && (
        <div className="card">
          <p className="text-sm font-mono text-white/60 mb-3">Uploading and processing...</p>
          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div className="h-full bg-amber rounded-full transition-all duration-300" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {status === 'done' && result && (
        <div className="card border-jade/20 bg-jade/5">
          <div className="flex items-center gap-3 mb-3">
            <CheckCircle size={20} className="text-jade-light" />
            <p className="font-semibold text-jade-light">Upload successful</p>
          </div>
          <div className="grid grid-cols-3 gap-4 font-mono text-sm">
            <div><p className="text-white/40 text-xs mb-0.5">Inserted</p><p className="text-jade-light font-bold">{result.inserted}</p></div>
            <div><p className="text-white/40 text-xs mb-0.5">Skipped</p><p className="text-amber-light font-bold">{result.skipped}</p></div>
            <div><p className="text-white/40 text-xs mb-0.5">Total Rows</p><p className="font-bold">{result.total_rows}</p></div>
          </div>
        </div>
      )}

      <div className="card">
        <p className="font-serif font-bold text-sm mb-3">Required CSV Format</p>
        <div className="bg-[#0a0a0f] rounded-lg p-4 font-mono text-xs text-white/60 leading-relaxed">
          <p className="text-amber-light mb-1"># Required columns:</p>
          <p>date, product, demand</p>
          <p className="text-white/30 mt-2"># Example row:</p>
          <p>2025-01-15, Wireless Headphones, 42</p>
        </div>
      </div>
    </div>
  )
}
