"""
Calibration eval: the HMM's theoretical stationary distribution (left eigenvector)
must closely match the empirical regime frequencies observed across 10,000 simulated
paths over 30 years.

Requires a trained regime_model (i.e., data ingestion must have run).
Skips gracefully if the model is not yet trained.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "services" / "simulation-engine"))

try:
    from app.engine.monte_carlo import SimulationInput, run
    from app.engine.hmm_model import regime_model
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False

TOLERANCE = 0.05  # max allowed deviation per regime (5 percentage points)


def run_calibration() -> bool:
    print("\n── Calibration Eval ──")

    if not _DEPS_OK:
        print("  SKIP: simulation-engine deps not installed in this environment.")
        return True

    if not regime_model.is_trained:
        print("  SKIP: regime_model not trained — run data ingestion first.")
        return True  # untrained model is not a failure of this eval

    pi_theoretical = regime_model.stationary_distribution()
    params = regime_model.regime_params()

    inp = SimulationInput(
        age=35,
        monthly_income=4_000,
        monthly_expenses=2_500,
        current_savings=50_000,
        base_annual_job_loss_rate=0.04,
        risk_tolerance=0.5,
        years=30,
        n_paths=10_000,
        seed=42,
    )
    out = run(inp, regime_model)

    passed = True
    for i, p in enumerate(params):
        name        = p["name"]
        empirical   = out.regime_fractions[name]
        theoretical = float(pi_theoretical[i])
        deviation   = abs(empirical - theoretical)
        ok          = deviation <= TOLERANCE
        symbol      = "✓" if ok else "✗"
        print(f"  {symbol} {name}: empirical={empirical:.3f}, theoretical={theoretical:.3f}, |Δ|={deviation:.3f} (tol={TOLERANCE})")
        if not ok:
            passed = False

    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    return passed