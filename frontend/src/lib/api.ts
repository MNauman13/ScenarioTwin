const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

function token() {
    return typeof window !== 'undefined' ? localStorage.getItem('token') : null
}

async function req<T>(path: string, init: RequestInit = {}): Promise<T> {
    const res = await fetch(`${BASE}${path}`, {
        ...init,
        headers: {
            'Content-Type': 'application/json',
            ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
            ...(init.headers ?? {})
        },
    })
    
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail ?? "Request Failed")
    }
    
    return res.json()
}


export const api = {
  register: (username: string, password: string) =>
    req('/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  login: (username: string, password: string) =>
    req<{ access_token: string }>('/v1/auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username, password }).toString(),
    }),

  createProfile: (data: Omit<import('./types').Profile, 'id'>) =>
    req<import('./types').Profile>('/v1/profile', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  simulate: (profileId: number, years = 30, extraMonthly = 0) =>
    req<import('./types').SimulationResult>('/v1/simulate', {
      method: 'POST',
      body: JSON.stringify({
        profile_id: profileId,
        scenario: { years_to_simulate: years, extra_monthly_contribution: extraMonthly },
      }),
    }),

  whatif: (profileId: number, userMessage: string) =>
    req<import('./types').WhatIfResponse>('/v1/whatif', {
      method: 'POST',
      body: JSON.stringify({ profile_id: profileId, user_message: userMessage }),
    }),
}