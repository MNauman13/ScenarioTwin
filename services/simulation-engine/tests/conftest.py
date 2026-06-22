""" Shared fixtures for simulation engine tests. """
import numpy as np
import pytest

from app.engine.monte_carlo import SimulationInput

class FakeRegimeModel:
    """
    Deterministic stand-in for RegimeModel = no database, 
    no hmm-learn.

    Values are calibrated to be realistic but fixed, so tests
    are reproducible.
    """

    def transition_matrix(self) -> np.ndarray:
        # Row-stochastic: each row sums to 1
        return np.array([
            [0.80, 0.15, 0.05],  # crisis -> usually stays crisis
            [0.10, 0.75, 0.15],  # recession -> usually stays recession
            [0.02, 0.08, 0.90]   # normal -> mostly stays normal
        ])

    def regime_params(self) -> list[dict]:
        return [
            {"name": "crisis",    "monthly_mean": -0.020, "monthly_std": 0.050, "job_loss_multiplier": 5.0},
            {"name": "recession", "monthly_mean": -0.005, "monthly_std": 0.030, "job_loss_multiplier": 2.5},
            {"name": "normal",    "monthly_mean":  0.008, "monthly_std": 0.015, "job_loss_multiplier": 1.0},
        ]
    
    def stationary_distribution(self) -> np.ndarray:
        # Approximate stationary dist for the above transition matrix
        return np.array([0.10, 0.20, 0.70])
    

@pytest.fixture
def fake_model() -> FakeRegimeModel:
    return FakeRegimeModel()

@pytest.fixture
def base_inp() -> SimulationInput:
    return SimulationInput(
        age=35,
        monthly_income=4_000,
        monthly_expenses=2_500,
        current_savings=50_000,
        base_annual_job_loss_rate=0.04,
        risk_tolerance=0.5,
        years=10,
        n_paths=500,  # small for fast tests; production uses 10000
        seed=42
    )