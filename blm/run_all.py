"""Regenerate every number: `python -m blm.run_all` (or `make all`).

Steps write results/*.json; results/manifest.json records the git commit the
numbers came from and whether the working tree was clean.  Heavy steps
(validation, design grid) use a process pool; on the shared Mac run this
through the queue: `gpurun --on mac --cpus 6 --mem 4 make all`.
"""
import json
import os
import subprocess
import sys
import time

from . import (clock, compare, design, design_mc, distance, figures, front, frontier, numbers,
               ppc, predict, profile, report, response, validate, xcorr)

R = "results"


def git_state():
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True).stdout.strip()
    return head, bool(dirty)


def step(name, fn, *a, **k):
    t0 = time.time()
    print(f"[run_all] {name} ...", flush=True)
    out = fn(*a, **k)
    print(f"[run_all] {name} done in {time.time() - t0:.0f} s", flush=True)
    return out


def main(workers=6, skip_heavy=False):
    os.makedirs(R, exist_ok=True)
    head, dirty = git_state()
    t0 = time.time()
    step("clock", clock.run, out=f"{R}/clock.json")
    step("front", front.run, out=f"{R}/front.json")
    step("response", response.run, out=f"{R}/response.json")
    if not skip_heavy:
        for sh, ou in [(0.0, 1.0), (8.0, 1.0), (7.0, 1.0), (-7.0, 1.0), (0.0, 0.75), (0.0, 1.5)]:
            step(f"validate shift {sh:+g} outage {ou:g}", validate.run, shift_h=sh, outage_h=ou,
                 workers=workers, out=f"{R}/validate_shift{sh:+g}_out{ou:g}.json")
    val = f"{R}/validate_shift+0_out1.json"
    step("compare (ref transport)", compare.run, val=val, ref="exp+diffusion", out=f"{R}/compare_exp_diffusion.json")
    step("compare (ref best)", compare.run, val=val, ref="exp+diffusion+cascade",
         out=f"{R}/compare_exp_diffusion_cascade.json")
    step("distance", distance.run, out=f"{R}/distance.json")
    step("distance loco", distance.loco, out=f"{R}/distance_loco.json")
    step("profiles", profile.run, out=f"{R}/profiles.json")
    step("xcorr", xcorr.run, out=f"{R}/xcorr.json")
    step("ppc", ppc.run, val=val, out=f"{R}/ppc.json")
    step("predict", predict.run, val=val, out=f"{R}/predict.json")
    if not skip_heavy:
        step("design grid", design.run_grid, val=val, out=f"{R}/design_grid.json", workers=workers)
        step("design Monte Carlo check", design_mc.run, val=val, out=f"{R}/design_mc.json", workers=workers)
    step("frontier", frontier.run, out=f"{R}/frontier.json")
    step("numbers", numbers.run, out=f"{R}/numbers.json")
    with open(f"{R}/manifest.json", "w") as fh:
        json.dump(dict(commit=head, dirty_tree_at_start=dirty, seconds=round(time.time() - t0),
                       python=sys.version.split()[0]), fh, indent=1)
    step("figures", figures.run)
    step("documents", report.run)


if __name__ == "__main__":
    main(skip_heavy="--light" in sys.argv)
