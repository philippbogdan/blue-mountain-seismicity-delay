"""The frontier: held-out skill x separation between explanations x test cost.

skill       held-out gain (nats/event over a constant rate, leave-one-cycle-out)
            of the best explanation, and of the paper's readings for reference
separation  for each candidate design, the effective expected log-likelihood
            ratio (E[dll]/phi) of the hardest key pair of explanations
cost        deferred generation (MWh at 3.5 MW per curtailed hour) and days
A design is on the frontier if no other design has at least its separation at
no more cost.  'Weakest axis' compares each axis with its target: separation
>= 5 for every key pair (decisive), cost no more than the 2023 cycles, skill
above the paper's best reading by more than the block-bootstrap interval.
"""
import json

import numpy as np

from . import validate

KEY_PAIRS = [("dieterich+diffusion(ta=178h)", "exp+diffusion"),   # finite fault response on top of transport
             ("exp+diffusion", "nucleation"), ("nucleation", "exp+diffusion"),   # site vs schedule
             ("exp+diffusion", "exp+cascade"), ("exp+cascade", "exp+diffusion")]
DECISIVE = 5.0
# monitoring cost tiers (no money figures are invented): 0 existing 73-22 gauge and fibre;
# 1 multi-event detection (processing only); 3 a pressure gauge at the seismic depth
# (a deepened or new monitoring well).  GPS-disciplined UTC time stamps on every stream
# are assumed in all tiers.
TIER = {("occupancy", "gauge"): 0, ("counts", "gauge"): 1, ("counts", "deepgauge"): 3}
# cost / risk target: within the operating envelope of the 2023 test: no new well, at most
# four days of full production deferred (4 x 24 h x 3.5 MW), three weeks, and no larger
# event expected than the largest catalogued in 2023 (M 0.46)
COST_TARGET = dict(tier=1, MWh=4 * 24 * 3.5, days=21.0, max_mag=0.46)


def skill(val="results/validate_shift+0_out1.json"):
    res = json.load(open(val))
    by = {(r["model"], r["scheme"]): r for r in res}
    out = {}
    for m in sorted({r["model"] for r in res}):
        num = sum(by[(m, f"loco:{c}")]["ll_test"] - by[("const", f"loco:{c}")]["ll_test"] for c in validate.CYC)
        den = sum(sum(by[(m, f"loco:{c}")]["n_events_seg"].values()) for c in validate.CYC)
        tab = validate.skill_table([r for r in res if r["model"] in (m, "const")])
        out[m] = dict(loco=num / den, slow2fast=tab.get((m, "slow2fast")), fast2slow=tab.get((m, "fast2slow")))
    return out


# transport kernel of each explanation: where truth and alternative differ, a gauge at
# the seismic depth settles the pair by the pressure record itself
KERNEL = {"exp+diffusion": "diffusion", "dieterich+diffusion(ta=178h)": "diffusion", "nucleation": "none",
          "exp+cascade": "none", "exp+lag": "lag"}
DIRECT = 1000.0


def designs(grid="results/design_grid_v2.json"):
    rows = json.load(open(grid))
    gauge_counts = {(r["design"], r["truth"], r["alt"]): r["dll_eff"] for r in rows
                    if r["mode"] == "counts" and r.get("monitoring", "gauge") == "gauge"}
    for r in rows:
        if r.get("monitoring") == "deepgauge":
            # a deep-gauge plan keeps the 73-22 record and adds the measured fault pressure
            vals = [r["dll_eff"], gauge_counts.get((r["design"], r["truth"], r["alt"]), 0.0)]
            if KERNEL.get(r["truth"]) != KERNEL.get(r["alt"]):
                vals.append(DIRECT)
            r["dll_eff"] = max(vals)
    out = {}
    for r in rows:
        mon = r.get("monitoring", "gauge")
        k = (r["design"], r["mode"], mon)
        o = out.setdefault(k, dict(design=r["design"], mode=r["mode"], monitoring=mon, cost=dict(r["cost"]),
                                   pairs={}, max_mag=0.0, n_events=0.0))
        o["cost"]["tier"] = TIER[(r["mode"], mon)]
        o["pairs"][f"{r['truth']} -> {r['alt']}"] = r["dll_eff"]
        if r["truth"] == "exp+diffusion":
            from .design import risk
            o["max_mag"], o["n_events"] = risk(r["n_events"]), r["n_events"]
    for o in out.values():
        vals = [o["pairs"][f"{a} -> {b}"] for a, b in KEY_PAIRS if f"{a} -> {b}" in o["pairs"]]
        o["min_sep"] = float(min(vals)) if vals else float("nan")
        o["hardest"] = min(o["pairs"], key=o["pairs"].get)
    return list(out.values())


