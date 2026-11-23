"""Download a deterministic, baby-stratified subset of BABYCRY-UJM-AXA (81 GB zip)
via HTTP range requests. Subset: N_PER_CLASS babies per delivery method,
CLIPS_PER_BABY random clips each. Writes data/raw/ujm_axa/audio + subset.csv."""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.remote_zip import open_remote_zip  # noqa: E402

URL = "https://zenodo.org/records/19205929/files/BABYCRY-UJM-AXA.zip"
ROOT = Path("data/raw/ujm_axa")
N_PER_CLASS, CLIPS_PER_BABY, SEED, WORKERS = 100, 6, 0, 2

d = pd.read_csv(ROOT / "metadata.csv", low_memory=False).dropna(subset=["baby", "cry", "delivery.method"])
d["baby"] = d["baby"].astype(int)
d["cry"] = d["cry"].astype(int)
d["zip_name"] = d["baby"].astype(str) + "_" + d["cry"].astype(str) + ".WAV"
rng = pd.Series(range(len(d))).sample(frac=1, random_state=SEED).values
d = d.iloc[rng]
babies = (
    d.drop_duplicates("baby")
    .groupby("delivery.method", group_keys=False)
    .apply(lambda g: g.sample(min(N_PER_CLASS, len(g)), random_state=SEED))["baby"]
)
sub = d[d["baby"].isin(babies)].groupby("baby", group_keys=False).head(CLIPS_PER_BABY)
cols = ["baby", "cry", "zip_name", "sex", "delivery.method", "term", "age", "duration"]
sub[cols].to_csv(ROOT / "subset.csv", index=False)
print("subset clips", len(sub), "babies", sub.baby.nunique(), flush=True)

(ROOT / "audio").mkdir(exist_ok=True)
names = sub["zip_name"].tolist()
chunks = [names[i::WORKERS] for i in range(WORKERS)]


def work(chunk):
    z = open_remote_zip(URL)
    for n in chunk:
        out = ROOT / "audio" / n
        if out.exists() and out.stat().st_size > 0:
            continue
        out.write_bytes(z.read("BABYCRY-UJM-AXA/audio/" + n))
    return len(chunk)


with ThreadPoolExecutor(WORKERS) as ex:
    print("done", sum(ex.map(work, chunks)), flush=True)
