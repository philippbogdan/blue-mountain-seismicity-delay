"""Paired comparison of held-out skill with a moving-block bootstrap.

For each model the leave-one-cycle-out fits are evaluated on their held-out
cycle; the per-minute log-likelihood terms are concatenated over the five
cycles.  For a pair (A, B) the difference series is resampled in blocks of
BLOCK_H hours (keeping event clustering and serial correlation) to give an
interval for the total and per-event held-out log-likelihood difference.
"""
import json

import numpy as np

from . import fit, models

CYC = ["I", "II", "III", "IV", "V"]
BLOCK_H = 3.0


def heldout_terms(res, name, d, scheme_prefix="loco"):
    by = {(r["model"], r["scheme"]): r for r in res}
    terms = np.zeros(len(d.t))
    mask = np.zeros(len(d.t), bool)
    for c in CYC:
        th = by[(name, f"{scheme_prefix}:{c}")]["theta"]
        R = fit.predict(name, d, th)
        m = d.mask([c])
        terms[m] = models.loglik_terms(R, d)[m]
        mask |= m
    return terms, mask


def block_bootstrap(diff, mask, n_boot=2000, block_h=BLOCK_H, seed=0):
    x = diff[mask]
    L = int(round(block_h * 60))
    nb = int(np.ceil(len(x) / L))
    blocks = np.array([x[i * L:(i + 1) * L].sum() for i in range(nb)])
    rng = np.random.default_rng(seed)
    tot = np.array([blocks[rng.integers(0, nb, nb)].sum() for _ in range(n_boot)])
    return float(x.sum()), [float(np.percentile(tot, 2.5)), float(np.percentile(tot, 97.5))], float(np.mean(tot > 0))


def run(val="results/validate_shift+0_out1.json", ref="exp+diffusion", out="results/compare.json"):
    res = json.load(open(val))
    names = sorted({r["model"] for r in res})
    d = models.Data(shift_h=res[0]["shift_h"], outage_h=res[0]["outage_h"])
    T = {n: heldout_terms(res, n, d) for n in names}
    mask = T[ref][1]
    n_ev = int(d.occ[mask & d.obs].sum())
    rows = {}
    for n in names:
        if n == ref:
            continue
        diff = T[ref][0] - T[n][0]
        tot, ci, frac = block_bootstrap(diff, mask)
        per_cycle = {c: float(diff[d.mask([c])].sum()) for c in CYC}
        rows[n] = dict(dll_total=tot, ci95=ci, frac_boot_ref_better=frac,
                       dll_per_event=tot / n_ev, per_cycle=per_cycle)
    out_d = dict(reference=ref, heldout_events=n_ev, block_h=BLOCK_H, versus=rows)
    with open(out, "w") as fh:
        json.dump(out_d, fh, indent=1)
    return out_d
