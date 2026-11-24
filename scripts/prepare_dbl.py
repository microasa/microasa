"""Build the cleaned InfantCry-DBL manifest (protocol v2; supervisor findings D1, D3).

Steps (all decided before any v2 result was seen):
  1. Verify every DBL file against the sha256 published in the Mendeley metadata.
  2. Candidates: Tier-2 clips with source == online_or_volunteer.
  3. Drop byte-identical duplicates (keep the first occurrence).
  4. Cross-corpus overlap: drop candidates whose z-scored v2 feature vector has cosine
     >= CROSS_THR with any Tier-1 (Dunstan) clip or any CryCeleb2023 clip (all 26,093).
  5. Remaining near-duplicates inside DBL (cosine >= GROUP_THR) are merged into one
     CV group (connected components), so they can never straddle train/test.
Output: data/interim/dbl_manifest.csv  (+ a summary printed for the report)
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.features import GROUPS, extract  # noqa: E402

RAW = Path("data/raw")
CROSS_THR, GROUP_THR = 0.95, 0.90
CACHE = Path("data/interim/dbl_prep_cache.npz")


def vec(paths):
    feats = Parallel(n_jobs=4)(delayed(extract)(p) for p in paths)
    return np.stack([np.concatenate([f[g] for g in GROUPS]) for f in feats])


meta = pd.read_csv(RAW / "infantcry_dbl/metadata.csv")
api = json.loads(subprocess.run(
    ["curl", "-s", "-m", "60", "https://data.mendeley.com/public-api/datasets/x493z8nmwc"],
    capture_output=True, text=True, check=True).stdout)
sha_pub = {f["filename"]: f["content_details"].get("sha256_hash") for f in api["files"]}
sha_loc = {fn: hashlib.sha256((RAW / "infantcry_dbl" / fn).read_bytes()).hexdigest() for fn in meta.filename}
bad = [fn for fn in meta.filename if sha_pub.get(fn) != sha_loc[fn]]
print(f"sha256 check: {len(meta) - len(bad)}/{len(meta)} match the published hashes; mismatches: {bad[:5]}")

cand = meta[(meta.tier == 2) & (meta.source == "online_or_volunteer")].copy().reset_index(drop=True)
cand["sha256"] = cand.filename.map(sha_loc)
cand["status"], cand["reason"] = "kept", ""
dupe = cand.sha256.duplicated(keep="first")
cand.loc[dupe, ["status", "reason"]] = ["excluded", "byte-identical duplicate"]

tier1 = meta[meta.tier == 1]
cc = pd.read_csv(RAW / "cryceleb/metadata.csv", dtype={"baby_id": str})
if CACHE.exists():
    z = np.load(CACHE)
    Vc, Vt, Vcc = z["cand"], z["tier1"], z["cryceleb"]
else:
    Vc = vec([str(RAW / "infantcry_dbl" / f) for f in cand.filename])
    Vt = vec([str(RAW / "infantcry_dbl" / f) for f in tier1.filename])
    print("extracting CryCeleb (26k clips) ...", flush=True)
    Vcc = vec([str(RAW / "cryceleb" / f) for f in cc.file_name])
    np.savez_compressed(CACHE, cand=Vc, tier1=Vt, cryceleb=Vcc)

allv = np.vstack([Vc, Vt, Vcc])
mu, sd = np.nanmean(allv, 0), np.nanstd(allv, 0) + 1e-9


def unit(V):
    Z = np.nan_to_num((V - mu) / sd)  # NaN pitch stats -> 0 (= pooled mean) for similarity only
    return Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)


Uc, Ut, Ucc = unit(Vc), unit(Vt), unit(Vcc)
cand["max_cos_tier1"] = (Uc @ Ut.T).max(1)
cand["max_cos_cryceleb"] = (Uc @ Ucc.T).max(1)
hit = (cand.status == "kept") & ((cand.max_cos_tier1 >= CROSS_THR) | (cand.max_cos_cryceleb >= CROSS_THR))
cand.loc[hit, ["status", "reason"]] = ["excluded", f"cross-corpus match (cos >= {CROSS_THR})"]

kept = cand.status == "kept"
S = Uc[kept] @ Uc[kept].T
np.fill_diagonal(S, 0)
ncomp, lab = connected_components(csr_matrix(S >= GROUP_THR), directed=False)
cand["group"] = ""
cand.loc[kept, "group"] = [f"dblc{l:03d}" for l in lab]
cand.to_csv("data/interim/dbl_manifest.csv", index=False)

print(f"candidates {len(cand)} | byte-identical removed {int(dupe.sum())} | cross-corpus removed {int(hit.sum())}")
print(f"kept {int(kept.sum())} clips in {ncomp} CV groups (near-duplicate threshold cos >= {GROUP_THR})")
print("kept class counts:", cand[kept]["class"].value_counts().to_dict())
for col in ["max_cos_tier1", "max_cos_cryceleb"]:
    print(col, "quantiles:", cand[col].quantile([0.5, 0.9, 0.99, 1.0]).round(3).to_dict())
