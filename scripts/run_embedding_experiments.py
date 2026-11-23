"""Layer-weighting experiments on pretrained-encoder embeddings.
usage: run_embedding_experiments.py <task> <w2v2|hubert> [n_seeds]"""
import sys
from functools import partial
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.evaluate import evaluate, load_embeddings  # noqa: E402
from infantcry.weighting import (GroupFusionClassifier, MeanGroupClassifier,  # noqa: E402
                                 SingleLayerClassifier)

task, model = sys.argv[1], sys.argv[2]
n_seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
C = 0.05  # strong L2: 768-d embeddings, few subjects
PROPOSED = "layers_classwise+balanced"
MODELS = {
    "last_layer+balanced": partial(SingleLayerClassifier, "L12", "balanced", C),
    "mean_layers+balanced": partial(MeanGroupClassifier, "balanced", C),
    "best_layer(inner-CV)+balanced": partial(GroupFusionClassifier, "balanced", "global", 1000.0, C=C),
    "layers_equal+none": partial(GroupFusionClassifier, "none", "equal", C=C),
    "layers_equal+balanced": partial(GroupFusionClassifier, "balanced", "equal", C=C),
    "layers_global+balanced": partial(GroupFusionClassifier, "balanced", "global", C=C),
    PROPOSED: partial(GroupFusionClassifier, "balanced", "classwise", C=C),
}
X, y, groups = load_embeddings(task, model)
print(task, model, "n =", len(y), "| subjects =", len(set(groups)), "|", dict(pd.Series(y).value_counts()), flush=True)
res = evaluate(MODELS, X, y, groups, seeds=tuple(range(n_seeds)))
Path("results").mkdir(exist_ok=True)
res.to_csv(f"results/emb_{model}_{task}_folds.csv", index=False)
summ = res.groupby("model")[["macro_f1", "bal_acc", "acc"]].agg(["mean", "std"]).round(3)
piv = res.pivot_table(index=["seed", "fold"], columns="model", values="macro_f1")
summ["p_vs_proposed"] = pd.Series({m: (wilcoxon(piv[PROPOSED], piv[m]).pvalue if (piv[PROPOSED] != piv[m]).any() else 1.0) for m in MODELS if m != PROPOSED}).round(4)
summ.to_csv(f"results/emb_{model}_{task}_summary.csv")
print(summ.sort_values(("macro_f1", "mean"), ascending=False).to_string())
