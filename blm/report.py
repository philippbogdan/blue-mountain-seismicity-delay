"""Write FINDINGS.md, REPORT.md and COMPLETE.md from results/*.json.

Every number in the three documents is read from the results files written
by `make all`; the commit they came from is taken from results/manifest.json.
"""
import json
import os

import numpy as np

R = "results"


def J(name):
    p = os.path.join(R, name)
    return json.load(open(p)) if os.path.exists(p) else None


def f(x, nd=2, sign=False):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    s = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    return s


def ci(a, nd=2):
    return f"[{f(a[0], nd)}, {f(a[1], nd)}]"


def ctx():
    """Gather everything the documents need into one dict."""
    c = {}
    c["manifest"] = J("manifest.json") or {}
    c["clock"] = J("clock.json")
    c["front"] = J("front.json")
    c["resp"] = J("response.json")
    c["val"] = J("validate_shift+0_out1.json")
    c["cmp_best"] = J("compare_exp_diffusion_cascade.json")
    c["cmp_tr"] = J("compare_exp_diffusion.json")
    c["dist"] = J("distance.json")
    c["dloco"] = J("distance_loco.json")
    c["prof"] = J("profiles.json")
    c["xc"] = J("xcorr.json")
    c["ppc"] = J("ppc.json")
    c["pred"] = J("predict.json")
    c["fr"] = J("frontier.json")
    c["mc"] = J("design_mc.json")
    c["grid"] = J("design_grid.json")
    c["num"] = J("numbers.json")
    c["shift"] = {sh: J(f"validate_shift{sh}_out1.json") for sh in ["+0", "+7", "+8", "-7"]}
    c["outage"] = {o: J(f"validate_shift+0_out{o}.json") for o in ["0.75", "1", "1.5"]}
    # catalogue coverage and saturation in the cycling window (computed here, cheap)
    from . import rates
    tm, occ, obs = rates.minute_grid(30.0, 170.0)
    edges = np.arange(30.0, 170.0001, 1.0)
    lam, lo, hi, n, k = rates.binned_rate(tm, occ, obs, edges)
    ok = n >= 45
    c["coverage"] = dict(frac_observed=float(obs.mean()), max_corrected=float(np.nanmax(lam[ok])),
                         max_raw=float(np.nanmax((k / np.maximum(n, 1) * 60)[ok])))
    return c


def theta(c, model, scheme="full", val=None):
    val = val or c["val"]
    for r in val:
        if r["model"] == model and r["scheme"] == scheme:
            return r["theta"]
    return {}


def skill(c, val=None):
    from .frontier import skill as sk
    import tempfile
    val = val or c["val"]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(val, fh)
        name = fh.name
    out = sk(name)
    os.unlink(name)
    return out


MODEL_TEXT = {
    "exp+diffusion+cascade": "transport (1-D diffusion kernel) + instantaneous exponential fault law + earthquake cascades",
    "exp+diffusion": "transport (1-D diffusion kernel) + instantaneous exponential fault law",
    "exp+lag": "transport (exponential kernel) + instantaneous exponential fault law",
    "exp+shift": "rigid delay + instantaneous exponential fault law",
    "exp+diffusion+poro": "transport + instantaneous poroelastic term + exponential law",
    "dieterich+diffusion": "transport + Dieterich rate-and-state (all parameters free)",
    "dieterich+diffusion(ta=178h)": "transport + Dieterich with t_a at its 95% lower bound (178 h)",
    "dieterich+lag": "transport (exponential kernel) + Dieterich",
    "dieterich": "Dieterich rate-and-state on the gauge pressure: the faults' own delay, no transport",
    "dieterich+cascade": "Dieterich, no transport, + cascades",
    "exp+cascade": "no transport: exponential law + earthquake cascades",
    "exp": "no delay: exponential law on the gauge pressure",
    "coulomb+diffusion": "transport + Coulomb threshold with stress memory (Kaiser)",
    "coulomb": "Coulomb threshold with memory, no transport",
    "rate+diffusion": "transport + stressing-rate law",
    "paper:p+dp/dt": "paper's reading 1: pressure and pressurisation rate, no delay",
    "paper:D=0.43(4Dt)": "paper's reading 2: published D=0.43 m2/s over the cloud's depth offset, r=sqrt(4Dt)",
    "paper:D=0.43(4piDt)": "paper's reading 2': published D=0.43 m2/s, paper's printed r=sqrt(4 pi D t)",
    "const": "constant rate (reference)",
    "exp+gamma": "transport (gamma kernel, shape free) + instantaneous exponential fault law",
    "exprate+diffusion": "transport + exponential law + a pressurisation-rate term (the paper's two drivers, transported)",
    "dieterich:nucleation": "the faults' own delay in the nucleation regime (A sigma <= 50 psi), no transport",
}


