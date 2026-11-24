"""Dataset registry for Paper 4: three infant-cry corpora disjoint from Paper 1.

Each loader returns a DataFrame with columns: path, label, group, dataset.
`group` is the unit that must never straddle train/test (infant id when known).
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw")
MAX_CLIPS_PER_BABY_CRYCELEB = 10
SEED = 0


def load_cryceleb() -> pd.DataFrame:
    """CryCeleb2023: binary period (B = first hours of life, D = at discharge)."""
    m = pd.read_csv(RAW / "cryceleb/metadata.csv", dtype={"baby_id": str})
    # Drop the competition test split's `anonymousNNN` ids: the organisers anonymised
    # each baby's two recording periods under different ids, so grouping by them
    # cannot prevent same-infant leakage.
    m = m[(m.duration >= 0.5) & ~m.baby_id.str.startswith("anonymous")]
    m = m.sample(frac=1, random_state=SEED).groupby(["baby_id", "period"]).head(
        MAX_CLIPS_PER_BABY_CRYCELEB // 2
    )
    return pd.DataFrame(
        {
            "path": [str(RAW / "cryceleb" / f) for f in m.file_name],
            "label": m.period.values,
            "group": m.baby_id.values,
            "dataset": "cryceleb",
        }
    )


def load_ujm() -> pd.DataFrame:
    """BABYCRY-UJM-AXA subset: 3-class delivery method (Vaginal/Assisted/C-section)."""
    m = pd.read_csv(RAW / "ujm_axa/subset.csv")
    keep = [(RAW / "ujm_axa/audio" / n).exists() for n in m.zip_name]
    m = m[keep]
    return pd.DataFrame(
        {
            "path": [str(RAW / "ujm_axa/audio" / n) for n in m.zip_name],
            "label": m["delivery.method"].values,
            "group": m.baby.astype(str).values,
            "dataset": "ujm_axa",
        }
    )


def _ujm_base() -> pd.DataFrame:
    m = pd.read_csv(RAW / "ujm_axa/subset.csv")
    m = m[[(RAW / "ujm_axa/audio" / n).exists() for n in m.zip_name]].copy()
    m["path"] = [str(RAW / "ujm_axa/audio" / n) for n in m.zip_name]
    m["age_h"] = pd.to_timedelta(m.age).dt.total_seconds() / 3600
    return m


def load_ujm_sex() -> pd.DataFrame:
    """UJM-AXA subset: newborn sex (F/M), near-balanced. Pre-declared task."""
    m = _ujm_base()
    return pd.DataFrame({"path": m.path.values, "label": m.sex.values,
                         "group": m.baby.astype(str).values, "dataset": "ujm_sex"})


def load_ujm_age() -> pd.DataFrame:
    """UJM-AXA subset: recording age, lowest vs highest tertile of age in hours
    (middle tertile dropped). Pre-declared task; thresholds from the whole subset."""
    m = _ujm_base()
    lo, hi = m.age_h.quantile([1 / 3, 2 / 3])
    m = m[(m.age_h <= lo) | (m.age_h >= hi)]
    return pd.DataFrame({"path": m.path.values,
                         "label": np.where(m.age_h <= lo, "young", "old"),
                         "group": m.baby.astype(str).values, "dataset": "ujm_age"})


def load_dbl_clean() -> pd.DataFrame:
    """InfantCry-DBL, only Tier-2 clips with source `online_or_volunteer`.

    Excluded on purpose: Tier 1 (Dunstan videos, overlaps Paper 1) and Tier-2 clips
    whose source is `cryceleb_likely` or `unknown` (possible CryCeleb overlap).
    No infant id exists, so each clip is its own group (LIMITATION: subject
    independence cannot be guaranteed on this corpus).
    """
    manifest = Path("data/interim/dbl_manifest.csv")
    if not manifest.exists():
        raise FileNotFoundError("run scripts/prepare_dbl.py first (protocol v2 DBL cleaning)")
    m = pd.read_csv(manifest)
    m = m[m.status == "kept"]
    # v2: byte-identical and cross-corpus duplicates removed; near-duplicate clips share
    # one CV group (connected components), see scripts/prepare_dbl.py.
    return pd.DataFrame(
        {
            "path": [str(RAW / "infantcry_dbl" / f) for f in m.filename],
            "label": m["class"].values,
            "group": m.group.values,
            "dataset": "infantcry_dbl",
        }
    )


LOADERS = {
    "cryceleb": load_cryceleb,
    "infantcry_dbl": load_dbl_clean,
    "ujm_sex": load_ujm_sex,
    "ujm_age": load_ujm_age,
    "ujm_axa": load_ujm,  # delivery method (supplementary; ~chance level)
}


def quality_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Protocol v3: drop clips flagged by scripts/quality_v3.py."""
    q = pd.read_csv("data/interim/quality_v3.csv")
    bad = set(q.loc[q.exclude, "path"])
    return df[~df.path.isin(bad)].reset_index(drop=True)


def load_task(name: str, protocol: str = "v2") -> pd.DataFrame:
    df = LOADERS[name]()
    return quality_filter(df) if protocol == "v3" else df


# Embeddings are extracted once per audio pool, then matched to task rows by path.
EMB_POOL = {"cryceleb": "cryceleb", "infantcry_dbl": "infantcry_dbl",
            "ujm_sex": "ujm_axa", "ujm_age": "ujm_axa", "ujm_axa": "ujm_axa"}
