"""Does the transport time grow with distance?

Events are split into classes by catalogue depth (distance below the injector
lateral, 2336 m TVD) or by radial distance from 73-22.  Each class k has its
own rate R_k = r0_k exp((p_f(tau_k) - p_f0)/As) (transport + instantaneous law,
the best held-out model).  Because a 1-minute file holds at most one event,
classes compete for the record; the joint likelihood per observed minute is
  empty:     -R_tot dt
  class k:   log(1 - e^{-R_tot dt}) + log(R_k / R_tot)
H0 (one tau for all classes) is tested against H1 (tau_k per class).
"""
import json

import numpy as np
from scipy import optimize, stats

from . import io, models, rates

Z_INJ = 2336.0
DEPTH = {"shallow": lambda c: c.z <= 2760, "mid": lambda c: (c.z >= 2800) & (c.z <= 2960),
         "deep": lambda c: c.z >= 3000}
RADIAL = {"near": lambda c: c.x <= 880, "middle": lambda c: (c.x >= 920) & (c.x <= 960),
          "far": lambda c: c.x >= 1000}


def class_grid(classes, d):
    """Class index (0..K-1) of the event in each minute of d's grid, -1 if none."""
    c = io.load_catalog()
    lab = np.full(len(c), -1)
    for i, f in enumerate(classes.values()):
        lab[f(c).to_numpy()] = i
    k = np.floor((c.th.to_numpy() - d.shift_h - d.t[0]) * 60 + 1e-6).astype(int)
    ok = (k >= 0) & (k < len(d.t))
    g = np.full(len(d.t), -1)
    g[k[ok]] = lab[ok]
    return g, c


def joint_ll(params, d, cls, mask, K, shared_tau):
    r0 = np.exp(params[:K])
    As = np.exp(params[K])
    taus = np.exp(params[K + 1:K + 2]) if shared_tau else np.exp(params[K + 1:2 * K + 1])
    if As < 1 or As > 1e5 or np.any(taus < 0.01) or np.any(taus > 300):
        return -1e12
    Rk = []
    for k in range(K):
        tau = taus[0] if shared_tau else taus[k]
        pf = models.transport(d.p, "diffusion", tau)
        Rk.append(r0[k] * np.exp(np.clip((pf - pf[0]) / As, -50, 50)))
    Rk = np.array(Rk)
    Rt = Rk.sum(0)
    m = mask & d.obs
    lam = Rt[m] * models.DT_H
    c = cls[m]
    occ = c >= 0
    ll = np.sum(-lam[~occ]) + np.sum(np.log(-np.expm1(-lam[occ])))
    ll += np.sum(np.log(Rk[c[occ], np.flatnonzero(m)[occ]] / Rt[m][occ]))
    return float(ll)


def fit_classes(classes, shared_tau, d=None, mask=None, x0=None, n_starts=4, seed=0):
    d = d or models.Data()
    mask = d.mask(list(models.SEGMENTS)) if mask is None else mask
    cls, _ = class_grid(classes, d)
    K = len(classes)
    base = x0 if x0 is not None else np.r_[np.log(np.full(K, 3.0)), np.log(200.0),
                                           np.log(np.full(1 if shared_tau else K, 2.5))]
    rng = np.random.default_rng(seed)
    best = None
    for s in [base] + [base + rng.normal(0, 0.5, len(base)) for _ in range(n_starts - 1)]:
        r = optimize.minimize(lambda p: -joint_ll(p, d, cls, mask, K, shared_tau), s,
                              method="Nelder-Mead",
                              options={"maxiter": 6000, "xatol": 1e-4, "fatol": 1e-3, "adaptive": True})
        if best is None or r.fun < best.fun:
            best = r
    return best.x, -best.fun


def profile_tau(classes, xbest, d, mask, which, grid):
    """Profile log-likelihood of tau_which (other parameters re-optimised)."""
    cls, _ = class_grid(classes, d)
    K = len(classes)
    out = []
    for tv in grid:
        def f(q):
            p = np.insert(q, K + 1 + which, np.log(tv))
            return -joint_ll(p, d, cls, mask, K, False)
        q0 = np.delete(xbest, K + 1 + which)
        r = optimize.minimize(f, q0, method="Nelder-Mead",
                              options={"maxiter": 3000, "xatol": 1e-4, "fatol": 1e-3, "adaptive": True})
        out.append(-r.fun)
    return np.array(out)


def analyse(classes, name, d=None):
    d = d or models.Data()
    mask = d.mask(list(models.SEGMENTS))
    x0, ll0 = fit_classes(classes, True, d, mask)
    K = len(classes)
    start = np.r_[x0[:K + 1], np.full(K, x0[K + 1])]
    x1, ll1 = fit_classes(classes, False, d, mask, x0=start)
    if ll1 < ll0:                          # nested: H1 can't be worse
        x1, ll1 = start, ll0
    LR = 2 * (ll1 - ll0)
    p = float(stats.chi2.sf(LR, K - 1))
    taus = np.exp(x1[K + 1:])
    grid = np.exp(np.linspace(np.log(0.1), np.log(40), 41))
    cis = {}
    c = io.load_catalog()
    for k, (cname, f) in enumerate(classes.items()):
        prof = profile_tau(classes, x1, d, mask, k, grid)
        okp = prof >= prof.max() - 1.92
        sub = c[f(c)]
        cis[cname] = dict(tau_h=float(taus[k]), ci95=[float(grid[okp].min()), float(grid[okp].max())],
                          n_events=int(f(c).sum()), median_z=float(sub.z.median()),
                          median_x=float(sub.x.median()), L_below_injector_m=float(sub.z.median() - Z_INJ))
    return dict(classes=name, ll_shared=ll0, ll_separate=ll1, LR=LR, df=K - 1, p=p,
                tau_shared_h=float(np.exp(x0[K + 1])), As_shared=float(np.exp(x0[K])),
                As_separate=float(np.exp(x1[K])), per_class=cis)


def run(out="results/distance.json"):
    d = models.Data()
    res = {"depth": analyse(DEPTH, "depth", d), "radial": analyse(RADIAL, "radial", d)}
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    return res


def loco(classes=DEPTH, out=None):
    """Held-out (leave-one-cycle-out) multi-class log-likelihood: class-specific
    transport times versus one shared transport time."""
    d = models.Data()
    cls, _ = class_grid(classes, d)
    K = len(classes)
    rows = {}
    for c in ["I", "II", "III", "IV", "V"]:
        train = d.mask([s for s in models.SEGMENTS if s != c])
        test = d.mask([c])
        x0, _ = fit_classes(classes, True, d, train, n_starts=3)
        start = np.r_[x0[:K + 1], np.full(K, x0[K + 1])]
        x1, l1 = fit_classes(classes, False, d, train, x0=start, n_starts=3)
        rows[c] = dict(ll_shared=joint_ll(x0, d, cls, test, K, True),
                       ll_separate=joint_ll(x1, d, cls, test, K, False),
                       n_events=int(((cls >= 0) & test & d.obs).sum()),
                       taus=np.exp(x1[K + 1:]).tolist())
    tot = sum(r["ll_separate"] - r["ll_shared"] for r in rows.values())
    n = sum(r["n_events"] for r in rows.values())
    res = dict(per_cycle=rows, dll_total=tot, dll_per_event=tot / n)
    if out:
        with open(out, "w") as fh:
            json.dump(res, fh, indent=1)
    return res