def _vec(d):
    # larger is better for every coordinate (risk and days are reported alongside)
    return np.array([min(d["min_sep"], 1e3), -d["cost"]["deferred_MWh"], -d["cost"]["tier"]])


def nondominated(ds):
    keep = []
    for a in ds:
        va = _vec(a)
        dom = any(np.all(_vec(b) >= va) and np.any(_vec(b) > va) for b in ds if b is not a)
        if not dom:
            keep.append(a)
    return keep


def run(out="results/frontier.json", val="results/validate_shift+0_out1.json",
        cmp="results/compare_exp_diffusion_cascade.json", grid="results/design_grid_v2.json"):
    sk = skill(val)
    best = max((m for m in sk if not m.startswith("paper")), key=lambda m: sk[m]["loco"])
    paper_best = max((m for m in sk if m.startswith("paper")), key=lambda m: sk[m]["loco"])
    c = json.load(open(cmp))
    margin = c["versus"].get(paper_best, {})
    ds = designs(grid)
    front = nondominated(ds)
    bm = [d for d in ds if d["design"] == "BM2023" and d["mode"] == "occupancy" and d["monitoring"] == "gauge"][0]
    decisive = [d for d in ds if d["min_sep"] >= DECISIVE]
    # the operator's question (does the ramp rate set the delay?) needs a model-free answer:
    # the recommended schedule must contain ramps of different rate to the same pressure
    decisive_rate = [d for d in decisive if d["design"].startswith("rate") or "+rate" in d["design"]]
    pool = decisive_rate or decisive
    cheapest_decisive = (min(pool, key=lambda d: (d["cost"]["tier"], d["cost"]["deferred_MWh"], d["cost"]["days"]))
                         if pool else None)
    cheapest_any = (min(decisive, key=lambda d: (d["cost"]["tier"], d["cost"]["deferred_MWh"], d["cost"]["days"]))
                    if decisive else None)
    decisive_deep = [d for d in decisive if d["monitoring"] == "deepgauge"]
    cheapest_deep = min(decisive_deep, key=lambda d: (d["cost"]["deferred_MWh"], d["cost"]["days"])) if decisive_deep else None
    axes = {
        "skill": dict(best=best, loco=sk[best]["loco"], paper_best=paper_best, paper_loco=sk[paper_best]["loco"],
                      dll_vs_paper=margin.get("dll_total"), ci95=margin.get("ci95"),
                      met=bool(margin and margin["ci95"][0] > 0)),
        "separation": dict(BM2023_min=bm["min_sep"], BM2023_hardest=bm["hardest"],
                           best_min=max(d["min_sep"] for d in ds), met=bool(decisive)),
        "cost": dict(BM2023_MWh=bm["cost"]["deferred_MWh"],
                     cheapest_decisive=None if cheapest_decisive is None else
                     dict(design=cheapest_decisive["design"], mode=cheapest_decisive["mode"],
                          monitoring=cheapest_decisive["monitoring"], tier=cheapest_decisive["cost"]["tier"],
                          MWh=cheapest_decisive["cost"]["deferred_MWh"], days=cheapest_decisive["cost"]["days"],
                          max_mag=cheapest_decisive["max_mag"]),
                     met=bool(cheapest_decisive and cheapest_decisive["cost"]["tier"] <= COST_TARGET["tier"]
                              and cheapest_decisive["cost"]["deferred_MWh"] <= COST_TARGET["MWh"]
                              and cheapest_decisive["cost"]["days"] <= COST_TARGET["days"]
                              and cheapest_decisive["max_mag"] <= COST_TARGET["max_mag"])),
    }
    if cheapest_deep:
        axes["cost"]["cheapest_decisive_with_deep_gauge"] = dict(design=cheapest_deep["design"],
                                                             MWh=cheapest_deep["cost"]["deferred_MWh"],
                                                             days=cheapest_deep["cost"]["days"],
                                                             max_mag=cheapest_deep["max_mag"])
    axes["cost"]["target"] = COST_TARGET
    if cheapest_any:
        axes["cost"]["cheapest_decisive_any_schedule"] = dict(design=cheapest_any["design"], mode=cheapest_any["mode"],
                                                          monitoring=cheapest_any["monitoring"],
                                                          MWh=cheapest_any["cost"]["deferred_MWh"],
                                                          days=cheapest_any["cost"]["days"], max_mag=cheapest_any["max_mag"])
    unmet = [k for k, v in axes.items() if not v["met"]]
    res = dict(skill=sk, designs=ds, frontier=[(d["design"], d["mode"], d["monitoring"]) for d in front], axes=axes,
               weakest=unmet[0] if unmet else None)
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    return res
