"""Extract grouped features for one dataset -> data/interim/<name>.npz"""
import sys
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.data import LOADERS  # noqa: E402
from infantcry.features import GROUPS, extract  # noqa: E402

name = sys.argv[1]
df = LOADERS[name]()
print(name, len(df), "clips;", df.label.value_counts().to_dict(), flush=True)
feats = Parallel(n_jobs=4, verbose=0)(delayed(extract)(p) for p in df.path)
X = {g: np.stack([f[g] for f in feats]) for g in GROUPS}
Path("data/interim").mkdir(parents=True, exist_ok=True)
np.savez_compressed(
    f"data/interim/{name}.npz",
    y=np.array(df.label.tolist(), dtype="U32"),
    groups=np.array(df.group.tolist(), dtype="U32"),
    paths=np.array(df.path.tolist(), dtype="U256"),
    **{f"X_{g}": X[g] for g in GROUPS},
)
print("saved", {g: X[g].shape for g in GROUPS})