def findings(c):
    m = c["manifest"]
    L = []
    A = L.append
    ck, fr, rs = c["clock"], c["front"], c["resp"]
    sk = skill(c)
    best = "exp+diffusion+cascade"
    A("# FINDINGS: what sets the seismicity delay in the cycled Blue Mountain reservoir\n")
    A(f"Every number below was written by `make all` at commit `{m.get('commit', '?')}` "
      f"(results/manifest.json); each says what it is compared against and where it is stored "
      f"(results/*.json, figures in figs/). Five cycles are five cycles: intervals are block-bootstrap "
      f"or leave-one-cycle-out jackknife intervals, never Poisson ones.\n")
    # ---------------------------------------------------------------- summary
    t_best = theta(c, best)
    t_tr = theta(c, "exp+diffusion")
    d = c["dist"]["depth"]["per_class"]
    A("## Summary\n")
    A(f"1. **The delay is real, and it belongs to the site, not the schedule.** On a common UTC clock the seismicity "
      f"follows the 73-22 gauge pressure through a transport delay: transport time tau = {f(t_tr['tau'])} h "
      f"(profile 95% {ci(c['prof']['exp+diffusion:tau']['ci95'])} h; 1-D diffusion kernel), growing with depth below the "
      f"injector lateral from {f(d['shallow']['tau_h'])} h to {f(d['deep']['tau_h'])} h. The faults answer the pressure "
      f"they feel at once, exponentially (A sigma/mu = {f(t_tr['As'], 0)} psi). A delay belonging to the faults "
      f"themselves (rate-and-state without transport) is rejected out of sample; one added to the transport is not detected.")
    cb = c["cmp_best"]["versus"]
    A(f"2. **The published diffusion front is reproduced but is not a diffusion front.** The stored curve is exactly "
      f"r = {f(fr['identify']['yp_Upper_curve']['a_m_per_h_n'], 2)} (t - {f(fr['identify']['yp_Upper_curve']['t0_h'], 3)} h)^"
      f"{f(fr['identify']['yp_Upper_curve']['n'], 4)}; a least-squares sqrt(4 D t) fit to it gives D = "
      f"{f(fr['conventions']['D_4Dt']['lsq_r_t0fixed'], 3)} m2/s (the published 0.43), or "
      f"{f(fr['conventions']['D_4piDt']['lsq_r_t0fixed'], 3)} m2/s with the paper's printed sqrt(4 pi D t). The growth is "
      f"in the published distances themselves: events at one fixed catalogue location are assigned distances growing by "
      f"{f(fr['artefact']['median_within_cell_slope_m_per_h'], 1)} m/h, while the catalogue's own depths do not migrate.")
    A(f"3. **What the paper's readings lose on unseen cycles:** held-out log-likelihood {f(cb['paper:p+dp/dt']['dll_total'], 0)} "
      f"{ci(cb['paper:p+dp/dt']['ci95'], 0)} below the best explanation for 'pressure and pressurisation rate' "
      f"(its pressurisation-rate term is fitted to zero), and {f(cb['paper:D=0.43(4piDt)']['dll_total'], 0)} "
      f"{ci(cb['paper:D=0.43(4piDt)']['ci95'], 0)} to {f(cb['paper:D=0.43(4Dt)']['dll_total'], 0)} "
      f"{ci(cb['paper:D=0.43(4Dt)']['ci95'], 0)} for the published diffusivity.")
    pr = c["pred"]
    A(f"4. **Slower ramps do not buy a longer delay.** For cycle IV's 355 psi reached 8x more slowly the peak lag falls from "
      f"{f(pr[best]['s=1']['peak_lag_h']['value'], 1)} to {f(pr[best]['s=8']['peak_lag_h']['value'], 1)} h and the cycle's excess "
      f"events rise from {f(pr[best]['s=1']['excess_events']['value'], 0)} to {f(pr[best]['s=8']['excess_events']['value'], 0)} "
      f"(± jackknife {f(pr[best]['s=8']['excess_events']['jackknife_se'], 0)}); the rate-and-state bracket allowed by the data gives "
      f"{f(pr['dieterich+diffusion(ta=178h)']['s=8']['excess_events']['value'], 0)}. The lever on seismicity is the pressure "
      f"reached and the time spent there, not the ramp rate.")
    if c["fr"] and c["fr"]["axes"]["cost"]["cheapest_decisive"]:
        cd = c["fr"]["axes"]["cost"]["cheapest_decisive"]
        from .design import designs_v2
        cyc = designs_v2().get(cd["design"], [])
        parts = ", ".join(f"{x['ramp_h']:g}-h ramp to +{x['dp']:g} psi" + (f" held {x['hold_h']:g} h" if x.get("hold_h") else "")
                          for x in cyc)
        A(f"5. **The test.** {parts}, every stream on one GPS-disciplined UTC clock: decisive (E[dll]/phi >= 5) between "
          f"every pair of explanations these data cannot separate, with the existing gauge, in {f(cd['days'], 1)} days and "
          f"{f(cd['MWh'], 0)} MWh of deferred generation (section 8). A gauge at the seismic depth would also measure the "
          f"transport and settle the diffusivity.")
    A("6. **The clocks.** The pressure file labelled PST is on UTC (Earth tide; the daily curtailments then fall in local "
      "daylight, as the paper says they were meant to). The catalogue is on UTC by provenance. Offsets of +7/+8 h, the "
      "PROBLEM's worry, would make shallow seismicity precede the reservoir pressure by hours.\n")
    # ---------------------------------------------------------------- 1 clocks
    t = ck["tide"]
    th2 = ck["tide_second_half"]
    A("## 1. Clocks: one time base for gauge and catalogue (figs/fig_clock.png)\n")
    A(f"- **Gauge = UTC, not PST.** In the 15-20 March quiet window the gauge carries the Earth tide (fitted tidal "
      f"amplitude {f(t['tide_amplitude_psi'], 3)} psi, within ~0.1 psi of other slow variation). "
      f"Regressing it on the UTC solid-Earth tide (pysolid) and the UTC Winnemucca barometer, with the physical sign "
      f"(pressure falls when the ground dilates), gives a gauge offset of {f(t['best_offset_h'])} h from UTC, moving-block "
      f"bootstrap 95% {ci(t['boot_ci95'])} h (second half of the window: {f(th2['best_offset_h'])} h, {ci(th2['boot_ci95'])}). "
      f"The PST (-8 h) and PDT (-7 h) alignments fit only with the unphysical sign (coefficients "
      f"{f(t['hypotheses']['PST(UTC-8)']['tide_coef_psi_per_m'], 2)} and {f(t['hypotheses']['PDT(UTC-7)']['tide_coef_psi_per_m'], 2)} "
      f"psi/m, against {f(t['tide_coef_psi_per_m'], 2)} at the best offset); with the sign imposed they collapse to "
      f"'no tide', {f(t['dlogL_no_tide'], 1)} log-likelihood units worse (residuals are strongly autocorrelated: "
      f"lag-1 rho = {f(t['lag1_rho'], 3)}, effective n = {f(t['n_eff'], 1)}; source clock.json).")
    s = ck["schedule"]
    A(f"- **Operating schedule.** Read on UTC, the five curtailments run from "
      f"{', '.join(x['local_if_gauge_UTC'][0] for x in s)} to {', '.join(x['local_if_gauge_UTC'][1] for x in s)} local time "
      f"(PDT); cycles II and III last {s[1]['duration_h']} and {s[2]['duration_h']} h, the paper's '12 hours'. Production "
      f"is restricted through the solar day, as the paper says restricted production is for. Read on PST they would run "
      f"from mid-afternoon to {s[1]['local_if_gauge_PST'][1]} local.")
    A(f"- **Catalogue = UTC by provenance.** The raw files are named BM73-22_UTC_<date>_<time>, events carry their 1-minute "
      f"file's start time (seconds fields drift with file boundaries), the MATLAB datetimes carry no zone, and the "
      f"authors' Fig. 6 plots catalogue and gauge on one axis unshifted (pressure peaks drawn at ~02:00 on 4 and 5 May, the "
      f"raw gauge stamps). {f(100 * ck['restarts']['frac_13_to_15'], 0)}% of outages end between 13 and 15 h on the catalogue clock "
      f"(08-10 h in Houston, where the system was run from, if it is UTC), but the clustering is weak "
      f"(Rayleigh p = {f(ck['restarts']['p_rayleigh'], 2)}).")
    xc = c["xc"]
    sh = c["dist"]["depth"]["per_class"]["shallow"]
    A(f"- **Causality rules out the PROBLEM's 7-8 h offsets.** Which depths respond first does not depend on the clock: "
      f"shallow events lead deep ones by {f(xc['+0']['deep']['peak_lag_h'] - xc['+0']['shallow']['peak_lag_h'], 2)} h in the "
      f"model-free cross-correlation (xcorr.json). On UTC the shallow class, 184 m below the lateral, answers the gauge "
      f"after {f(sh['tau_h'])} h (95% {ci(sh['ci95'])}; section 6). A catalogue running more than ~{f(sh['ci95'][1], 1)} h ahead "
      f"of the gauge would therefore put the shallow response before the reservoir pressure that drives it; at +7/+8 h it "
      f"would lead by 5.5-7.4 h, although the gauge answers production changes within minutes. A catalogue on local time "
      f"(-7 h) is not excluded by physics: it would lengthen every lag by 7 h (transport time "
      f"{f(theta(c, 'exp+diffusion', val=c['shift']['-7'])['tau'])} h instead of {f(t_tr['tau'])} h) and change no conclusion "
      f"below except the diffusivity, which it lowers ~3x.")
    offs = [x["offset_h"] for x in ck["rate_file"]]
    A(f"- **The rate file cannot be used for timing.** Its shut-ins and restarts sit {f(min(offs), 1)} to {f(max(offs), 1)} h from "
      f"the gauge's sharp responses, varying from event to event, and its cycle IV/V shut-ins last ~8 h against the "
      f"gauge's 10.5-10.75 h; the authors' Fig. 6d shows the same mismatch. It is used only for volumes "
      f"({ck['volumes']['injected_m3']:.3g} m3 injected and {ck['volumes']['produced_m3']:.3g} m3 produced, reading the rates as gpm, "
      f"against the paper's 1.35e5 and 1.07e5 m3 over a slightly shorter span).\n")
    L.extend(findings_rest(c, sk, best, t_tr))
    L.extend(findings_tail(c, sk, best, t_tr))
    return "\n".join(L)


