"""Profile likelihoods of model parameters (other parameters re-optimised)."""
import json

import numpy as np
from scipy import optimize

from . import fit, models


def profile(name, pname, grid, d=None, mask=None):
    d = d or models.Data()
    mask = d.mask(list(models.SEGMENTS)) if mask is None else mask
    spec = fit.MODELS[name]
    th0, ll0, z0 = fit.fit(name, d, mask)
    names = list(spec["free"].keys())
    j = names.index(pname)
    out = []
    zc = np.delete(z0, j)
    for v in grid:
        def f(q):
            return fit.nll(np.insert(q, j, np.log(v)), name, d, mask)
        best = None
        for s in [zc, np.delete(z0, j)]:
            r = optimize.minimize(f, s, method="Nelder-Mead",
                                  options={"maxiter": 4000, "xatol": 1e-4, "fatol": 1e-3, "adaptive": True})
            if best is None or r.fun < best.fun:
                best = r
        zc = best.x
        out.append(-best.fun)
    out = np.array(out)
    ok = out >= max(out.max(), ll0) - 1.92
    return dict(model=name, param=pname, grid=list(map(float, grid)), ll=out.tolist(), ll_best=ll0,
                best=float(th0[pname]), ci95=[float(np.min(np.array(grid)[ok])), float(np.max(np.array(grid)[ok]))])


GRIDS = {
    ("exp+diffusion", "tau"): np.exp(np.linspace(np.log(0.2), np.log(30), 25)),
    ("exp+diffusion", "As"): np.exp(np.linspace(np.log(50), np.log(1000), 21)),
    ("dieterich+diffusion", "ta"): np.exp(np.linspace(np.log(1), np.log(1e5), 21)),
    ("dieterich+diffusion", "As"): np.exp(np.linspace(np.log(5), np.log(2000), 21)),
    ("dieterich", "ta"): np.exp(np.linspace(np.log(1), np.log(1e5), 21)),
    ("exp+diffusion+cascade", "tau"): np.exp(np.linspace(np.log(0.2), np.log(30), 21)),
    ("exp+diffusion+cascade", "K"): np.exp(np.linspace(np.log(0.01), np.log(0.95), 15)),
}


def run(out="results/profiles.json"):
    d = models.Data()
    res = {f"{m}:{p}": profile(m, p, g, d=d) for (m, p), g in GRIDS.items()}
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    return res
