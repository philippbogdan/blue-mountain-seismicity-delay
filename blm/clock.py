"""Which clock does each file use?

Evidence assembled here (numbers go to results/clock.json):
  1. Earth tide in the 73-22 gauge (pre-stimulation quiet window): the gauge
     pressure must fall when the tidal dilatation (in phase with radial uplift)
     rises; regressing the record on the UTC tide and the UTC barometer while
     scanning the gauge offset g (gauge clock = UTC + g) gives a profile
     likelihood for g, with a moving-block bootstrap interval.
  2. Operating schedule: the cycle ramp starts and production restarts read
     off the gauge, expressed in local time under each hypothesis.
  3. Catalogue outages: the hour at which the real-time system came back.
  4. Rate file: offsets between its shut-ins/restarts and the gauge's.
"""
import datetime as dt

import numpy as np
import pandas as pd

from . import io, models, tides

QUIET = (-1070.0, -956.5)   # 15-20 March, before the 34-22 stimulation reached 73-22


def _design(a, b, deg, dt_h=1 / 6.0):
    p = io.load_pressure()
    tg = np.arange(a, b, dt_h)
    y = np.interp(tg, p["th"], p["p"])
    s = 2 * (tg - a) / (b - a) - 1
    P = np.polynomial.legendre.legvander(s, deg)
    t0 = io.T_REF.to_pydatetime() + dt.timedelta(hours=a - 24)
    t1 = io.T_REF.to_pydatetime() + dt.timedelta(hours=b + 24)
    thu, u = tides.uplift_tide(t0, t1)
    thb, B = tides.barometer()
    return tg, y, P, (thu, u), (thb, B)


