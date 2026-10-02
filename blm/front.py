"""The published diffusion front (paper Fig. 6a; OSF Diffusion_data.mat).

1. identify    the stored 'best-fit synthetic diffusion curve' exactly
2. conventions what diffusivity that curve implies under r = sqrt(4 D t) and the
               paper's printed r = sqrt(4 pi D t)
3. refit       fronts fitted to the published (t, distance) pairs themselves
4. artefact    the published distances against the catalogue's own locations:
               within one 40-m catalogue cell the published distance grows with time
5. stationary  the catalogue's depth / radial-distance distribution over the cycles
"""
import json

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from . import io

T0_PUB = 18.95028           # origin of the stored curve (h since 29 Apr 00:00, catalogue clock)
Z_INJ = 2336.0              # 34A-22 TVD, 7,664 ft (Fercho et al. 2023)


def _matched():
    """FLEX events joined to the catalogue events with the same time stamp."""
    c, f = io.load_catalog(), io.load_flex()
    ct = c.time.values.astype("datetime64[s]").astype(np.int64)
    ft = f.time.values.astype("datetime64[s]").astype(np.int64)
    i = np.clip(np.searchsorted(ct, ft), 1, len(ct) - 1)
    j = np.where(np.abs(ct[i] - ft) < np.abs(ct[i - 1] - ft), i, i - 1)
    ok = np.abs(ct[j] - ft) <= 30
    m = pd.DataFrame({"t": f.th.values[ok], "dv": f.dv.values[ok], "x": c.x.values[j[ok]],
                      "z": c.z.values[j[ok]], "i": np.arange(len(f))[ok]})
    m["cell"] = m.x.astype(str) + "_" + m.z.astype(str)
    return m, int((~ok).sum()), len(f)


def identify():
    d, t = io.load_diffusion_curves(), io.load_flex().th.values
    out = {}
    for k in ["yp_Upper_curve", "yp_uncert_1", "yp_uncert_2"]:
        y = d[k]
        s = least_squares(lambda p: p[0] * np.clip(t - p[1], 1e-9, None) ** p[2] - y,
                          [90, 18.9, 0.47])
        out[k] = dict(a_m_per_h_n=float(s.x[0]), t0_h=float(s.x[1]), n=float(s.x[2]),
                      t0_utc=str(io.T_REF + pd.Timedelta(hours=float(s.x[1]))),
                      rms_m=float(np.sqrt(np.mean(s.fun ** 2))),
                      max_abs_m=float(np.abs(s.fun).max()))
    return out


def conventions():
    """Diffusivity implied by the stored best curve."""
    d, t = io.load_diffusion_curves(), io.load_flex().th.values
    y = d["yp_Upper_curve"]
    ts = (t - T0_PUB) * 3600.0
    end = dict(r_m=float(y[-1]), t_s=float(ts[-1]),
               D_4Dt=float(y[-1] ** 2 / (4 * ts[-1])), D_4piDt=float(y[-1] ** 2 / (4 * np.pi * ts[-1])))
    # least squares in r with t0 fixed at the curve origin
    D4 = least_squares(lambda p: np.sqrt(4 * p[0] * ts) - y, [0.4]).x[0]
    # least squares with t0 free
    s = least_squares(lambda p: np.sqrt(4 * p[0] * np.clip(ts - p[1] * 3600, 0, None)) - y, [0.4, 0.0])
    # linear r^2 = 4 D (t - t0)
    A = np.c_[ts, np.ones_like(ts)]
    co, *_ = np.linalg.lstsq(A, y ** 2, rcond=None)
    vals = {"endpoint": end["D_4Dt"], "lsq_r_t0fixed": float(D4), "lsq_r_t0free": float(s.x[0]),
            "lsq_r2_linear": float(co[0] / 4)}
    return dict(endpoint=end, D_4Dt=vals, D_4piDt={k: v / np.pi for k, v in vals.items()},
                published_D=0.43)


def refit(t0=T0_PUB, qs=(0.5, 0.75, 0.9), bin_h=6.0):
    """Fronts r = sqrt(4 D (t - t0)) fitted to quantiles of the published distances
    in time bins, and the same with the paper's printed sqrt(4 pi D t)."""
    f = io.load_flex()
    t, r = f.th.values, f.dv.values
    edges = np.arange(t.min(), t.max() + bin_h, bin_h)
    out = {}
    for q in qs:
        tc, rq = [], []
        for a, b in zip(edges[:-1], edges[1:]):
            s = (t >= a) & (t < b)
            if s.sum() >= 10:
                tc.append(np.median(t[s]))
                rq.append(np.quantile(r[s], q))
        tc, rq = np.array(tc), np.array(rq)
        ts = (tc - t0) * 3600
        D = least_squares(lambda p: np.sqrt(4 * p[0] * ts) - rq, [0.4]).x[0]
        res = rq - np.sqrt(4 * D * ts)
        out[f"q{int(q * 100)}"] = dict(D_4Dt=float(D), D_4piDt=float(D / np.pi),
                                       rms_m=float(np.sqrt(np.mean(res ** 2))), n_bins=len(tc))
    return out


