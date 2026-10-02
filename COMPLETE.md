# COMPLETE

All numbers from commit `81a6bd05ce4e544332c37230dd5f0a7271390afc`; `make all` regenerates results/, figs/ and these documents.

## The four deliverables hold

1. **The cause** (FINDINGS 4-6). Response per cycle against pressurisation rate and depth; held-out comparison of 21 explanations; transport delay tau = 2.35 h [1.99, 3.02], growing with depth (p = 3.4e-05; held-out +10.9 nats); fault-own delay loses 46.7 [20.6, 79.4].
2. **The prediction** (FINDINGS 7). Slower ramps to the same pressure: peak lag 2.18 -> 0.98 h, excess events 238 -> 1963 ± 307 (jackknife), with the rate-and-state bracket the data allow.
3. **The test** (FINDINGS 8). 'rate2@300+hold48@600' with occupancy detection and the existing gauge: every key pair separated with E[dll]/phi >= 5; 12.8 days, 234 MWh deferred, expected largest magnitude 0.35; Monte-Carlo check in results/design_mc.json.
4. **FINDINGS.md** (each claim with its evidence), **REPORT.md** (each criterion against the floor, what failed, what remains open), **one command** (`make all`).

## The published diffusion front is reproduced

D = 0.434 m2/s from the public Diffusion_data.mat (published 0.43); 0.138 m2/s under the paper's printed formula. The front is not migration: the catalogue's depths do not move while the published distances grow at fixed locations (FINDINGS 3).

## Every explanation is judged on data it was not fitted to

D = L^2/(4 tau) at the cloud's median depth below the lateral (L = 584 m) for 1-D diffusion kernels (for the paper's printed convention tau = L^2/(4 pi D), so its row shows pi D); kernels of other shapes have no such D.

| explanation | held-out gain/event (LOCO) | Δll vs best [95%] | transport time (h) | D = L^2/4tau at 584 m (m2/s) |
|---|---|---|---|---|
| exp+diffusion+cascade | 0.1544 | best | 2.31 | 10.25 |
| dieterich+diffusion(ta=178h) | 0.1458 | 13.6 [1.1, 25.9] | 3.87 | 6.12 |
| dieterich+diffusion | 0.1450 | 14.8 [5.3, 24.8] | 3.19 | 7.43 |
| exp+diffusion | 0.1449 | 15.0 [5.6, 25.0] | 2.35 | 10.07 |
| exprate+diffusion | 0.1446 | 15.5 [6.0, 25.6] | 2.35 | 10.07 |
| dieterich+lag | 0.1442 | 16.0 [5.6, 26.8] | 10.56 | - |
| exp+cascade | 0.1437 | 16.8 [6.7, 27.4] | - | - |
| exp+lag | 0.1435 | 17.2 [6.3, 28.4] | 10.56 | - |
| exp+gamma | 0.1425 | 18.8 [7.3, 31.3] | 9.51 | 2.49 |
| exp+diffusion+poro | 0.1423 | 19.1 [7.9, 30.7] | 1.30 | 18.25 |
| dieterich+cascade | 0.1418 | 19.9 [8.3, 33.0] | - | - |
| exp+shift | 0.1311 | 36.9 [9.2, 68.9] | 5.75 | - |
| coulomb+diffusion | 0.1217 | 51.7 [22.6, 81.9] | 38.95 | 0.61 |
| dieterich | 0.1154 | 61.7 [31.1, 98.3] | - | - |
| rate+diffusion | 0.1035 | 80.6 [43.8, 118.2] | 69.94 | 0.34 |
| exp | 0.1028 | 81.7 [47.8, 121.4] | - | - |
| paper:p+dp/dt | 0.1028 | 81.7 [47.8, 121.4] | - | - |
| paper:D=0.43(4piDt) | 0.0842 | 111.1 [51.1, 175.7] | 17.53 | 1.35 |
| paper:D=0.43(4Dt) | 0.0233 | 207.4 [110.7, 313.1] | 55.08 | 0.43 |
| coulomb | -0.0011 | 246.1 [144.4, 351.7] | - | - |
| dieterich:nucleation | -0.0097 | 259.7 [147.6, 375.0] | - | - |

Against the independent fault-zone diffusivity 0.08-0.33 m2/s: the transport times imply 2.3-10.3 m2/s at the catalogue's depths and fall in the range only within ~34-133 m (FINDINGS 6).

## Every remaining limit belongs to the problem itself

| limit | kind | settling measurement |
|---|---|---|
| event positions relative to the stimulated fractures (diffusivity) | unpublished quantity | 3-D locations or a gauge at the seismic depth |
| the catalogue's time zone (scale of tau) | unpublished quantity | raw DAS file name of any catalogued event |
| a finite fault response time (slow-ramp saturation) | physics not excited by 10-h ramps | holds with a gauge at the seismic depth |
| ramp rate at fixed amplitude | the experiment as run | the rate series of FINDINGS 8 |
| five cycles | the experiment as run | more cycles (the test) |
| how the published distances were computed | unpublished method | the authors' location code |
