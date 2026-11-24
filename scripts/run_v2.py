"""Protocol v2 runner: one task x one representation -> results/v2/<rep>_<task>_*.csv

usage: run_v2.py <task: cryceleb|infantcry_dbl|ujm_sex|ujm_age|ujm_axa> <rep: hand|w2v2|hubert> [v2|v3]
Protocol (PROTOCOL.md): StratifiedGroupKFold 5 folds x seeds {0,1,2} for every run.
"""
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score  # noqa: E402
from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.evaluate import load_embeddings  # noqa: E402
from infantcry.features import GROUPS  # noqa: E402
from infantcry.fusion import combine, fit_bank, fit_expert, superb_weighted_sum  # noqa: E402

SEEDS, N_SPLITS, PCA_DIM = (0, 1, 2), 5, 64
task, rep = sys.argv[1], sys.argv[2]
PROTOCOL = sys.argv[3] if len(sys.argv) > 3 else "v2"
TAG = "" if PROTOCOL == "v2" else PROTOCOL + "_"
SHA = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()

hz = np.load(f"data/interim/hand_{TAG}{task}.npz")
dur_by_path = dict(zip(hz["paths"], hz["duration"]))
if rep == "hand":
    X = {g: hz[f"X_{g}"].astype(np.float64) for g in GROUPS}
    y, groups, paths = hz["y"], hz["groups"], hz["paths"]
else:
    X, y, groups = load_embeddings(task, rep, PROTOCOL)
    from infantcry.data import load_task

    paths = np.array(load_task(task, PROTOCOL).path.tolist())
dur = np.array([dur_by_path[p] for p in paths], dtype=np.float64)[:, None]
classes = np.unique(y)
print(f"{rep} {task}: n={len(y)} subjects={len(set(groups))} classes={dict(pd.Series(y).value_counts())} sha={SHA}",
      flush=True)


def run_fold(seed, fold, tr, te):
    assert not set(groups[tr]) & set(groups[te]), "subject leakage"
    Xtr = {k: v[tr] for k, v in X.items()}
    Xte = {k: v[te] for k, v in X.items()}
    bank = fit_bank(Xtr, y[tr], groups[tr], Xte, classes, "balanced",
                    PCA_DIM if rep != "hand" else None, seed)
    probs, diag = combine(bank, y[tr], classes, seed)
    if rep == "hand":
        Xc_tr, Xc_te = np.hstack([Xtr[g] for g in GROUPS]), np.hstack([Xte[g] for g in GROUPS])
        for scheme in ("none", "balanced", "effective"):
            probs[f"concat_{scheme}"] = fit_expert(Xc_tr, y[tr], groups[tr], Xc_te, classes, scheme, None, seed)[1]
    else:
        last = sorted(X)[-1]
        probs["last_layer"] = bank[last][1]
        L = np.stack([X[k] for k in sorted(X)], axis=1)
        probs["superb_wsum"], d2 = superb_weighted_sum(L[tr], y[tr], groups[tr], L[te], classes, seed)
        diag.update({f"superb_{k}": v for k, v in d2.items()})
    probs["duration_only"] = fit_expert(dur[tr], y[tr], groups[tr], dur[te], classes, "balanced", None, seed,
                                        Cs=(1.0,))[1]
    rows, preds = [], []
    for name, P in probs.items():
        pred = classes[P.argmax(1)]
        rows.append(dict(task=task, rep=rep, method=name, seed=seed, fold=fold, n_test=len(te),
                         macro_f1=f1_score(y[te], pred, average="macro", labels=classes, zero_division=0),
                         bal_acc=balanced_accuracy_score(y[te], pred), acc=accuracy_score(y[te], pred),
                         protocol=PROTOCOL, git_sha=SHA))
        preds.append(pd.DataFrame(dict(method=name, seed=seed, fold=fold, idx=te, y=y[te], pred=pred)))
    d = dict(task=task, rep=rep, seed=seed, fold=fold, tau=diag["tau"], w_max=diag["w_max"],
             best_single=diag["best_single"], **{k: v for k, v in diag.items() if k.startswith("superb_")})
    return rows, pd.concat(preds), d


jobs = []
for seed in SEEDS:
    cv = StratifiedGroupKFold(N_SPLITS, shuffle=True, random_state=seed)
    jobs += [(seed, f, tr, te) for f, (tr, te) in enumerate(cv.split(np.zeros(len(y)), y, groups))]
out = Parallel(n_jobs=4)(delayed(run_fold)(*j) for j in jobs)
Path(f"results/{PROTOCOL}").mkdir(parents=True, exist_ok=True)
stem = f"results/{PROTOCOL}/{rep}_{task}"
res = pd.DataFrame([r for o in out for r in o[0]])
res.to_csv(f"{stem}_folds.csv", index=False)
pd.concat([o[1] for o in out]).to_csv(f"{stem}_preds.csv.gz", index=False)
pd.DataFrame([o[2] for o in out]).to_csv(f"{stem}_diag.csv", index=False)
print(res.groupby("method")[["macro_f1", "bal_acc"]].mean().sort_values("macro_f1", ascending=False).round(3)
      .to_string())
