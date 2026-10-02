"""Design grid v2: deep gauge, schedule-controlled archetype, risk."""
import sys
import time

sys.path.insert(0, ".")
from blm import design  # noqa: E402

if __name__ == "__main__":
    t0 = time.time()
    design.run_grid_v2(workers=int(sys.argv[1]) if len(sys.argv) > 1 else 6)
    print("done", round(time.time() - t0), "s")
