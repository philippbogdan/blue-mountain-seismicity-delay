"""Model-free lag between seismicity and gauge pressure (cycling period).

Saturation-corrected rate in 30-min bins (unobserved bins dropped) is
correlated with the gauge pressure shifted by L; the lag maximising the
correlation is reported for all events and per depth class, with a
moving-block bootstrap (6-h blocks) interval.  The relative lag between
depth classes does not depend on the clock offset between the files; the
absolute lag does (catalogue clock = gauge clock + shift).
"""
import json

import numpy as np

from . import io, rates

BIN = 0.5
WINDOW = (30.0, 200.0)
LAGS = np.arange(-15, 15.01, 0.25)
CLASSES = {"all": lambda c: np.ones(len(c), bool), "shallow": lambda c: (c.z <= 2760).to_numpy(),
           "mid": lambda c: ((c.z >= 2800) & (c.z <= 2960)).to_numpy(), "deep": lambda c: (c.z >= 3000).to_numpy()}


def series(cls, shift_h=0.0):
    c = io.load_catalog()
    a, b = WINDOW
    tm, _, obs = rates.minute_grid(a + shift_h, b + shift_h, cat=c)
    _, occ, _ = rates.minute_grid(a + shift_h, b + shift_h, cat=c[CLASSES[cls](c)])
    edges = np.arange(a + shift_h, b + shift_h + 1e-9, BIN)
    lam, lo, hi, n, k = rates.binned_rate(tm, occ, obs, edges)
    t = 0.5 * (edges[1:] + edges[:-1]) - shift_h        # gauge clock
    ok = n >= 20
    return t[ok], lam[ok]


def xcorr(t, lam, P):
    out = []
    for L in LAGS:
        pl = np.interp(t - L, P["th"], P["p"])
        out.append(np.corrcoef(lam, pl)[0, 1])
    return np.array(out)


def run(shifts=(0.0, 8.0, 7.0, -7.0), n_boot=300, seed=0, out="results/xcorr.json"):
    P = io.load_pressure()
    rng = np.random.default_rng(seed)
    res = {}
    for sh in shifts:
        res[f"{sh:+g}"] = {}
        for cls in CLASSES:
            t, lam = series(cls, sh)
            cc = xcorr(t, lam, P)
            L0 = float(LAGS[np.argmax(cc)])
            nb = int(6 / BIN)
            starts = np.arange(0, len(t) - nb)
            boots = []
            for _ in range(n_boot):
                idx = np.concatenate([np.arange(s, s + nb) for s in rng.choice(starts, len(t) // nb)])
                boots.append(LAGS[np.argmax(xcorr(t[idx], lam[idx], P))])
            res[f"{sh:+g}"][cls] = dict(peak_lag_h=L0, peak_r=float(cc.max()),
                                        ci95=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))])
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    return res
