"""Maximum-likelihood fitting and held-out evaluation of the rate models."""
import numpy as np
from scipy import optimize

from . import models

# model registry: name -> (law, transport, parameter names, initial guesses)
MODELS = {
    "coulomb":            ("coulomb", "none",      ["r0", "k"],                    [10, 0.05]),
    "coulomb+diffusion":  ("coulomb", "diffusion", ["r0", "k", "tau"],             [10, 0.05, 3]),
    "rate":               ("rate", "none",         ["r0", "k"],                    [10, 0.05]),
    "rate+diffusion":     ("rate", "diffusion",    ["r0", "k", "tau"],             [10, 0.05, 3]),
    "dieterich":          ("dieterich", "none",    ["r0", "ta", "As", "g0"],       [10, 30, 30, 1]),
    "dieterich+diffusion": ("dieterich", "diffusion", ["r0", "ta", "As", "g0", "tau"], [10, 30, 30, 1, 3]),
}


def unpack(name, z):
    law, tr, names, _ = MODELS[name]
    return dict(zip(names, np.exp(z)))


def nll(z, name, d, mask):
    th = unpack(name, z)
    law, tr, _, _ = MODELS[name]
    try:
        R = models.rate_model(d, th, law, tr)
    except FloatingPointError:
        return 1e12
    if not np.all(np.isfinite(R)):
        return 1e12
    return -models.loglik(R, d, mask)


def fit(name, d, mask, starts=None, seed=0):
    """Multi-start Nelder-Mead in log-parameters; returns (theta, loglik)."""
    _, _, names, x0 = MODELS[name]
    rng = np.random.default_rng(seed)
    if starts is None:
        starts = [np.log(x0)] + [np.log(x0) + rng.normal(0, 1.0, len(x0)) for _ in range(5)]
    best = None
    for s in starts:
        r = optimize.minimize(nll, s, args=(name, d, mask), method="Nelder-Mead",
                              options={"maxiter": 4000, "xatol": 1e-4, "fatol": 1e-4})
        if best is None or r.fun < best.fun:
            best = r
    return unpack(name, best.x), -best.fun, best.x