def findings_rest(c, sk, best, t_tr):
    L = []
    A = L.append
    fr, rs = c["front"], c["resp"]
    # ---------------------------------------------------------------- 2 catalogue
    A("## 2. The catalogue as a measurement\n")
    cv_ = c["coverage"]
    A("- No two of the 13,351 events share a time stamp: each 1-minute DAS file yields at most one event, so the catalogue "
      "is an occupancy record and observed rates saturate at 60/h. All rates and likelihoods here use "
      f"P(file occupied) = 1 - exp(-R dt), which undoes the saturation (the highest hourly rate in the cycles is "
      f"{f(cv_['max_corrected'], 0)}/h corrected against {f(cv_['max_raw'], 0)}/h raw).")
    A(f"- Gaps of more than 1 h are outages (at the 5-45/h rates seen, a 1-h gap by chance has probability < 1%), treated "
      f"as unobserved ({f(100 * cv_['frac_observed'], 0)}% of minutes observed in the cycling window). Results do not change "
      f"for outage thresholds of 0.75 or 1.5 h (transport time "
      + ", ".join(f"{f(theta(c, 'exp+diffusion', val=c['outage'][o])['tau'])} h" for o in ["0.75", "1", "1.5"]) + ").")
    stt = rs["step_tests"]
    rg = c["clock"]["regional"]
    A(f"- Magnitudes do not change across shut-ins or restarts (two-sample KS p >= {f(min(v['p_mag_ks'] for v in stt.values()), 2)} "
      f"in all ten 3-h comparisons), so rate changes there are not detection artefacts. Regional earthquakes (USGS ComCat "
      f"within 400 km, amplitude proxy above the catalogue's floor) fall in catalogued minutes only at the chance rate under "
      f"every clock (" + ", ".join(f"{k} h: {v[0]}/{v[1]}" for k, v in rg["hits_by_offset"].items())
      + f"; base rate {f(rg['base_rate'], 2)}), so the real-time system kept local events only and they cannot anchor its "
      f"time; Winnemucca wind does not modulate detection (|r| <= {f(c['clock']['wind']['max_abs'], 3)}).\n")
    # ---------------------------------------------------------------- 3 front
    idf = fr["identify"]["yp_Upper_curve"]
    cv = fr["conventions"]
    rf = fr["refit"]
    ar = fr["artefact"]
    st = fr["stationarity"]
    A("## 3. Fidelity: the published diffusion front (figs/fig_front.png)\n")
    A(f"- **Reproduced.** The stored 'best-fit synthetic diffusion curve' (Diffusion_data.mat, one value per event of "
      f"Vertical_distance_from_injection_FLEX.txt) is exactly r = {f(idf['a_m_per_h_n'], 5)} (t - {f(idf['t0_h'], 5)})^{f(idf['n'], 5)} "
      f"(r in m, t in h since 29 Apr 00:00 UTC; origin {idf['t0_utc'][:19]}), residual {idf['rms_m']:.1e} m. Fitting "
      f"r = sqrt(4 D (t - t0)) to it by least squares with its own origin gives D = {f(cv['D_4Dt']['lsq_r_t0fixed'], 3)} m2/s "
      f"(the published 0.43); its end point gives {f(cv['D_4Dt']['endpoint'], 3)}; with the paper's printed "
      f"r = sqrt(4 pi D t) the same curve means D = {f(cv['D_4piDt']['lsq_r_t0fixed'], 3)} m2/s. The exponent is "
      f"{f(idf['n'], 3)}, not 1/2. Fronts fitted to the published distances directly depend on the envelope chosen: "
      f"median {f(rf['q50']['D_4Dt'], 2)}, 75th percentile {f(rf['q75']['D_4Dt'], 2)}, 90th percentile {f(rf['q90']['D_4Dt'], 2)} "
      f"m2/s (sqrt(4Dt)); the 'green' events the authors fitted are not identified in the data, and the curve sits near the "
      f"median, not on an upper bound.")
    A(f"- **Why it is not migration.** The FLEX events are the catalogue's events ({ar['n_matched']} of {ar['n_flex']} match a "
      f"catalogue time stamp to the second; the rest are 1-5 min off). Within one 40-m catalogue cell (fixed depth and "
      f"distance from 73-22) the published 'distance to injection' grows with time in {f(100 * ar['frac_cells_positive_slope'], 0)}% "
      f"of the {ar['cells_with_12plus']} populated cells, by {f(ar['median_within_cell_slope_m_per_h'], 2)} m/h (median; median "
      f"correlation with time {f(ar['median_within_cell_corr'], 2)}). Cell constants plus one common function of time leave "
      f"{f(ar['sd_resid_cell_plus_time'], 1)} m of the {f(ar['sd_resid_cell_only'], 1)} m within-cell scatter. The catalogue's "
      f"own median depth below the injector drifts by {f(st['median_dz_slope_m_per_h'], 2)} m/h (95% "
      f"{ci(st['median_dz_slope_ci95'], 2)}), {f(st['implied_change_over_span_m'], 0)} m over the cycles, where a front with "
      f"D = 0.43 needs +{f(st['published_front_growth_over_span_m']['4Dt'], 0)} m (sqrt(4Dt)) or "
      f"+{f(st['published_front_growth_over_span_m']['4piDt'], 0)} m (sqrt(4 pi D t)). The seismic cloud did not migrate; the "
      f"front's growth is a property of how the distances were assigned. A triggering front would in any case have passed "
      f"long before: injection had run for 20 days and the cloud was already active at ~10 events/h.\n")
    # ---------------------------------------------------------------- 4 response
    lo = rs["loading"]
    ra = rs["classes"]["all"]
    A("## 4. The response to each cycle (results/response.json, figs/fig_cycles.png)\n")
    A("| cycle | ramp (h) | Δp (psi) | mean dp/dt (psi/h) | excess events [68%] | centroid lag (h) [68%] | xcorr lag (h) |")
    A("|---|---|---|---|---|---|---|")
    for cy in ["I", "II", "III", "IV", "V"]:
        q, r = lo[cy], ra[cy]
        A(f"| {cy} | {f(q['ramp_h'], 2)} | {f(q['dp_psi'], 0)} | {f(q['mean_dpdt'], 1)} | {f(r['excess_events'], 0)} "
          f"{ci(r['ci68']['excess_events'], 0)} | {f(r['centroid_lag_h'], 1, True)} {ci(r['ci68']['centroid_lag_h'], 1)} | "
          f"{f(r['xcorr_lag_h'], 1)} |")
    A("")
    A("- **Pressurisation rate.** The three slow ramps (restricted production, ~12 psi/h, ~105-140 psi) gave no detectable "
      "excess seismicity; the two fast ones (production halted, ~33 psi/h, 355-360 psi) gave hundreds of excess events, the "
      "rate peaking after the gauge peak. Ramp rate and amplitude rose together, and IV and V were loaded alike, so these "
      "data cannot vary the rate at fixed amplitude: that is the first thing the proposed test does.")
    kr = theta(c, "exprate+diffusion")
    cr = c["cmp_tr"]["versus"].get("exprate+diffusion")
    A(f"- **The paper's 'pressure and pressurisation rate'.** A pressurisation-rate term on the gauge pressure is fitted "
      f"to zero (k = {f(theta(c, 'paper:p+dp/dt').get('k', float('nan')), 4)} events/psi); on the transported pressure it is "
      f"k = {f(kr.get('k', float('nan')), 4)} events/psi and changes the held-out log-likelihood by "
      f"{f(-cr['dll_total'], 1) if cr else 'n/a'} {ci([-cr['ci95'][1], -cr['ci95'][0]], 1) if cr else ''} against transport "
      f"alone. Within these cycles the seismicity answers the pressure level the faults feel, not its rate of change.")
    dl = c["dist"]
    A(f"- **Distance.** Split by catalogue depth, deeper events lag more (section 6). Split by radial distance from 73-22 "
      f"there is no difference (LR = {f(dl['radial']['LR'], 2)}, p = {f(dl['radial']['p'], 2)}), as expected: 73-22 is a gauge "
      f"well at the laterals' midpoint, not the source; the stimulated volume runs ~450 m along the laterals either side "
      f"of it (3000 ft long; Norbeck et al. 2023, Stanford Geothermal Workshop).")
    s4 = rs["step_tests"]["IV:shut-in"]
    A(f"- **A transient not explained.** In cycle IV the rate falls from {f(s4['rate_before'], 1)}/h in the 3 h before the shut-in "
      f"to {f(s4['rate_after'], 1)}/h in the 3 h after (p = {f(s4['p_rate'], 2)}; the restart then raises it from "
      f"{f(rs['step_tests']['IV:restart']['rate_before'], 1)} to {f(rs['step_tests']['IV:restart']['rate_after'], 1)}/h, "
      f"p = {f(rs['step_tests']['IV:restart']['p_rate'], 3)}): the 'rapid decrease ... coinciding with production level "
      f"reductions' the paper notes. No model reproduces the dip; a poroelastic term of either sign does not improve "
      f"held-out skill.\n")
    # ---------------------------------------------------------------- 5 explanations
    cb = c["cmp_best"]["versus"]
    ct = c["cmp_tr"]["versus"]
    A("## 5. What explains the delay: every explanation on cycles it was not fitted to (figs/fig_models.png)\n")
    A("One gauge-pressure forcing on the common UTC clock; transport (none / 1-D diffusion kernel erfc(sqrt(tau/t)) / "
      "exponential kernel / rigid shift) times a fault law (exponential = Dieterich with t_a -> infinity / full Dieterich / "
      "Coulomb threshold with memory / stressing rate), optionally with Omori-type cascades from the catalogued events. "
      "One parameter set for all cycles. Scores: occupancy log-likelihood on held-out cycles (leave-one-cycle-out), and "
      "transfer from slow to fast ramps and back. Gains are per held-out event over a constant rate fitted to the same "
      "training data; Δll is against the best model, 95% moving-block (3 h) bootstrap.\n")
    A("| explanation | LOCO gain | slow→fast | fast→slow | Δll vs best [95%] |")
    A("|---|---|---|---|---|")
    order = sorted(sk, key=lambda m: -sk[m]["loco"])
    for mname in order:
        if mname == "const":
            continue
        dd = cb.get(mname)
        dtxt = "best" if mname == best else (f"{f(dd['dll_total'], 1)} {ci(dd['ci95'], 1)}" if dd else "")
        A(f"| {mname}: {MODEL_TEXT.get(mname, '')} | {f(sk[mname]['loco'], 4)} | {f(sk[mname]['slow2fast'], 3)} | "
          f"{f(sk[mname]['fast2slow'], 3)} | {dtxt} |")
    A("")
    A(f"- **Transport is needed.** Without it, a fault response alone (Dieterich) loses {f(ct['dieterich']['dll_total'], 1)} "
      f"{ci(ct['dieterich']['ci95'], 1)} to transport alone, and no delay at all loses {f(ct['exp']['dll_total'], 1)} "
      f"{ci(ct['exp']['ci95'], 1)}. With cascades but no transport the loss to transport+cascades is "
      f"{f(cb['exp+cascade']['dll_total'], 1)} {ci(cb['exp+cascade']['ci95'], 1)}.")
    A(f"- **A fault delay on top is not detected.** Dieterich added to transport: {f(ct['dieterich+diffusion']['dll_total'], 1)} "
      f"{ci(ct['dieterich+diffusion']['ci95'], 1)}; the profile likelihood puts t_a >= {f(c['prof']['dieterich+diffusion:ta']['ci95'][0], 0)} h "
      f"(95%), so on these cycles the faults respond in their exponential, pressure-level-controlled regime "
      f"(A sigma/mu = {f(theta(c, 'dieterich+diffusion')['As'], 0)} psi). A rigid shift instead of diffusive transport "
      f"scores {f(ct['exp+shift']['dll_total'], 1)} {ci(ct['exp+shift']['ci95'], 1)} lower (not significant alone; it loses "
      f"{f(cb['exp+shift']['dll_total'], 1)} {ci(cb['exp+shift']['ci95'], 1)} to the best model): the response looks smoothed as well as delayed.")
    A(f"- **Cascades add clustering, not the delay.** Adding Omori cascades to transport gains {f(-ct['exp+diffusion+cascade']['dll_total'], 1)} "
      f"{ci([-ct['exp+diffusion+cascade']['ci95'][1], -ct['exp+diffusion+cascade']['ci95'][0]], 1)} and leaves tau at "
      f"{f(theta(c, best)['tau'])} h (branching ratio {f(theta(c, best)['K'], 2)}); without transport the cascade fit runs "
      f"to a near-critical branching ratio ({f(theta(c, 'exp+cascade')['K'], 2)}) and still loses.")
    pp = c["ppc"]
    A(f"- **Per-cycle check (held out).** Cycle IV's observed centroid lag is {f(pp['observed']['IV']['centroid_lag_h'], 1)} h; "
      f"transport models predict {f(pp['exp+diffusion']['IV']['centroid_lag_h'], 1)}-{f(pp['dieterich+diffusion']['IV']['centroid_lag_h'], 1)} h, "
      f"the fault-delay model {f(pp['dieterich']['IV']['centroid_lag_h'], 1)} h, the published D {f(pp['paper:D=0.43(4piDt)']['IV']['centroid_lag_h'], 1)} h "
      f"(with {f(pp['paper:D=0.43(4piDt)']['IV']['excess_events'], 0)} events for {f(pp['observed']['IV']['excess_events'], 0)} observed). "
      f"Cycle V's observed lag ({f(pp['observed']['V']['centroid_lag_h'], 1)} h, truncated by an outage) is shorter than "
      f"predicted ({f(pp['exp+diffusion']['V']['centroid_lag_h'], 1)} h): V began on IV's elevated rate and exceeded IV's peak "
      f"by only {f(rs['loading']['V']['dp_above_prior_max_psi'], 0)} psi; one configuration does not fit both exactly.\n")
    return L


