# Working notes (resume point)

State of the work, newest first. Numbers here are provisional; the final ones
come from `make all` (results/*.json) at a named commit.

- Clock: gauge file labelled PST is on UTC (Earth tide in 15-20 Mar quiet
  window: best offset -0.65 h, block-bootstrap 95% [-1.9, +0.5] h; PDT/PST need
  the unphysical sign). Operating schedule on UTC = daytime curtailment
  (07-09 -> 17-19 local), as the paper's stated purpose requires. Catalogue:
  raw DAS files are UTC-named; paper plotted catalogue and gauge unshifted.
  Rate file timing inconsistent with gauge (offsets -3 to +5.7 h): not used for timing.
- Catalogue: max one event per 1-min file (no duplicate stamps) -> occupancy
  likelihood; outages = gaps > 1 h.
- Front: stored curve = 89.986 (t-18.950 h)^0.4727 exactly; LSQ sqrt(4D(t-t0))
  on it gives D = 0.434 (0.138 in printed sqrt(4 pi D t)). Published distances grow
  ~2.3 m/h within fixed catalogue cells; catalogue locations do not migrate.
- Models: blm/models.py (transport x fault law), blm/fit.py, blm/validate.py
  (loco, slow2fast, fast2slow, fwd).
