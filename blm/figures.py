"""Figures for FINDINGS.md / REPORT.md, regenerated from results/*.json."""
import datetime as dt
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import clock, design, fit, front, io, models, predict, rates, tides  # noqa: E402

F = "figs"
R = "results"


def _j(name):
    return json.load(open(os.path.join(R, name)))


def fig_clock():
    tg, y, P, (thu, u), (thb, B) = clock._design(*clock.QUIET, 6)
    c, *_ = np.linalg.lstsq(P, y, rcond=None)
    yr = y - P @ c
    fig, ax = plt.subplots(3, 1, figsize=(10, 9))
    for g, col, lab in [(0, "r", "UTC"), (-8, "b", "PST (label)")]:
        uu = np.interp(tg - g, thu, u)
        cu, *_ = np.linalg.lstsq(P, uu, rcond=None)
        ur = uu - P @ cu
        ax[0].plot(tg, -ur / ur.std() * yr.std(), col, lw=1, label=f"-(tidal uplift), gauge = {lab}")
    ax[0].plot(tg, yr, "k", lw=1, label="73-22 gauge, detrended")
    ax[0].set_xlabel("h since 29 Apr 00:00 (gauge clock)")
    ax[0].set_ylabel("psi")
    ax[0].legend(fontsize=7)
    ax[0].set_title("Earth tide in the gauge, 15-20 March (pressure must fall when the ground dilates)")
    prof = np.array(_j("clock.json")["tide"]["profile"])
    ax[1].plot(prof[:, 0], prof[:, 1] / prof[:, 1].min(), "k")
    for g, lab in [(0, "UTC"), (-7, "PDT"), (-8, "PST")]:
        ax[1].axvline(g, ls="--", color="gray")
        ax[1].text(g, ax[1].get_ylim()[1] * 0.98, lab, ha="center", fontsize=8)
    ax[1].set_xlabel("assumed gauge offset from UTC (h)")
    ax[1].set_ylabel("RSS / min")
    sch = _j("clock.json")["schedule"]
    for i, s in enumerate(sch):
        for k, col in [("local_if_gauge_UTC", "r"), ("local_if_gauge_PST", "b")]:
            a, b = [int(x[:2]) + int(x[3:]) / 60 for x in s[k]]
            b = b + 24 if b < a else b
            ax[2].plot([a, b], [i + (0.15 if col == "r" else -0.15)] * 2, col, lw=6,
                       label=("gauge UTC" if col == "r" else "gauge PST") if i == 0 else None)
    ax[2].set_yticks(range(len(sch)))
    ax[2].set_yticklabels([s["cycle"] for s in sch])
    ax[2].set_xlabel("local clock time (PDT) of production curtailment (ramp start -> restart)")
    ax[2].axvspan(6, 20, color="gold", alpha=0.15, label="daylight")
    ax[2].legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(f"{F}/fig_clock.png", dpi=110)
    plt.close()


def fig_front():
    m, _, _ = front._matched()
    d = io.load_diffusion_curves()
    f = io.load_flex()
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    ax[0].plot(f.th, f.dv, ".", ms=2, color="gray", label="published distance (FLEX file)")
    ax[0].plot(f.th, d["yp_Upper_curve"], "r", label="stored front = 90.0 (t-18.95)^0.473")
    ax[0].set_xlabel("h since 29 Apr 00:00 (UTC)")
    ax[0].set_ylabel("distance to injection (m)")
    ax[0].legend(fontsize=7)
    top = m.groupby("cell").size().sort_values().index[-6:]
    for cell in top:
        g = m[m.cell == cell]
        ax[1].plot(g.t, g.dv, ".", ms=4, label=f"cell x,z={cell.replace('_', ',')} m")
    ax[1].set_xlabel("h (UTC)")
    ax[1].set_ylabel("published distance (m)")
    ax[1].set_title("same catalogue location, distance grows with time", fontsize=9)
    ax[1].legend(fontsize=6)
    s = _j("front.json")["stationarity"]["windows"]
    ax[2].plot(s["t"], s["dz50"], "ko-", label="catalogue: median depth below injector")
    ax[2].plot(s["t"], s["dz90"], "ks--", label="catalogue: 90th percentile")
    tt = np.array(s["t"])
    for fac, lab in [(1, "front, D=0.43, r=sqrt(4Dt)"), (np.pi, "front, D=0.43, r=sqrt(4 pi D t)")]:
        ax[2].plot(tt, np.sqrt(4 * fac * 0.43 * (tt - front.T0_PUB) * 3600), label=lab)
    ax[2].set_xlabel("h (UTC)")
    ax[2].set_ylabel("m")
    ax[2].legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(f"{F}/fig_front.png", dpi=110)
    plt.close()


