from __future__ import annotations

import numpy as np
from dataclasses import dataclass

from .hmm_model import RegimeModel

@dataclass(frozen=True, slots=True)
class SimulationInput:
    age: int
    monthly_income: float
    monthly_expenses: float
    current_savings: float
    base_annual_job_loss_rate: float
    risk_tolerance: float
    years: int = 30
    extra_monthly: float = 0.0
    n_paths: int = 10_000
    seed: int = 42

@dataclass(slots=True)
class SimulationOutput:
    years: list[int]
    percentiles: dict[str, list[float]]
    regime_fractions: dict[str, float]
    shock_summary: dict[str, float]
    regime_params: list[dict]

def run(inp: SimulationInput, model: RegimeModel) -> SimulationOutput:
    rng = np.random.default_rng(inp.seed)

    params = model.regime_params()  # list[dict], length 3
    transmat = model.transition_matrix()  # (3, 3)
    pi = model.stationary_distribution()  # (3,)

    n_paths = inp.n_paths
    n_months = inp.years * 12

    # Pre-extract per-regime arrays - avoids dict lookups inside the hot loop
    means = np.array([p["monthly_mean"] for p in params])  # (3,)
    stds = np.array([p["monthly_std"] for p in params])  # (3,)
    multipliers = np.array([p["job_loss_multiplier"] for p in params])  # (3,)

    # Precompute cumulative transition matrix for vectorised regime draws
    cum_transmat = np.cumsum(transmat, axis=1)  # (3, 3)

    # Asset Allocation: risk_tolerance ∈ [0, 1] -> equity fraction ∈ [30%, 80%]
    eq_frac = 0.3 + 0.5 * inp.risk_tolerance
    bond_frac = 1.0 - eq_frac
    bond_monthly = 0.003  # ~3.7% annualised real gilt proxy

    # Convert annual job-loss rate to monthly (correct compound formula, not /12)
    monthly_jl_base = 1.0 - (1.0 - inp.base_annual_job_loss_rate) ** (1.0 / 12)
    monthly_re_emp = 0.25  # P(re-employment | unemployed) - ~4-month mean spell

    monthly_net = inp.monthly_income - inp.monthly_expenses + inp.extra_monthly

    
    # Initialise all paths
    portfolios = np.full(n_paths, inp.current_savings, dtype=np.float64)
    employed = np.ones(n_paths, dtype=bool)
    regimes = rng.choice(3, size=n_paths, p=pi)

    year_snapshots = np.empty((inp.years, n_paths), dtype=np.float64)
    regime_counts = np.zeros(3, dtype=np.int64)
    total_job_losses = 0


    # Monthly Loop
    for month in range(n_months):
        # 1. Regime transition - fully vectorised categorical draw
        #    cum_transmat[regimes]: shape (n_paths, 3) - each row is the CDF
        #    for that path's current regime.
        #    u >= CDF produces booleans; .sum(axis=1) counts how many thresholds
        #    the draw clears, which is exactly the new regime index.
        u = rng.random((n_paths, 1))
        regimes = (u >= cum_transmat[regimes]).sum(axis=1).clip(0, 2)
        regime_counts += np.bincount(regimes, minlength=3)

        # 2. Equity return - Gaussian per regime, fully vectorised
        eq_log = rng.normal(means[regimes], stds[regimes])  # (n_paths,)
        eq_simp = np.expm1(eq_log)  # exp(x)-1, numerically stable for small x
        blended = eq_frac * eq_simp + bond_frac * bond_monthly

        # 3. Job loss and re-employment - vectorised Bernoulli
        jl_probs = np.clip(monthly_jl_base * multipliers[regimes], 0.0, 0.5)
        newly_lost = employed & (rng.random(n_paths) < jl_probs)
        newly_found = ~employed & (rng.random(n_paths) < monthly_re_emp)
        employed = (employed & ~newly_lost) | newly_found
        total_job_losses += int(newly_lost.sum())

        # 4. Portfolio update
        income = np.where(employed, monthly_net, -inp.monthly_expenses)
        portfolios = np.maximum(portfolios * (1.0 + blended) + income, 0.0)

        # 5. Year-end snapshot
        if (month + 1) % 12 == 0:
            year_snapshots[month // 12] = portfolios


    # Aggregate
    total_steps = n_months * n_paths
    return SimulationOutput(
        years = list(range(1, inp.years + 1)),
        percentiles={
            f"p{p}": np.percentile(year_snapshots, p, axis=1).tolist()
            for p in [10, 25, 50, 75, 90]
        },
        regime_fractions = {
            params[i]["name"]: float(regime_counts[i]) / total_steps
            for i in range(3)
        },
        shock_summary={
            "avg_job_losses_per_path": float(total_job_losses) / n_paths,
        },
        regime_params=params
    )