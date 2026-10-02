"""Held-out evaluation of every rate model.

Schemes (segments are defined in models.SEGMENTS, gauge clock = UTC):
  full      fit and score on everything (in-sample, for reference only)
  loco:<c>  fit on all segments except cycle c, score on c   (c = I..V)
  slow2fast fit on pre, I, II, III (slow ramps); score on IV, V, post
  fast2slow fit on IV, V, post (fast ramps);     score on I, II, III
  fwd:<c>   fit on everything before cycle c;    score on c   (c = II..V)
Scores are occupancy log-likelihoods; skill is reported per held-out event
relative to the constant-rate model fitted on the same training segments.
"""
import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import fit, models

ALL = list(models.SEGMENTS)
CYC = ["I", "II", "III", "IV", "V"]


def schemes():
    s = {"full": (ALL, ALL)}
    for c in CYC:
        s[f"loco:{c}"] = ([x for x in ALL if x != c], [c])
    s["slow2fast"] = (["pre", "I", "II", "III"], ["IV", "V", "post"])
    s["fast2slow"] = (["IV", "V", "post"], ["I", "II", "III"])
    for i, c in enumerate(CYC[1:], start=1):
        s[f"fwd:{c}"] = (["pre"] + CYC[:i], [c])
    return s


def _task(args):
    name, scheme, train, test, shift_h, outage_h = args
    d = models.Data(shift_h=shift_h, outage_h=outage_h)
    mtr, mte = d.mask(train), d.mask(test)
    th, ll_tr, z = fit.fit(name, d, mtr)
    R = fit.predict(name, d, th)
    terms = models.loglik_terms(R, d)
    per_seg = {s: float(terms[d.mask([s])].sum()) for s in test}
    n_ev = {s: int(d.occ[d.mask([s]) & d.obs].sum()) for s in test}
    return dict(model=name, scheme=scheme, train=train, test=test, theta=th,
                ll_train=ll_tr, ll_test=float(terms[mte].sum()), ll_seg=per_seg,
                n_events_seg=n_ev, shift_h=shift_h, outage_h=outage_h)


def run(model_names=None, scheme_names=None, shift_h=0.0, outage_h=1.0, workers=6,
        out=None):
    model_names = model_names or list(fit.MODELS)
    sch = schemes()
    scheme_names = scheme_names or list(sch)
    tasks = [(m, s, sch[s][0], sch[s][1], shift_h, outage_h)
             for m in model_names for s in scheme_names]
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(_task, tasks))
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as fh:
            json.dump(res, fh, indent=1, default=float)
    return res


def skill_table(res):
    """Held-out gain (nats/event) over the constant-rate model, per scheme."""
    by = {(r["model"], r["scheme"]): r for r in res}
    models_ = sorted({r["model"] for r in res})
    schemes_ = sorted({r["scheme"] for r in res})
    tab = {}
    for m in models_:
        for s in schemes_:
            if (m, s) not in by or ("const", s) not in by:
                continue
            r, c = by[(m, s)], by[("const", s)]
            n = sum(r["n_events_seg"].values())
            tab[(m, s)] = (r["ll_test"] - c["ll_test"]) / max(n, 1)
    return tab
