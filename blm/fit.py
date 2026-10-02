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
    "dieterich+diffusion(ta=178h)": dict(transport="diffusion", law="dieterich",
                                free={"r0": 10, "As": 150, "g0": 1, "tau": 3}, fixed={"ta": 178.0}),
    "exp+lag":             dict(transport="lag", law="exp",
                                free={"r0": 10, "As": 150, "tau": 5}),
    "dieterich+lag":       dict(transport="lag", law="dieterich",
                                free={"r0": 10, "ta": 300, "As": 150, "g0": 1, "tau": 5}),
    "coulomb+diffusion":   dict(transport="diffusion", law="coulomb",
                                free={"r0": 10, "k": 5, "tau": 30}),
    "rate+diffusion":      dict(transport="diffusion", law="rate",
                                free={"r0": 10, "k": 5, "tau": 30}),
    "exp+diffusion+poro":  dict(transport="diffusion", law="exp",
                                free={"r0": 10, "As": 150, "tau": 3}, linear={"beta": 0.0}),
    "exp+shift":           dict(transport="shift", law="exp",
                                free={"r0": 10, "As": 150, "tau": 3}),
    "exp+cascade":         dict(transport="none", law="exp", cascade=True,
                                free={"r0": 8, "As": 300, "K": 0.2, "c": 0.5, "pm": 1.3}),
    "dieterich+cascade":   dict(transport="none", law="dieterich", cascade=True,
                                free={"r0": 8, "ta": 100, "As": 100, "g0": 1, "K": 0.2, "c": 0.5, "pm": 1.3}),
    "coulomb":             dict(transport="none", law="coulomb", free={"r0": 10, "k": 0.05}),
    "exp+diffusion+cascade": dict(transport="diffusion", law="exp", cascade=True,
                                free={"r0": 8, "As": 200, "tau": 2, "K": 0.1, "c": 0.5, "pm": 1.3}),
    "paper:p+dp/dt":       dict(transport="none", law="exprate",
                                free={"r0": 10, "As": 200, "k": 0.02}),
    "paper:D=0.43(4Dt)":   dict(transport="diffusion", law="exp",
                                free={"r0": 10, "As": 100}, fixed={"tau": TAU_PAPER_4D}),
    "paper:D=0.43(4piDt)": dict(transport="diffusion", law="exp",
                                free={"r0": 10, "As": 100}, fixed={"tau": TAU_PAPER_4PI}),
}

BOUNDS = {"r0": (1e-2, 1e3), "As": (1e-2, 1e5), "ta": (1e-1, 1e6), "g0": (1e-3, 1e3),
          "tau": (1e-2, 500.0), "k": (1e-5, 1e3), "K": (1e-4, 0.99), "c": (1e-3, 100.0),
          "pm": (1.001, 5.0), "beta": (-5.0, 5.0)}


def _names(spec):
    return list(spec["free"].keys()) + list(spec.get("linear", {}).keys())


def unpack(name, z):
    """z holds log-parameters for 'free' and raw values for 'linear' parameters."""
    spec = MODELS[name]
    nf = len(spec["free"])
    th = dict(zip(spec["free"].keys(), np.exp(z[:nf])))
    th.update(dict(zip(spec.get("linear", {}).keys(), z[nf:])))
    th.update(spec.get("fixed", {}))
    return th


def rate(name, d, th):
    spec = MODELS[name]
    if spec.get("classes"):
        # total rate = sum over depth classes with class-specific transport times
        R = np.zeros(len(d.t))
        for k in spec["classes"]:
            pf = models.transport(d.p, spec["transport"], th[f"tau_{k}"])
            R += th[f"r0_{k}"] * np.exp(np.clip((pf - pf[0]) / th["As"], -50, 50))
        return R
    R = models.rate_model(d, spec, th)
    if spec.get("cascade"):
        R = R + models.omori_rate(d, th["K"], th["c"], th["pm"])
    return R


def nll(z, name, d, mask):
    th = unpack(name, z)
    for k in _names(MODELS[name]):
        lo, hi = BOUNDS[k.split("_")[0]]
        if not lo <= th[k] <= hi:
            return 1e12
    with np.errstate(all="ignore"):
        R = rate(name, d, th)
    if not np.all(np.isfinite(R[mask])):
        return 1e12
    return -models.loglik(R, d, mask)


def fit(name, d, mask, n_starts=6, seed=0, x0=None):
    """Multi-start Nelder-Mead in log-parameters. Returns (theta, loglik, z)."""
    spec = MODELS[name]
    base = (np.r_[np.log(list(spec["free"].values())), list(spec.get("linear", {}).values())]
            if x0 is None else np.asarray(x0, float))
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


def expected_rate(name, d, th, n_iter=60):
    """Expected rate for counterfactual forcing: cascade models solved in mean
    field, R = mu + (Omori kernel * R), instead of using observed triggers."""
    spec = MODELS[name]
    if not spec.get("cascade"):
        return predict(name, d, th)
    from scipy import signal
    with np.errstate(all="ignore"):
        mu = models.rate_model(d, spec, th)
    n = len(d.t)
    lag = (np.arange(n) + 1) * models.DT_H
    ker = th["K"] * (th["pm"] - 1) / th["c"] * (1 + lag / th["c"]) ** (-th["pm"])
    R = mu.copy()
    for _ in range(n_iter):
        trig = signal.fftconvolve(R * models.DT_H, ker)[:n]
        Rn = mu + np.r_[0.0, trig[:-1]]
        if np.max(np.abs(Rn - R)) < 1e-6:
            R = Rn
            break
        R = Rn
    return R


def predict(name, d, theta):
    with np.errstate(all="ignore"):
        return rate(name, d, theta)
