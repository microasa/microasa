"""Analyse protocol v2 results: pre-declared primary family (Holm) + exploratory tables.
-> results/v2/primary_tests.csv, results/v2/exploratory_tests.csv, results/v2/summary.csv"""
import glob
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.stats import holm, nb_test  # noqa: E402

D = sys.argv[1] if len(sys.argv) > 1 else "results/v2"
TASKS = ["cryceleb", "infantcry_dbl", "ujm_sex", "ujm_age"]
REPS = ["hand", "w2v2", "hubert"]
res = pd.concat([pd.read_csv(f) for f in glob.glob(f"{D}/*_folds.csv")], ignore_index=True)


def diff(task, rep, a, b):
    r = res[(res.task == task) & (res.rep == rep)]
    piv = r.pivot_table(index=["seed", "fold"], columns="method", values="macro_f1")
    if a not in piv or b not in piv:
        return None
    return (piv[a] - piv[b]).values


def family(spec):
    rows = []
    for hyp, a, b, reps in spec:
        for rep in reps:
            for task in TASKS:
                d = diff(task, rep, a, b)
                if d is not None:
                    rows.append(dict(hypothesis=hyp, rep=rep, task=task, a=a, b=b, **nb_test(d)))
    return pd.DataFrame(rows)


prim = family([("H1", "stacking", "equal", REPS), ("H2", "stacking", "best_single", REPS),
               ("H3", "stacking", "superb_wsum", ["w2v2", "hubert"]),
               ("H4", "concat_balanced", "concat_none", ["hand"])])
prim["p_holm"] = holm(prim.p)
prim["verdict"] = np.where((prim.p_holm < 0.05) & (prim.ci_low > 0), "A better",
                           np.where((prim.p_holm < 0.05) & (prim.ci_high < 0), "B better", "no evidence"))
prim.to_csv(f"{D}/primary_tests.csv", index=False)

expl = family([("E1", "softmax_tau", "equal", REPS), ("E2", "best_single", "last_layer", ["w2v2", "hubert"]),
               ("E3", "superb_wsum", "last_layer", ["w2v2", "hubert"]),
               ("E4", "stacking", "duration_only", REPS)])
expl.to_csv(f"{D}/exploratory_tests.csv", index=False)

# summary: mean +- sd fold macro-F1, plus pooled macro-F1 (predictions pooled per seed)
summ = res.groupby(["task", "rep", "method"]).agg(macro_f1=("macro_f1", "mean"), sd=("macro_f1", "std"),
                                                  bal_acc=("bal_acc", "mean")).reset_index()
pooled = []
for f in glob.glob(f"{D}/*_preds.csv.gz"):
    p = pd.read_csv(f)
    rep, task = Path(f).name.replace("_preds.csv.gz", "").split("_", 1)
    for (m, s), g in p.groupby(["method", "seed"]):
        pooled.append(dict(task=task, rep=rep, method=m, seed=s,
                           pooled=f1_score(g.y.astype(str), g.pred.astype(str), average="macro")))
pooled = pd.DataFrame(pooled).groupby(["task", "rep", "method"]).pooled.mean().reset_index()
summ = summ.merge(pooled, on=["task", "rep", "method"], how="left")
summ.to_csv(f"{D}/summary.csv", index=False)

pd.set_option("display.width", 220)
print("PRIMARY FAMILY (Nadeau-Bengio, Holm over", len(prim), "tests)")
print(prim[["hypothesis", "rep", "task", "mean", "ci_low", "ci_high", "p", "p_holm", "verdict"]].round(4)
      .to_string(index=False))
print("\nverdict counts:", prim.verdict.value_counts().to_dict())
print("\nEXPLORATORY (unadjusted)")
print(expl[["hypothesis", "rep", "task", "mean", "ci_low", "ci_high", "p"]].round(4).to_string(index=False))
print("\nSUMMARY (fold-mean macro-F1)")
print(summ.pivot_table(index=["task", "rep"], columns="method", values="macro_f1").round(3).to_string())