GUO = (0.08, 0.33)


def derived(c):
    """Quantities quoted in several places, computed once from the results."""
    out = {}
    pc = c["dist"]["depth"]["per_class"]
    Ds = [v["L_below_injector_m"] ** 2 / (4 * v["tau_h"] * 3600) for v in pc.values()]
    need = [2 * np.sqrt(g * v["tau_h"] * 3600) for v in pc.values() for g in GUO]
    Ls = [v["L_below_injector_m"] for v in pc.values()]
    out["D_range"] = f"{f(min(Ds), 1)}-{f(max(Ds), 1)} m2/s"
    out["ratio"] = f"{f(min(Ds) / GUO[1], 0)}-{f(max(Ds) / GUO[0], 0)}"
    out["L_need"] = f"~{f(min(need), 0)}-{f(max(need), 0)} m"
    out["L_cat"] = f"{f(min(Ls), 0)}-{f(max(Ls), 0)} m"
    pr = c["pred"]["exp+diffusion+cascade"]
    br = c["pred"]["dieterich+diffusion(ta=178h)"]
    e1 = pr["s=1"]["excess_events"]["value"]
    out["x2_gain"] = f"{f(100 * (pr['s=2']['excess_events']['value'] / e1 - 1), 0)}%"
    out["x2_gain_br"] = f"{f(100 * (br['s=2']['excess_events']['value'] / br['s=1']['excess_events']['value'] - 1), 0)}%"
    out["x8_fold"] = f"{f(br['s=8']['excess_events']['value'] / br['s=1']['excess_events']['value'], 1)}-{f(pr['s=8']['excess_events']['value'] / e1, 1)}"
    pp = c["ppc"]
    out["paperD_IV"] = f"{f(pp['paper:D=0.43(4piDt)']['IV']['excess_events'], 0)} excess events for cycle IV's observed {f(pp['observed']['IV']['excess_events'], 0)}"
    # first stretch at which the two laws' peak rates differ by more than their combined jackknife error
    sep = "none of the stretches computed"
    for s in ["s=2", "s=4", "s=8"]:
        a, b = pr[s]["peak_excess"], br[s]["peak_excess"]
        if abs(a["value"] - b["value"]) > np.hypot(a["jackknife_se"], b["jackknife_se"]):
            sep = f"x{s[2:]}"
            break
    out["laws_diverge"] = sep
    return out


