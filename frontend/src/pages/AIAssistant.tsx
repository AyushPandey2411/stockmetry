// src/pages/AIAssistant.tsx
import { useState, useRef, useEffect } from 'react'
import { api } from '../services/api'
import { Send, Cpu } from 'lucide-react'
import clsx from 'clsx'

interface Msg { role: 'user'|'assistant'; content: string; ts: Date }

const STARTERS = [
  'Which products are at stockout risk right now?',
  'What are my biggest cost-saving opportunities?',
  'Explain the anomalies detected this week',
  'What should I order this week and how much?',
]

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<Msg[]>([{
    role: 'assistant',
    content: "Hello! I'm Stockmetry's AI analyst. I have full access to your live inventory data — ask me about stockout risks, demand forecasts, cost savings, or anomaly patterns.\n\nAdd your Anthropic API key below to enable full Claude AI responses.",
    ts: new Date(),
  }])
  const [input,  setInput]  = useState('')
  const [apiKey, setApiKey] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (text?: string) => {
    const q = (text || input).trim()
    if (!q || loading) return
    setInput('')
    const userMsg: Msg = { role: 'user', content: q, ts: new Date() }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)
    try {
      const { data } = await api.post('/chat/', {
        messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content })),
        api_key: apiKey,
      })
      setMessages(prev => [...prev, { role: 'assistant', content: data.response, ts: new Date() }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error — please try again.', ts: new Date() }])
    } finally { setLoading(false) }
  }

  return (
    <div className="flex gap-5 h-[calc(100vh-160px)] page-enter">
      {/* Left panel */}
      <div className="w-72 flex flex-col gap-4">
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <Cpu size={16} className="text-amber" />
            <p className="font-semibold text-sm">AI Assistant</p>
          </div>
          <div className="flex items-center gap-2 bg-[#0a0a0f] rounded-lg px-3 py-2 mb-3">
            <span className="w-1.5 h-1.5 rounded-full bg-jade-light animate-pulse-dot flex-shrink-0" />
            <span className="text-[10px] font-mono text-jade-light">claude-sonnet-4</span>
          </div>
          <p className="text-[11px] text-white/40 leading-relaxed">
            Your AI analyst has real-time access to all inventory data and can explain recommendations.
          </p>
        </div>

        <div className="card">
          <p className="text-[10px] font-mono text-white/40 uppercase tracking-wider mb-2">Anthropic API Key</p>
          <input type="password" className="input text-xs" placeholder="sk-ant-..." value={apiKey}
            onChange={e => setApiKey(e.target.value)} />
          <p className="text-[9px] text-white/25 mt-1.5">Optional — works in demo mode without key</p>
        </div>

        <div className="card flex-1">
          <p className="text-[10px] font-mono text-white/40 uppercase tracking-wider mb-3">Quick Prompts</p>
          <div className="space-y-2">
            {STARTERS.map(s => (
              <button key={s} onClick={() => send(s)}
                className="w-full text-left text-[11px] text-white/50 hover:text-white/80 bg-white/3 hover:bg-white/6 rounded-lg px-3 py-2 transition-all border border-white/5">
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat */}
      <div className="flex-1 card flex flex-col overflow-hidden p-0">
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={clsx('flex gap-3', m.role === 'user' && 'flex-row-reverse')}>
              <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 font-bold text-sm text-black',
                m.role === 'assistant' ? 'bg-gradient-to-br from-amber to-amber-light' : 'bg-gradient-to-br from-violet to-sky')}>
                {m.role === 'assistant' ? '✦' : 'U'}
              </div>
              <div className={clsx('max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed',
                m.role === 'assistant'
                  ? 'bg-[#17171f] border border-white/7 rounded-tl-sm'
                  : 'bg-amber/10 border border-amber/20 rounded-tr-sm text-right')}>
                <p className="whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: m.content.replace(/\*\*(.*?)\*\*/g, '<strong class="text-amber-light">$1</strong>') }}
                />
                <p className="text-[9px] font-mono text-white/20 mt-2">{m.ts.toLocaleTimeString()}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber to-amber-light flex items-center justify-center text-black font-bold text-sm">✦</div>
              <div className="bg-[#17171f] border border-white/7 rounded-xl rounded-tl-sm px-4 py-4 flex gap-1.5">
                {[0,1,2].map(i => <span key={i} className="w-1.5 h-1.5 rounded-full bg-amber animate-pulse-dot" style={{ animationDelay: `${i*0.2}s` }} />)}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-white/7 p-4 flex gap-3">
          <textarea
            className="input flex-1 resize-none"
            rows={2}
            placeholder="Ask about your inventory... (Enter to send)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
          />
          <button onClick={() => send()} disabled={loading || !input.trim()}
            className="btn-primary self-end px-5">
            <Send size={15} />
          </button>
        </div>
      </div>
    </div>
  )
}
