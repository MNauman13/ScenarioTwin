from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from hmmlearn import hmm
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

_REGIME_NAMES = ["crisis", "recession", "normal"]  # ascending mean-return order

# Empirical job-loss multipliers by regime, calibrated to UK recession data:
# 2008 GFC roughly doubled unemployment within 18 months (2.5x)
# 2020 COVID showed 4-5x spikes in exposed sectors
_JOB_LOSS_MULTIPLIERS: dict[str, float] = {
    "crisis": 5.0,
    "recession": 2.5,
    "normal": 1.0
}

class RegimeModel:
    """
    GaussianHMM with 3 latent states trained on monthly FTSE 100 log returns

    After fitting, states are relabelled by ascending mean return so that
    indices always mean: 0=crisis, 1=recession, 2=normal.
    """

    def __init__(self, n_components: int = 3, random_state: int = 42) -> None:
        self.n_components = n_components
        self.random_state = random_state
        self._model: hmm.GaussianHMM | None = None
        self._sorted_idx: np.ndarray | None = None

    # ── Training ──────────────────────────────────────────────────────────────

    def train(self, database_url: str) -> None:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            df = pd.read_sql(
                text(
                    "SELECT date, daily_return FROM market_returns "
                    "WHERE ticker = '^FTSE' ORDER BY date"
                ),
                conn,
            )
        engine.dispose()

        if df.empty:
            raise RuntimeError("No FTSE data in DB - run data ingestion first")

        df["date"] = pd.to_datetime(df["date"])
        monthly = (
            df.set_index("date")["daily_return"]
            .resample("ME")  # "ME" = month-end anchor
            .sum()
            .dropna()
        )

        X = monthly.to_numpy().reshape(-1, 1)

        model = hmm.GaussianHMM(
            n_components=self.n_components,
            covariance_type="full",
            n_iter=200,
            tol=1e-4,
            random_state=self.random_state,
        )
        model.fit(X)

        # Relabel: sort states by ascending mean return (worst -> best)
        self._sorted_idx = np.argsort(model.means_.flatten())
        self._model = model

        means = model.means_.flatten()[self._sorted_idx]
        logger.info(
            "HMM trained on %d monthly observations. State means: %s",
            len(X),
            {name: round(float(m), 5) for name, m in zip(_REGIME_NAMES, means)},
        )

    # ── Public interface ──────────────────────────────────────────────────────

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def transition_matrix(self) -> np.ndarray:
        """(3, 3) transition matrix reordered to (crisis, recession, normal)."""
        idx = self._sorted_idx
        return self._model.transmat_[np.ix_(idx, idx)]

    def regime_params(self) -> list[dict]:
        """Per-regime (monthly_mean, monthly_std, job_loss_multiplier) stats."""
        idx = self._sorted_idx
        means = self._model.means_.flatten()[idx]
        # covariance_type="full" -> covars_ shape (n_components, n_features, n_features)
        stds = np.sqrt(self._model.covars_[:, 0, 0][idx])
        return [
            {
                "name":                _REGIME_NAMES[i],
                "monthly_mean":        float(means[i]),
                "monthly_std":         float(stds[i]),
                "job_loss_multiplier": _JOB_LOSS_MULTIPLIERS[_REGIME_NAMES[i]],
            }
            for i in range(self.n_components)
        ]

    def stationary_distribution(self) -> np.ndarray:
        """Long-run probability of each regime (left eigenvector for eigenvalue 1)."""
        T = self.transition_matrix()
        eigenvalues, eigenvectors = np.linalg.eig(T.T)
        idx = np.argmin(np.abs(eigenvalues - 1.0))
        pi = eigenvectors[:, idx].real
        return pi / pi.sum()
        

# Module-level singleton - populated once at FastAPI lifespan startup
regime_model = RegimeModel()