from __future__ import annotations

import dataclasses

import pytest

from app.engine.monte_carlo import SimulationInput, run


def test_percentile_ordering(fake_model, base_inp):
    """p10 ≤ p25 ≤ p50 ≤ p75 ≤ p90 must hold at every year snapshot."""
    out = run(base_inp, fake_model)
    for i, year in enumerate(out.years):
        assert out.percentiles["p10"][i] <= out.percentiles["p25"][i], f"p10 > p25 at year {year}"
        assert out.percentiles["p25"][i] <= out.percentiles["p50"][i], f"p25 > p50 at year {year}"
        assert out.percentiles["p50"][i] <= out.percentiles["p75"][i], f"p50 > p75 at year {year}"
        assert out.percentiles["p75"][i] <= out.percentiles["p90"][i], f"p75 > p90 at year {year}"

def test_regime_fractions_sum_to_one(fake_model, base_inp):
    """
    All regime probabilities across all months must sum to
    exactly 1.
    """
    out = run(base_inp, fake_model)
    total = sum(out.regime_fractions.values())
    assert abs(total - 1.0) < 1e-6

def test_output_arrays_match_years(fake_model, base_inp):
    """
    Each percentile array must have exactly 
    years_to_simulate entries.
    """
    out = run(base_inp, fake_model)
    assert len(out.years) == base_inp.years
    for key in ("p10", "p25", "p50", "p75", "p90"):
        assert len(out.percentiles[key]) == base_inp.years, f"{key} length mismatch"

def test_determinism(fake_model, base_inp):
    """Same seed must produce byte-identical output every time."""
    out1 = run(base_inp, fake_model)
    out2 = run(base_inp, fake_model)
    assert out1.percentiles["p50"] == out2.percentiles["p50"]


def test_higher_savings_higher_median(fake_model, base_inp):
    """Doubling initial savings must raise the median outcome at year 10."""
    low  = run(base_inp, fake_model)
    high = run(dataclasses.replace(base_inp, current_savings=200_000), fake_model)
    assert high.percentiles["p50"][-1] > low.percentiles["p50"][-1]


def test_higher_risk_wider_fan(fake_model, base_inp):
    """
    Higher risk tolerance → more equity → wider p10–p90 spread.
    Tested at year 10 so the difference has time to compound.
    """
    low_risk  = run(dataclasses.replace(base_inp, risk_tolerance=0.0), fake_model)
    high_risk = run(dataclasses.replace(base_inp, risk_tolerance=1.0), fake_model)

    low_spread  = low_risk.percentiles["p90"][-1]  - low_risk.percentiles["p10"][-1]
    high_spread = high_risk.percentiles["p90"][-1] - high_risk.percentiles["p10"][-1]
    assert high_spread > low_spread


def test_all_regime_names_present(fake_model, base_inp):
    """Output must include all three regime names."""
    out = run(base_inp, fake_model)
    assert set(out.regime_fractions.keys()) == {"crisis", "recession", "normal"}