def tide_profile(a=QUIET[0], b=QUIET[1], deg=6, offsets=np.arange(-12, 12.001, 0.05),
                 baro=True, n_boot=300, block_h=12.0, seed=1):
    tg, y, P, (thu, u), (thb, B) = _design(a, b, deg)

    def solve(off, yy):
        cols = [np.interp(tg - off, thu, u)]
        if baro:
            cols.append(np.interp(tg - off, thb, B))
        X = np.c_[P, np.array(cols).T]
        coef, *_ = np.linalg.lstsq(X, yy, rcond=None)
        r = yy - X @ coef
        return coef[P.shape[1]], float(r @ r), X @ coef

    rows = np.array([[o, *solve(o, y)[:2]] for o in offsets])
    phys = rows[:, 1] < 0                       # pressure falls with dilatation
    ib = int(np.argmin(np.where(phys, rows[:, 2], np.inf)))
    off_best = rows[ib, 0]
    c_best, rss_best, fitted = solve(off_best, y)
    res = y - fitted
    rho = float(np.corrcoef(res[:-1], res[1:])[0, 1])
    n = len(y)
    n_eff = n * (1 - rho) / (1 + rho)
    dlogL = 0.5 * n_eff * np.log(rows[:, 2] / rss_best)   # >0: worse than best

    # moving-block bootstrap of the residuals around the best physical fit
    rng = np.random.default_rng(seed)
    L = int(round(block_h * 6))
    boots = []
    fine = np.arange(off_best - 6, off_best + 6.001, 0.05)
    for _ in range(n_boot):
        idx = np.concatenate([np.arange(s, s + L) for s in rng.integers(0, n - L, n // L + 1)])[:n]
        yb = fitted + res[idx]
        rr = np.array([[o, *solve(o, yb)[:2]] for o in fine])
        ok = rr[:, 1] < 0
        boots.append(rr[int(np.argmin(np.where(ok, rr[:, 2], np.inf))), 0])
    boots = np.array(boots)

    def at(g):
        k = int(np.argmin(np.abs(rows[:, 0] - g)))
        return dict(offset_h=g, dlogL=float(dlogL[k]), tide_coef_psi_per_m=float(rows[k, 1]),
                    physical_sign=bool(rows[k, 1] < 0), rss_ratio=float(rows[k, 2] / rss_best))

    # with the physical sign imposed, an offset whose best coefficient is positive
    # collapses to 'no tide': compare that against the best physical fit
    Xn = P if not baro else np.c_[P, np.interp(tg - off_best, thb, B)]
    cn, *_ = np.linalg.lstsq(Xn, y, rcond=None)
    rss_none = float(np.sum((y - Xn @ cn) ** 2))
    dlogL_no_tide = float(0.5 * n_eff * np.log(rss_none / rss_best))
    ub = np.interp(tg - off_best, thu, u)
    tide_amp = float(abs(c_best) * 0.5 * (ub.max() - ub.min()))
    return dict(window_h=[a, b], legendre_deg=deg, barometer=baro, n=n, lag1_rho=rho,
                dlogL_no_tide=dlogL_no_tide, tide_amplitude_psi=tide_amp,
                n_eff=n_eff, best_offset_h=float(off_best), tide_coef_psi_per_m=float(c_best),
                boot_ci68=[float(np.percentile(boots, 16)), float(np.percentile(boots, 84))],
                boot_ci95=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                hypotheses={"UTC": at(0.0), "PDT(UTC-7)": at(-7.0), "PST(UTC-8)": at(-8.0)},
                profile=rows[:, [0, 2]].tolist())


def schedule():
    """Ramp starts and production restarts (gauge kinks) in local time."""
    out = []
    for name, s, e in models.CYCLES:
        ts, te = io.T_REF + pd.Timedelta(hours=s), io.T_REF + pd.Timedelta(hours=e)
        out.append(dict(cycle=name, ramp_start_gauge=str(ts), restart_gauge=str(te),
                        duration_h=round(e - s, 2),
                        local_if_gauge_UTC=[str(ts - pd.Timedelta(hours=7))[11:16],
                                            str(te - pd.Timedelta(hours=7))[11:16]],
                        local_if_gauge_PST=[str(ts + pd.Timedelta(hours=1))[11:16],
                                            str(te + pd.Timedelta(hours=1))[11:16]]))
    return out


def restarts(min_gap_h=2.0):
    """Hour of day (catalogue clock) at which the system came back after outages."""
    c = io.load_catalog()
    t = c.th.to_numpy()
    g = np.diff(t)
    idx = np.flatnonzero(g > min_gap_h)
    hours = np.mod(t[idx + 1], 24.0)
    ang = 2 * np.pi * hours / 24
    C, S = np.cos(ang).mean(), np.sin(ang).mean()
    Rbar = np.hypot(C, S)
    n = len(hours)
    z = n * Rbar ** 2
    p_rayleigh = float(np.exp(-z) * (1 + (2 * z - z ** 2) / (4 * n)))  # Zar's approximation
    mean_h = float(np.mod(np.arctan2(S, C) * 24 / (2 * np.pi), 24))
    return dict(n=n, end_hours_catalogue_clock=[round(float(h), 2) for h in hours],
                frac_13_to_15=float(np.mean((hours >= 13) & (hours < 15))),
                mean_hour=mean_h, Rbar=float(Rbar), p_rayleigh=p_rayleigh,
                mean_hour_if_UTC={"Nevada PDT": (mean_h - 7) % 24, "Houston CDT": (mean_h - 5) % 24},
                mean_hour_if_PDT={"Nevada PDT": mean_h, "Houston CDT": (mean_h + 2) % 24})


# Rate-file events matched by eye to sharp gauge kinks (rate clock vs gauge clock, h)
RATE_EVENTS = [
    ("double shut-in (inj+prod stop)", -273.4, -270.3),
    ("double restart", -264.0, -261.0),
    ("production stop", -146.5, -146.85),
    ("cycle IV shut-in", 116.45, 111.42),
    ("cycle IV restart", 124.6, 122.17),
    ("cycle V shut-in", 141.25, 135.75),
    ("cycle V restart", 150.1, 146.25),
]


def rate_file_offsets():
    return [dict(event=e, rate_clock_h=a, gauge_clock_h=b, offset_h=round(a - b, 2))
            for e, a, b in RATE_EVENTS]


def run(out="results/clock.json"):
    import json
    res = dict(tide=tide_profile(), tide_no_baro=tide_profile(baro=False, n_boot=100),
               tide_second_half=tide_profile(a=-1013.0, b=QUIET[1], deg=4, n_boot=100),
               schedule=schedule(), restarts=restarts(), rate_file=rate_file_offsets(),
               regional=regional(), wind=wind(), volumes=volumes())
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    return res


def regional(offsets=(0, -7, -8, 7, 8), amp_min=-1.8):
    """Are regional earthquakes (USGS ComCat, UTC) in the catalogue under any clock?
    For events whose expected DAS amplitude proxy 0.69 M - 1.588 log10(R km) exceeds
    amp_min, count catalogue events in the 1-minute file holding the S arrival."""
    e = pd.read_csv(f"{io.ROOT}/data/external/usgs_400km_M1.5.csv")
    lat0, lon0 = tides.SITE
    p1, p2 = np.radians(lat0), np.radians(e.latitude)
    dkm = 6371 * np.arccos(np.clip(np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2)
                                   * np.cos(np.radians(e.longitude - lon0)), -1, 1))
    hyp = np.sqrt(dkm ** 2 + (e.depth + 2.7) ** 2)
    amp = 0.69 * e.mag - 1.588 * np.log10(hyp)
    t = pd.to_datetime(e.time).dt.tz_localize(None) + pd.to_timedelta(hyp / 3.5, unit="s")
    sel = amp > amp_min
    c = io.load_catalog()
    ct = c.time.values.astype("datetime64[s]").astype(np.int64)
    out = {}
    for off in offsets:
        ts = (t[sel] + pd.Timedelta(hours=off)).values.astype("datetime64[s]").astype(np.int64)
        ts = ts[(ts > ct.min()) & (ts < ct.max())]
        hits = sum(bool(np.any((ct > s - 62) & (ct <= s + 1))) for s in ts)
        out[f"{off:+d}"] = [int(hits), int(len(ts))]
    # base rate: fraction of catalogue-span minutes holding an event
    span = (ct.max() - ct.min()) / 60
    return dict(hits_by_offset=out, base_rate=float(len(ct) / span), amp_min=amp_min)


def wind(offsets=range(-12, 13)):
    """Correlation of hourly detection anomalies with Winnemucca wind speed (UTC)."""
    w = pd.read_csv(f"{io.ROOT}/data/external/asos_WMC_2023.csv", na_values=["M", "T"])
    w = w.dropna(subset=["sknt"])
    wh = np.floor(((pd.to_datetime(w.valid) - io.T_REF) / pd.Timedelta(hours=1)).to_numpy())
    W = pd.Series(w.sknt.to_numpy()).groupby(wh).mean()
    c = io.load_catalog()
    t = c.th.to_numpy()
    hb = np.arange(np.floor(t.min()), np.ceil(t.max()))
    cnt, _ = np.histogram(t, bins=np.r_[hb, hb[-1] + 1])
    valid = np.ones(len(hb), bool)
    for i in np.flatnonzero(np.diff(t) > 1.5):
        valid[(hb >= t[i]) & (hb + 1 <= t[i + 1])] = False
    valid &= (hb > -850) & ~((hb > 0) & (hb < 200))
    base = pd.Series(cnt.astype(float)).rolling(49, center=True, min_periods=10).median().to_numpy()
    out = {}
    for off in offsets:
        ws = W.reindex(hb - off).to_numpy()
        m = valid & np.isfinite(ws) & np.isfinite(base)
        out[f"{off:+d}"] = float(np.corrcoef(ws[m], (cnt - base)[m])[0, 1])
    return dict(corr_by_offset=out, max_abs=float(max(abs(v) for v in out.values())))


def volumes():
    """Injected and produced volumes from the rate file (gpm -> m3)."""
    r = io.load_rates()
    dt_min = float(np.median(np.diff(r["th"])) * 60)
    gal = 3.785411784e-3
    return dict(injected_m3=float(np.sum(r["qi"]) * dt_min * gal), produced_m3=float(np.sum(r["qp"]) * dt_min * gal),
                paper_injected_m3=1.35e5, paper_produced_m3=1.07e5)
