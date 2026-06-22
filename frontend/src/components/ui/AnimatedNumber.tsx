'use client'
import { useEffect, useRef } from 'react'
import { useMotionValue, animate } from 'framer-motion'

interface Props {
    value: number
    format?: (n: number) => string
    duration?: number
    className?: string
}

const identity = (n: number) => String(Math.round(n))

export function AnimatedNumber({ value, format = identity, duration = 1.2, className }: Props) {
  const motionVal = useMotionValue(0)
  const ref       = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    const stop = animate(motionVal, value, {
      duration,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: v => {
        if (ref.current) ref.current.textContent = format(v)
      },
    })
    return stop
  }, [value]) // eslint-disable-line react-hooks/exhaustive-deps

  return <span ref={ref} className={className}>{format(0)}</span>
}