def fig_cycles():
    val = _j("validate_shift+0_out1.json")
    by = {(r["model"], r["scheme"]): r for r in val}
    d = models.Data()
    fig, axs = plt.subplots(5, 1, figsize=(10, 14), sharex=True)
    for ax, (c, s, e) in zip(axs, models.CYCLES):
        edges = np.arange(s - 10, s + 30.01, 1.0)
        lam, lo, hi, n, k = rates.binned_rate(d.t, d.occ, d.obs, edges)
        cen = 0.5 * (edges[1:] + edges[:-1])
        ok = n >= 20
        ax.fill_between(cen[ok] - s, lo[ok], hi[ok], step="mid", color="k", alpha=0.2)
        ax.step(cen[ok] - s, lam[ok], "k", where="mid", lw=1, label="observed (1 h, saturation-corrected)")
        for name, col in [("exp+diffusion+cascade", "r"), ("dieterich", "b"), ("paper:D=0.43(4piDt)", "g")]:
            R_ = fit.expected_rate(name, d, by[(name, f"loco:{c}")]["theta"])
            w = (d.t > s - 10) & (d.t < s + 30)
            ax.plot(d.t[w] - s, R_[w], col, lw=1.3, label=f"{name} (fitted without the cycle shown)")
        a2 = ax.twinx()
        w = (d.t > s - 10) & (d.t < s + 30)
        a2.plot(d.t[w] - s, d.p[w], color="orange", lw=1)
        a2.set_ylabel("gauge psig", color="orange", fontsize=8)
        ax.set_ylabel(f"cycle {c}\nevents/h")
        ax.axvline(0, color="orange", ls=":")
        ax.axvline(e - s, color="orange", ls="--")
    axs[0].legend(fontsize=6, loc="upper left")
    axs[-1].set_xlabel("h since ramp start (gauge = catalogue = UTC)")
    plt.tight_layout()
    plt.savefig(f"{F}/fig_cycles.png", dpi=110)
    plt.close()


