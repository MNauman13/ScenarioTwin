export interface FanChart {
    years: number[]
    p10: number[]
    p25: number[]
    p50: number[]
    p75: number[]
    p90: number[]
}

export interface RegimeFractions {
    normal: number
    recession: number
    crisis: number
}

export interface SimulationResult {
    id: number
    fan_chart: FanChart
    regime_fractions: RegimeFractions
    shock_summary: { avg_job_losses_per_path: number }
    cached?: boolean
}

export interface WhatIfResponse {
    narrative: string
    fan_chart: FanChart
    regime_fractions: RegimeFractions
    shock_summary: { avg_job_losses_per_path: number }
    guardrail: { passed: boolean; flag: string | null }
}

export interface Profile {
    id: number
    age: number
    sector: string
    region: string
    dependents?: number
    risk_tolerance: number
    monthly_income: number
    monthly_expenses: number
    current_savings: number
}