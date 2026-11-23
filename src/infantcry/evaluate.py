"""Subject-independent, repeated, stratified-group cross-validation."""
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold

from .features import GROUPS


def load_npz(name: str):
    z = np.load(f"data/interim/{name}.npz", allow_pickle=False)
    X = {g: z[f"X_{g}"] for g in GROUPS}
    return X, z["y"], z["groups"]  # noqa: RET504


def load_embeddings(task: str, model: str):
    """Layer-wise embeddings aligned to a task's rows by audio path."""
    from .data import EMB_POOL, LOADERS

    df = LOADERS[task]()
    z = np.load(f"data/interim/emb_{model}_{EMB_POOL[task]}.npz")
    pos = {p: i for i, p in enumerate(z["paths"])}
    layers = z["layers"][[pos[p] for p in df.path]].astype(np.float32)
    X = {f"L{i:02d}": layers[:, i] for i in range(layers.shape[1])}
    return X, df.label.values.astype(str), df.group.values.astype(str)


def subset(X, idx):
    return {k: v[idx] for k, v in X.items()}


def evaluate(make_models: dict, X, y, groups, n_splits=5, seeds=(0, 1, 2)):
    rows = []
    for seed in seeds:
        cv = StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed)
        for fold, (tr, te) in enumerate(cv.split(np.zeros(len(y)), y, groups)):
            assert not set(groups[tr]) & set(groups[te]), "subject leakage"
            for name, factory in make_models.items():
                m = factory().fit(subset(X, tr), y[tr], groups=groups[tr])
                p = m.predict(subset(X, te))
                rows.append(
                    dict(
                        model=name, seed=seed, fold=fold,
                        macro_f1=f1_score(y[te], p, average="macro", zero_division=0),
                        bal_acc=balanced_accuracy_score(y[te], p),
                        acc=accuracy_score(y[te], p),
                    )
                )
    return pd.DataFrame(rows)
