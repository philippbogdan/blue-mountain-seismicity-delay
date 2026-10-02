"""Design of the test that would settle what the Blue Mountain cycles cannot.

A design = a gauge-pressure schedule (the operator's lever) + a monitoring
plan.  For a truth model X (parameters from the Blue Mountain fits) and an
alternative Y, the expected log-likelihood ratio a test would deliver is
  E[dll] = E_X[ll_X(theta_X)] - max_theta E_X[ll_Y(theta)]
i.e. the alternative is given its best possible parameters for the truth's
expected intensity (a KL divergence; no simulation noise).  It is divided by
the over-dispersion phi measured at Blue Mountain (Pearson, 3-6 h bins) to
give an effective separation; dll_eff > 5 (likelihood ratio > ~150) is called
decisive.  A Monte-Carlo check of this approximation is in blm.design_mc.

Monitoring options
  'occupancy' one event per 1-minute file at most (the 2023 system)
  'counts'    all events counted (multi-event detection)
  'depth'     events carry depth class (shallow/mid/deep: the vertical fibre
              resolves depth; class-specific transport times from blm.distance)
  'deepgauge' a pressure gauge at the seismic depth: the transport is observed,
              so the alternatives must explain seismicity given the measured
              fault pressure
Cost: test duration (days) and deferred generation (MWh) at 3.5 MW (the
doublet's peak gross output, paper section 1) for every curtailed hour.
"""
import json

import numpy as np
from scipy import optimize

from . import fit, models

PHI = 2.0
MW = 3.5
DT = models.DT_H
P0 = 3950.0                          # baseline gauge pressure (psig), pre-cycle IV level


class Synth:
    """Minimal data object for forward models."""

    def __init__(self, t, p):
        self.t, self.p = t, p
        self.obs = np.ones(len(t), bool)
        self.occ = np.zeros(len(t), int)
        self.mag = np.full(len(t), np.nan)
        self.shift_h = 0.0


def _decline_template():
    """Normalised decline after a production restart (cycle V, the last cycle)."""
    d = models.Data(t1=330.0)
    pk, v5 = 146.25, 135.75
    dp5 = np.interp(pk, d.t, d.p) - np.interp(v5, d.t, d.p)
    v = np.arange(0, 330.0 - pk, DT)
    return v, (np.interp(pk + v, d.t, d.p) - np.interp(pk, d.t, d.p)) / dp5


_DEC = None


def schedule(cycles, spin_h=96.0, tail_h=72.0):
    """Gauge pressure for a list of cycles: dict(ramp_h, dp, hold_h, rest_h).
    Ramps are linear; after the hold the pressure is released with the
    observed (normalised) decline shape.  Returns t, p, test window mask, cost."""
    global _DEC
    if _DEC is None:
        _DEC = _decline_template()
    v, dec = _DEC
    T = spin_h + sum(c["ramp_h"] + c.get("hold_h", 0) + c["rest_h"] for c in cycles) + tail_h
    t = np.arange(-spin_h, T - spin_h, DT)
    p = np.full(len(t), P0)
    t0 = 0.0
    curtailed = 0.0
    for c in cycles:
        r, h, rest, dp = c["ramp_h"], c.get("hold_h", 0.0), c["rest_h"], c["dp"]
        a = (t >= t0) & (t < t0 + r)
        p[a] += dp * (t[a] - t0) / r
        b = (t >= t0 + r) & (t < t0 + r + h)
        p[b] += dp
        e = t >= t0 + r + h
        p[e] += dp * (1 + np.interp(t[e] - (t0 + r + h), v, dec, right=dec[-1]))
        curtailed += r + h
        t0 += r + h + rest
    win = t >= 0
    cost = dict(days=float((T - spin_h) / 24), deferred_MWh=float(curtailed * MW), curtailed_h=float(curtailed))
    return t, p, win, cost


def blue_mountain():
    """The 2023 gauge history itself (cycles I-V plus a day after)."""
    d = models.Data(t1=200.0)
    win = (d.t >= 30.0) & (d.t < 200.0)
    curt = sum(e - s for _, s, e in models.CYCLES)
    return d.t, d.p, win, dict(days=float((200 - 30) / 24), deferred_MWh=float(curt * MW * 0.5),
                               curtailed_h=float(curt))


# ------------------------------------------------------------------ likelihoods
def exp_ll(lam_t, lam_a, mode):
    """Expected log-likelihood of intensity lam_a when data come from lam_t."""
    lt, la = np.clip(lam_t, 1e-9, None) * DT, np.clip(lam_a, 1e-9, None) * DT
    if mode == "occupancy":
        P = -np.expm1(-lt)
        return float(np.sum(P * np.log(-np.expm1(-la)) - (1 - P) * la))
    return float(np.sum(lt * np.log(la) - la))


