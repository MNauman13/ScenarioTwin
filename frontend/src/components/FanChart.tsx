'use client'
import {
  ComposedChart, Area, Line, XAxis, YAxis,
  Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'
import type { TooltipProps } from 'recharts'
import type { FanChart as FanChartData } from '@/lib/types'

interface Props {
  data: FanChartData
}

const fmtGBP = (v: number) => {
  if (v >= 1_000_000) return `£${(v / 1_000_000).toFixed(1)}m`
  if (v >= 1_000)     return `£${(v / 1_000).toFixed(0)}k`
  return `£${v}`
}

// Transform fan chart data into stacked format.
// Recharts stacks areas additively: base(p10) + lo_band = p25, etc.
// This is cleaner than the "paint with background colour" hack.
function toStacked(fc: FanChartData) {
  return fc.years.map((year, i) => ({
    year,
    base:     fc.p10[i],
    lo_band:  fc.p25[i] - fc.p10[i],
    mid_band: fc.p75[i] - fc.p25[i],
    hi_band:  fc.p90[i] - fc.p75[i],
    median:   fc.p50[i],
  }))
}

function CustomTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null

  const get = (key: string) => payload.find(p => p.dataKey === key)?.value ?? 0
  const base = get('base')
  const p25  = base  + get('lo_band')
  const p75  = p25   + get('mid_band')
  const p90  = p75   + get('hi_band')
  const p50  = get('median')

  const rows = [
    { label: 'Optimistic (p90)', value: p90,  color: '#818CF8' },
    { label: 'Upper (p75)',       value: p75,  color: '#A78BFA' },
    { label: 'Median (p50)',      value: p50,  color: '#C4B5FD', bold: true },
    { label: 'Lower (p25)',       value: p25,  color: '#A78BFA' },
    { label: 'Pessimistic (p10)', value: base, color: '#818CF8' },
  ]

  return (
    <div className="glass rounded-xl p-4 text-xs min-w-[200px]">
      <p className="text-slate-400 mb-3 font-medium text-sm">Year {label}</p>
      <div className="space-y-1.5">
        {rows.map(r => (
          <div key={r.label} className="flex items-center justify-between gap-6">
            <span className="text-slate-400">{r.label}</span>
            <span className={`font-medium ${r.bold ? 'text-white' : 'text-slate-200'}`}>
              {fmtGBP(r.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function FanChart({ data }: Props) {
  const chartData = toStacked(data)

  return (
    <ResponsiveContainer width="100%" height={340}>
      <ComposedChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
        <defs>
          <linearGradient id="gradOuter" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#6366F1" stopOpacity={0.12} />
            <stop offset="100%" stopColor="#6366F1" stopOpacity={0.04} />
          </linearGradient>
          <linearGradient id="gradInner" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#6366F1" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#6366F1" stopOpacity={0.15} />
          </linearGradient>
        </defs>

        <CartesianGrid
          strokeDasharray="1 6"
          stroke="rgba(255,255,255,0.06)"
          vertical={false}
        />

        <XAxis
          dataKey="year"
          tick={{ fill: '#475569', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={v => `Yr ${v}`}
          interval={4}
        />
        <YAxis
          tick={{ fill: '#475569', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={fmtGBP}
          width={52}
        />

        <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.08)', strokeWidth: 1 }} />

        {/* Stacked bands: base (invisible) → lo_band → mid_band → hi_band */}
        <Area dataKey="base"     stackId="fan" fill="transparent"    stroke="none" isAnimationActive={false} />
        <Area dataKey="lo_band"  stackId="fan" fill="url(#gradOuter)" stroke="none" animationDuration={800} animationBegin={200} />
        <Area dataKey="mid_band" stackId="fan" fill="url(#gradInner)" stroke="none" animationDuration={800} animationBegin={200} />
        <Area dataKey="hi_band"  stackId="fan" fill="url(#gradOuter)" stroke="none" animationDuration={800} animationBegin={200} />

        {/* Median line on top */}
        <Line
          dataKey="median"
          type="monotone"
          stroke="#818CF8"
          strokeWidth={2}
          dot={false}
          animationDuration={800}
          animationBegin={200}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}