def fig_depth():
    dist = _j("distance.json")["depth"]["per_class"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    L = [v["L_below_injector_m"] for v in dist.values()]
    tau = [v["tau_h"] for v in dist.values()]
    lo = [v["tau_h"] - v["ci95"][0] for v in dist.values()]
    hi = [v["ci95"][1] - v["tau_h"] for v in dist.values()]
    ax[0].errorbar(L, tau, yerr=[lo, hi], fmt="ko", capsize=4)
    for k, x, y in zip(dist, L, tau):
        ax[0].text(x + 10, y, k)
    LL = np.linspace(50, 800, 100)
    for D in [0.08, 0.33, 3.0, 10.0]:
        ax[0].plot(LL, LL ** 2 / (4 * D * 3600), "--", lw=0.8, label=f"tau = L^2/4D, D = {D} m2/s")
    ax[0].set_ylim(0, 8)
    ax[0].set_xlabel("catalogue depth below injector lateral, L (m)")
    ax[0].set_ylabel("transport time tau (h)")
    ax[0].legend(fontsize=7)
    xc = _j("xcorr.json")
    for sh, col in [("+0", "k"), ("-7", "gray"), ("+8", "b")]:
        v = xc[sh]
        ks = ["shallow", "mid", "deep"]
        ax[1].errorbar(range(3), [v[k]["peak_lag_h"] for k in ks],
                       yerr=[[v[k]["peak_lag_h"] - v[k]["ci95"][0] for k in ks], [v[k]["ci95"][1] - v[k]["peak_lag_h"] for k in ks]],
                       fmt="o-", color=col, capsize=3, label=f"catalogue clock = gauge {sh} h")
    ax[1].axhline(0, color="r", lw=0.8)
    ax[1].set_xticks(range(3))
    ax[1].set_xticklabels(["shallow", "mid", "deep"])
    ax[1].set_ylabel("model-free lag of seismicity behind gauge (h)")
    ax[1].legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(f"{F}/fig_depth.png", dpi=110)
    plt.close()


def fig_models():
    c = _j("compare_exp_diffusion_cascade.json")
    items = sorted(c["versus"].items(), key=lambda kv: kv[1]["dll_total"])
    fig, ax = plt.subplots(figsize=(9, 6))
    for i, (k, v) in enumerate(items):
        ax.errorbar(v["dll_total"], i, xerr=[[v["dll_total"] - v["ci95"][0]], [v["ci95"][1] - v["dll_total"]]],
                    fmt="o", color="g" if k.startswith("paper") else "k", capsize=3)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([k for k, _ in items], fontsize=8)
    ax.axvline(0, color="r")
    ax.set_xscale("symlog", linthresh=10)
    ax.set_xlabel(f"held-out log-likelihood of {c['reference']} minus model (95% block bootstrap); >0: model worse")
    plt.tight_layout()
    plt.savefig(f"{F}/fig_models.png", dpi=110)
    plt.close()


def fig_predict():
    val = _j("validate_shift+0_out1.json")
    by = {(r["model"], r["scheme"]): r for r in val}
    d = models.Data(t1=330.0)
    p0 = d.p.copy()
    fig, ax = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    for s, col in zip(predict.S_LIST, ["k", "b", "g", "r"]):
        q, tpk = predict.scenario(d, s)
        ax[0].plot(d.t - predict.RAMP0, q, col, label=f"ramp x{s}")
        d.p = q
        for name, axi in [("exp+diffusion+cascade", 1), ("dieterich+diffusion(ta=178h)", 2)]:
            ax[axi].plot(d.t - predict.RAMP0, fit.expected_rate(name, d, by[(name, "full")]["theta"]), col)
            ax[axi].set_title(name, fontsize=9)
        d.p = p0
    ax[0].set_ylabel("gauge psig")
    ax[0].legend(fontsize=7)
    for a in ax[1:]:
        a.set_ylabel("events/h")
    ax[-1].set_xlabel("h since ramp start")
    for a in ax:
        a.set_xlim(-10, 110)
    plt.tight_layout()
    plt.savefig(f"{F}/fig_predict.png", dpi=110)
    plt.close()


def fig_design():
    fr = _j("frontier.json")
    ds = fr["designs"]
    front_keys = [tuple(x) for x in fr["frontier"]]
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
    mk = {"gauge": "s", "deepgauge": "o"}
    for dd in ds:
        key = (dd["design"], dd["mode"], dd["monitoring"])
        on = key in front_keys
        y = min(max(dd["min_sep"], 1e-2), 999)
        ax[0].scatter(dd["cost"]["deferred_MWh"], y, marker=mk[dd["monitoring"]],
                      facecolors="r" if on else "none", edgecolors="r" if on else "gray", s=45)
        if on or dd["design"] == "BM2023":
            ax[0].annotate(f"{dd['design']}/{dd['mode'][:3]}/{dd['monitoring'][:4]}",
                           (dd["cost"]["deferred_MWh"], y), fontsize=6)
    ax[0].axhline(5, color="k", ls="--", lw=0.8)
    ax[0].axvline(fr["axes"]["cost"]["target"]["MWh"], color="b", ls=":", lw=0.8)
    ax[0].set_yscale("log")
    ax[0].set_xlabel("deferred generation (MWh); dotted: cost target")
    ax[0].set_ylabel("worst key-pair separation E[dll]/phi (>5 decisive)")
    ax[0].set_title("squares: 73-22 gauge only; circles: + gauge at seismic depth; red: frontier", fontsize=8)
    cd = fr["axes"]["cost"]["cheapest_decisive"]
    name = cd["design"] if cd else max((x for x in ds if x["design"] != "BM2023"), key=lambda x: x["min_sep"])["design"]
    t, p, win, cost = design.schedule(design.designs_v2()[name])
    ax[1].plot(t / 24, p, "k")
    ax[1].set_xlabel("days from the start of the test")
    ax[1].set_ylabel("prescribed 73-22 pressure (psig)")
    ax[1].set_title(f"recommended schedule '{name}'", fontsize=9)
    plt.tight_layout()
    plt.savefig(f"{F}/fig_design.png", dpi=110)
    plt.close()


def run():
    os.makedirs(F, exist_ok=True)
    for fn in [fig_clock, fig_front, fig_cycles, fig_depth, fig_models, fig_predict, fig_design]:
        try:
            fn()
        except FileNotFoundError as e:
            print("skip", fn.__name__, e)
