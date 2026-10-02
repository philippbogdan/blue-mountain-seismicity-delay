"""Maximum-likelihood fitting and held-out evaluation of the rate models."""
import numpy as np
from scipy import optimize

from . import models

# Paper's reading, made quantitative: published D = 0.43 m^2/s carried over the
# catalogue's median depth offset of the cycle seismicity below the injector
# lateral (2920 m - 2336 m TVD = 584 m; Fercho et al. 2023 for the TVD).
L_PAPER_M = 2920.0 - 2336.0
TAU_PAPER_4D = L_PAPER_M ** 2 / (4 * 0.43) / 3600          # r = sqrt(4 D t) convention
TAU_PAPER_4PI = L_PAPER_M ** 2 / (4 * np.pi * 0.43) / 3600  # paper's printed r = sqrt(4 pi D t)

# name -> spec: transport, law, free parameters (initial values), fixed parameters
MODELS = {
    "const":               dict(transport="none", law="const", free={"r0": 12}),
    "exp":                 dict(transport="none", law="exp", free={"r0": 10, "As": 200}),
    "dieterich":           dict(transport="none", law="dieterich",
                                free={"r0": 10, "ta": 100, "As": 50, "g0": 1}),
    "exp+diffusion":       dict(transport="diffusion", law="exp",
                                free={"r0": 10, "As": 150, "tau": 3}),
    "dieterich+diffusion": dict(transport="diffusion", law="dieterich",
                                free={"r0": 10, "ta": 300, "As": 150, "g0": 1, "tau": 3}),
    "exp+lag":             dict(transport="lag", law="exp",
                                free={"r0": 10, "As": 150, "tau": 5}),
    "dieterich+lag":       dict(transport="lag", law="dieterich",
                                free={"r0": 10, "ta": 300, "As": 150, "g0": 1, "tau": 5}),
    "coulomb+diffusion":   dict(transport="diffusion", law="coulomb",
                                free={"r0": 10, "k": 5, "tau": 30}),
    "rate+diffusion":      dict(transport="diffusion", law="rate",
                                free={"r0": 10, "k": 5, "tau": 30}),
    "paper:p+dp/dt":       dict(transport="none", law="exprate",
                                free={"r0": 10, "As": 200, "k": 0.02}),
    "paper:D=0.43(4Dt)":   dict(transport="diffusion", law="exp",
                                free={"r0": 10, "As": 100}, fixed={"tau": TAU_PAPER_4D}),
    "paper:D=0.43(4piDt)": dict(transport="diffusion", law="exp",
                                free={"r0": 10, "As": 100}, fixed={"tau": TAU_PAPER_4PI}),
}

BOUNDS = {"r0": (1e-2, 1e3), "As": (1e-2, 1e5), "ta": (1e-1, 1e6), "g0": (1e-3, 1e3),
          "tau": (1e-2, 500.0), "k": (1e-5, 1e3)}


def unpack(name, z):
    spec = MODELS[name]
    th = dict(zip(spec["free"].keys(), np.exp(z)))
    th.update(spec.get("fixed", {}))
    return th


def nll(z, name, d, mask):
    spec = MODELS[name]
    for k, v in zip(spec["free"].keys(), np.exp(z)):
        lo, hi = BOUNDS[k]
        if not lo <= v <= hi:
            return 1e12
    with np.errstate(all="ignore"):
        R = models.rate_model(d, spec, unpack(name, z))
    if not np.all(np.isfinite(R[mask])):
        return 1e12
    return -models.loglik(R, d, mask)


def fit(name, d, mask, n_starts=6, seed=0, x0=None):
    """Multi-start Nelder-Mead in log-parameters. Returns (theta, loglik, z)."""
    spec = MODELS[name]
    base = np.log(list(spec["free"].values())) if x0 is None else np.asarray(x0)
    rng = np.random.default_rng(seed)
    starts = [base] + [base + rng.normal(0, 1.0, len(base)) for _ in range(n_starts - 1)]
    best = None
    for s in starts:
        r = optimize.minimize(nll, s, args=(name, d, mask), method="Nelder-Mead",
                              options={"maxiter": 3000 * len(base), "xatol": 1e-4,
                                       "fatol": 1e-3, "adaptive": True})
        if best is None or r.fun < best.fun:
            best = r
    # polish from the best point
    r = optimize.minimize(nll, best.x, args=(name, d, mask), method="Nelder-Mead",
                          options={"maxiter": 3000 * len(base), "xatol": 1e-5,
                                   "fatol": 1e-4, "adaptive": True})
    if r.fun < best.fun:
        best = r
    return unpack(name, best.x), -best.fun, best.x


def predict(name, d, theta):
    with np.errstate(all="ignore"):
        return models.rate_model(d, MODELS[name], theta)
