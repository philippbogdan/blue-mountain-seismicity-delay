# What sets the seismicity delay in the cycled Blue Mountain reservoir

Problem: `PROBLEM.md`; goal: `GOAL.md`. Results: `FINDINGS.md` (claims with evidence),
`REPORT.md` (criteria against the floor, failures, open questions), `COMPLETE.md`.

## Regenerate everything

```
make all          # results/*.json, figs/*.png, FINDINGS.md, REPORT.md, COMPLETE.md
make light        # same, reusing the validation sweeps and design grid already in results/
```

On the shared Mac run it through the queue: `gpurun --on mac --cpus 6 --mem 4 make all`.
`results/manifest.json` records the commit the numbers came from.

Environment: Python 3.12, `uv pip install -r requirements.txt` into `.venv`.

## Data

- `data/osf-d65ba/`: the public OSF data set (doi:10.17605/OSF.IO/D65BA), see `data/README.md`.
- `data/paper/`: text of the accepted manuscript (doi:10.1029/2025JB031634).
- `data/external/`: UTC references fetched for the clock checks: USGS ComCat events
  within 400 km and global M>=6 (fdsnws, 2 Oct 2026); Winnemucca (KWMC) ASOS hourly
  barometer and wind from the Iowa Environmental Mesonet.

## Code (`blm/`)

| module | what |
|---|---|
| `io` | loaders; every file on its own clock |
| `tides`, `clock` | Earth tide / barometer regression of the gauge, operating schedule, outage restarts, rate-file offsets |
| `front` | the published diffusion front: exact identification, conventions, distance artefact, catalogue stationarity |
| `rates` | occupancy (one event per 1-minute file) and outage handling |
| `response` | model-free per-cycle response (excess, lags) by depth and radial class |
| `models`, `fit` | transport x fault-law models, occupancy likelihood, maximum likelihood |
| `validate`, `compare` | held-out schemes (leave-one-cycle-out, slow<->fast, forward) and block-bootstrap comparisons |
| `distance` | depth-resolved transport times (joint multi-class likelihood) |
| `profile`, `xcorr`, `ppc` | profile likelihoods, model-free lags per clock shift, per-cycle predictive checks |
| `predict` | slower-ramp scenarios with jackknife uncertainty |
| `design`, `design_mc`, `frontier` | expected separation of explanations for candidate tests, Monte-Carlo check, frontier |
| `numbers`, `figures`, `report`, `run_all` | collected numbers, figures, documents, the one command |
