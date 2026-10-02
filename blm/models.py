"""Forward models of the seismicity rate driven by the 73-22 gauge pressure.

Every model is transport + fault law, driven by one forcing: the gauge
pressure p_g(t) on the common (UTC) clock.

transport (what pressure the faults feel)
  'none'       p_f = p_g
  'diffusion'  p_f = p_g * erfc(sqrt(tau/t)) step response: 1-D half space with
               the gauge pressure on its boundary, tau = L^2/(4D); a spherical
               source gives the same time function with a smaller amplitude
  'lag'        p_f = p_g * exponential kernel (1/tau) e^{-t/tau} (lumped
               compartment; an alternative kernel shape)
fault law (how the rate answers p_f)
  'exp'        R = r0 exp((p_f - p_f0)/As)          (Dieterich with t_a -> inf)
  'dieterich'  Dieterich (1994): R/r0 = e^{t/ta+S/As}/(g0 + (1/ta) int e^{s/ta+S/As})
  'coulomb'    R = r0 + k d/dt max_{s<=t} p_f(s)       (threshold with memory)
  'rate'       R = r0 + k max(dp_f/dt, 0)              (stress rate, no memory)
  'exprate'    R = r0 exp((p_f-p_f0)/As) + k max(dp_f/dt, 0)
               (the paper's 'value of pressure and injection rate' reading)

The rate maps onto the catalogue's minute occupancy record through
P(occupied) = 1 - exp(-R dt).  One parameter set holds for every cycle.
"""
import numpy as np
from scipy import signal, special

from . import io, rates

DT_H = 1 / 60.0
SPIN_START_H = -96.0     # 25 Apr 00:00 UTC
WIN = (0.0, 220.0)       # analysis window (h since 29 Apr 00:00 UTC)

# cycle timing on the gauge clock (UTC): ramp start, pressure peak (kinks in p_g)
CYCLES = [("I", 40.08, 48.00), ("II", 62.08, 74.17), ("III", 86.17, 98.17),
          ("IV", 111.42, 122.17), ("V", 135.75, 146.25)]
# held-out segments: ramp start to next ramp start (V: one day), plus pre / post
SEGMENTS = {"pre": (0.0, 40.08), "I": (40.08, 62.08), "II": (62.08, 86.17),
            "III": (86.17, 111.42), "IV": (111.42, 135.75), "V": (135.75, 160.0),
            "post": (160.0, 220.0)}


class Data:
    """Minute grid with gauge pressure and catalogue occupancy on one clock.

    shift_h: catalogue clock minus gauge clock (0 when both are UTC)."""

    def __init__(self, t0=SPIN_START_H, t1=WIN[1], shift_h=0.0, cat=None,
                 outage_h=rates.OUTAGE_H):
        p = io.load_pressure()
        self.t = np.arange(t0, t1, DT_H)
        self.p = np.interp(self.t, p["th"], p["p"])
        tm, occ, obs = rates.minute_grid(t0 + shift_h, t1 + shift_h, cat=cat,
                                         outage_h=outage_h)
        n = min(len(tm), len(self.t))
        self.occ = np.zeros(len(self.t), int)
        self.obs = np.zeros(len(self.t), bool)
        self.occ[:n] = occ[:n]
        self.obs[:n] = obs[:n]
        self.shift_h = shift_h
        # magnitude of the catalogued event in each occupied minute (for cascades)
        c = io.load_catalog() if cat is None else cat
        k = np.floor((c.th.to_numpy() - shift_h - t0) * 60 + 1e-6).astype(int)
        ok = (k >= 0) & (k < len(self.t))
        self.mag = np.full(len(self.t), np.nan)
        self.mag[k[ok]] = c.mag.to_numpy()[ok]

    def mask(self, names):
        m = np.zeros(len(self.t), bool)
        for s in names:
            a, b = SEGMENTS[s]
            m |= (self.t >= a) & (self.t < b)
        return m


def transport(p, kind, tau_h, dt=DT_H):
    if kind == "none" or tau_h <= 0:
        return p.copy()
    if kind == "shift":
        k = min(int(round(tau_h / dt)), len(p))
        return np.r_[np.full(k, p[0]), p[:len(p) - k]]
    n = len(p)
    tk = (np.arange(n) + 0.5) * dt
    if kind == "diffusion":
        step = special.erfc(np.sqrt(tau_h / tk))
    elif kind == "lag":
        step = -np.expm1(-tk / tau_h)
    else:
        raise ValueError(kind)
    dp = np.diff(np.r_[p[0], p])
    return p[0] + signal.fftconvolve(dp, step)[:n]


def dieterich_rate(S, r0, ta_h, As, dt=DT_H, g0=1.0):
    """Dieterich rate for a stress perturbation S (units of As, S[0]=0) on top of
    steady background loading: R/r0 = e^{t/ta+S/As} / (g0 + (1/ta) int_0^t e^{s/ta+S/As} ds);
    g0 = 1 starts at steady state."""
    t = np.arange(len(S)) * dt
    x = t / ta_h + S / As
    logI = np.logaddexp.accumulate(x + np.log(dt))
    logden = np.logaddexp(np.log(g0), logI - np.log(ta_h))
    return r0 * np.exp(x - logden)


def rate_model(d, spec, th):
    """Rate (events/h) on the data grid for model spec and parameters th."""
    pf = transport(d.p, spec["transport"], th.get("tau", 0.0))
    law = spec["law"]
    S = pf - pf[0]
    if "beta" in th:                      # instantaneous poroelastic stress, either sign
        S = S + th["beta"] * (d.p - d.p[0])
    if law == "exp":
        return th["r0"] * np.exp(np.clip(S / th["As"], -50, 50))
    if law == "dieterich":
        return dieterich_rate(S, th["r0"], th["ta"], th["As"], g0=th.get("g0", 1.0))
    if law == "coulomb":
        run = np.maximum.accumulate(pf)
        return th["r0"] + th["k"] * np.diff(np.r_[run[0], run]) / DT_H
    if law == "rate":
        return th["r0"] + th["k"] * np.maximum(np.diff(np.r_[pf[0], pf]) / DT_H, 0.0)
    if law == "exprate":
        return (th["r0"] * np.exp(np.clip(S / th["As"], -50, 50))
                + th["k"] * np.maximum(np.diff(np.r_[pf[0], pf]) / DT_H, 0.0))
    if law == "const":
        return np.full(len(d.t), th["r0"])
    raise ValueError(law)


def omori_rate(d, K, c_h, p_om, alpha=0.0, m0=-0.8):
    """Rate triggered by the catalogued events: sum_i K e^{alpha (m_i - m0)}
    (p-1)/c (1 + (t - t_i)/c)^{-p}, starting one minute after each event."""
    n = len(d.t)
    w = np.where(np.isfinite(d.mag), np.exp(alpha * (np.nan_to_num(d.mag, nan=m0) - m0)), 0.0)
    lag = (np.arange(n) + 1) * DT_H
    ker = K * (p_om - 1) / c_h * (1 + lag / c_h) ** (-p_om)
    trig = signal.fftconvolve(w, ker)[:n]
    return np.r_[0.0, trig[:-1]]


def loglik_terms(R, d):
    """Per-minute occupancy log-likelihood (0 where unobserved)."""
    lam = np.clip(R, 1e-9, None) * DT_H
    ll = np.where(d.occ > 0, np.log(-np.expm1(-lam)), -lam)
    return np.where(d.obs, ll, 0.0)


def loglik(R, d, mask):
    return float(np.sum(loglik_terms(R, d)[mask]))