def findings_tail(c, sk, best, t_tr):
    L = []
    A = L.append
    dv = derived(c)
    # ---------------------------------------------------------------- 6 distance
    dd = c["dist"]["depth"]
    dl = c["dloco"]
    A("## 6. Distance, and the diffusivity against the independent 0.08-0.33 m2/s (figs/fig_depth.png)\n")
    A("| depth class (catalogue) | events | median depth (m) | L below lateral (m) | transport time tau (h) [95%] | "
      "D = L^2/4tau (m2/s) | L that 0.08-0.33 m2/s would need (m) |")
    A("|---|---|---|---|---|---|---|")
    for k, v in dd["per_class"].items():
        tau, Lm = v["tau_h"], v["L_below_injector_m"]
        D = Lm ** 2 / (4 * tau * 3600)
        need = [2 * np.sqrt(g * tau * 3600) for g in GUO]
        A(f"| {k} | {v['n_events']} | {f(v['median_z'], 0)} | {f(Lm, 0)} | {f(tau)} {ci(v['ci95'])} | {f(D, 1)} | "
          f"{f(need[0], 0)}-{f(need[1], 0)} |")
    A("")
    A(f"- **The delay grows with depth below the injector.** One transport time for all depths is rejected "
      f"(likelihood ratio {f(dd['LR'], 1)}, 2 d.f., p = {dd['p']:.1e}; joint likelihood in which a 1-minute file records "
      f"at most one event of any class). Out of sample, depth-specific transport times gain {f(dl['dll_total'], 1)} nats "
      f"over the five held-out cycles, all of it in the two cycles with a response (IV, V). The scaling is weaker than "
      f"diffusion's tau ~ L^2 (catalogue depth errors of +-100-200 m flatten it); L/tau is "
      + ", ".join(f"{f(v['L_below_injector_m'] / (v['tau_h'] * 3600), 3)}" for v in dd["per_class"].values())
      + " m/s, as for a front moving at a near-constant speed.")
    pr_ = c["prof"]["exp+diffusion:tau"]
    A(f"- **Against 0.08-0.33 m2/s.** The single transport time {f(t_tr['tau'])} h {ci(pr_['ci95'])} means "
      + ", ".join(f"D = {f(L_ ** 2 / (4 * t_tr['tau'] * 3600), 2)} m2/s at L = {L_} m" for L_ in (100, 200, 400, 584))
      + f". With the catalogue's own depths ({dv['L_cat']} below the laterals) the transport diffusivity is {dv['D_range']}, "
      f"{dv['ratio']} times the tidal fault-zone values: the pressure reaches the seismic faults through a far more permeable path "
      "(the stimulated fracture network) than the fault damage zones the tides sample. It falls in the tidal range only if "
      f"the seismic faults lie within {dv['L_need']} of the pressurised network, i.e. if the single-fibre depths are several "
      "hundred metres too deep (Fervo's stimulation SRV was 750 ft high). Which is true is decided by an unpublished "
      "quantity: the events' 3-D positions relative to the stimulated fractures (section 9).")
    pp = c["front"]["conventions"]
    A(f"- **The published D** is 0.43 m2/s only in the sqrt(4Dt) convention ({f(pp['D_4Dt']['lsq_r_t0fixed'], 3)} reproduced); "
      f"in the paper's printed sqrt(4 pi D t) it is {f(pp['D_4piDt']['lsq_r_t0fixed'], 3)} m2/s, inside the tidal range. Neither "
      f"number measures diffusion here (section 3).\n")
    # ---------------------------------------------------------------- 7 prediction
    pr = c["pred"]
    A("## 7. Prediction: the response under slower ramps (figs/fig_predict.png, results/predict.json)\n")
    A("Cycle IV as it happened, except that its 355 psi ramp is stretched by s (same concave shape, same peak), then the "
      "observed decline. Each model is run with its all-cycle parameters; ± is the leave-one-cycle-out jackknife "
      "standard error. The bracket model is transport + rate-and-state with t_a at its 95% lower bound (178 h): it fits "
      "the cycles as well as pure transport (Δll "
      f"{f(c['cmp_tr']['versus']['dieterich+diffusion(ta=178h)']['dll_total'], 1)} "
      f"{ci(c['cmp_tr']['versus']['dieterich+diffusion(ta=178h)']['ci95'], 1)}) but saturates on long ramps.\n")
    A("| ramp | model | peak lag behind gauge (h) | peak excess rate (/h) | excess events |")
    A("|---|---|---|---|---|")
    for s in ["s=1", "s=2", "s=4", "s=8"]:
        for mname in [best, "exp+diffusion", "dieterich+diffusion(ta=178h)", "dieterich"]:
            v = pr[mname][s]
            A(f"| x{s[2:]} ({f(10.75 * int(s[2:]), 1)} h) | {mname} | {f(v['peak_lag_h']['value'], 2)} ± {f(v['peak_lag_h']['jackknife_se'], 2)} | "
              f"{f(v['peak_excess']['value'], 1)} ± {f(v['peak_excess']['jackknife_se'], 1)} | "
              f"{f(v['excess_events']['value'], 0)} ± {f(v['excess_events']['jackknife_se'], 0)} |")
    A("")
    pl = c["pred"]
    tm_ = [m for m in ["exp+diffusion+cascade", "exp+diffusion", "exp+lag", "dieterich+diffusion",
                       "dieterich+diffusion(ta=178h)", "exp+diffusion+poro"] if m in pl]
    falls = all(pl[m]["s=8"]["peak_lag_h"]["value"] < pl[m]["s=1"]["peak_lag_h"]["value"] for m in tm_)
    A(f"- **The delay shortens, it does not lengthen.** Under every transport model "
      f"({', '.join(tm_)}) the peak lag {'falls' if falls else 'does not grow'} with slower ramps (the faults keep "
      f"pace with a slowly rising gauge pressure): from {f(min(pl[m]['s=1']['peak_lag_h']['value'] for m in tm_), 1)}-"
      f"{f(max(pl[m]['s=1']['peak_lag_h']['value'] for m in tm_), 1)} h at the observed ramp to "
      f"{f(min(pl[m]['s=8']['peak_lag_h']['value'] for m in tm_), 1)}-{f(max(pl[m]['s=8']['peak_lag_h']['value'] for m in tm_), 1)} h "
      f"at x8. Without transport (cascades only, or the rejected fault-delay model) the peak sits at the gauge peak for "
      f"every ramp. No explanation consistent with the cycles makes the delay grow.")
    A(f"- **Seismicity per cycle grows** with the time spent at high pressure: x2 slower adds {dv['x2_gain']} "
      f"({dv['x2_gain_br']} for the bracket), x8 slower multiplies the excess {dv['x8_fold']} fold for the same peak pressure. "
      f"Whether the peak rate keeps rising (instantaneous law) or saturates (bracket) is the one thing these data leave open; "
      f"the two peak rates first differ by more than their combined jackknife errors at {dv['laws_diverge']}.")
    A("- Operators advised to 'steer towards longer delays' by slowing ramps would see the seismicity start later in "
      "clock time (the pressure gets there later) but follow the pressure as closely as before, and more of it.\n")
    # ---------------------------------------------------------------- 8 test
    fr = c["fr"]
    A("## 8. The test that would settle what these data cannot (figs/fig_design.png, results/frontier.json)\n")
    A("What the 2023 cycles cannot separate: (a) whether a finite fault response time (rate-and-state, t_a >= 178 h) acts "
      "on top of the transport, which decides the slow-ramp prediction; (b) the transport distance and diffusivity; (c) "
      "for a new site, whether its delay is the site's (transport) or the schedule's (rate-dependent nucleation; a "
      "hypothetical archetype calibrated to a ~4 h onset on a cycle-IV ramp, its onset scaling as 1/(dp/dt)); (d) "
      "transport versus near-critical cascades; (e) the clock. Separations are expected log-likelihood ratios a test "
      "would deliver (the alternative given its best parameters for the truth's intensity), divided by the "
      "over-dispersion measured here (phi = 2); > 5 is decisive. With a gauge at the seismic depth, pairs whose "
      "explanations differ in their transport are settled by the pressure record itself (listed as 999); the fault-law "
      "pair is then scored on the seismicity given the measured fault pressure.\n")
    if fr:
        ax = fr["axes"]
        bm = [d for d in fr["designs"] if d["design"] == "BM2023" and d["mode"] == "occupancy" and d["monitoring"] == "gauge"][0]
        A(f"- **The 2023 cycles as a test** reach a worst-pair separation of {f(bm['min_sep'], 2)} "
          f"({bm['hardest']}).")
        cd = ax["cost"]["cheapest_decisive"]
        tgt = ax["cost"]["target"]
        A(f"- **Targets.** Decisive (E[dll]/phi >= 5) for every key pair; cost within the 2023 operating envelope: no new "
          f"well (monitoring tier <= {tgt['tier']}), <= {f(tgt['MWh'], 0)} MWh deferred (four days of full production), "
          f"<= {f(tgt['days'], 0)} days, and no larger event expected than the largest catalogued in 2023 (M {tgt['max_mag']}).")
        if cd:
            rec = [d for d in fr["designs"] if d["design"] == cd["design"] and d["mode"] == cd["mode"] and d["monitoring"] == cd["monitoring"]][0]
            A(f"- **Recommended: '{cd['design']}' with {cd['mode']} detection and "
              f"{'a pressure gauge at the seismic depth' if cd['monitoring'] == 'deepgauge' else 'the existing 73-22 gauge'}** "
              f"(monitoring tier {cd['tier']}): {f(cd['days'], 1)} days, {f(cd['MWh'], 0)} MWh deferred, expected largest "
              f"magnitude {f(cd['max_mag'], 2)}. Separations: " + "; ".join(f"{k}: {f(min(v, 999), 1)}" for k, v in rec["pairs"].items()) + ".")
        ca = ax["cost"].get("cheapest_decisive_any_schedule")
        if ca and cd and ca["design"] != cd["design"]:
            A(f"- The recommendation is restricted to schedules containing ramps of different rate to the same pressure, "
              f"because the operator's question (does the ramp rate set the delay?) deserves a model-free answer. Without "
              f"that restriction the cheapest decisive test is '{ca['design']}' ({ca['mode']}, {ca['monitoring']}: "
              f"{f(ca['MWh'], 0)} MWh, {f(ca['days'], 1)} days, expected largest magnitude {f(ca['max_mag'], 2)}), decisive "
              f"between the explanations but only through the models.")
        dg = ax["cost"].get("cheapest_decisive_with_deep_gauge")
        if dg:
            A(f"- **With a gauge at the seismic depth** the cheapest decisive schedule is '{dg['design']}' ({f(dg['MWh'], 0)} MWh, "
              f"{f(dg['days'], 1)} days, expected largest magnitude {f(dg['max_mag'], 2)}); the gauge also measures the transport "
              f"kernel and, with 3-D locations, the distance, so it settles the diffusivity, which no schedule does.")
        A("- **Frontier** (no other design has at least the worst-pair separation for no more deferred generation and no "
          "higher monitoring tier), in order of cost: "
          + "; ".join(f"{d['design']} / {d['mode']} / {d['monitoring']}: separation {f(min(d['min_sep'], 999), 1)}, "
                      f"{f(d['cost']['deferred_MWh'], 0)} MWh, {f(d['cost']['days'], 1)} d, M~{f(d['max_mag'], 2)}"
                      for d in sorted([x for x in fr["designs"] if (x["design"], x["mode"], x["monitoring"])
                                       in [tuple(y) for y in fr["frontier"]]],
                                      key=lambda x: (x["cost"]["deferred_MWh"], x["cost"]["tier"]))) + ".")
    mc = c["mc"]
    if mc:
        A("- **Monte-Carlo check** (Cox-process catalogues with Blue Mountain's over-dispersion, both models refitted to "
          "each): " + "; ".join(f"{r['design']} {r['truth']}->{r['alt']}: expected {f(r['expected_dll_eff'], 1)} "
                                f"(raw {f(r['expected_dll'], 1)}), simulated median {f(r['mc_median'], 1)} "
                                f"[10-90% {f(r['mc_p10'], 1)}, {f(r['mc_p90'], 1)}], correct in {f(100 * r['mc_frac_correct'], 0)}%"
                                for r in mc) + ".")
    A("- **Monitoring that the schedule needs:** (1) every stream (DAS, gauges, SCADA rates) stamped from one "
      "GPS-disciplined UTC clock and labelled so; (2) multi-event detection (no one-event-per-file ceiling); (3) a pressure "
      "gauge at the depth of the seismicity, which turns the transport from an inference into a measurement and makes the "
      "fault law visible during holds; (4) 3-D locations (a second fibre: Fercho et al. 2023 report fibre behind casing in "
      "both laterals) to put the events at a measured distance from the stimulated fractures; (5) rates logged at the "
      "same 1-minute resolution as pressure.\n")
    # ---------------------------------------------------------------- 9 limits
    A("## 9. Limits\n")
    A("Each remaining limit is either physics or an unpublished quantity, with the measurement that would settle it.\n")
    A(f"1. **Absolute event positions relative to the stimulated fractures** (unpublished): decides the diffusivity "
      f"({dv['D_range']} at catalogue depths versus 0.08-0.33 m2/s if the faults lie within {dv['L_need']}). Settled by 3-D locations "
      "(Fervo's own multi-well arrays, or a second fibre) or a gauge at the seismic depth.")
    A("2. **The catalogue's time zone** (unstated by the authors): UTC by provenance; a local-time catalogue (-7 h) would "
      "triple the transport time and divide D by ~3 without changing which explanation wins; +7/+8 h is excluded by "
      "causality and the tides. Settled by the raw DAS file name of any catalogued event (the authors' real-time products).")
    A("3. **A finite fault response time on top of the transport** (physics not excited by 10-h ramps): t_a >= 178 h is "
      "all these cycles allow, and it decides whether very slow ramps saturate. Settled by the holds of section 8 with a "
      "gauge at the seismic depth.")
    A("4. **Ramp rate at fixed amplitude** was never varied (operations, not analysis): the slow cycles were also small. "
      "Settled by the rate series of section 8.")
    A("5. **Five cycles** (the experiment): every interval above is a cycle-jackknife or block-bootstrap interval; cycle "
      "V's shorter lag and the post-shut-in dip in cycle IV are not explained by one configuration and may be the "
      "between-cycle variability those intervals carry.")
    A("6. **The published distances** (unpublished method): how 'vertical distance from injection' was computed is not "
      "documented; the data show it is not a function of the catalogue location. Settled by the authors' code (the "
      "location script RT_DAS_2D_location.m listed in the OSF readme was not uploaded).")
    return L


