# FINDINGS: what sets the seismicity delay in the cycled Blue Mountain reservoir

Every number below was written by `make all` at commit `81a6bd05ce4e544332c37230dd5f0a7271390afc` (results/manifest.json); each says what it is compared against and where it is stored (results/*.json, figures in figs/). Five cycles are five cycles: intervals are block-bootstrap or leave-one-cycle-out jackknife intervals, never Poisson ones.

## Summary

1. **The delay is real, and it belongs to the site, not the schedule.** On a common UTC clock the seismicity follows the 73-22 gauge pressure through a transport delay: transport time tau = 2.35 h (profile 95% [1.99, 3.02] h; 1-D diffusion kernel), growing with depth below the injector lateral from 1.03 h to 3.72 h. The faults answer the pressure they feel at once, exponentially (A sigma/mu = 203 psi). A delay belonging to the faults themselves (rate-and-state without transport) is rejected out of sample; one added to the transport is not detected.
2. **The published diffusion front is reproduced but is not a diffusion front.** The stored curve is exactly r = 89.99 (t - 18.950 h)^0.4727; a least-squares sqrt(4 D t) fit to it gives D = 0.434 m2/s (the published 0.43), or 0.138 m2/s with the paper's printed sqrt(4 pi D t). The growth is in the published distances themselves: events at one fixed catalogue location are assigned distances growing by 2.3 m/h, while the catalogue's own depths do not migrate.
3. **What the paper's readings lose on unseen cycles:** held-out log-likelihood 82 [48, 121] below the best explanation for 'pressure and pressurisation rate' (its pressurisation-rate term is fitted to zero), and 111 [51, 176] to 207 [111, 313] for the published diffusivity.
4. **Slower ramps do not buy a longer delay.** For cycle IV's 355 psi reached 8x more slowly the peak lag falls from 2.2 to 1.0 h and the cycle's excess events rise from 238 to 1963 (± jackknife 307); the rate-and-state bracket allowed by the data gives 1263. The lever on seismicity is the pressure reached and the time spent there, not the ramp rate.
5. **The test.** 1-h ramp to +300 psi, 16-h ramp to +300 psi, 2-h ramp to +600 psi held 48 h, every stream on one GPS-disciplined UTC clock: decisive (E[dll]/phi >= 5) between every pair of explanations these data cannot separate, with the existing gauge, in 12.8 days and 234 MWh of deferred generation (section 8). A gauge at the seismic depth would also measure the transport and settle the diffusivity.
6. **The clocks.** The pressure file labelled PST is on UTC (Earth tide; the daily curtailments then fall in local daylight, as the paper says they were meant to). The catalogue is on UTC by provenance. Offsets of +7/+8 h, the PROBLEM's worry, would make shallow seismicity precede the reservoir pressure by hours.

## 1. Clocks: one time base for gauge and catalogue (figs/fig_clock.png)

- **Gauge = UTC, not PST.** In the 15-20 March quiet window the gauge carries the Earth tide (fitted tidal amplitude 0.072 psi, within ~0.1 psi of other slow variation). Regressing it on the UTC solid-Earth tide (pysolid) and the UTC Winnemucca barometer, with the physical sign (pressure falls when the ground dilates), gives a gauge offset of -0.65 h from UTC, moving-block bootstrap 95% [-1.90, 0.48] h (second half of the window: -0.05 h, [-0.78, 1.06]). The PST (-8 h) and PDT (-7 h) alignments fit only with the unphysical sign (coefficients 0.12 and 0.14 psi/m, against -0.37 at the best offset); with the sign imposed they collapse to 'no tide', 1.4 log-likelihood units worse (residuals are strongly autocorrelated: lag-1 rho = 0.983, effective n = 5.9; source clock.json).
- **Operating schedule.** Read on UTC, the five curtailments run from 09:04, 07:04, 07:10, 08:25, 08:45 to 17:00, 19:10, 19:10, 19:10, 19:15 local time (PDT); cycles II and III last 12.09 and 12.0 h, the paper's '12 hours'. Production is restricted through the solar day, as the paper says restricted production is for. Read on PST they would run from mid-afternoon to 03:10 local.
- **Catalogue = UTC by provenance.** The raw files are named BM73-22_UTC_<date>_<time>, events carry their 1-minute file's start time (seconds fields drift with file boundaries), the MATLAB datetimes carry no zone, and the authors' Fig. 6 plots catalogue and gauge on one axis unshifted (pressure peaks drawn at ~02:00 on 4 and 5 May, the raw gauge stamps). 44% of outages end between 13 and 15 h on the catalogue clock (08-10 h in Houston, where the system was run from, if it is UTC), but the clustering is weak (Rayleigh p = 0.13).
- **Causality rules out the PROBLEM's 7-8 h offsets.** Which depths respond first does not depend on the clock: shallow events lead deep ones by 3.25 h in the model-free cross-correlation (xcorr.json). On UTC the shallow class, 184 m below the lateral, answers the gauge after 1.03 h (95% [0.59, 1.59]; section 6). A catalogue running more than ~1.6 h ahead of the gauge would therefore put the shallow response before the reservoir pressure that drives it; at +7/+8 h it would lead by 5.5-7.4 h, although the gauge answers production changes within minutes. A catalogue on local time (-7 h) is not excluded by physics: it would lengthen every lag by 7 h (transport time 7.14 h instead of 2.35 h) and change no conclusion below except the diffusivity, which it lowers ~3x.
- **The rate file cannot be used for timing.** Its shut-ins and restarts sit -3.1 to 5.5 h from the gauge's sharp responses, varying from event to event, and its cycle IV/V shut-ins last ~8 h against the gauge's 10.5-10.75 h; the authors' Fig. 6d shows the same mismatch. It is used only for volumes (1.4e+05 m3 injected and 1.15e+05 m3 produced, reading the rates as gpm, against the paper's 1.35e5 and 1.07e5 m3 over a slightly shorter span).

## 2. The catalogue as a measurement

- No two of the 13,351 events share a time stamp: each 1-minute DAS file yields at most one event, so the catalogue is an occupancy record and observed rates saturate at 60/h. All rates and likelihoods here use P(file occupied) = 1 - exp(-R dt), which undoes the saturation (the highest hourly rate in the cycles is 46/h corrected against 32/h raw).
- Gaps of more than 1 h are outages (at the 5-45/h rates seen, a 1-h gap by chance has probability < 1%), treated as unobserved (89% of minutes observed in the cycling window). Results do not change for outage thresholds of 0.75 or 1.5 h (transport time 2.29 h, 2.35 h, 2.35 h).
- Magnitudes do not change across shut-ins or restarts (two-sample KS p >= 0.24 in all ten 3-h comparisons), so rate changes there are not detection artefacts. Regional earthquakes (USGS ComCat within 400 km, amplitude proxy above the catalogue's floor) fall in catalogued minutes only at the chance rate under every clock (+0 h: 2/17, -7 h: 5/17, -8 h: 1/17, +7 h: 3/16, +8 h: 2/17; base rate 0.16), so the real-time system kept local events only and they cannot anchor its time; Winnemucca wind does not modulate detection (|r| <= 0.072).

## 3. Fidelity: the published diffusion front (figs/fig_front.png)

- **Reproduced.** The stored 'best-fit synthetic diffusion curve' (Diffusion_data.mat, one value per event of Vertical_distance_from_injection_FLEX.txt) is exactly r = 89.98553 (t - 18.95028)^0.47269 (r in m, t in h since 29 Apr 00:00 UTC; origin 2023-04-29 18:57:00), residual 3.2e-10 m. Fitting r = sqrt(4 D (t - t0)) to it by least squares with its own origin gives D = 0.434 m2/s (the published 0.43); its end point gives 0.423; with the paper's printed r = sqrt(4 pi D t) the same curve means D = 0.138 m2/s. The exponent is 0.473, not 1/2. Fronts fitted to the published distances directly depend on the envelope chosen: median 0.33, 75th percentile 0.48, 90th percentile 0.74 m2/s (sqrt(4Dt)); the 'green' events the authors fitted are not identified in the data, and the curve sits near the median, not on an upper bound.
- **Why it is not migration.** The FLEX events are the catalogue's events (2251 of 2279 match a catalogue time stamp to the second; the rest are 1-5 min off). Within one 40-m catalogue cell (fixed depth and distance from 73-22) the published 'distance to injection' grows with time in 98% of the 53 populated cells, by 2.30 m/h (median; median correlation with time 0.68). Cell constants plus one common function of time leave 22.9 m of the 148.4 m within-cell scatter. The catalogue's own median depth below the injector drifts by -0.20 m/h (95% [-0.41, 0.02]), -39 m over the cycles, where a front with D = 0.43 needs +961 m (sqrt(4Dt)) or +1703 m (sqrt(4 pi D t)). The seismic cloud did not migrate; the front's growth is a property of how the distances were assigned. A triggering front would in any case have passed long before: injection had run for 20 days and the cloud was already active at ~10 events/h.

## 4. The response to each cycle (results/response.json, figs/fig_cycles.png)

| cycle | ramp (h) | Δp (psi) | mean dp/dt (psi/h) | excess events [68%] | centroid lag (h) [68%] | xcorr lag (h) |
|---|---|---|---|---|---|---|
| I | 7.92 | 105 | 13.3 | -63 [-32, 83] | -0.1 [-0.4, 2.4] | 11.5 |
| II | 12.09 | 142 | 11.7 | -7 [-53, 37] | -0.9 [-1.0, 1.4] | 2.5 |
| III | 12.00 | 138 | 11.5 | 24 [-17, 63] | -0.5 [-2.7, -0.1] | 9.5 |
| IV | 10.75 | 355 | 33.0 | 240 [185, 311] | +4.3 [3.8, 4.8] | 5.5 |
| V | 10.50 | 360 | 34.3 | 163 [137, 255] | +1.5 [1.1, 2.2] | 5.0 |

- **Pressurisation rate.** The three slow ramps (restricted production, ~12 psi/h, ~105-140 psi) gave no detectable excess seismicity; the two fast ones (production halted, ~33 psi/h, 355-360 psi) gave hundreds of excess events, the rate peaking after the gauge peak. Ramp rate and amplitude rose together, and IV and V were loaded alike, so these data cannot vary the rate at fixed amplitude: that is the first thing the proposed test does.
- **The paper's 'pressure and pressurisation rate'.** A pressurisation-rate term on the gauge pressure is fitted to zero (k = 0.0000 events/psi); on the transported pressure it is k = 0.0000 events/psi and changes the held-out log-likelihood by -0.5 [-1.2, 0.2] against transport alone. Within these cycles the seismicity answers the pressure level the faults feel, not its rate of change.
- **Distance.** Split by catalogue depth, deeper events lag more (section 6). Split by radial distance from 73-22 there is no difference (LR = 0.97, p = 0.62), as expected: 73-22 is a gauge well at the laterals' midpoint, not the source; the stimulated volume runs ~450 m along the laterals either side of it (3000 ft long; Norbeck et al. 2023, Stanford Geothermal Workshop).
- **A transient not explained.** In cycle IV the rate falls from 15.0/h in the 3 h before the shut-in to 9.8/h in the 3 h after (p = 0.11; the restart then raises it from 20.5 to 32.9/h, p = 0.008): the 'rapid decrease ... coinciding with production level reductions' the paper notes. No model reproduces the dip; a poroelastic term of either sign does not improve held-out skill.

## 5. What explains the delay: every explanation on cycles it was not fitted to (figs/fig_models.png)

One gauge-pressure forcing on the common UTC clock; transport (none / 1-D diffusion kernel erfc(sqrt(tau/t)) / exponential kernel / rigid shift) times a fault law (exponential = Dieterich with t_a -> infinity / full Dieterich / Coulomb threshold with memory / stressing rate), optionally with Omori-type cascades from the catalogued events. One parameter set for all cycles. Scores: occupancy log-likelihood on held-out cycles (leave-one-cycle-out), and transfer from slow to fast ramps and back. Gains are per held-out event over a constant rate fitted to the same training data; Δll is against the best model, 95% moving-block (3 h) bootstrap.

| explanation | LOCO gain | slow→fast | fast→slow | Δll vs best [95%] |
|---|---|---|---|---|
| exp+diffusion+cascade: transport (1-D diffusion kernel) + instantaneous exponential fault law + earthquake cascades | 0.1544 | 0.208 | 0.185 | best |
| dieterich+diffusion(ta=178h): transport + Dieterich with t_a at its 95% lower bound (178 h) | 0.1458 | 0.062 | 0.167 | 13.6 [1.1, 25.9] |
| dieterich+diffusion: transport + Dieterich rate-and-state (all parameters free) | 0.1450 | 0.028 | 0.045 | 14.8 [5.3, 24.8] |
| exp+diffusion: transport (1-D diffusion kernel) + instantaneous exponential fault law | 0.1449 | 0.193 | 0.173 | 15.0 [5.6, 25.0] |
| exprate+diffusion: transport + exponential law + a pressurisation-rate term (the paper's two drivers, transported) | 0.1446 | 0.193 | 0.173 | 15.5 [6.0, 25.6] |
| dieterich+lag: transport (exponential kernel) + Dieterich | 0.1442 | -0.295 | 0.171 | 16.0 [5.6, 26.8] |
| exp+cascade: no transport: exponential law + earthquake cascades | 0.1437 | 0.220 | 0.174 | 16.8 [6.7, 27.4] |
| exp+lag: transport (exponential kernel) + instantaneous exponential fault law | 0.1435 | 0.227 | 0.171 | 17.2 [6.3, 28.4] |
| exp+gamma: transport (gamma kernel, shape free) + instantaneous exponential fault law | 0.1425 | 0.228 | 0.161 | 18.8 [7.3, 31.3] |
| exp+diffusion+poro: transport + instantaneous poroelastic term + exponential law | 0.1423 | 0.197 | 0.173 | 19.1 [7.9, 30.7] |
| dieterich+cascade: Dieterich, no transport, + cascades | 0.1418 | 0.091 | 0.174 | 19.9 [8.3, 33.0] |
| exp+shift: rigid delay + instantaneous exponential fault law | 0.1311 | 0.185 | 0.139 | 36.9 [9.2, 68.9] |
| coulomb+diffusion: transport + Coulomb threshold with stress memory (Kaiser) | 0.1217 | 0.165 | 0.096 | 51.7 [22.6, 81.9] |
| dieterich: Dieterich rate-and-state on the gauge pressure: the faults' own delay, no transport | 0.1154 | 0.030 | 0.033 | 61.7 [31.1, 98.3] |
| rate+diffusion: transport + stressing-rate law | 0.1035 | 0.156 | -0.038 | 80.6 [43.8, 118.2] |
| exp: no delay: exponential law on the gauge pressure | 0.1028 | 0.175 | 0.101 | 81.7 [47.8, 121.4] |
| paper:p+dp/dt: paper's reading 1: pressure and pressurisation rate, no delay | 0.1028 | 0.174 | 0.101 | 81.7 [47.8, 121.4] |
| paper:D=0.43(4piDt): paper's reading 2': published D=0.43 m2/s, paper's printed r=sqrt(4 pi D t) | 0.0842 | 0.002 | 0.166 | 111.1 [51.1, 175.7] |
| paper:D=0.43(4Dt): paper's reading 2: published D=0.43 m2/s over the cloud's depth offset, r=sqrt(4Dt) | 0.0233 | -1.338 | 0.000 | 207.4 [110.7, 313.1] |
| coulomb: Coulomb threshold with memory, no transport | -0.0011 | 0.001 | -0.000 | 246.1 [144.4, 351.7] |
| dieterich:nucleation: the faults' own delay in the nucleation regime (A sigma <= 50 psi), no transport | -0.0097 | -0.011 | -0.003 | 259.7 [147.6, 375.0] |

- **Transport is needed.** Without it, a fault response alone (Dieterich) loses 46.7 [20.6, 79.4] to transport alone, and no delay at all loses 66.7 [36.2, 100.9]. With cascades but no transport the loss to transport+cascades is 16.8 [6.7, 27.4].
- **A fault delay on top is not detected.** Dieterich added to transport: -0.2 [-4.6, 3.8]; the profile likelihood puts t_a >= 178 h (95%), so on these cycles the faults respond in their exponential, pressure-level-controlled regime (A sigma/mu = 184 psi). A rigid shift instead of diffusive transport scores 21.9 [-5.9, 54.4] lower (not significant alone; it loses 36.9 [9.2, 68.9] to the best model): the response looks smoothed as well as delayed.
- **Cascades add clustering, not the delay.** Adding Omori cascades to transport gains 15.0 [5.6, 25.0] and leaves tau at 2.31 h (branching ratio 0.32); without transport the cascade fit runs to a near-critical branching ratio (0.99) and still loses.
- **Per-cycle check (held out).** Cycle IV's observed centroid lag is 4.3 h; transport models predict 3.8-4.3 h, the fault-delay model 0.1 h, the published D 6.5 h (with 37 events for 240 observed). Cycle V's observed lag (1.5 h, truncated by an outage) is shorter than predicted (3.3 h): V began on IV's elevated rate and exceeded IV's peak by only 61 psi; one configuration does not fit both exactly.

## 6. Distance, and the diffusivity against the independent 0.08-0.33 m2/s (figs/fig_depth.png)

| depth class (catalogue) | events | median depth (m) | L below lateral (m) | transport time tau (h) [95%] | D = L^2/4tau (m2/s) | L that 0.08-0.33 m2/s would need (m) |
|---|---|---|---|---|---|---|
| shallow | 702 | 2520 | 184 | 1.03 [0.59, 1.59] | 2.3 | 34-70 |
| mid | 997 | 2880 | 544 | 3.33 [2.16, 5.02] | 6.2 | 62-126 |
| deep | 896 | 3080 | 744 | 3.72 [2.52, 5.42] | 10.3 | 65-133 |

- **The delay grows with depth below the injector.** One transport time for all depths is rejected (likelihood ratio 20.5, 2 d.f., p = 3.4e-05; joint likelihood in which a 1-minute file records at most one event of any class). Out of sample, depth-specific transport times gain 10.9 nats over the five held-out cycles, all of it in the two cycles with a response (IV, V). The scaling is weaker than diffusion's tau ~ L^2 (catalogue depth errors of +-100-200 m flatten it); L/tau is 0.050, 0.045, 0.055 m/s, as for a front moving at a near-constant speed.
- **Against 0.08-0.33 m2/s.** The single transport time 2.35 h [1.99, 3.02] means D = 0.30 m2/s at L = 100 m, D = 1.18 m2/s at L = 200 m, D = 4.72 m2/s at L = 400 m, D = 10.07 m2/s at L = 584 m. With the catalogue's own depths (184-744 m below the laterals) the transport diffusivity is 2.3-10.3 m2/s, 7-129 times the tidal fault-zone values: the pressure reaches the seismic faults through a far more permeable path (the stimulated fracture network) than the fault damage zones the tides sample. It falls in the tidal range only if the seismic faults lie within ~34-133 m of the pressurised network, i.e. if the single-fibre depths are several hundred metres too deep (Fervo's stimulation SRV was 750 ft high). Which is true is decided by an unpublished quantity: the events' 3-D positions relative to the stimulated fractures (section 9).
- **The published D** is 0.43 m2/s only in the sqrt(4Dt) convention (0.434 reproduced); in the paper's printed sqrt(4 pi D t) it is 0.138 m2/s, inside the tidal range. Neither number measures diffusion here (section 3).

## 7. Prediction: the response under slower ramps (figs/fig_predict.png, results/predict.json)

Cycle IV as it happened, except that its 355 psi ramp is stretched by s (same concave shape, same peak), then the observed decline. Each model is run with its all-cycle parameters; ± is the leave-one-cycle-out jackknife standard error. The bracket model is transport + rate-and-state with t_a at its 95% lower bound (178 h): it fits the cycles as well as pure transport (Δll -1.4 [-11.4, 7.6]) but saturates on long ramps.

| ramp | model | peak lag behind gauge (h) | peak excess rate (/h) | excess events |
|---|---|---|---|---|
| x1 (10.8 h) | exp+diffusion+cascade | 2.18 ± 0.15 | 15.8 ± 2.6 | 238 ± 34 |
| x1 (10.8 h) | exp+diffusion | 2.11 ± 0.16 | 14.7 ± 2.2 | 220 ± 28 |
| x1 (10.8 h) | dieterich+diffusion(ta=178h) | 3.16 ± 0.53 | 13.1 ± 1.6 | 202 ± 18 |
| x1 (10.8 h) | dieterich | -0.05 ± 0.00 | 17.9 ± 1.1 | 194 ± 9 |
| x2 (21.5 h) | exp+diffusion+cascade | 1.61 ± 0.12 | 22.7 ± 3.9 | 439 ± 65 |
| x2 (21.5 h) | exp+diffusion | 1.58 ± 0.11 | 21.0 ± 3.2 | 405 ± 53 |
| x2 (21.5 h) | dieterich+diffusion(ta=178h) | 2.25 ± 0.37 | 18.7 ± 2.0 | 360 ± 31 |
| x2 (21.5 h) | dieterich | -0.10 ± 0.00 | 18.8 ± 1.1 | 326 ± 16 |
| x4 (43.0 h) | exp+diffusion+cascade | 1.25 ± 0.09 | 31.0 ± 5.3 | 900 ± 138 |
| x4 (43.0 h) | exp+diffusion | 1.21 ± 0.09 | 28.3 ± 4.4 | 825 ± 112 |
| x4 (43.0 h) | dieterich+diffusion(ta=178h) | 1.56 ± 0.28 | 23.0 ± 2.1 | 683 ± 56 |
| x4 (43.0 h) | dieterich | -0.15 ± 0.00 | 20.6 ± 1.2 | 618 ± 30 |
| x8 (86.0 h) | exp+diffusion+cascade | 0.98 ± 0.06 | 39.8 ± 6.9 | 1963 ± 307 |
| x8 (86.0 h) | exp+diffusion | 0.96 ± 0.08 | 36.1 ± 5.6 | 1790 ± 248 |
| x8 (86.0 h) | dieterich+diffusion(ta=178h) | 0.96 ± 0.19 | 22.1 ± 1.7 | 1263 ± 99 |
| x8 (86.0 h) | dieterich | -0.29 ± 0.02 | 24.6 ± 1.4 | 1313 ± 63 |

- **The delay shortens, it does not lengthen.** Under every transport model (exp+diffusion+cascade, exp+diffusion, exp+lag, dieterich+diffusion, dieterich+diffusion(ta=178h), exp+diffusion+poro) the peak lag falls with slower ramps (the faults keep pace with a slowly rising gauge pressure): from 2.0-3.2 h at the observed ramp to 0.3-1.4 h at x8. Without transport (cascades only, or the rejected fault-delay model) the peak sits at the gauge peak for every ramp. No explanation consistent with the cycles makes the delay grow.
- **Seismicity per cycle grows** with the time spent at high pressure: x2 slower adds 84% (78% for the bracket), x8 slower multiplies the excess 6.2-8.2 fold for the same peak pressure. Whether the peak rate keeps rising (instantaneous law) or saturates (bracket) is the one thing these data leave open; the two peak rates first differ by more than their combined jackknife errors at x4.
- Operators advised to 'steer towards longer delays' by slowing ramps would see the seismicity start later in clock time (the pressure gets there later) but follow the pressure as closely as before, and more of it.

## 8. The test that would settle what these data cannot (figs/fig_design.png, results/frontier.json)

What the 2023 cycles cannot separate: (a) whether a finite fault response time (rate-and-state, t_a >= 178 h) acts on top of the transport, which decides the slow-ramp prediction; (b) the transport distance and diffusivity; (c) for a new site, whether its delay is the site's (transport) or the schedule's (rate-dependent nucleation; a hypothetical archetype calibrated to a ~4 h onset on a cycle-IV ramp, its onset scaling as 1/(dp/dt)); (d) transport versus near-critical cascades; (e) the clock. Separations are expected log-likelihood ratios a test would deliver (the alternative given its best parameters for the truth's intensity), divided by the over-dispersion measured here (phi = 2); > 5 is decisive. With a gauge at the seismic depth, pairs whose explanations differ in their transport are settled by the pressure record itself (listed as 999); the fault-law pair is then scored on the seismicity given the measured fault pressure.

- **The 2023 cycles as a test** reach a worst-pair separation of 0.90 (exp+diffusion -> exp+cascade).
- **Targets.** Decisive (E[dll]/phi >= 5) for every key pair; cost within the 2023 operating envelope: no new well (monitoring tier <= 1), <= 336 MWh deferred (four days of full production), <= 21 days, and no larger event expected than the largest catalogued in 2023 (M 0.46).
- **Recommended: 'rate2@300+hold48@600' with occupancy detection and the existing 73-22 gauge** (monitoring tier 0): 12.8 days, 234 MWh deferred, expected largest magnitude 0.35. Separations: dieterich+diffusion(ta=178h) -> exp+diffusion: 17.0; exp+diffusion -> nucleation: 183.8; nucleation -> exp+diffusion: 451.7; exp+diffusion -> exp+cascade: 15.7; exp+cascade -> exp+diffusion: 112.5; exp+lag -> exp+diffusion: 5.2.
- **With a gauge at the seismic depth** the cheapest decisive schedule is 'BM2023' (93 MWh, 7.1 days, expected largest magnitude 0.27); the gauge also measures the transport kernel and, with 3-D locations, the distance, so it settles the diffusivity, which no schedule does.
- **Frontier** (no other design has at least the worst-pair separation for no more deferred generation and no higher monitoring tier), in order of cost: amp3@6h / occupancy / gauge: separation 0.4, 63 MWh, 8.2 d, M~0.24; amp3@6h / counts / gauge: separation 0.5, 63 MWh, 8.2 d, M~0.24; amp3@6h / counts / deepgauge: separation 2.5, 63 MWh, 8.2 d, M~0.24; rate3@300 / occupancy / gauge: separation 0.4, 74 MWh, 8.4 d, M~0.25; rate3@300 / counts / gauge: separation 0.5, 74 MWh, 8.4 d, M~0.25; rate3@300 / counts / deepgauge: separation 2.6, 74 MWh, 8.4 d, M~0.25; BM2023 / occupancy / gauge: separation 0.9, 93 MWh, 7.1 d, M~0.27; BM2023 / counts / gauge: separation 1.1, 93 MWh, 7.1 d, M~0.27; BM2023 / counts / deepgauge: separation 5.0, 93 MWh, 7.1 d, M~0.27; rate3@300x2 / counts / deepgauge: separation 5.7, 147 MWh, 13.8 d, M~0.30; rate2@300+hold48@600 / occupancy / gauge: separation 15.7, 234 MWh, 12.8 d, M~0.35; rate2@300+hold48@600 / counts / gauge: separation 19.4, 234 MWh, 12.8 d, M~0.35; rate2@300+hold48@600 / counts / deepgauge: separation 57.5, 234 MWh, 12.8 d, M~0.35; hold72@600 / counts / deepgauge: separation 73.1, 259 MWh, 10.1 d, M~0.37; rate3@300+hold72@600 / occupancy / gauge: separation 25.7, 332 MWh, 15.5 d, M~0.39; rate3@300+hold72@600 / counts / gauge: separation 39.5, 332 MWh, 15.5 d, M~0.39; rate3@300+hold72@600 / counts / deepgauge: separation 157.6, 332 MWh, 15.5 d, M~0.39; rate3@300x2+hold72@600 / occupancy / gauge: separation 85.4, 406 MWh, 20.8 d, M~0.40; rate3@300x2+hold72@600 / counts / deepgauge: separation 205.7, 406 MWh, 20.8 d, M~0.40.
- **Monte-Carlo check** (Cox-process catalogues with Blue Mountain's over-dispersion, both models refitted to each): BM2023 exp+diffusion->dieterich: expected 21.4 (raw 42.9), simulated median 38.0 [10-90% 23.7, 60.5], correct in 100%; hold72@450 dieterich+diffusion(ta=178h)->exp+diffusion: expected 19.7 (raw 39.4), simulated median 39.4 [10-90% 30.5, 56.5], correct in 100%; hold72@450 dieterich+diffusion(ta=178h)->exp+diffusion: expected 3.3 (raw 6.6), simulated median 8.9 [10-90% 2.3, 21.1], correct in 100%; rate3@300 nucleation->exp+diffusion: expected 132.2 (raw 264.4), simulated median 265.3 [10-90% 197.5, 341.6], correct in 100%.
- **Monitoring that the schedule needs:** (1) every stream (DAS, gauges, SCADA rates) stamped from one GPS-disciplined UTC clock and labelled so; (2) multi-event detection (no one-event-per-file ceiling); (3) a pressure gauge at the depth of the seismicity, which turns the transport from an inference into a measurement and makes the fault law visible during holds; (4) 3-D locations (a second fibre: Fercho et al. 2023 report fibre behind casing in both laterals) to put the events at a measured distance from the stimulated fractures; (5) rates logged at the same 1-minute resolution as pressure.

## 9. Limits

Each remaining limit is either physics or an unpublished quantity, with the measurement that would settle it.

1. **Absolute event positions relative to the stimulated fractures** (unpublished): decides the diffusivity (2.3-10.3 m2/s at catalogue depths versus 0.08-0.33 m2/s if the faults lie within ~34-133 m). Settled by 3-D locations (Fervo's own multi-well arrays, or a second fibre) or a gauge at the seismic depth.
2. **The catalogue's time zone** (unstated by the authors): UTC by provenance; a local-time catalogue (-7 h) would triple the transport time and divide D by ~3 without changing which explanation wins; +7/+8 h is excluded by causality and the tides. Settled by the raw DAS file name of any catalogued event (the authors' real-time products).
3. **A finite fault response time on top of the transport** (physics not excited by 10-h ramps): t_a >= 178 h is all these cycles allow, and it decides whether very slow ramps saturate. Settled by the holds of section 8 with a gauge at the seismic depth.
4. **Ramp rate at fixed amplitude** was never varied (operations, not analysis): the slow cycles were also small. Settled by the rate series of section 8.
5. **Five cycles** (the experiment): every interval above is a cycle-jackknife or block-bootstrap interval; cycle V's shorter lag and the post-shut-in dip in cycle IV are not explained by one configuration and may be the between-cycle variability those intervals carry.
6. **The published distances** (unpublished method): how 'vertical distance from injection' was computed is not documented; the data show it is not a function of the catalogue location. Settled by the authors' code (the location script RT_DAS_2D_location.m listed in the OSF readme was not uploaded).
