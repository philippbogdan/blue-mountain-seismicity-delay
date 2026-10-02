PY = .venv/bin/python

# Regenerate every number, figure and document (heavy steps use 6 processes;
# on the shared Mac: gpurun --on mac --cpus 6 --mem 4 make all)
all:
	$(PY) -m blm.run_all

# Everything except the validation sweeps and design grid (uses existing results)
light:
	$(PY) -m blm.run_all --light

.PHONY: all light
