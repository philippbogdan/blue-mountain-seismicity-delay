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
import os

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
    """Normalised decline after a production restart (shape of cycle V's decline, the
    last cycle), clipped at -1: a test operator restores the pre-cycle level, whereas
    the observed tail kept falling below it as the whole reservoir relaxed."""
    d = models.Data(t1=330.0)
    pk, v5 = 146.25, 135.75
    dp5 = np.interp(pk, d.t, d.p) - np.interp(v5, d.t, d.p)
    v = np.arange(0, 330.0 - pk, DT)
    dec = (np.interp(pk + v, d.t, d.p) - np.interp(pk, d.t, d.p)) / dp5
    return v, np.maximum(dec, -1.0)


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


# ------------------------------------------------------------------ design v2
# Hypothetical 'schedule-controlled delay' site (not fitted: Dieterich nucleation
# in its non-linear regime, no transport), calibrated so that a cycle-IV ramp
# (33 psi/h) gives a ~4 h onset and a ~4x rate rise; its onset scales as 1/(dp/dt).
ARCHETYPES = {"nucleation": ("dieterich", {"r0": 10.0, "ta": 11.5, "As": 95.0, "g0": 1.0})}
_SURV = None


def risk(n_events):
    """Expected largest magnitude among n catalogued events, from the catalogue's own
    magnitude survival function S(m) (N S(m) = 1); beyond the data S is extended with
    the upper-tail b-value of events M >= -0.1 (Aki estimate, ~4.5; the distribution
    steepens with magnitude, so a single Gutenberg-Richter b = 1.73 would overstate it)."""
    global _SURV
    from . import io
    if _SURV is None:
        m = np.sort(io.load_catalog().mag.to_numpy())
        tail = m[m >= -0.1]
        b_tail = np.log10(np.e) / (tail.mean() + 0.1)
        _SURV = (m, b_tail, len(tail) / len(m))
    m, b_tail, s_tail = _SURV
    target = 1.0 / max(n_events, 1.0)
    S = 1.0 - np.arange(len(m)) / len(m)
    if target >= S[-1] and target >= s_tail:
        return float(np.interp(-target, -S, m))
    return float(-0.1 + np.log10(s_tail / target) / b_tail)


def designs_v2():
    D = {}
    rate = lambda r, dp, h=0, rest=36: dict(ramp_h=r, dp=dp, hold_h=h, rest_h=rest)
    D["rate3@300"] = [rate(1, 300), rate(4, 300), rate(16, 300)]
    D["rate3@300x2"] = [rate(1, 300), rate(4, 300), rate(16, 300), rate(16, 300), rate(4, 300), rate(1, 300)]
    D["hold72@300"] = [rate(2, 300, 72, 72)]
    D["hold72@450"] = [rate(2, 450, 72, 72)]
    D["hold168@300"] = [rate(2, 300, 168, 96)]
    D["hold72@450+rate3@300"] = [rate(1, 300), rate(4, 300), rate(16, 300), rate(2, 450, 72, 72)]
    D["hold48@450+rate2@300"] = [rate(1, 300), rate(16, 300), rate(2, 450, 48, 72)]
    D["amp3@6h"] = [rate(6, 150), rate(6, 300), rate(6, 450)]
    # iteration 3 (push cost): decisive without a new well, using a higher hold
    D["hold72@600"] = [rate(2, 600, 72, 96)]
    D["rate3@300+hold72@600"] = [rate(1, 300), rate(4, 300), rate(16, 300), rate(2, 600, 72, 96)]
    D["rate2@300+hold48@600"] = [rate(1, 300), rate(16, 300), rate(2, 600, 48, 96)]
    D["rate3@300x2+hold72@600"] = D["rate3@300x2"] + [rate(2, 600, 72, 96)]
    return D


def _resolve(name, thetas):
    if name in ARCHETYPES:
        base, th = ARCHETYPES[name]
        return base, th
    return name, thetas[name]


