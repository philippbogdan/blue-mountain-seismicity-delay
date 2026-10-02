"""Run held-out validation for all models.

usage: run_validate.py <shift_h> <outage_h> <workers>
"""
import sys
import time

sys.path.insert(0, ".")
from blm import validate  # noqa: E402

if __name__ == "__main__":
    shift = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    outage = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    t0 = time.time()
    tag = f"shift{shift:+g}_out{outage:g}"
    validate.run(out=f"results/validate_{tag}.json", shift_h=shift, outage_h=outage,
                 workers=workers)
    print("done", tag, round(time.time() - t0), "s")
