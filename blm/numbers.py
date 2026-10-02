"""Collect every headline number into results/numbers.json.

Each entry: value, what it is, what it is compared against, source file.
Diffusivities are computed here: D = L^2 / (4 tau) for the 1-D transport
kernel erfc(sqrt(tau/t)), with L the catalogue depth of each class below the
injector lateral (2336 m TVD), and the distance that the independent
fault-zone range 0.08-0.33 m^2/s (Guo et al. 2021) would require.
"""
import json
import os

import numpy as np

R = "results"
GUO = (0.08, 0.33)
Z_INJ = 2336.0
SRV_HALF_HEIGHT = 0.5 * 750 * 0.3048        # Fervo SRV height 750 ft (Norbeck et al. 2023 summary)


def _load(name):
    path = os.path.join(R, name)
    return json.load(open(path)) if os.path.exists(path) else None


def entry(value, what, against, source):
    return dict(value=value, what=what, compared_against=against, source=source)


def diffusivity(tau_h, L_m):
    return L_m ** 2 / (4 * tau_h * 3600.0)


def run(out=f"{R}/numbers.json"):
    N = {}
    clock = _load("clock.json")
    if clock:
        t = clock["tide"]
        N["gauge_clock_offset_h"] = entry(t["best_offset_h"], "best gauge-clock offset from UTC (Earth tide, 15-20 Mar)",
                                          "PST label (-8 h), PDT (-7 h)", "clock.json")
        N["gauge_clock_ci95_h"] = entry(t["boot_ci95"], "block-bootstrap 95% interval of the offset", "-8 and -7 h", "clock.json")
        N["tide_dlogL_PST"] = entry(t["hypotheses"]["PST(UTC-8)"]["dlogL"], "log-likelihood deficit of PST vs best", "UTC", "clock.json")
        N["tide_sign_PST"] = entry(t["hypotheses"]["PST(UTC-8)"]["physical_sign"], "PST fit has the physical sign?", "pressure must fall with dilatation", "clock.json")
        N["restart_rayleigh_p"] = entry(clock["restarts"]["p_rayleigh"], "clustering of outage-end hours", "uniform", "clock.json")
        N["rate_file_offsets_h"] = entry([r["offset_h"] for r in clock["rate_file"]], "rate-file minus gauge times of matched events", "0 if consistent", "clock.json")
    front = _load("front.json")
    if front:
        idf = front["identify"]["yp_Upper_curve"]
        N["front_powerlaw"] = entry([idf["a_m_per_h_n"], idf["t0_h"], idf["n"], idf["rms_m"]],
                                    "stored front r = a (t - t0)^n (m, h): a, t0, n, rms", "sqrt(t) diffusion front", "front.json")
        cv = front["conventions"]
        N["front_D_4Dt_lsq"] = entry(cv["D_4Dt"]["lsq_r_t0fixed"], "D from LSQ r = sqrt(4 D (t - t0)) on the stored curve", "published 0.43 m2/s", "front.json")
        N["front_D_4piDt_lsq"] = entry(cv["D_4piDt"]["lsq_r_t0fixed"], "same curve, paper's printed r = sqrt(4 pi D t)", "published 0.43 m2/s", "front.json")
        N["front_D_endpoint_4Dt"] = entry(cv["D_4Dt"]["endpoint"], "r^2/(4t) at the end of the window", "published 0.43", "front.json")
        a = front["artefact"]
        N["dv_within_cell_slope_m_per_h"] = entry(a["median_within_cell_slope_m_per_h"], "growth of published distance with time inside one 40-m catalogue cell (median of cells)", "0 for fixed sources", "front.json")
        N["dv_cells_positive_frac"] = entry(a["frac_cells_positive_slope"], "fraction of populated cells with positive slope", "0.5 if random", "front.json")
        N["dv_resid_sd"] = entry([a["sd_resid_cell_only"], a["sd_resid_cell_plus_time"]], "sd of published distance after cell effects, and after cell + common time effect (m)", "location noise", "front.json")
        s = front["stationarity"]
        N["catalogue_depth_drift_m_per_h"] = entry([s["median_dz_slope_m_per_h"]] + s["median_dz_slope_ci95"],
                                                   "drift of the catalogue's median depth below the injector, with 95% CI", "front growth implied by D=0.43", "front.json")
        N["front_growth_required_m"] = entry(s["published_front_growth_over_span_m"], "growth a D=0.43 front needs over the same span (m)", "catalogue drift", "front.json")
    resp = _load("response.json")
    if resp:
        N["cycle_loading"] = entry(resp["loading"], "per-cycle ramp: duration, dp, mean and max dp/dt, rise above prior max", "-", "response.json")
        N["cycle_response_all"] = entry({c: {k: v[k] for k in ["baseline", "excess_events", "centroid_lag_h", "peak_lag_h", "xcorr_lag_h"]} | {"ci68": v["ci68"]}
                                         for c, v in resp["classes"]["all"].items()}, "per-cycle response, all events", "-", "response.json")
    val = _load("validate_shift+0_out1.json")
    if val:
        from .frontier import skill
        sk = skill(f"{R}/validate_shift+0_out1.json")
        N["heldout_skill"] = entry(sk, "held-out gain per event over a constant rate (loco, slow2fast, fast2slow)", "paper readings", "validate_shift+0_out1.json")
        by = {(r["model"], r["scheme"]): r for r in val}
        N["fits_full"] = entry({m: by[(m, "full")]["theta"] for m in sorted({r["model"] for r in val})},
                               "parameters fitted to all cycles (one configuration)", "-", "validate_shift+0_out1.json")
    for ref in ["exp_diffusion", "exp_diffusion_cascade"]:
        c = _load(f"compare_{ref}.json")
        if c:
            N[f"compare_{ref}"] = entry({k: [v["dll_total"]] + v["ci95"] for k, v in c["versus"].items()},
                                        f"held-out dll of {c['reference']} minus each model, 95% block-bootstrap", "0 = indistinguishable", f"compare_{ref}.json")
    dist = _load("distance.json")
    dl = _load("distance_loco.json")
    if dist:
        dd = {}
        for k, v in dist["depth"]["per_class"].items():
            tau = v["tau_h"]
            L = v["L_below_injector_m"]
            L_srv = max(L - SRV_HALF_HEIGHT, 1.0)
            dd[k] = dict(tau_h=tau, ci95=v["ci95"], L_m=L, D_from_lateral=diffusivity(tau, L),
                         D_from_srv_base=diffusivity(tau, L_srv),
                         L_needed_for_guo_m=[2 * np.sqrt(GUO[0] * tau * 3600), 2 * np.sqrt(GUO[1] * tau * 3600)])
        N["depth_transport"] = entry(dd, "transport time per catalogue depth class and implied diffusivity", "Guo et al. 0.08-0.33 m2/s", "distance.json")
        N["depth_LR"] = entry([dist["depth"]["LR"], dist["depth"]["p"]], "LR test: one transport time for all depths", "chi2(2)", "distance.json")
        N["radial_LR"] = entry([dist["radial"]["LR"], dist["radial"]["p"]], "LR test across radial classes", "chi2(2)", "distance.json")
    if dl:
        N["depth_heldout_dll"] = entry([dl["dll_total"], dl["dll_per_event"]], "held-out gain of depth-specific transport times", "shared time", "distance_loco.json")
    prof = _load("profiles.json")
    if prof:
        N["profiles"] = entry({k: [v["best"]] + v["ci95"] for k, v in prof.items()}, "profile-likelihood 95% intervals", "-", "profiles.json")
        tau = prof["exp+diffusion:tau"]
        N["transport_D_range"] = entry({str(L): [diffusivity(tau["ci95"][1], L), diffusivity(tau["best"], L), diffusivity(tau["ci95"][0], L)]
                                        for L in (100, 200, 400, 584)}, "D (m2/s) for the fitted tau at assumed transport distances L (m)", "Guo 0.08-0.33", "profiles.json")
    xc = _load("xcorr.json")
    if xc:
        N["xcorr_lags"] = entry(xc, "model-free lag of seismicity behind gauge pressure, per clock shift and depth class", "0 = no delay", "xcorr.json")
    for sh in ["+0", "+8", "+7", "-7"]:
        v = _load(f"validate_shift{sh}_out1.json")
        if v:
            by = {(r["model"], r["scheme"]): r for r in v}
            from .frontier import skill
            s = skill(f"{R}/validate_shift{sh}_out1.json")
            N[f"clockshift_{sh}"] = entry(dict(tau=by[("exp+diffusion", "full")]["theta"]["tau"],
                                               loco={m: s[m]["loco"] for m in ["exp+diffusion+cascade", "exp+diffusion", "exp+cascade", "dieterich", "exp"]}),
                                          "transport time and held-out skill if the catalogue clock were gauge + shift", "shift 0", f"validate_shift{sh}_out1.json")
    pr = _load("predict.json")
    if pr:
        N["slower_ramps"] = entry(pr, "isolated cycle-IV ramp stretched by s: lag, excess events, peak rate (value, jackknife se)", "s = 1 (observed)", "predict.json")
    ppc = _load("ppc.json")
    if ppc:
        N["per_cycle_predictive"] = entry(ppc, "held-out (loco) predictions of each cycle vs observation", "observation", "ppc.json")
    fr = _load("frontier.json")
    if fr:
        N["frontier"] = entry(dict(axes=fr["axes"], frontier=fr["frontier"], weakest=fr["weakest"]), "frontier axes", "targets", "frontier.json")
    mc = _load("design_mc.json")
    if mc:
        N["design_mc"] = entry(mc, "Monte-Carlo check of expected separations", "deterministic E[dll]/phi", "design_mc.json")
    # convergence checks: no profile point may beat the model's best fit; fold stability of tau
    chk = {}
    if prof:
        for k, v in prof.items():
            chk[f"profile_max_minus_fit:{k}"] = float(max(v["ll"]) - v["ll_best"])
    if val:
        by = {(r["model"], r["scheme"]): r for r in val}
        for m in ["exp+diffusion", "exp+diffusion+cascade", "dieterich+diffusion"]:
            chk[f"tau_by_fold:{m}"] = [by[(m, f"loco:{c}")]["theta"].get("tau") for c in ["I", "II", "III", "IV", "V"]]
    N["convergence_checks"] = entry(chk, "profile maxima minus best-fit log-likelihood (must be <= ~0.05); "
                                    "transport time in each leave-one-cycle-out fit", "0 / the all-cycle fit", "profiles.json, validate")
    with open(out, "w") as fh:
        json.dump(N, fh, indent=1, default=float)
    return N
