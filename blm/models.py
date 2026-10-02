"""Forward models of the seismicity rate driven by the 73-22 gauge pressure.

All models share one forcing, the gauge pressure p_g(t) on the common (UTC)
clock, and differ in two places:

* transport  - whether the faults feel p_g directly or a diffused version
               p_f = p_g * h_tau (1-D half-space step response erfc(sqrt(tau/t)),
               tau = L^2 / (4 D));
* fault law  - how the rate answers the load:
    'coulomb'  rate = r0 + k * d/dt max_{s<=t} p_f(s)    (threshold, Kaiser memory)
    'rate'     rate = r0 + k * max(dp_f/dt, 0)           (stress-rate, no memory)
    'dieterich' Dieterich (1994) rate-and-state, closed form for a stress history
               dS = mu dp_f added to steady background loading:
               R/r0 = e^{S/As} / (1 + (1/t_a) int_0^t e^{S/As} ds).

The rate is then mapped onto the catalogue's minute occupancy record by
P(occupied) = 1 - exp(-R dt).  One parameter set holds for every cycle.
"""
import numpy as np
from scipy import signal, special

from . import io, rates

DT_H = 1 / 60.0
SPIN_START_H = -96.0     # 25 Apr 00:00 UTC: quasi-steady crossflow pressure
WIN = (0.0, 220.0)       # analysis window (h since 29 Apr 00:00 UTC)


class Data:
    """Minute grid with gauge pressure and catalogue occupancy, common clock."""

    def __init__(self, t0=SPIN_START_H, t1=WIN[1], win=WIN, shift_h=0.0, cat=None):
        p = io.load_pressure()
        self.t = np.arange(t0, t1, DT_H)
        self.p = np.interp(self.t, p["th"], p["p"])
        # catalogue clock = gauge clock + shift_h  (shift_h = 0: both UTC)
        tm, occ, obs = rates.minute_grid(t0 + shift_h, t1 + shift_h, cat=cat)
        n = min(len(tm), len(self.t))
        self.occ = np.zeros(len(self.t), int)
        self.obs = np.zeros(len(self.t), bool)
        self.occ[:n] = occ[:n]
        self.obs[:n] = obs[:n]
        self.inwin = (self.t >= win[0]) & (self.t < win[1])
        self.p0 = self.p[0]


def diffuse(p, tau_h, dt=DT_H):
    """Pressure felt at the faults: p convolved with the 1-D diffusion step
    response erfc(sqrt(tau/t)) (boundary at the gauge, tau = L^2/4D)."""
    if tau_h <= 0:
        return p.copy()
    n = len(p)
    tk = (np.arange(n) + 0.5) * dt
    step = special.erfc(np.sqrt(tau_h / tk))   # response to a unit pressure step
    dp = np.diff(np.r_[p[0], p])               # pressure increments
    return p[0] + signal.fftconvolve(dp, step)[:n]


def dieterich_rate(S, r0, ta_h, As, dt=DT_H, g0=1.0):
    """Dieterich rate for stress perturbation S (same units as As, S[0]=0) on top
    of steady background loading (t_a = As / background stressing rate):
    R/r0 = e^{t/ta + S/As} / (1 + (1/ta) int_0^t e^{s/ta + S/As} ds)."""
    t = np.arange(len(S)) * dt
    x = t / ta_h + S / As
    logI = np.logaddexp.accumulate(x + np.log(dt))   # log int_0^t e^{x} ds, exact and stable
    # initial state gamma(0) = g0 / background stressing rate (g0 = 1: steady state)
    logden = np.logaddexp(np.log(g0), logI - np.log(ta_h))
    return r0 * np.exp(x - logden)


def rate_model(d, theta, law, transport):
    """Rate (events/h) on the minute grid for parameters theta (dict)."""
    tau = theta.get("tau", 0.0) if transport == "diffusion" else 0.0
    pf = diffuse(d.p, tau)
    if law == "coulomb":
        run = np.maximum.accumulate(pf)
        dr = np.diff(np.r_[run[0], run]) / DT_H
        return theta["r0"] + theta["k"] * dr
    if law == "rate":
        dr = np.diff(np.r_[pf[0], pf]) / DT_H
        return theta["r0"] + theta["k"] * np.maximum(dr, 0.0)
    if law == "dieterich":
        S = pf - pf[0]
        return dieterich_rate(S, theta["r0"], theta["ta"], theta["As"], g0=theta.get("g0", 1.0))
    raise ValueError(law)


def loglik(R, d, mask):
    """Occupancy log-likelihood over observed minutes in mask."""
    m = mask & d.obs
    lam = np.clip(R[m], 1e-9, None) * DT_H
    o = d.occ[m]
    return float(np.sum(np.where(o > 0, np.log(-np.expm1(-lam)), -lam)))