def intensity(name, th, t, p):
    return fit.expected_rate(name, Synth(t, p), th)


def best_alt(name_a, th_a0, lam_t, t, p, win, mode, n_starts=3):
    spec = fit.MODELS[name_a]
    z0 = np.r_[np.log([th_a0[k] for k in spec["free"]]), [th_a0[k] for k in spec.get("linear", {})]]

    def f(z):
        th = fit.unpack(name_a, z)
        for k in fit._names(spec):
            lo, hi = fit.BOUNDS[k.split("_")[0]]
            if not lo <= th[k] <= hi:
                return 1e12
        with np.errstate(all="ignore"):
            la = intensity(name_a, th, t, p)
        if not np.all(np.isfinite(la[win])):
            return 1e12
        return -exp_ll(lam_t[win], la[win], mode)

    rng = np.random.default_rng(0)
    best = None
    for s in [z0] + [z0 + rng.normal(0, 0.5, len(z0)) for _ in range(n_starts - 1)]:
        r = optimize.minimize(f, s, method="Nelder-Mead",
                              options={"maxiter": 2500 * len(z0), "xatol": 1e-4, "fatol": 1e-3, "adaptive": True})
        if best is None or r.fun < best.fun:
            best = r
    return fit.unpack(name_a, best.x), -best.fun


def separation(truth, th_t, alt, th_a0, t, p, win, mode="occupancy"):
    lam_t = intensity(truth, th_t, t, p)
    ll_t = exp_ll(lam_t[win], lam_t[win], mode)
    th_a, ll_a = best_alt(alt, th_a0, lam_t, t, p, win, mode)
    n = float(np.sum(lam_t[win]) * DT)
    return dict(dll=ll_t - ll_a, dll_eff=(ll_t - ll_a) / PHI, n_events=n, theta_alt=th_a)


# ------------------------------------------------------------------ designs
def designs():
    """Candidate schedules (gauge-pressure paths) for a future cycled test."""
    D = {}
    D["rate3x2"] = [dict(ramp_h=r, dp=300, hold_h=0, rest_h=36) for r in (1, 4, 16, 16, 4, 1)]
    D["hold72"] = [dict(ramp_h=2, dp=300, hold_h=72, rest_h=72)]
    D["rate3x2+hold72"] = D["rate3x2"] + D["hold72"]
    D["rate2+hold48"] = [dict(ramp_h=1, dp=300, hold_h=0, rest_h=36), dict(ramp_h=16, dp=300, hold_h=0, rest_h=36),
                         dict(ramp_h=2, dp=300, hold_h=48, rest_h=48)]
    D["hold24"] = [dict(ramp_h=2, dp=300, hold_h=24, rest_h=48)]
    D["amp3"] = [dict(ramp_h=6, dp=a, hold_h=0, rest_h=36) for a in (150, 300, 450)]
    D["bm-like5"] = [dict(ramp_h=10.5, dp=355, hold_h=0, rest_h=13.5) for _ in range(5)]
    return D


PAIRS = [("dieterich+diffusion(ta=178h)", "exp+diffusion"),   # finite fault response vs none
         ("exp+diffusion", "dieterich"),                       # transport vs fault delay only
         ("dieterich", "exp+diffusion"),
         ("exp+diffusion", "exp+cascade"),                     # transport vs cascade only
         ("exp+cascade", "exp+diffusion")]


def _job(args):
    dname, truth, alt, mode, thetas = args
    if dname == "BM2023":
        t, p, win, cost = blue_mountain()
    else:
        t, p, win, cost = schedule(designs()[dname])
    s = separation(truth, thetas[truth], alt, thetas[alt], t, p, win, mode)
    return dict(design=dname, truth=truth, alt=alt, mode=mode, dll=s["dll"], dll_eff=s["dll_eff"],
                n_events=s["n_events"], cost=cost)


def run_grid(val="results/validate_shift+0_out1.json", out="results/design_grid.json", workers=6):
    from concurrent.futures import ProcessPoolExecutor
    res = json.load(open(val))
    by = {(r["model"], r["scheme"]): r for r in res}
    names = {m for pr in PAIRS for m in pr}
    thetas = {m: by[(m, "full")]["theta"] for m in names}
    jobs = [(dn, tr, al, mode, thetas) for dn in ["BM2023"] + list(designs())
            for tr, al in PAIRS for mode in ("occupancy", "counts")]
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(_job, jobs))
    with open(out, "w") as fh:
        json.dump(rows, fh, indent=1)
    return rows
