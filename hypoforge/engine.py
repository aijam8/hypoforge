"""
Principle-evolvable discovery engine (PiEvo, hackathon-honest adaptation).

Real numbers, deliberately simple so they can't be subtly wrong:
  * one sklearn GaussianProcessRegressor over (temperature, shear) -> domain spacing
  * info-gain = variance-reduction proxy  ½·ln(1 + σ²(x)/σ_obs²)   [reported as
    "expected model-discrimination (proxy, nats)"]
  * a 2-principle posterior  P = {thermodynamic (T-only), shear-dependent (T,shear)}
    whose Shannon entropy is updated as new observations arrive -> the entropy
    sparkline genuinely bends.
  * anomaly score S = 1 - exp(-|z|) of an observation under the THERMODYNAMIC
    principle -> fires when the user's local data contradicts the literature prior.

Warm-up fits on the low-shear regime (where "temperature-only" looks fine); the
loop then feeds higher-shear observations, which are anomalous under the thermo
principle and shift the posterior to the shear-dependent one.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

PRINCIPLES = [
    {"id": "P0", "name": "thermodynamic (temperature-only)",
     "claim": "Equilibrium domain spacing depends only on annealing temperature."},
    {"id": "P1", "name": "shear-dependent (temperature + shear)",
     "claim": "Equilibrium domain spacing depends on both temperature and applied shear."},
]


@dataclass
class Round:
    t: int
    x: tuple
    y: float
    mu_thermo: float
    mu_full: float
    entropy: float
    posterior: list
    anomaly_S: float
    anomaly: bool


@dataclass
class EngineState:
    rounds: list = field(default_factory=list)
    entropies: list = field(default_factory=list)
    posterior: list = field(default_factory=lambda: [0.72, 0.28])
    anomaly_round: int | None = None
    sigma_obs: float = 0.18


class DiscoveryEngine:
    def __init__(self, df: pd.DataFrame, anomaly_theta: float = 0.70):
        df = df.rename(columns={
            "temperature_C": "T", "shear_rate_s-1": "shear",
            "domain_spacing_nm": "d"})
        self.df = df[["T", "shear", "d"]].dropna().reset_index(drop=True)
        self.theta = anomaly_theta
        self.state = EngineState()
        self._scaler = StandardScaler()
        self._gp: GaussianProcessRegressor | None = None
        self._thermo: LinearRegression | None = None
        self._thermo_sigma = 1.0
        self._Xraw = np.empty((0, 2))   # running training inputs (raw units)
        self._yraw = np.empty((0,))     # running training targets

    # ------------------------------------------------------------------ warm-up
    def warmup(self, shear_max: float = 1.0):
        warm = self.df[self.df["shear"] <= shear_max]
        self._Xraw = warm[["T", "shear"]].values.astype(float)
        self._yraw = warm["d"].values.astype(float)
        Xs = self._scaler.fit_transform(self._Xraw)
        kernel = (ConstantKernel(1.0) * RBF(length_scale=[1.0, 1.0])
                  + WhiteKernel(noise_level=0.05))
        self._gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                            n_restarts_optimizer=2, random_state=0)
        self._gp.fit(Xs, self._yraw)
        # thermodynamic principle: temperature only
        self._thermo = LinearRegression().fit(warm[["T"]].values, warm["d"].values)
        resid = warm["d"].values - self._thermo.predict(warm[["T"]].values)
        self._thermo_sigma = max(float(np.std(resid)), 0.15)
        self.state.sigma_obs = max(float(np.std(resid[abs(warm["shear"]) < 1e-6]
                                              if (abs(warm["shear"]) < 1e-6).any()
                                              else resid)) * 0.5, 0.12)
        return warm

    # ------------------------------------------------------------- predictions
    def _gp_predict(self, T, shear):
        x = self._scaler.transform([[T, shear]])
        mu, sd = self._gp.predict(x, return_std=True)
        return float(mu[0]), float(sd[0])

    def _thermo_predict(self, T):
        return float(self._thermo.predict([[T]])[0])

    def info_gain(self, T, shear) -> float:
        """Expected model-discrimination proxy (nats) at a candidate design point."""
        _, sd = self._gp_predict(T, shear)
        so = self.state.sigma_obs
        return 0.5 * math.log(1.0 + (sd * sd) / (so * so))

    # ------------------------------------------------------------------- loop
    def run_loop(self, n_rounds: int = 6):
        """Feed in higher-shear observations; update posterior + detect anomalies."""
        loop = (self.df[self.df["shear"] >= 2.0]
                .sort_values("shear")
                .reset_index(drop=True))
        # spread the chosen points across the shear range, deterministically
        idx = np.linspace(0, len(loop) - 1, num=min(n_rounds, len(loop))).round().astype(int)
        picks = loop.iloc[idx].reset_index(drop=True)

        logpost = [math.log(p) for p in self.state.posterior]

        for t, row in picks.iterrows():
            T, shear, y = float(row["T"]), float(row["shear"]), float(row["d"])
            so = self.state.sigma_obs

            mu_thermo = self._thermo_predict(T)
            mu_full, sd_full = self._gp_predict(T, shear)

            # likelihoods under each principle
            ll_thermo = _log_norm(y, mu_thermo, self._thermo_sigma**2 + so**2)
            ll_full = _log_norm(y, mu_full, sd_full**2 + so**2)
            logpost[0] += ll_thermo
            logpost[1] += ll_full
            post = _softmax(logpost)
            H = _entropy(post)

            # anomaly under the thermodynamic principle
            z = (y - mu_thermo) / math.sqrt(self._thermo_sigma**2 + so**2)
            S = 1.0 - math.exp(-abs(z))
            fired = S > self.theta
            if fired and self.state.anomaly_round is None:
                self.state.anomaly_round = int(t)

            self.state.rounds.append(Round(
                t=int(t), x=(T, shear), y=y, mu_thermo=mu_thermo, mu_full=mu_full,
                entropy=H, posterior=post, anomaly_S=S, anomaly=fired))
            self.state.entropies.append(H)
            self.state.posterior = post

            # incorporate the observation into the full GP (it learns shear matters)
            self._augment_gp(T, shear, y)
        return self.state.rounds

    def _augment_gp(self, T, shear, y):
        """Refit the full GP on stored raw data + the new observation."""
        self._Xraw = np.vstack([self._Xraw, [T, shear]])
        self._yraw = np.append(self._yraw, y)
        Xs = self._scaler.transform(self._Xraw)
        self._gp.fit(Xs, self._yraw)

    def map_principle(self) -> dict:
        return PRINCIPLES[int(np.argmax(self.state.posterior))]


# --------------------------------------------------------------------- helpers
def _log_norm(y, mu, var):
    var = max(var, 1e-6)
    return -0.5 * math.log(2 * math.pi * var) - (y - mu) ** 2 / (2 * var)


def _softmax(logs):
    m = max(logs)
    exps = [math.exp(l - m) for l in logs]
    s = sum(exps)
    return [e / s for e in exps]


def _entropy(p):
    return max(0.0, -sum(pi * math.log(pi) for pi in p if pi > 1e-12))
