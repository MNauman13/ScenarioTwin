"""
Tests for RegimeModel — without a real database or fitting an HMM.
We inject a minimal fake internal state to test the maths.
"""
from __future__ import annotations

import numpy as np
import pytest

from app.engine.hmm_model import RegimeModel


class _FakeHMM:
    """Mimics the fields of hmmlearn.GaussianHMM that RegimeModel reads."""

    transmat_ = np.array([
        [0.80, 0.15, 0.05],
        [0.10, 0.75, 0.15],
        [0.02, 0.08, 0.90],
    ])
    means_ = np.array([[-0.020], [-0.005], [0.008]])
    covars_ = np.array([
        [[0.0025]],
        [[0.0009]],
        [[0.0002]],
    ])


@pytest.fixture
def trained_model() -> RegimeModel:
    """RegimeModel with fake internal state — no DB or fitting needed."""
    m = RegimeModel()
    m._model      = _FakeHMM()
    m._sorted_idx = np.array([0, 1, 2])  # already sorted by ascending mean
    return m


def test_stationary_distribution_sums_to_one(trained_model):
    pi = trained_model.stationary_distribution()
    assert abs(pi.sum() - 1.0) < 1e-10


def test_stationary_distribution_non_negative(trained_model):
    pi = trained_model.stationary_distribution()
    assert all(p >= 0 for p in pi)


def test_regime_params_returns_three_entries(trained_model):
    params = trained_model.regime_params()
    assert len(params) == 3


def test_regime_params_have_required_keys(trained_model):
    required = {"name", "monthly_mean", "monthly_std", "job_loss_multiplier"}
    for p in trained_model.regime_params():
        assert required.issubset(p.keys())


def test_transition_matrix_is_row_stochastic(trained_model):
    T = trained_model.transition_matrix()
    row_sums = T.sum(axis=1)
    np.testing.assert_allclose(row_sums, np.ones(3), atol=1e-10)


def test_is_trained_true_after_setup(trained_model):
    assert trained_model.is_trained is True


def test_is_trained_false_on_fresh_model():
    assert RegimeModel().is_trained is False