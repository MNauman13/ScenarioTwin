'use client'
import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send } from 'lucide-react'
import { api } from '@/lib/api'
import type { WhatIfResponse } from '@/lib/types'

interface Message {
  role: 'user' | 'assistant'
  text: string
}

interface Props {
  profileId: number
  isOpen:    boolean
  onClose:   () => void
  onResult:  (r: WhatIfResponse) => void
}

const HINTS = [
  'What if I got a £1,000 pay rise?',
  'What if I saved £500 more per month?',
  'What if I retire at 60 instead of 67?',
]

export function WhatIfChat({ profileId, isOpen, onClose, onResult }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input,    setInput]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async (text?: string) => {
    const msg = (text ?? input).trim()
    if (!msg || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: msg }])
    setLoading(true)
    try {
      const result = await api.whatif(profileId, msg)
      onResult(result)
      setMessages(prev => [...prev, { role: 'assistant', text: result.narrative }])
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />

          {/* Drawer */}
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="fixed right-0 top-0 bottom-0 w-full max-w-[420px] z-50 flex flex-col"
            style={{ background: 'rgba(8,8,20,0.92)', borderLeft: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}
          >
            {/* Header */}
            <div className="px-6 py-5 border-b border-white/8 flex items-center justify-between flex-shrink-0">
              <div>
                <h3 className="font-semibold text-white text-sm">What-if Scenarios</h3>
                <p className="text-xs text-slate-500 mt-0.5">Ask how changes affect your projection</p>
              </div>
              <button
                onClick={onClose}
                className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-white hover:bg-white/8 transition-colors"
              >
                <X size={15} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
              {messages.length === 0 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.15 }}
                  className="pt-4"
                >
                  <p className="text-xs text-slate-500 mb-3 text-center">Try asking:</p>
                  <div className="space-y-2">
                    {HINTS.map(hint => (
                      <button
                        key={hint}
                        onClick={() => send(hint)}
                        className="w-full text-left text-xs text-slate-400 hover:text-slate-200 bg-white/3 hover:bg-white/6 border border-white/8 hover:border-white/14 rounded-xl px-4 py-3 transition-all duration-200"
                      >
                        {hint}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}

              <AnimatePresence initial={false}>
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-brand/20 border border-brand/25 text-slate-100 rounded-tr-sm'
                          : 'bg-white/4 border border-white/8 text-slate-300 rounded-tl-sm'
                      }`}
                    >
                      {msg.text}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Typing indicator */}
              {loading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="bg-white/4 border border-white/8 rounded-2xl rounded-tl-sm px-4 py-3.5 flex gap-1.5">
                    {[0, 1, 2].map(i => (
                      <motion.div
                        key={i}
                        className="w-1.5 h-1.5 rounded-full bg-slate-500"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2, ease: 'easeInOut' }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="px-4 py-4 border-t border-white/8 flex-shrink-0">
              <form
                onSubmit={e => { e.preventDefault(); send() }}
                className="flex gap-2"
              >
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="What if I earned more..."
                  className="flex-1 bg-white/4 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-brand/50 focus:ring-1 focus:ring-brand/20 transition-colors"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || loading}
                  className="px-4 py-2.5 bg-brand hover:bg-brand-dark disabled:opacity-30 disabled:cursor-not-allowed rounded-xl transition-colors"
                >
                  <Send size={15} className="text-white" />
                </button>
              </form>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}