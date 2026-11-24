# microasa — Paper 4: weighting for infant-cry classification

Experiment code for a study of where weighting helps in infant-cry classification:
class weighting, feature-group weighting (handcrafted acoustics), and layer weighting
(wav2vec2 / HuBERT embeddings). The current protocol is **v2** (`PROTOCOL.md`), written in
response to the critical review in `reports/supervisor_review.pdf`.

## Layout
| Path | Content |
|---|---|
| `src/infantcry/data.py` | dataset loaders (CryCeleb2023, BABYCRY-UJM-AXA subset, cleaned InfantCry-DBL) |
| `src/infantcry/features.py` | v2 handcrafted feature groups and the corrected F0 tracker |
| `src/infantcry/fusion.py` | expert bank (tuned C), combiners (equal, best_single, softmax_tau, stacking), SUPERB weighted sum |
| `src/infantcry/stats.py` | Nadeau–Bengio corrected resampled t-test, Holm correction |
| `src/infantcry/remote_zip.py` | partial download of the 81 GB UJM-AXA zip via HTTP range requests |
| `scripts/` | download, cleaning (`prepare_dbl.py`), extraction, `run_v2.py`, `analyze_v2.py` |
| `tests/` | unit tests (F0 tracker on synthetic signals, weights, statistics, combiners) |
| `results/v2/` | current results (each row carries the git SHA that produced it) |
| `results/v1/` | superseded v1 results, kept for the record |
| `reports/` | supervisor review (PDF) and its build script |

## Reproduce (from the repo root)
```bash
pip install -r requirements.lock          # Python 3.13; versions used for v2
export PYTHONPATH=src HF_HUB_DISABLE_XET=1
python -m pytest -q tests
# data: see DATASETS.md (CryCeleb needs a Hugging Face token; UJM via download_ujm_subset.py)
python scripts/prepare_dbl.py             # DBL cleaning -> data/interim/dbl_manifest.csv
for t in infantcry_dbl ujm_sex ujm_age ujm_axa cryceleb; do python scripts/extract_features.py $t; done
for m in w2v2 hubert; do for p in infantcry_dbl ujm_axa cryceleb; do python scripts/extract_embeddings.py $m $p; done; done
for r in hand w2v2 hubert; do for t in infantcry_dbl ujm_age ujm_sex cryceleb; do python scripts/run_v2.py $t $r; done; done
python scripts/analyze_v2.py
```
Run everything from the repository root (paths are relative). Raw data and
`data/interim/` are not committed.

## Environment notes
* `librosa.yin`/`pyin` segfault in the original container (numba); the F0 tracker is pure numpy.
* Hugging Face downloads need `HF_HUB_DISABLE_XET=1` behind the session proxy.