def prepare_v2(truth, alt, p, monitoring, thetas):
    """Model names, parameters and the pressure each is driven by.  monitoring:
    'gauge' (73-22 only) or 'deepgauge' (fault pressure measured: the truth's
    transport is applied to the gauge pressure and both models are then scored
    without transport on that measured fault pressure)."""
    tname, tth = _resolve(truth, thetas)
    aname, ath = _resolve(alt, thetas)
    if monitoring != "deepgauge":
        return tname, tth, aname, ath, p
    spec = fit.MODELS[tname]
    tau = tth.get("tau", 0.0) if spec["transport"] != "none" else 0.0
    pf = models.transport(p, spec["transport"], tau) if tau > 0 else p.copy()
    strip = {"exp+diffusion": "exp", "exp+lag": "exp", "exp+diffusion+cascade": "exp+cascade",
             "dieterich+diffusion": "dieterich", "dieterich+diffusion(ta=178h)": "dieterich",
             "exp": "exp", "dieterich": "dieterich", "exp+cascade": "exp+cascade"}
    tname2, aname2 = strip[tname], strip[aname]
    tth2 = {k: v for k, v in tth.items() if k != "tau"}
    ath2 = {k: v for k, v in ath.items() if k != "tau"}
    if tname2 == "dieterich" and "ta" not in tth2:
        tth2["ta"] = 1e6
    if aname2 == "dieterich" and "ta" not in ath2:
        ath2.update(ta=300.0, g0=1.0)
    return tname2, tth2, aname2, ath2, pf


def separation_v2(truth, alt, t, p, win, mode, monitoring, thetas):
    tname, tth, aname, ath, pu = prepare_v2(truth, alt, p, monitoring, thetas)
    return separation(tname, tth, aname, ath, t, pu, win, mode)


PAIRS_V2 = [("dieterich+diffusion(ta=178h)", "exp+diffusion"),   # fault law (finite t_a) on top of transport
            ("exp+diffusion", "nucleation"), ("nucleation", "exp+diffusion"),   # site vs schedule
            ("exp+diffusion", "exp+cascade"), ("exp+cascade", "exp+diffusion"),
            ("exp+lag", "exp+diffusion")]                                        # transport kernel shape


def _job_v2(args):
    dname, truth, alt, mode, mon, thetas = args
    if dname == "BM2023":
        t, p, win, cost = blue_mountain()
    else:
        t, p, win, cost = schedule(designs_v2()[dname])
    s = separation_v2(truth, alt, t, p, win, mode, mon, thetas)
    return dict(design=dname, truth=truth, alt=alt, mode=mode, monitoring=mon, dll=s["dll"],
                dll_eff=s["dll_eff"], n_events=s["n_events"], max_mag=risk(s["n_events"]), cost=cost)


def run_grid_v2(val="results/validate_shift+0_out1.json", out="results/design_grid_v2.json", workers=6,
                only=None):
    """only: restrict to these design names and merge into an existing output file."""
    from concurrent.futures import ProcessPoolExecutor
    res = json.load(open(val))
    by = {(r["model"], r["scheme"]): r for r in res}
    names = {m for pr in PAIRS_V2 for m in pr if m not in ARCHETYPES}
    thetas = {m: by[(m, "full")]["theta"] for m in names}
    dnames = only or (["BM2023"] + list(designs_v2()))
    jobs = [(dn, tr, al, mode, mon, thetas) for dn in dnames
            for tr, al in PAIRS_V2 for mode in ("occupancy", "counts") for mon in ("gauge", "deepgauge")
            if not (mode == "occupancy" and mon == "deepgauge")]
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(_job_v2, jobs))
    if only and os.path.exists(out):
        old = [r for r in json.load(open(out)) if r["design"] not in only]
        rows = old + rows
    with open(out, "w") as fh:
        json.dump(rows, fh, indent=1)
    return rows