def artefact():
    m, n_unmatched, n_flex = _matched()
    rows = []
    for cell, g in m.groupby("cell"):
        if len(g) < 12:
            continue
        A = np.c_[g.t, np.ones(len(g))]
        co, *_ = np.linalg.lstsq(A, g.dv, rcond=None)
        rows.append(dict(cell=cell, n=len(g), slope_m_per_h=float(co[0]),
                         corr_t=float(np.corrcoef(g.t, g.dv)[0, 1]), sd_dv=float(g.dv.std())))
    R = pd.DataFrame(rows)
    # fixed effects: cell + piecewise-linear time (30 knots); and cell only
    X1 = pd.get_dummies(pd.Categorical(m.cell)).values.astype(float)
    kn = np.quantile(m.t, np.linspace(0, 1, 31))[:-1]
    B = np.c_[[np.clip(m.t.values - k, 0, None) for k in kn]].T
    def resid(X):
        co, *_ = np.linalg.lstsq(X, m.dv.values, rcond=None)
        return m.dv.values - X @ co, co
    r_cell, _ = resid(X1)
    r_both, co = resid(np.c_[X1, B])
    # common time effect on a grid
    tg = np.arange(20, 200, 2.0)
    Bg = np.c_[[np.clip(tg - k, 0, None) for k in kn]].T
    h = Bg @ co[X1.shape[1]:]
    return dict(n_flex=n_flex, n_matched=len(m), n_unmatched=n_unmatched,
                cells_with_12plus=len(R), median_within_cell_slope_m_per_h=float(R.slope_m_per_h.median()),
                frac_cells_positive_slope=float((R.slope_m_per_h > 0).mean()),
                median_within_cell_corr=float(R.corr_t.median()),
                sd_dv_total=float(m.dv.std()), sd_resid_cell_only=float(r_cell.std()),
                sd_resid_cell_plus_time=float(r_both.std()),
                time_effect_grid_h=tg.tolist(), time_effect_m=(h - h.mean()).tolist())


def stationarity(win_h=12.0, t_range=(15.0, 205.0)):
    """Catalogue depth / radial distance quantiles through the cycling period."""
    c = io.load_catalog()
    c = c[(c.th >= t_range[0]) & (c.th < t_range[1])].copy()
    c["w"] = np.floor((c.th - t_range[0]) / win_h).astype(int)
    c["dz"] = c.z - Z_INJ
    g = c.groupby("w").agg(t=("th", "mean"), n=("z", "size"),
                           dz50=("dz", "median"), dz90=("dz", lambda s: s.quantile(.9)),
                           x50=("x", "median"), x90=("x", lambda s: s.quantile(.9)))
    # bootstrap slope of the median depth offset (m/h)
    rng = np.random.default_rng(0)
    slopes = []
    for _ in range(500):
        b = c.sample(len(c), replace=True, random_state=int(rng.integers(1e9)))
        gb = b.groupby("w").agg(t=("th", "mean"), dz50=("dz", "median"))
        slopes.append(np.polyfit(gb.t, gb.dz50, 1)[0])
    slope = float(np.polyfit(g.t, g.dz50, 1)[0])
    # what a front with the published D would require over the same span
    span = (t_range[1] - T0_PUB) * 3600, (t_range[0] + win_h / 2 - T0_PUB) * 3600
    front_growth = {k: float(np.sqrt(4 * fac * 0.43 * span[0]) - np.sqrt(4 * fac * 0.43 * span[1]))
                    for k, fac in [("4Dt", 1.0), ("4piDt", np.pi)]}
    return dict(windows=g.round(1).reset_index().to_dict(orient="list"),
                median_dz_slope_m_per_h=slope,
                median_dz_slope_ci95=[float(np.percentile(slopes, 2.5)), float(np.percentile(slopes, 97.5))],
                implied_change_over_span_m=slope * (t_range[1] - t_range[0]),
                published_front_growth_over_span_m=front_growth)


def run(out="results/front.json"):
    res = dict(identify=identify(), conventions=conventions(), refit=refit(),
               artefact=artefact(), stationarity=stationarity())
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    return res
