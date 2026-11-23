"""Layer-wise mean-pooled embeddings of a pretrained speech encoder.
usage: extract_embeddings.py <w2v2|hubert> <pool: cryceleb|infantcry_dbl|ujm_axa>
-> data/interim/emb_<model>_<pool>.npz  (layers: N x L x D float16, paths)"""
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
import librosa
import numpy as np
import torch
from transformers import AutoModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infantcry.data import LOADERS  # noqa: E402

MODELS = {"w2v2": "facebook/wav2vec2-base", "hubert": "facebook/hubert-base-ls960"}
SR, MAX_S, MIN_S = 16000, 6.0, 0.4
model_key, pool = sys.argv[1], sys.argv[2]
paths = LOADERS[pool]().path.tolist()
net = AutoModel.from_pretrained(MODELS[model_key]).eval()
torch.set_num_threads(4)
out = []
with torch.inference_mode():
    for i, p in enumerate(paths):
        y, _ = librosa.load(p, sr=SR, mono=True, duration=MAX_S)
        y = np.pad(y, (0, max(0, int(MIN_S * SR) - len(y))))
        y = (y - y.mean()) / (y.std() + 1e-7)
        hs = net(torch.from_numpy(y)[None], output_hidden_states=True).hidden_states
        out.append(torch.stack([h[0].mean(0) for h in hs]).numpy().astype(np.float16))
        if i % 500 == 0:
            print(model_key, pool, i, "/", len(paths), flush=True)
np.savez_compressed(f"data/interim/emb_{model_key}_{pool}.npz",
                    layers=np.stack(out), paths=np.array(paths, dtype="U256"))
print("saved", np.stack(out).shape)
