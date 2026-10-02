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

KEY_PAIRS = [("dieterich+diffusion(ta=178h)", "exp+diffusion"),
             ("exp+diffusion", "dieterich"), ("dieterich", "exp+diffusion"),
             ("exp+diffusion", "exp+cascade"), ("exp+cascade", "exp+diffusion")]
DECISIVE = 5.0


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


def designs(grid="results/design_grid.json"):
    rows = json.load(open(grid))
    out = {}
    for r in rows:
        k = (r["design"], r["mode"])
        o = out.setdefault(k, dict(design=r["design"], mode=r["mode"], cost=r["cost"], pairs={}))
        o["pairs"][f"{r['truth']} -> {r['alt']}"] = r["dll_eff"]
    for o in out.values():
        vals = [o["pairs"][f"{a} -> {b}"] for a, b in KEY_PAIRS if f"{a} -> {b}" in o["pairs"]]
        o["min_sep"] = float(min(vals)) if vals else float("nan")
        o["hardest"] = min(o["pairs"], key=o["pairs"].get)
    return list(out.values())


def nondominated(ds):
    keep = []
    for a in ds:
        dom = any((b["min_sep"] >= a["min_sep"] and b["cost"]["deferred_MWh"] <= a["cost"]["deferred_MWh"]
                   and b["cost"]["days"] <= a["cost"]["days"]
                   and (b["min_sep"] > a["min_sep"] or b["cost"]["deferred_MWh"] < a["cost"]["deferred_MWh"]
                        or b["cost"]["days"] < a["cost"]["days"])) for b in ds)
        if not dom:
            keep.append(a)
    return keep


def run(out="results/frontier.json", val="results/validate_shift+0_out1.json",
        cmp="results/compare_exp_diffusion_cascade.json", grid="results/design_grid.json"):
    sk = skill(val)
    best = max((m for m in sk if not m.startswith("paper")), key=lambda m: sk[m]["loco"])
    paper_best = max((m for m in sk if m.startswith("paper")), key=lambda m: sk[m]["loco"])
    c = json.load(open(cmp))
    margin = c["versus"].get(paper_best, {})
    ds = designs(grid)
    front = nondominated(ds)
    bm = [d for d in ds if d["design"] == "BM2023" and d["mode"] == "occupancy"][0]
    decisive = [d for d in ds if d["min_sep"] >= DECISIVE]
    cheapest_decisive = min(decisive, key=lambda d: d["cost"]["deferred_MWh"]) if decisive else None
    axes = {
        "skill": dict(best=best, loco=sk[best]["loco"], paper_best=paper_best, paper_loco=sk[paper_best]["loco"],
                      dll_vs_paper=margin.get("dll_total"), ci95=margin.get("ci95"),
                      met=bool(margin and margin["ci95"][0] > 0)),
        "separation": dict(BM2023_min=bm["min_sep"], BM2023_hardest=bm["hardest"],
                           best_min=max(d["min_sep"] for d in ds), met=bool(decisive)),
        "cost": dict(BM2023_MWh=bm["cost"]["deferred_MWh"],
                     cheapest_decisive=None if cheapest_decisive is None else
                     dict(design=cheapest_decisive["design"], mode=cheapest_decisive["mode"],
                          MWh=cheapest_decisive["cost"]["deferred_MWh"], days=cheapest_decisive["cost"]["days"]),
                     met=bool(cheapest_decisive and cheapest_decisive["cost"]["deferred_MWh"] <= bm["cost"]["deferred_MWh"])),
    }
    unmet = [k for k, v in axes.items() if not v["met"]]
    res = dict(skill=sk, designs=ds, frontier=[(d["design"], d["mode"]) for d in front], axes=axes,
               weakest=unmet[0] if unmet else None)
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    return res
