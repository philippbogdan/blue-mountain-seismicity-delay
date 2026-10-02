"""Earth-tide and barometric clock check for the 73-22 pressure gauge.

The gauge file is labelled PST.  A confined reservoir's pore pressure responds
to the tidal dilatation (in phase with radial uplift) with the opposite sign,
up to a modest hydraulic phase shift, and to barometric loading at once.  Both
forcings are known on UTC, so regressing the gauge record on them while
scanning a clock offset tells which clock the gauge used.
"""
import datetime as dt

import numpy as np
import pandas as pd

from . import io

SITE = (40.98, -118.12)  # paper, Fig. 1


def uplift_tide(t0, t1, step_sec=600):
    """Solid-Earth-tide radial displacement (m) at the site, UTC hours since io.T_REF."""
    import pysolid
    d, _, _, u = pysolid.calc_solid_earth_tides_point(
        SITE[0], SITE[1], t0, t1, step_sec=step_sec, verbose=False)
    h = np.array([(x - io.T_REF.to_pydatetime()).total_seconds() / 3600 for x in d])
    return h, np.asarray(u, float)


def barometer():
    """Winnemucca (KWMC, 27 km) hourly altimeter setting -> psi, UTC hours."""
    w = pd.read_csv(f"{io.ROOT}/data/external/asos_WMC_2023.csv", na_values="M")
    w = w.dropna(subset=["alti"])
    t = pd.to_datetime(w.valid)
    h = ((t - io.T_REF) / pd.Timedelta(hours=1)).to_numpy(float)
    # altimeter setting (inHg) -> station pressure variations (psi), elevation 1310 m
    return h, w.alti.to_numpy(float) * 0.4911541 * 0.86


def window_fit(a, b, offsets, deg=8, use_baro=True, dt_h=1 / 6.):
    """Regress gauge pressure in [a, b] (gauge clock) on a Legendre trend,
    the uplift tide and the barometer evaluated at UTC = gauge time - offset.
    Returns array rows (offset, tide coef psi/m, baro coef, rss, n)."""
    p = io.load_pressure()
    tg = np.arange(a, b, dt_h)
    y = np.interp(tg, p["th"], p["p"])
    s = 2 * (tg - a) / (b - a) - 1
    P = np.polynomial.legendre.legvander(s, deg)
    th_u, u = uplift_tide(io.T_REF.to_pydatetime() + dt.timedelta(hours=a - 20),
                          io.T_REF.to_pydatetime() + dt.timedelta(hours=b + 20))
    th_b, B = barometer()
    out = []
    for off in offsets:
        cols = [np.interp(tg - off, th_u, u)]
        if use_baro:
            cols.append(np.interp(tg - off, th_b, B))
        X = np.c_[P, np.array(cols).T]
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ coef
        out.append([off, coef[deg + 1], coef[deg + 2] if use_baro else np.nan,
                    float(r @ r), len(y)])
    return np.array(out)
