"""Extract grouped handcrafted features for one task -> data/interim/hand_[v3_]<task>.npz
usage: extract_features.py <task> [v2|v3]   (v3 = quality-filtered + band-limited audio)

Also stores the true clip duration separately (NOT a model feature; used only by the
duration-only shortcut baseline) and logs NaN counts per group.
"""
import sys
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.data import load_task  # noqa: E402
from infantcry.features import FEATURE_VERSION, GROUPS, clip_duration, extract  # noqa: E402

name = sys.argv[1]
protocol = sys.argv[2] if len(sys.argv) > 2 else "v2"
bandlimit = protocol == "v3"
df = load_task(name, protocol)
print(name, len(df), "clips;", df.label.value_counts().to_dict(), flush=True)
feats = Parallel(n_jobs=4)(delayed(extract)(p, bandlimit) for p in df.path)
dur = np.array(Parallel(n_jobs=4)(delayed(clip_duration)(p) for p in df.path), dtype=np.float32)
X = {g: np.stack([f[g] for f in feats]) for g in GROUPS}
print("NaN rows per group:", {g: int(np.isnan(X[g]).any(1).sum()) for g in GROUPS})
Path("data/interim").mkdir(parents=True, exist_ok=True)
np.savez_compressed(
    f"data/interim/hand_{'' if protocol == 'v2' else protocol + '_'}{name}.npz",
    y=np.array(df.label.tolist(), dtype="U32"),
    groups=np.array(df.group.tolist(), dtype="U64"),
    paths=np.array(df.path.tolist(), dtype="U256"),
    duration=dur,
    feature_version=np.array(FEATURE_VERSION),
    **{f"X_{g}": X[g] for g in GROUPS},
)
print("saved", {g: X[g].shape for g in GROUPS})