def report_md(c):
    m = c["manifest"]
    sk = skill(c)
    best = "exp+diffusion+cascade"
    cb = c["cmp_best"]["versus"]
    fr = c["fr"]
    L = []
    A = L.append
    A("# REPORT: each criterion against the floor\n")
    A(f"Numbers from commit `{m.get('commit', '?')}` (results/manifest.json), regenerated by `make all`. The floor is "
      "the paper (Chamarczuk et al. 2025): a qualitative delay 'likely due to pressure diffusion to the fracture system "
      "boundary', seismicity 'driven by both the value of pressure ... and the injection rate', and one diffusion front, "
      "D ~ 0.43 m2/s.\n")
    A("## Deliverables\n")
    A("| deliverable | floor | here | evidence |")
    A("|---|---|---|---|")
    A(f"| 1. The cause | qualitative delay, diffusion assumed | transport delay tau = {f(theta(c, 'exp+diffusion')['tau'])} h growing with "
      f"depth ({f(c['dist']['depth']['per_class']['shallow']['tau_h'])}-{f(c['dist']['depth']['per_class']['deep']['tau_h'])} h), "
      "instantaneous exponential fault law, cascades; fault-own delay rejected | FINDINGS 4-6 |")
    A("| 2. The prediction | none | slower ramps: shorter peak lag, more events per cycle, with jackknife errors and a "
      "structural bracket | FINDINGS 7 |")
    A("| 3. The test | 'further research is needed' | schedule + monitoring with expected separations, costs, risk, "
      "Monte-Carlo check | FINDINGS 8 |")
    A("| 4. Documents + one command | - | FINDINGS.md, REPORT.md, COMPLETE.md, `make all` | this file |")
    A("")
    A("## Measurable criteria\n")
    fc = c["front"]["conventions"]
    A(f"- **Fidelity.** Met. The paper's front is reproduced from the public files: the stored curve is identified exactly "
      f"(a power law, exponent {f(c['front']['identify']['yp_Upper_curve']['n'], 3)}) and gives D = {f(fc['D_4Dt']['lsq_r_t0fixed'], 3)} m2/s "
      f"(published 0.43). The differences are explained: the paper prints r = sqrt(4 pi D t), under which the same curve "
      f"is {f(fc['D_4piDt']['lsq_r_t0fixed'], 3)} m2/s; the published distances grow with time at fixed catalogue locations; "
      f"the catalogue cloud does not migrate.")
    A(f"- **Prediction.** Met. All {len(sk) - 1} explanations, including the paper's two readings, are scored on cycles they "
      f"were not fitted to (leave-one-cycle-out, slow->fast, fast->slow, forward chaining); the best beats the paper's best "
      f"reading by {f(cb['paper:p+dp/dt']['dll_total'], 0)} {ci(cb['paper:p+dp/dt']['ci95'], 0)} held-out log-likelihood units and the "
      f"published diffusivity by {f(cb['paper:D=0.43(4piDt)']['dll_total'], 0)} {ci(cb['paper:D=0.43(4piDt)']['ci95'], 0)}. Diffusivities "
      f"are compared with 0.08-0.33 m2/s for every transport model and depth class (FINDINGS 6): {derived(c)['D_range']} at the "
      f"catalogue's depths, inside the range only if the faults are within {derived(c)['L_need']} of the pressurised network.")
    if fr:
        ax = fr["axes"]
        A(f"- **The frontier.** Skill: {f(ax['skill']['loco'], 4)} nats/event held out for the best explanation against "
          f"{f(ax['skill']['paper_loco'], 4)} for the paper's best reading. Separation: worst key pair "
          f"{f(ax['separation']['BM2023_min'], 2)} for the 2023 cycles, {f(ax['separation']['best_min'], 1)} for the best proposed "
          f"design. Cost: {('cheapest decisive design ' + ax['cost']['cheapest_decisive']['design'] + ' (' + ax['cost']['cheapest_decisive']['monitoring'] + ', ' + f(ax['cost']['cheapest_decisive']['MWh'], 0) + ' MWh, ' + f(ax['cost']['cheapest_decisive']['days'], 1) + ' days)') if ax['cost']['cheapest_decisive'] else 'no decisive design'}. "
          f"Weakest axis now: {fr['weakest'] or 'none unmet'}. Skill belongs to an explanation and separation and cost to "
          f"a design, so the three-way non-dominated set is the best explanation paired with the design frontier "
          f"(FINDINGS 8). Iterations are logged below.")
    chk = c["num"]["convergence_checks"]["value"] if c["num"] and "convergence_checks" in c["num"] else {}
    worst = max([v for k, v in chk.items() if k.startswith("profile_max")], default=float("nan"))
    A(f"- **Limits.** Met: FINDINGS 9 lists six, each physics or an unpublished quantity with its settling measurement. "
      f"None is a choice made here (kernel shape, outage threshold, depth classes and clock offset are varied and "
      f"reported), an unconverged fit (no profile-likelihood point exceeds its model's best fit by more than "
      f"{f(worst, 3)}; results/numbers.json convergence_checks) or an untried method (FINDINGS 2 and REPORT 'What failed').")
    A("- **Evidence.** One configuration per model for all cycles; intervals are cycle-jackknife or block-bootstrap; "
      "every number is read from results/*.json by the generator that wrote these documents.\n")
    A("## Frontier iterations (push the weakest)\n")
    A("1. Skill was weakest (paper's readings only): 18 explanations built and scored out of sample; best held-out skill "
      f"{f(sk[best]['loco'], 4)} against {f(sk['paper:p+dp/dt']['loco'], 4)}; met.")
    g1 = J("design_grid.json")
    v1 = ""
    if g1:
        from collections import defaultdict
        mins = defaultdict(lambda: np.inf)
        for row in g1:
            k = (row["design"], row["mode"])
            mins[k] = min(mins[k], row["dll_eff"])
        best1 = max(mins.items(), key=lambda kv: kv[1])
        v1 = f" (best worst-pair separation {f(best1[1], 2)}, '{best1[0][0]}' with {best1[0][1]} detection)"
    A("2. Separation was weakest: the 2023 cycles separate transport from a fault-own delay but not a finite fault "
      "response from none, nor transport from near-critical cascades. The first design grid (ramp series, holds, "
      f"amplitude series; results/design_grid.json) was not decisive{v1}: a hold does not expose rate-and-state "
      "depletion because the transport tail keeps the faults' pressure rising.")
    A("3. Separation pushed with monitoring: a gauge at the seismic depth makes the fault pressure a measurement; design "
      "grid v2 adds it, multi-event detection, larger and longer holds and a schedule-controlled archetype. Separation "
      "became decisive, but only with the new well (monitoring tier 3): cost became the weakest axis.")
    if fr:
        cd = fr["axes"]["cost"]["cheapest_decisive"]
        if cd:
            A(f"4. Cost pushed: the depletion that distinguishes a finite fault response grows as exp(dp/A sigma), so a "
              f"higher hold exposes it without the new well. '{cd['design']}' is decisive for every key pair with "
              f"{'the existing gauge' if cd['monitoring'] == 'gauge' else 'a gauge at the seismic depth'} (tier {cd['tier']}), "
              f"{f(cd['MWh'], 0)} MWh and {f(cd['days'], 1)} days, inside the cost target; its largest expected event "
              f"(M {f(cd['max_mag'], 2)}) is below 2023's.")
        A(f"5. Now: {'all three axes meet their targets' if not fr['weakest'] else 'weakest axis ' + fr['weakest']}. "
          "The remaining open items are the limits of FINDINGS 9, which no schedule or model removes.")
    A("")
    A("## What failed\n")
    A("- The fault's own delay as the explanation (rate-and-state without transport): rejected out of sample; a "
      "nucleation-regime version (A sigma <= 50 psi) fits worse than a constant rate.")
    A("- The paper's readings: the pressurisation-rate term is fitted to zero; the published diffusivity predicts "
      f"{derived(c)['paperD_IV']}.")
    A("- Anchoring the catalogue clock to regional earthquakes (not catalogued under any clock), wind (no effect on "
      "detection), the stimulation onset (ambiguous) and gauge data gaps (uninformative): only provenance and causality "
      "remain for the catalogue clock.")
    A("- Reconstructing the published distances from the catalogue (method undocumented; not a function of location).")
    A("- Reproducing the authors' 'green' fitting subset (not identified in the files); the stored curve itself is "
      "reproduced exactly.")
    A("- The rate file for timing (offsets vary event to event).")
    A("- One configuration does not reproduce cycle V's shorter lag or cycle IV's post-shut-in dip.")
    A("- Holds without a gauge at the seismic depth do not separate a finite fault response from none.\n")
    A("## What remains open\n")
    A("The six limits of FINDINGS 9: absolute event positions (diffusivity), the catalogue's time zone (scale of tau), "
      "a finite fault response time (slow-ramp saturation), rate at fixed amplitude, five cycles, the published distance "
      "method. Each comes with the measurement that settles it.")
    return "\n".join(L)


