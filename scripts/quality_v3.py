"""Protocol v3 data-quality manifest -> data/interim/quality_v3.csv

Per clip (native audio): fraction of samples at |x| >= 0.999, fraction of 25-ms frames with
RMS < 1e-3, native sample rate, UJM published SNR. A clip is excluded if
clip_frac > 0.001 or silent_frac > 0.5 or (UJM and SNR < 10 dB). Criteria: PROTOCOL.md (v3).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.data import LOADERS  # noqa: E402

CLIP_THR, SILENT_THR, SNR_THR = 0.001, 0.5, 10.0


def measure(path):
    x, sr = sf.read(path, always_2d=True)
    x = x.mean(1)
    n = max(1, int(0.025 * sr))
    fr = x[: len(x) // n * n].reshape(-1, n) if len(x) >= n else x[None]
    rms = np.sqrt((fr ** 2).mean(1))
    return dict(path=path, sr=sr, clip_frac=float((np.abs(x) >= 0.999).mean()),
                silent_frac=float((rms < 1e-3).mean()))


paths = sorted({p for name in ("cryceleb", "infantcry_dbl", "ujm_axa") for p in LOADERS[name]().path})
q = pd.DataFrame(Parallel(n_jobs=4)(delayed(measure)(p) for p in paths))
meta = pd.read_csv("data/raw/ujm_axa/metadata.csv", low_memory=False, usecols=["baby", "cry", "SNR"]).dropna()
meta["path"] = [f"data/raw/ujm_axa/audio/{int(b)}_{int(c)}.WAV" for b, c in zip(meta.baby, meta.cry)]
q = q.merge(meta[["path", "SNR"]], on="path", how="left")
q["reason"] = ""
q.loc[q.clip_frac > CLIP_THR, "reason"] += "clipped;"
q.loc[q.silent_frac > SILENT_THR, "reason"] += "silent;"
q.loc[q.SNR < SNR_THR, "reason"] += "low_snr;"
q["exclude"] = q.reason != ""
Path("data/interim").mkdir(parents=True, exist_ok=True)
q.to_csv("data/interim/quality_v3.csv", index=False)
corpus = q.path.str.split("/").str[2]
print(pd.crosstab(corpus, q.exclude).rename(columns={False: "kept", True: "excluded"}).to_string())
print("reasons:", q[q.exclude].reason.value_counts().to_dict())
