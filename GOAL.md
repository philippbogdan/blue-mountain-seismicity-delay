# Goal

Establish what sets the delay between reservoir pressure and induced seismicity in the cycled Blue Mountain reservoir, and so whether the ramp schedule controls it; predict the delay under slower ramps, and design the test that would settle what these data cannot. Aspire to the best that could exist, not a good one. The published reading is a floor, not a target.

## Specific

1. **The cause:** the response to each cycle against distance and pressurisation rate, and the quantitative models that explain it.
2. **The prediction:** the response under slower ramps, with its uncertainty.
3. **The test:** a ramp schedule and monitoring plan for a future cycled reservoir that would separate what these data cannot, and how decisively.
4. **`FINDINGS.md`** (each claim with its evidence), **`REPORT.md`** (each criterion against the floor, what failed, what remains open), and one command that regenerates every number.

## Measurable

- **Fidelity:** the paper's diffusion front is reproduced from the public data, or the difference is explained.
- **Prediction:** each explanation is judged on data it was not fitted to, against the paper's reading, and its diffusivities against the independent 0.08 to 0.33 m²/s.
- **The frontier:** the non-dominated set of held-out skill, separation between explanations and cost of the proposed test. After every success, push the weakest.
- **Limits:** Only physics, or an unpublished quantity shown to decide the answer with the measurement that would settle it. A choice made here, an unconverged fit and anything left untried are not limits.
- **Evidence:** every number comes from one named commit and says what it is compared against; no claim is stronger than its data (five cycles are five cycles); one configuration holds for every cycle.

## Relevant

Operators of geothermal storage, and those who regulate its seismicity, need to know whether the delay belongs to the site or to the schedule; whoever designs the next cycled test needs to know what would settle it.

## Done

Done means `COMPLETE.md` shows, through the measurements above, that all four deliverables hold, the published diffusion front is reproduced, every explanation is judged on data it was not fitted to, and every remaining limit belongs to the problem itself. There is no deadline and no other way to finish.

## Rules

- Every choice is yours.
- Never invent results or references; label estimates as estimates.
- Contact nobody and publish nothing: no email, posts, issue comments, pushes or pull requests.
- Work only inside this directory; do not read or search local files elsewhere. The internet is yours.
- Commit as you go, so the repository alone can resume the work. Do not edit PROBLEM.md or GOAL.md.
- The machine: Apple M4, 10 cores, 16 GB memory, no FP64 GPU, shared with other long runs. Past 75% memory use the largest process any run started here is stopped, and disk is short, so keep data and environments here small.
- Quick scripts run here directly. Heavier work goes through `gpurun`, run from inside this directory: to Imperial's clusters (GPUs, CPU servers and a pool of lab machines), or to this Mac with `--on mac`, where jobs wait their turn so the Mac stays responsive. `gpurun --help` says what each offers and how to ask for it. Results come back by themselves when a job ends; `gpurun pull` fetches a file sooner.
