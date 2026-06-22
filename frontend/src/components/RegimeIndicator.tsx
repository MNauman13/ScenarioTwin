'use client'
import { motion } from 'framer-motion'
import type { RegimeFractions } from '@/lib/types'

const REGIMES = [
  { key: 'normal'    as const, label: 'Normal',    colour: '#10B981' },
  { key: 'recession' as const, label: 'Recession', colour: '#F59E0B' },
  { key: 'crisis'    as const, label: 'Crisis',    colour: '#EF4444' },
]

interface Props {
  fractions: RegimeFractions
}

export function RegimeIndicator({ fractions }: Props) {
  return (
    <div className="space-y-3">
      {REGIMES.map(({ key, label, colour }, i) => {
        const pct = Math.round(fractions[key] * 100)
        return (
          <motion.div
            key={key}
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1], delay: 0.1 + i * 0.08 }}
            className="flex items-center gap-3"
          >
            {/* Pulsing dot — CSS animation, not JS */}
            <div
              className="regime-dot w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: colour }}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-400">{label}</span>
                <span className="text-xs font-medium text-slate-300">{pct}%</span>
              </div>
              {/* Animated bar */}
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: colour }}
                  initial={{ width: 0 }}
                  animate={{ width: `${pct}%` }}
                  transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.2 + i * 0.08 }}
                />
              </div>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}