"""Loaders for the OSF D65BA data set (doi:10.17605/OSF.IO/D65BA).

All times are returned as float hours since T_REF on each file's *own* clock;
the relation between clocks is established in blm.timebase, not assumed here.
"""
import gzip
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "osf-d65ba")
CACHE = os.path.join(ROOT, ".tmp")
T_REF = pd.Timestamp("2023-04-29 00:00:00")  # naive reference instant on each clock


def hours(t):
    """Naive timestamps -> float hours since T_REF."""
    t = pd.to_datetime(t)
    return (t - T_REF) / pd.Timedelta(hours=1)


def load_catalog():
    """Full real-time catalogue (13,351 events), catalogue clock."""
    c = pd.read_csv(os.path.join(DATA, "BM_event_DAS_edgeproc_catalog.txt"))
    c["time"] = pd.to_datetime(c.t0, format="%d-%b-%Y %H:%M:%S")
    c["th"] = hours(c.time).astype(float)
    c = c.rename(columns={"Loc_x": "x", "Loc_y": "z", "Magnitude": "mag"})
    return c[["Event_no", "time", "th", "x", "z", "mag"]]


def load_flex():
    """Cycling-period events with vertical distance from the injector (Fig. 6a)."""
    f = pd.read_csv(os.path.join(DATA, "Vertical_distance_from_injection_FLEX.txt"))
    f["time"] = pd.to_datetime(f.t0, format="%d-%b-%Y %H:%M:%S")
    f["th"] = hours(f.time).astype(float)
    f = f.rename(columns={"Vertical_distance_from_injection": "dv"})
    return f[["Event_no", "time", "th", "dv"]]


def load_diffusion_curves():
    """Curves stored in Diffusion_data.mat, one value per FLEX event."""
    import scipy.io as sio

    m = sio.loadmat(os.path.join(DATA, "Diffusion_data.mat"))
    out = {k: np.asarray(m[k], float).ravel()
           for k in ["Vertical_distance_from_injection", "yp_Upper_curve",
                     "yp_uncert_1", "yp_uncert_2"]}
    return out


def _cached(name, builder):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name + ".npz")
    if os.path.exists(path):
        z = np.load(path)
        return {k: z[k] for k in z.files}
    d = builder()
    np.savez(path, **d)
    return d


def load_pressure():
    """73-22 gauge: th (h, gauge clock labelled PST), p (psig), T (degF)."""
    def build():
        with gzip.open(os.path.join(DATA, "Pressure_Time_Series.txt.gz"), "rt") as fh:
            d = pd.read_csv(fh)
        t = pd.to_datetime(d.iloc[:, 0], format="%Y-%m-%d %H:%M:%S")
        return {"th": hours(t).to_numpy(float), "T": d.iloc[:, 1].to_numpy(float),
                "p": d.iloc[:, 2].to_numpy(float)}
    return _cached("pressure", build)


def load_rates():
    """Injection / production rates (gpm), rate-file clock (zone not stated)."""
    def build():
        with gzip.open(os.path.join(DATA, "Injection_Production_Rate_Time_Series.txt.gz"), "rt") as fh:
            d = pd.read_csv(fh)
        t = pd.to_datetime(d.iloc[:, 0], format="%m/%d/%Y %I:%M:%S %p")
        return {"th": hours(t).to_numpy(float), "qi": d.iloc[:, 1].to_numpy(float),
                "qp": d.iloc[:, 2].to_numpy(float)}
    return _cached("rates", build)
