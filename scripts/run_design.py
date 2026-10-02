"""Expected separation of explanations for candidate test designs."""
import sys
import time

sys.path.insert(0, ".")
from blm import design  # noqa: E402

if __name__ == "__main__":
    t0 = time.time()
    design.run_grid(workers=int(sys.argv[1]) if len(sys.argv) > 1 else 6)
    print("done", round(time.time() - t0), "s")
