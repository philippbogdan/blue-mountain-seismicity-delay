"""Monte-Carlo check of the expected-separation approximation in blm.design.

Catalogues are simulated from the truth model as a Cox process: the expected
rate times exp(eps(t)), eps an AR(1) log-rate noise (correlation time 3 h)
whose amplitude is calibrated so that the Pearson dispersion of 3-6 h counts
matches Blue Mountain (phi ~ 2).  Both the truth and the alternative are
refitted to every replicate; the realised dll distribution is compared with
the deterministic E[dll] and E[dll]/phi.
"""
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy import optimize

from . import design, fit, models

TCORR_H = 3.0


def ar1_noise(n, sigma, rng, dt=models.DT_H, tc=TCORR_H):
    a = np.exp(-dt / tc)
    e = np.empty(n)
    e[0] = rng.normal(0, sigma)
    s = sigma * np.sqrt(1 - a * a)
    w = rng.normal(0, s, n)
    for i in range(1, n):
        e[i] = a * e[i - 1] + w[i]
    return e - 0.5 * sigma ** 2


def simulate(lam, mode, sigma, rng):
    rate = lam * np.exp(ar1_noise(len(lam), sigma, rng))
    mu = rate * models.DT_H
    if mode == "occupancy":
        return (rng.random(len(mu)) < -np.expm1(-mu)).astype(int)
    return rng.poisson(mu)


def dispersion(counts_min, lam, bin_min=360):
    nb = len(lam) // bin_min
    o = counts_min[:nb * bin_min].reshape(nb, bin_min).sum(1)
    e = (lam[:nb * bin_min] * models.DT_H).reshape(nb, bin_min).sum(1)
    return float(np.sum((o - e) ** 2 / e) / (nb - 1))


def calibrate_sigma(lam, target=2.0, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    for s in np.linspace(0.0, 0.5, 26):
        phis = [dispersion(simulate(lam, "counts", s, rng), lam) for _ in range(8)]
        err = abs(np.mean(phis) - target)
        if best is None or err < best[1]:
            best = (s, err, float(np.mean(phis)))
    return best[0], best[2]


def fit_counts(name, th0, data, t, p, win, mode):
    spec = fit.MODELS[name]
    z0 = np.r_[np.log([th0[k] for k in spec["free"]]), [th0[k] for k in spec.get("linear", {})]]

    def nll(z):
        th = fit.unpack(name, z)
        for k in fit._names(spec):
            lo, hi = fit.BOUNDS[k.split("_")[0]]
            if not lo <= th[k] <= hi:
                return 1e12
        with np.errstate(all="ignore"):
            la = design.intensity(name, th, t, p)[win] * models.DT_H
        if not np.all(np.isfinite(la)):
            return 1e12
        x = data[win]
        if mode == "occupancy":
            return -float(np.sum(np.where(x > 0, np.log(-np.expm1(-la)), -la)))
        return -float(np.sum(x * np.log(np.clip(la, 1e-12, None)) - la))

    r = optimize.minimize(nll, z0, method="Nelder-Mead",
                          options={"maxiter": 2000 * len(z0), "xatol": 1e-4, "fatol": 1e-3, "adaptive": True})
    return -r.fun


def _case(args):
    dname, truth, alt, mode, thetas, n_rep, seed = args
    if dname == "BM2023":
        t, p, win, cost = design.blue_mountain()
    else:
        t, p, win, cost = design.schedule(design.designs()[dname])
    lam = design.intensity(truth, thetas[truth], t, p)
    sigma, phi = calibrate_sigma(lam[win])
    exp_sep = design.separation(truth, thetas[truth], alt, thetas[alt], t, p, win, mode)
    rng = np.random.default_rng(seed)
    dlls = []
    for _ in range(n_rep):
        x = np.zeros(len(t), int)
        x[win] = simulate(lam[win], mode, sigma, rng)
        lt = fit_counts(truth, thetas[truth], x, t, p, win, mode)
        la = fit_counts(alt, exp_sep["theta_alt"], x, t, p, win, mode)
        dlls.append(lt - la)
    dlls = np.array(dlls)
    return dict(design=dname, truth=truth, alt=alt, mode=mode, sigma=sigma, phi_sim=phi,
                expected_dll=exp_sep["dll"], expected_dll_eff=exp_sep["dll_eff"],
                mc_median=float(np.median(dlls)), mc_p10=float(np.percentile(dlls, 10)),
                mc_p90=float(np.percentile(dlls, 90)), mc_frac_gt5=float(np.mean(dlls > 5)),
                mc_frac_correct=float(np.mean(dlls > 0)))


CASES = [("BM2023", "exp+diffusion", "dieterich", "occupancy"),
         ("hold72", "dieterich+diffusion(ta=178h)", "exp+diffusion", "counts"),
         ("rate3x2+hold72", "dieterich+diffusion(ta=178h)", "exp+diffusion", "counts")]


def run(val="results/validate_shift+0_out1.json", out="results/design_mc.json", n_rep=24, workers=3):
    res = json.load(open(val))
    by = {(r["model"], r["scheme"]): r for r in res}
    names = {m for c in CASES for m in c[1:3]}
    thetas = {m: by[(m, "full")]["theta"] for m in names}
    jobs = [(d, tr, al, mo, thetas, n_rep, i) for i, (d, tr, al, mo) in enumerate(CASES)]
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(_case, jobs))
    with open(out, "w") as fh:
        json.dump(rows, fh, indent=1)
    return rows
