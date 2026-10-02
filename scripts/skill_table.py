"""Print the held-out skill table from a validation results file."""
import json
import sys

import numpy as np

sys.path.insert(0, ".")
from blm import validate  # noqa: E402

res = json.load(open(sys.argv[1]))
tab = validate.skill_table(res)
by = {(r["model"], r["scheme"]): r for r in res}
models = sorted({m for m, s in tab}, key=lambda m: -tab.get((m, "full"), 0))
cols = ["full", "loco:I", "loco:II", "loco:III", "loco:IV", "loco:V", "slow2fast", "fast2slow",
        "fwd:II", "fwd:III", "fwd:IV", "fwd:V"]
print(f"{'model':24s}" + "".join(f"{c:>9s}" for c in cols) + "  LOCO-all")
for m in models:
    num = sum(by[(m, f"loco:{c}")]["ll_test"] - by[("const", f"loco:{c}")]["ll_test"] for c in validate.CYC)
    den = sum(sum(by[(m, f"loco:{c}")]["n_events_seg"].values()) for c in validate.CYC)
    print(f"{m:24s}" + "".join(f"{tab.get((m, c), np.nan):+9.4f}" for c in cols) + f"  {num / den:+.4f}")
