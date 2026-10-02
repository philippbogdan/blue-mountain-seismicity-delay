"""Model-independent description of the seismicity response to each cycle.

For every cycle (ramp start s, pressure peak e on the gauge clock = UTC) and
every event class (all; catalogue depth classes; radial classes):
  baseline   saturation-corrected rate in [s-3 h, s)
  excess     events above baseline in [s, s+22 h)
  lags       centroid lag   (excess-rate centroid minus pressure-rise centroid)
             peak lag       (3-h smoothed rate maximum minus pressure peak e)
             xcorr lag      (lag maximising corr(rate(t), p_g(t - lag)), 0-12 h)
  loading    pressure rise, mean and maximum dp/dt over the ramp
Uncertainties: parametric bootstrap of the minute occupancy record from the
smoothed observed rate (block structure kept by resampling 30-min blocks).
"""
import json

import numpy as np

from . import io, models, rates

CLASSES = {
    "all": lambda c: np.ones(len(c), bool),
    "shallow z<=2760": lambda c: (c.z <= 2760).to_numpy(),
    "mid 2800-2960": lambda c: ((c.z >= 2800) & (c.z <= 2960)).to_numpy(),
    "deep z>=3000": lambda c: (c.z >= 3000).to_numpy(),
    "radial x<=880": lambda c: (c.x <= 880).to_numpy(),
    "radial x>=1000": lambda c: (c.x >= 1000).to_numpy(),
}
BIN_H = 0.5


def _series(cls="all", t0=-10.0, t1=200.0):
    c = io.load_catalog()
    tm, occ_all, obs = rates.minute_grid(t0, t1, cat=c)
    sel = c[CLASSES[cls](c)]
    _, occ, _ = rates.minute_grid(t0, t1, cat=sel)
    return tm, occ, obs


def _rate_bins(tm, occ, obs, edges):
    lam, lo, hi, n, k = rates.binned_rate(tm, occ, obs, edges)
    return lam, n


def _metrics(tm, occ, obs, p_t, p, s, e):
    edges = np.arange(s - 3.0, s + 22.0 + 1e-9, BIN_H)
    lam, n = _rate_bins(tm, occ, obs, edges)
    cen = 0.5 * (edges[1:] + edges[:-1])
    ok = n >= 10
    base_m = (cen < s) & ok
    base = np.nanmean(lam[base_m]) if base_m.any() else np.nan
    post = (cen >= s) & ok
    exc = np.where(post, lam - base, 0.0)
    pg = np.interp(cen, p_t, p)
    dpr = np.clip(pg - np.interp(s, p_t, p), 0, None) * (cen >= s)
    w = np.clip(exc, 0, None)
    cen_lag = (np.sum(w * cen) / w.sum() - np.sum(dpr * cen) / dpr.sum()) if w.sum() > 0 else np.nan
    # 3-h smoothed rate peak (only bins with enough observation)
    k = int(round(3.0 / BIN_H))
    lam_f = np.where(ok, lam, np.nan)
    sm = np.array([np.nanmean(lam_f[max(0, i - k // 2): i + k // 2 + 1]) for i in range(len(lam_f))])
    sm[~post] = -np.inf
    peak_lag = cen[int(np.nanargmax(sm))] - e if np.isfinite(sm).any() else np.nan
    # cross-correlation lag with the gauge pressure
    lags = np.arange(0, 12.01, BIN_H)
    cc = []
    for L in lags:
        pl = np.interp(cen - L, p_t, p)
        m = ok & (cen >= s)
        cc.append(np.corrcoef(lam[m], pl[m])[0, 1] if m.sum() > 5 else np.nan)
    cc = np.array(cc)
    xlag = lags[int(np.nanargmax(cc))] if np.isfinite(cc).any() else np.nan
    excess_events = float(np.nansum(exc[post] * BIN_H))
    return dict(baseline=float(base), excess_events=excess_events, centroid_lag_h=float(cen_lag),
                peak_lag_h=float(peak_lag), xcorr_lag_h=float(xlag), xcorr_max=float(np.nanmax(cc)))


def loading(p_t, p, s, e):
    tt = np.arange(s, e, 1 / 12)
    pp = np.interp(tt, p_t, p)
    dpdt = np.gradient(pp, tt)
    return dict(ramp_h=round(e - s, 2), dp_psi=float(pp[-1] - pp[0]), mean_dpdt=float((pp[-1] - pp[0]) / (e - s)),
                max_dpdt_1h=float(np.max(np.convolve(dpdt, np.ones(12) / 12, mode="valid"))),
                dp_above_prior_max_psi=float(pp[-1] - np.max(np.interp(np.arange(-96, s, 0.1), p_t, p))))


def run(n_boot=200, seed=0, out="results/response.json"):
    P = io.load_pressure()
    rng = np.random.default_rng(seed)
    res = {"loading": {c: loading(P["th"], P["p"], s, e) for c, s, e in models.CYCLES}, "classes": {}}
    for cls in CLASSES:
        tm, occ, obs = _series(cls)
        # smooth rate for the parametric bootstrap (1-h running mean of occupancy)
        k = 60
        pr = np.convolve(np.where(obs, occ, 0), np.ones(k), "same") / np.maximum(
            np.convolve(obs.astype(float), np.ones(k), "same"), 1)
        out_c = {}
        for c, s, e in models.CYCLES:
            m0 = _metrics(tm, occ, obs, P["th"], P["p"], s, e)
            boots = []
            for _ in range(n_boot):
                ob = (rng.random(len(pr)) < pr).astype(int)
                boots.append(_metrics(tm, ob, obs, P["th"], P["p"], s, e))
            ci = {key: [float(np.nanpercentile([b[key] for b in boots], q)) for q in (16, 84)]
                  for key in ["centroid_lag_h", "peak_lag_h", "xcorr_lag_h", "excess_events"]}
            out_c[c] = dict(m0, ci68=ci)
        res["classes"][cls] = out_c
    res["step_tests"] = step_tests()
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    return res


def step_tests(win_h=3.0):
    """Rate (saturation-corrected) in the win_h hours before and after each
    shut-in (ramp start) and restart (pressure peak), occupancy likelihood-ratio
    test of equal rates, and a two-sample KS test of the magnitudes (a detection
    change would shift them)."""
    from scipy import stats
    c = io.load_catalog()
    tm, occ, obs = rates.minute_grid(-10.0, 220.0, cat=c)

    def win(a, b):
        m = (tm >= a) & (tm < b) & obs
        n, k = int(m.sum()), int(occ[m].sum())
        lam = float(-np.log(1 - k / n) * 60) if 0 < k < n else float("nan")
        mags = c.mag[(c.th >= a) & (c.th < b)].to_numpy()
        return n, k, lam, mags

    def ll(k, n, p):
        return k * np.log(p) + (n - k) * np.log(1 - p)

    out = {}
    for name, s, e in models.CYCLES:
        for kind, t0 in [("shut-in", s), ("restart", e)]:
            n1, k1, l1, m1 = win(t0 - win_h, t0)
            n2, k2, l2, m2 = win(t0, t0 + win_h)
            p0 = (k1 + k2) / (n1 + n2)
            LR = 2 * (ll(k1, n1, k1 / n1) + ll(k2, n2, k2 / n2) - ll(k1, n1, p0) - ll(k2, n2, p0))
            out[f"{name}:{kind}"] = dict(rate_before=l1, rate_after=l2, p_rate=float(stats.chi2.sf(LR, 1)),
                                         p_mag_ks=float(stats.ks_2samp(m1, m2).pvalue))
    return out
