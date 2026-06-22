'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageSquare, LogOut, Zap } from 'lucide-react'
import { api } from '@/lib/api'
import { GlassCard } from '@/components/ui/GlassCard'
import { AnimatedNumber } from '@/components/ui/AnimatedNumber'
import { FanChart } from '@/components/FanChart'
import { RegimeIndicator } from '@/components/RegimeIndicator'
import { WhatIfChat } from '@/components/WhatIfChat'
import type { Profile, SimulationResult, WhatIfResponse } from '@/lib/types'

// Stagger container variant — children inherit these timings
const container = {
  hidden:  {},
  visible: { transition: { staggerChildren: 0.07, delayChildren: 0.1 } },
}

const ease = [0.22, 1, 0.36, 1] as const

const fmtGBP = (n: number) => {
  if (n >= 1_000_000) return `£${(n / 1_000_000).toFixed(1)}m`
  if (n >= 1_000)     return `£${(n / 1_000).toFixed(0)}k`
  return `£${Math.round(n)}`
}

// ── Profile setup form ────────────────────────────────────────────────────────

function ProfileSetup({ onDone }: { onDone: (p: Profile) => void }) {
  const [step,    setStep]    = useState(0)
  const [loading, setLoading] = useState(false)
  const [form,    setForm]    = useState({
    age: '', sector: '', region: '',
    risk_tolerance: '0.5', monthly_income: '',
    monthly_expenses: '', current_savings: '',
  })

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const submit = async () => {
    setLoading(true)
    try {
      const profile = await api.createProfile({
        age:              Number(form.age),
        sector:           form.sector || 'All',
        region:           form.region || 'Great Britain',
        dependents:       0,
        risk_tolerance:   Number(form.risk_tolerance),
        monthly_income:   Number(form.monthly_income),
        monthly_expenses: Number(form.monthly_expenses),
        current_savings:  Number(form.current_savings),
      })
      localStorage.setItem('profileId', String(profile.id))
      onDone(profile)
    } catch (e: any) {
      alert(e.message)
    } finally {
      setLoading(false)
    }
  }

  const steps = [
    {
      title: 'About you',
      fields: (
        <div className="space-y-4">
          <Field label="Age" type="number" value={form.age} onChange={v => set('age', v)} placeholder="35" />
          <Field label="Sector" value={form.sector} onChange={v => set('sector', v)} placeholder="e.g. Information and communication" />
          <Field label="Region" value={form.region} onChange={v => set('region', v)} placeholder="e.g. London" />
        </div>
      ),
    },
    {
      title: 'Your finances',
      fields: (
        <div className="space-y-4">
          <Field label="Monthly income (£)" type="number" value={form.monthly_income} onChange={v => set('monthly_income', v)} placeholder="4000" />
          <Field label="Monthly expenses (£)" type="number" value={form.monthly_expenses} onChange={v => set('monthly_expenses', v)} placeholder="2500" />
          <Field label="Current savings (£)" type="number" value={form.current_savings} onChange={v => set('current_savings', v)} placeholder="20000" />
          <div>
            <label className="block text-xs text-slate-400 mb-2">Risk tolerance</label>
            <div className="flex gap-2">
              {[['Conservative', '0.2'], ['Moderate', '0.5'], ['Aggressive', '0.8']].map(([l, v]) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => set('risk_tolerance', v)}
                  className={`flex-1 py-2 rounded-xl text-xs font-medium border transition-all duration-200 ${
                    form.risk_tolerance === v
                      ? 'bg-brand/20 border-brand/40 text-brand-light'
                      : 'bg-white/3 border-white/10 text-slate-500 hover:border-white/20'
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-brand/8 rounded-full blur-[100px]" />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease }}
        className="w-full max-w-md"
      >
        <div className="mb-8">
          <div className="flex gap-2 mb-6">
            {steps.map((_, i) => (
              <div key={i} className="flex-1 h-0.5 rounded-full overflow-hidden bg-white/8">
                <motion.div
                  className="h-full bg-brand"
                  animate={{ width: i <= step ? '100%' : '0%' }}
                  transition={{ duration: 0.4, ease }}
                />
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-500 mb-1">Step {step + 1} of {steps.length}</p>
          <h2 className="text-xl font-semibold text-white">{steps[step].title}</h2>
        </div>

        <div className="glass rounded-2xl p-7">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -16 }}
              transition={{ duration: 0.25, ease }}
            >
              {steps[step].fields}
            </motion.div>
          </AnimatePresence>

          <div className="flex gap-3 mt-7">
            {step > 0 && (
              <button
                onClick={() => setStep(s => s - 1)}
                className="flex-1 py-2.5 bg-white/5 hover:bg-white/8 border border-white/10 rounded-xl text-sm text-slate-400 transition-colors"
              >
                Back
              </button>
            )}
            <button
              onClick={() => step < steps.length - 1 ? setStep(s => s + 1) : submit()}
              disabled={loading}
              className="flex-1 py-2.5 bg-brand hover:bg-brand-dark text-white text-sm font-medium rounded-xl transition-colors disabled:opacity-50"
            >
              {loading ? 'Running simulation…' : step < steps.length - 1 ? 'Continue' : 'Run simulation'}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

function Field({
  label, value, onChange, placeholder, type = 'text',
}: { label: string; value: string; onChange: (v: string) => void; placeholder: string; type?: string }) {
  return (
    <div>
      <label className="block text-xs text-slate-400 mb-1.5">{label}</label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-white/4 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-brand/50 focus:ring-1 focus:ring-brand/20 transition-colors"
      />
    </div>
  )
}

// ── Main dashboard ────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const router = useRouter()
  const [profile,   setProfile]   = useState<Profile | null>(null)
  const [result,    setResult]    = useState<SimulationResult | null>(null)
  const [narrative, setNarrative] = useState<string | null>(null)
  const [chatOpen,  setChatOpen]  = useState(false)
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    const token     = localStorage.getItem('token')
    const profileId = localStorage.getItem('profileId')
    if (!token) { router.push('/'); return }

    if (profileId) {
      api.simulate(Number(profileId))
        .then(r => { setResult(r); setLoading(false) })
        .catch(() => { localStorage.removeItem('profileId'); setLoading(false) })
    } else {
      setLoading(false)
    }
  }, [router])

  const handleProfileDone = async (p: Profile) => {
    setProfile(p)
    setLoading(true)
    try {
      const r = await api.simulate(p.id)
      setResult(r)
    } finally {
      setLoading(false)
    }
  }

  const handleWhatIf = (r: WhatIfResponse) => {
    setResult(prev => prev ? { ...prev, fan_chart: r.fan_chart, regime_fractions: r.regime_fractions, shock_summary: r.shock_summary } : prev)
    setNarrative(r.narrative)
  }

  const logout = () => {
    localStorage.clear()
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-6 h-6 border-2 border-white/10 border-t-brand rounded-full"
        />
      </div>
    )
  }

  if (!result) return <ProfileSetup onDone={handleProfileDone} />

  const fc   = result.fan_chart
  const last = fc.years.length - 1

  return (
    <>
      <div className="min-h-screen p-4 md:p-8 max-w-6xl mx-auto">
        {/* Ambient glow */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-[-15%] left-1/2 -translate-x-1/2 w-[900px] h-[500px] bg-brand/7 rounded-full blur-[140px]" />
        </div>

        {/* Nav */}
        <motion.nav
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease }}
          className="flex items-center justify-between mb-10"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-brand/20 border border-brand/30 flex items-center justify-center">
              <Zap size={13} className="text-brand-light" />
            </div>
            <span className="font-semibold text-white text-sm">ScenarioTwin</span>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            <LogOut size={13} />
            Sign out
          </button>
        </motion.nav>

        {/* Narrative */}
        <AnimatePresence mode="wait">
          {narrative && (
            <motion.div
              key={narrative}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4, ease }}
              className="glass rounded-2xl p-5 mb-6 border-brand/15"
            >
              <p className="text-sm text-slate-300 leading-relaxed">{narrative}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Fan chart */}
        <GlassCard className="p-6 mb-6" delay={0.05}>
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-sm font-semibold text-white">Portfolio Projection</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                {fc.years[last]}-year Monte Carlo simulation · {(10000).toLocaleString()} paths
              </p>
            </div>
            {result.cached && (
              <span className="text-xs text-slate-600 bg-white/5 border border-white/8 rounded-full px-3 py-1">
                Cached
              </span>
            )}
          </div>
          <FanChart data={fc} />
        </GlassCard>

        {/* Stats grid */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"
        >
          {[
            {
              label: 'Median outcome',
              value: fc.p50[last],
              sub:   `Year ${fc.years[last]}`,
              color: 'text-brand-light',
            },
            {
              label: 'Optimistic (p90)',
              value: fc.p90[last],
              sub:   'Top 10% of paths',
              color: 'text-emerald-400',
            },
            {
              label: 'Pessimistic (p10)',
              value: fc.p10[last],
              sub:   'Bottom 10% of paths',
              color: 'text-slate-300',
            },
            {
              label: 'Avg. job disruptions',
              value: result.shock_summary.avg_job_losses_per_path,
              sub:   'Per simulated path',
              color: 'text-amber-400',
              isFloat: true,
            },
          ].map(({ label, value, sub, color, isFloat }, i) => (
            <GlassCard key={label} className="p-5" delay={0.1 + i * 0.06}>
              <p className="text-xs text-slate-500 mb-2">{label}</p>
              <p className={`text-xl font-semibold ${color}`}>
                <AnimatedNumber
                  value={value}
                  format={isFloat ? v => v.toFixed(1) : fmtGBP}
                  duration={1.2}
                />
              </p>
              <p className="text-xs text-slate-600 mt-1">{sub}</p>
            </GlassCard>
          ))}
        </motion.div>

        {/* Regime breakdown */}
        <GlassCard className="p-6" delay={0.25}>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-5">
            Economic Regime Distribution
          </h3>
          <RegimeIndicator fractions={result.regime_fractions} />
        </GlassCard>
      </div>

      {/* What-if trigger */}
      <motion.button
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.4, ease }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setChatOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-brand hover:bg-brand-dark rounded-2xl flex items-center justify-center shadow-lg shadow-brand/30 transition-colors z-30"
      >
        <MessageSquare size={20} className="text-white" />
      </motion.button>

      <WhatIfChat
        profileId={Number(localStorage.getItem('profileId'))}
        isOpen={chatOpen}
        onClose={() => setChatOpen(false)}
        onResult={handleWhatIf}
      />
    </>
  )
}