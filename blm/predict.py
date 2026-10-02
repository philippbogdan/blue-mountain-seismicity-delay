"""Seismicity response to slower pressurisation ramps.

Scenario: cycle IV as it happened, except that its ramp (ramp start 111.42 h,
355 psi over 10.75 h) is stretched by a factor s: the observed concave ramp
shape r(u), u = t / (s T), reaching the same pressure, followed by the observed
post-restart decline.  The scenario replaces the gauge history from the ramp
start onward; everything before is as observed.

Each model is run with its full-data parameters and with its five
leave-one-cycle-out parameter sets; the spread over those five refits is the
jackknife uncertainty ('five cycles are five cycles').  Metrics per scenario:
  peak_lag_h      time of the rate maximum minus time of the gauge peak
  centroid_lag_h  centroid of the excess rate minus centroid of the pressure rise
  onset_h         time from ramp start until the excess rate reaches half its peak
  peak_excess     maximum rate minus the pre-ramp rate (events/h)
  excess_events   excess events from ramp start to 24 h after the gauge peak
"""
import json

import numpy as np

from . import fit, models

S_LIST = [1, 2, 4, 8]
RAMP0, PEAK = 111.42, 122.17


def scenario(d, s, ramp0=RAMP0, peak=PEAK, shape="observed"):
    """Gauge pressure on d.t: history as observed up to cycle IV's ramp start,
    then one isolated cycle: IV's ramp (observed concave shape, or linear)
    stretched by s to the same pressure, then a decline with the shape of cycle
    V's long post-peak decline (the last cycle, no ramp after it), scaled to
    IV's amplitude."""
    t, p = d.t, d.p
    T = peak - ramp0
    p0 = np.interp(ramp0, t, p)
    dp = np.interp(peak, t, p) - p0
    u = np.linspace(0, 1, 2001)
    r = u if shape == "linear" else (np.interp(ramp0 + u * T, t, p) - p0) / dp
    v5, pk5 = 135.75, 146.25                       # cycle V ramp start and peak
    dp5 = np.interp(pk5, t, p) - np.interp(v5, t, p)
    q = p.copy()
    tt = t - ramp0
    ramp = (tt >= 0) & (tt < s * T)
    q[ramp] = p0 + dp * np.interp(tt[ramp] / (s * T), u, r)
    v = tt - s * T
    dec = v >= 0
    tmax = t[-1] - pk5
    vv = np.clip(v[dec], 0, tmax)
    q[dec] = p0 + dp + (np.interp(pk5 + vv, t, p) - np.interp(pk5, t, p)) * dp / dp5
    return q, ramp0 + s * T


def metrics(t, R, q, ramp0, tpk, horizon_h=24.0):
    pre = (t >= ramp0 - 3) & (t < ramp0)
    base = R[pre].mean()
    w = (t >= ramp0) & (t < tpk + horizon_h)
    exc = np.clip(R[w] - base, 0, None)
    tw = t[w]
    i = int(np.argmax(R[w]))
    dpr = np.clip(q[w] - q[w][0], 0, None)
    half = np.flatnonzero(exc >= 0.5 * exc.max())
    return dict(peak_lag_h=float(tw[i] - tpk),
                centroid_lag_h=float((exc * tw).sum() / exc.sum() - (dpr * tw).sum() / dpr.sum())
                if exc.sum() > 0 else float("nan"),
                onset_h=float(tw[half[0]] - ramp0) if len(half) else float("nan"),
                peak_excess=float(exc.max()), excess_events=float(exc.sum() * models.DT_H))


def run(val="results/validate_shift+0_out1.json", model_names=None, out="results/predict.json",
        shape="observed"):
    res = json.load(open(val))
    by = {(r["model"], r["scheme"]): r for r in res}
    model_names = model_names or ["exp+diffusion+cascade", "exp+diffusion", "exp+lag",
                                  "dieterich+diffusion", "dieterich",
                                  "exp+diffusion+poro", "exp+diffusion+cascade", "exp+cascade",
                                  "coulomb+diffusion", "exp", "paper:D=0.43(4piDt)", "paper:p+dp/dt"]
    d = models.Data(t1=330.0)
    p_obs = d.p.copy()
    out_d = {}
    for name in model_names:
        sets = {"full": by[(name, "full")]["theta"]}
        sets.update({c: by[(name, f"loco:{c}")]["theta"] for c in ["I", "II", "III", "IV", "V"]})
        rows = {}
        for s in S_LIST:
            q, tpk = scenario(d, s, shape=shape)
            d.p = q
            mets = {}
            for k, th in sets.items():
                R = fit.expected_rate(name, d, th)
                mets[k] = metrics(d.t, R, q, RAMP0, tpk)
            d.p = p_obs
            jk = {}
            for key in mets["full"]:
                xs = np.array([mets[c][key] for c in ["I", "II", "III", "IV", "V"]])
                se = float(np.sqrt(4 / 5 * np.sum((xs - xs.mean()) ** 2)))
                jk[key] = dict(value=mets["full"][key], jackknife_se=se,
                               loco_range=[float(xs.min()), float(xs.max())])
            rows[f"s={s}"] = jk
        out_d[name] = rows
    with open(out, "w") as fh:
        json.dump(out_d, fh, indent=1)
    return out_d
