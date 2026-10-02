"""Per-cycle predictive check: each cycle's response predicted by the model
fitted without that cycle (leave-one-cycle-out), against the observation.

Observed metrics come from blm.response (with bootstrap intervals); predicted
metrics are computed the same way on the model's expected rate curve.
"""
import json

import numpy as np

from . import fit, models, response


def predicted_metrics(name, theta, d, s, e):
    """Same metrics as blm.response, on the model's expected rate, using only the
    bins the catalogue observed (outage bins dropped as for the observation)."""
    R = fit.expected_rate(name, d, theta)
    edges = np.arange(s - 3.0, s + 22.0 + 1e-9, response.BIN_H)
    cen = 0.5 * (edges[1:] + edges[:-1])
    idx = np.digitize(d.t, edges) - 1
    nobs = np.bincount(idx[(idx >= 0) & (idx < len(cen)) & d.obs], minlength=len(cen))[:len(cen)]
    seen = nobs >= 10
    lam = np.interp(cen, d.t, R)
    base = lam[(cen < s) & seen].mean()
    post = (cen >= s) & seen
    exc = np.where(post, lam - base, 0.0)
    p = np.interp(cen, d.t, d.p)
    dpr = np.clip(p - np.interp(s, d.t, d.p), 0, None) * post
    w = np.clip(exc, 0, None)
    return dict(excess_events=float(np.sum(exc[post]) * response.BIN_H),
                centroid_lag_h=float(np.sum(w * cen) / w.sum() - np.sum(dpr * cen) / dpr.sum()) if w.sum() > 0 else float("nan"),
                peak_lag_h=float(cen[post][np.argmax(lam[post])] - e))


def run(val="results/validate_shift+0_out1.json", resp="results/response.json",
        model_names=("exp+diffusion+cascade", "exp+diffusion", "dieterich+diffusion", "dieterich",
                     "exp+cascade", "exp", "paper:D=0.43(4piDt)"), out="results/ppc.json"):
    res = json.load(open(val))
    by = {(r["model"], r["scheme"]): r for r in res}
    obs = json.load(open(resp))["classes"]["all"]
    d = models.Data()
    out_d = {"observed": {c: {k: obs[c][k] for k in ["excess_events", "centroid_lag_h", "peak_lag_h"]}
                          | {"ci68": obs[c]["ci68"]} for c, _, _ in models.CYCLES}}
    for name in model_names:
        out_d[name] = {c: predicted_metrics(name, by[(name, f"loco:{c}")]["theta"], d, s, e)
                       for c, s, e in models.CYCLES}
    with open(out, "w") as fh:
        json.dump(out_d, fh, indent=1)
    return out_d