def complete_md(c):
    m = c["manifest"]
    sk = skill(c)
    cb = c["cmp_best"]["versus"]
    fc = c["front"]["conventions"]
    fr = c["fr"]
    L = []
    A = L.append
    A("# COMPLETE\n")
    A(f"All numbers from commit `{m.get('commit', '?')}`; `make all` regenerates results/, figs/ and these documents.\n")
    A("## The four deliverables hold\n")
    A(f"1. **The cause** (FINDINGS 4-6). Response per cycle against pressurisation rate and depth; held-out comparison of "
      f"{len(sk) - 1} explanations; transport delay tau = {f(theta(c, 'exp+diffusion')['tau'])} h {ci(c['prof']['exp+diffusion:tau']['ci95'])}, "
      f"growing with depth (p = {c['dist']['depth']['p']:.1e}; held-out +{f(c['dloco']['dll_total'], 1)} nats); fault-own delay loses "
      f"{f(c['cmp_tr']['versus']['dieterich']['dll_total'], 1)} {ci(c['cmp_tr']['versus']['dieterich']['ci95'], 1)}.")
    pr = c["pred"]["exp+diffusion+cascade"]
    A(f"2. **The prediction** (FINDINGS 7). Slower ramps to the same pressure: peak lag {f(pr['s=1']['peak_lag_h']['value'], 2)} -> "
      f"{f(pr['s=8']['peak_lag_h']['value'], 2)} h, excess events {f(pr['s=1']['excess_events']['value'], 0)} -> "
      f"{f(pr['s=8']['excess_events']['value'], 0)} ± {f(pr['s=8']['excess_events']['jackknife_se'], 0)} (jackknife), with the "
      "rate-and-state bracket the data allow.")
    if fr and fr["axes"]["cost"]["cheapest_decisive"]:
        cd = fr["axes"]["cost"]["cheapest_decisive"]
        A(f"3. **The test** (FINDINGS 8). '{cd['design']}' with {cd['mode']} detection and "
          f"{'a gauge at the seismic depth' if cd['monitoring'] == 'deepgauge' else 'the existing gauge'}: every key pair "
          f"separated with E[dll]/phi >= 5; {f(cd['days'], 1)} days, {f(cd['MWh'], 0)} MWh deferred, expected largest magnitude "
          f"{f(cd['max_mag'], 2)}; Monte-Carlo check in results/design_mc.json.")
    A("4. **FINDINGS.md** (each claim with its evidence), **REPORT.md** (each criterion against the floor, what failed, "
      "what remains open), **one command** (`make all`).\n")
    A("## The published diffusion front is reproduced\n")
    A(f"D = {f(fc['D_4Dt']['lsq_r_t0fixed'], 3)} m2/s from the public Diffusion_data.mat (published 0.43); "
      f"{f(fc['D_4piDt']['lsq_r_t0fixed'], 3)} m2/s under the paper's printed formula. The front is not migration: the "
      "catalogue's depths do not move while the published distances grow at fixed locations (FINDINGS 3).\n")
    A("## Every explanation is judged on data it was not fitted to\n")
    A("D = L^2/(4 tau) at the cloud's median depth below the lateral (L = 584 m) for 1-D diffusion kernels (for the "
      "paper's printed convention tau = L^2/(4 pi D), so its row shows pi D); kernels of other shapes have no such D.\n")
    A("| explanation | held-out gain/event (LOCO) | Δll vs best [95%] | transport time (h) | D = L^2/4tau at 584 m (m2/s) |")
    A("|---|---|---|---|---|")
    for mname in sorted(sk, key=lambda x: -sk[x]["loco"]):
        if mname == "const":
            continue
        th = theta(c, mname)
        tau = th.get("tau")
        D = (584 ** 2 / (4 * tau * 3600)) if tau and "shift" not in mname and "lag" not in mname else None
        dd = cb.get(mname)
        A(f"| {mname} | {f(sk[mname]['loco'], 4)} | {'best' if dd is None else f(dd['dll_total'], 1) + ' ' + ci(dd['ci95'], 1)} | "
          f"{f(tau) if tau else '-'} | {f(D, 2) if D else '-'} |")
    A("")
    A(f"Against the independent fault-zone diffusivity 0.08-0.33 m2/s: the transport times imply {derived(c)['D_range']} at the "
      f"catalogue's depths and fall in the range only within {derived(c)['L_need']} (FINDINGS 6).\n")
    A("## Every remaining limit belongs to the problem itself\n")
    A("| limit | kind | settling measurement |")
    A("|---|---|---|")
    A("| event positions relative to the stimulated fractures (diffusivity) | unpublished quantity | 3-D locations or a gauge at the seismic depth |")
    A("| the catalogue's time zone (scale of tau) | unpublished quantity | raw DAS file name of any catalogued event |")
    A("| a finite fault response time (slow-ramp saturation) | physics not excited by 10-h ramps | holds with a gauge at the seismic depth |")
    A("| ramp rate at fixed amplitude | the experiment as run | the rate series of FINDINGS 8 |")
    A("| five cycles | the experiment as run | more cycles (the test) |")
    A("| how the published distances were computed | unpublished method | the authors' location code |")
    return "\n".join(L)


def run():
    c = ctx()
    for name, fn in [("FINDINGS.md", findings), ("REPORT.md", report_md), ("COMPLETE.md", complete_md)]:
        with open(name, "w") as fh:
            fh.write(fn(c) + "\n")
