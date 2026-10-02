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
