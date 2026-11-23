"""Run all weighting variants on one dataset -> results/<name>_*.csv"""
import sys
from functools import partial
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.evaluate import evaluate, load_npz  # noqa: E402
from infantcry.weighting import ConcatClassifier, GroupFusionClassifier  # noqa: E402

name = sys.argv[1]
PROPOSED = "fusion_classwise+balanced"
MODELS = {
    "concat+none": partial(ConcatClassifier, "none"),
    "concat+balanced": partial(ConcatClassifier, "balanced"),
    "fusion_equal+none": partial(GroupFusionClassifier, "none", "equal"),
    "fusion_equal+balanced": partial(GroupFusionClassifier, "balanced", "equal"),
    "fusion_global+balanced": partial(GroupFusionClassifier, "balanced", "global"),
    PROPOSED: partial(GroupFusionClassifier, "balanced", "classwise"),
    "fusion_classwise+effective": partial(GroupFusionClassifier, "effective", "classwise"),
}
X, y, groups = load_npz(name)
print(name, "n =", len(y), "| subjects =", len(set(groups)), "| classes =", dict(pd.Series(y).value_counts()), flush=True)
res = evaluate(MODELS, X, y, groups)
Path("results").mkdir(exist_ok=True)
res.to_csv(f"results/{name}_folds.csv", index=False)
summ = res.groupby("model")[["macro_f1", "bal_acc", "acc"]].agg(["mean", "std"]).round(3)
piv = res.pivot_table(index=["seed", "fold"], columns="model", values="macro_f1")
p = {m: (wilcoxon(piv[PROPOSED], piv[m]).pvalue if (piv[PROPOSED] != piv[m]).any() else 1.0) for m in MODELS if m != PROPOSED}
summ["p_vs_proposed(macroF1)"] = pd.Series(p).round(4)
summ.to_csv(f"results/{name}_summary.csv")
print(summ.sort_values(("macro_f1", "mean"), ascending=False).to_string())
