'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'

type Tab = 'login' | 'register'

const ease = [0.22, 1, 0.36, 1] as const

export default function AuthPage() {
  const [tab,      setTab]      = useState<Tab>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (tab === 'register') await api.register(username, password)
      const { access_token } = await api.login(username, password)
      localStorage.setItem('token', access_token)
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4 overflow-hidden">
      {/* Ambient background glow */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-brand/10 rounded-full blur-[120px]" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 28 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease }}
        className="relative w-full max-w-sm"
      >
        {/* Brand */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease, delay: 0.05 }}
          className="text-center mb-10"
        >
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-brand/20 border border-brand/30 mb-4">
            <span className="text-brand-light font-bold">S</span>
          </div>
          <h1 className="text-xl font-semibold text-white">ScenarioTwin</h1>
          <p className="text-slate-500 text-sm mt-1">Monte Carlo financial simulation</p>
        </motion.div>

        {/* Card */}
        <div className="glass rounded-2xl p-7">
          {/* Tab switcher — layoutId animates the background between tabs */}
          <div className="flex gap-1 p-1 bg-white/4 rounded-xl mb-7">
            {(['login', 'register'] as const).map(t => (
              <button
                key={t}
                onClick={() => { setTab(t); setError('') }}
                className="relative flex-1 py-2 text-xs font-medium rounded-lg z-10"
              >
                {tab === t && (
                  <motion.div
                    layoutId="tab-pill"
                    className="absolute inset-0 bg-brand/20 border border-brand/30 rounded-lg"
                    transition={{ duration: 0.22, ease }}
                  />
                )}
                <span className={`relative transition-colors duration-200 ${tab === t ? 'text-brand-light' : 'text-slate-500'}`}>
                  {t === 'login' ? 'Sign in' : 'Register'}
                </span>
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Username</label>
              <input
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                autoComplete="username"
                className="w-full bg-white/4 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-brand/50 focus:ring-1 focus:ring-brand/20 transition-colors"
                placeholder="your_username"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
                className="w-full bg-white/4 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-brand/50 focus:ring-1 focus:ring-brand/20 transition-colors"
                placeholder="••••••••"
              />
            </div>

            <AnimatePresence mode="wait">
              {error && (
                <motion.p
                  key="err"
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="text-red-400 text-xs pt-1"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              transition={{ duration: 0.15 }}
              className="w-full bg-brand hover:bg-brand-dark text-white text-sm font-medium py-2.5 rounded-xl transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed mt-1 flex items-center justify-center gap-2"
            >
              {loading && (
                <motion.span
                  animate={{ rotate: 360 }}
                  transition={{ duration: 0.9, repeat: Infinity, ease: 'linear' }}
                  className="inline-block w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full"
                />
              )}
              {tab === 'login' ? 'Sign in' : 'Create account'}
            </motion.button>
          </form>
        </div>
      </motion.div>
    </main>
  )
}