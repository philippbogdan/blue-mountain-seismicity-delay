"""Seismicity-rate estimation for the real-time catalogue.

Two properties of the catalogue shape every rate estimate:
* events carry the start time of their 1-minute DAS file, and no file holds
  more than one event (no duplicate time stamps among 13,351 events), so the
  catalogue is an occupancy record on a 1-minute grid: P(file occupied) =
  1 - exp(-lambda * dt) for a Poisson rate lambda;
* the system had outages (gaps of hours with no events at rates of 5-35/h);
  minutes inside an outage are unobserved, not empty.
"""
import numpy as np

from . import io

FILE_H = 1 / 60.0          # file length (h)
OUTAGE_H = 1.0             # a gap longer than this is treated as an outage


def minute_grid(t0, t1, cat=None, outage_h=OUTAGE_H):
    """Minute-resolution occupancy on the catalogue clock between t0 and t1 (h).

    Returns (tm, occ, obs): file start times, 1 if a catalogued event fell in
    the file, 1 if the file is observed (not inside an outage)."""
    if cat is None:
        cat = io.load_catalog()
    t = cat.th.to_numpy()
    tm = np.arange(np.floor(t0 * 60), np.ceil(t1 * 60)) / 60.0
    k = np.floor(t * 60 + 1e-6) - np.floor(t0 * 60)
    k = k[(k >= 0) & (k < len(tm))].astype(int)
    occ = np.zeros(len(tm), int)
    occ[k] = 1
    obs = np.ones(len(tm), bool)
    gaps = np.flatnonzero(np.diff(t) > outage_h)
    for i in gaps:
        a, b = t[i], t[i + 1]
        obs[(tm > a + FILE_H / 2) & (tm < b - FILE_H / 2)] = False
    obs[tm < t[0]] = False
    obs[tm > t[-1]] = False
    return tm, occ, obs


def binned_rate(tm, occ, obs, edges):
    """Saturation-corrected rate (events/h) per bin with a 68% interval.

    lambda = -ln(1 - k/n) / dt for k occupied of n observed files."""
    idx = np.digitize(tm, edges) - 1
    nb = len(edges) - 1
    n = np.bincount(idx[obs & (idx >= 0) & (idx < nb)], minlength=nb).astype(float)
    k = np.bincount(idx[obs & (occ > 0) & (idx >= 0) & (idx < nb)], minlength=nb).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        f = np.where(n > 0, k / n, np.nan)
        lam = -np.log1p(-np.clip(f, 0, 1 - 1e-9)) / FILE_H
        se = np.sqrt(np.clip(f * (1 - f), 1e-12, None) / np.maximum(n, 1))
        lo = -np.log1p(-np.clip(f - se, 0, 1 - 1e-9)) / FILE_H
        hi = -np.log1p(-np.clip(f + se, 0, 1 - 1e-9)) / FILE_H
    return lam, lo, hi, n, k
