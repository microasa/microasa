# Paper 4 — Evaluation protocol v2 (frozen before any v2 result)

Written in response to the supervisor review (`reports/supervisor_review.pdf`). Every
item below was fixed **before** running v2; any later change must be listed under
"Deviations" with a reason. v1 results are archived in `results/v1/` and are superseded.

## Data
| Task | Corpus | Label | CV group |
|---|---|---|---|
| `cryceleb` | CryCeleb2023, named ids only (626 babies, ≤5 clips per baby and period) | B vs D | baby |
| `infantcry_dbl` | InfantCry-DBL Tier-2 `online_or_volunteer`, cleaned by `scripts/prepare_dbl.py` | 5 DBL classes | near-duplicate cluster |
| `ujm_sex` | BABYCRY-UJM-AXA subset (300 babies) | F vs M | baby |
| `ujm_age` | same subset, lowest vs highest tertile of age (hours) | young vs old | baby |
| `ujm_axa` (supplementary) | same subset | delivery method (3) | baby |

DBL cleaning (D1, D3): sha256 verified against the publisher; byte-identical duplicates
removed; candidates with z-scored feature cosine ≥ 0.95 to any Tier-1 (Dunstan) clip or
any CryCeleb2023 clip removed; remaining clips with cosine ≥ 0.90 merged into one CV group.

## Representations
* `hand`: 6 groups (v2 features): mfcc mean+std (40), delta-MFCC std (20), spectral (22),
  pitch from the corrected F0 tracker (7), energy without duration (5), log-mel std (32).
* `w2v2` (facebook/wav2vec2-base) and `hubert` (facebook/hubert-base-ls960): 13 hidden
  states, mean-pooled over time, max 6 s of audio.
* Clip duration is never a model feature; it is used only by the `duration_only` baseline.

## Models (all class-weighted "balanced", weights normalised to sum n)
Per outer training fold, one expert per group/layer: median imputer → scaler →
(whitened PCA 64, embeddings only) → logistic regression, C ∈ {0.01, 0.1, 1} chosen by
inner 3-fold group-aware CV on macro-F1. Combiners use inner out-of-fold probabilities only:
* `equal` (mean of probabilities), `best_single` (hard argmax inner macro-F1),
  `softmax_tau` (τ ∈ {0,1,3,10,30,100,300,1000} tuned on inner OOF macro-F1),
* **`stacking` — PROPOSED v2**: multinomial LR on all experts' OOF log-probabilities.
* Baselines: `last_layer` and `superb_wsum` (learnable softmax layer weights + linear head,
  weight decay ∈ {1e-4,1e-3,1e-2} on one inner split) for embeddings; `concat_none`,
  `concat_balanced`, `concat_effective` for handcrafted; `duration_only` everywhere.

## Evaluation
StratifiedGroupKFold, 5 folds × seeds {0, 1, 2} = 15 outer folds for **every** run.
Metric: macro-F1 per outer fold (primary); balanced accuracy and pooled macro-F1 reported.

## Statistics (pre-declared primary family, 36 tests)
Nadeau–Bengio corrected resampled t-test (n_test/n_train = 1/4, df = 14), two-sided,
Holm correction across the whole family; 95% CI of the mean difference reported.
* H1 (12 runs): `stacking` − `equal`
* H2 (12 runs): `stacking` − `best_single`
* H3 (8 embedding runs): `stacking` − `superb_wsum`
* H4 (4 handcrafted runs): `concat_balanced` − `concat_none`

Runs = {hand, w2v2, hubert} × {cryceleb, infantcry_dbl, ujm_sex, ujm_age}.
Everything else (e.g. `softmax_tau` vs `equal`, `best_single` vs `last_layer`, `ujm_axa`)
is exploratory and reported unadjusted, labelled as such.

Decision rule: a method is called better only if the Holm-adjusted p < 0.05 **and** the
95% CI excludes 0. Shortcut check: if `duration_only` is within 0.02 macro-F1 of the
best model on a task, that task is reported as shortcut-dominated.

## Protocol v3 — data-quality sensitivity analysis (frozen before any v3 result)
Motivation: a quality scan after v2 found a sample-rate/label association in DBL
(χ² p = 0.0001; e.g. all `heh` clips are 44.1 kHz, all 8 kHz clips are `eh`), clipping
in DBL, and low-SNR clips in UJM. v3 is a **sensitivity analysis**: v2 remains the
primary result, and v3 is reported next to it whatever it shows.

Criteria (applied identically to every task, representation and method):
1. **Band-limiting:** every clip is resampled to 8 kHz (anti-aliased, removes content
   above 4 kHz) and back to 16 kHz before feature/embedding extraction, so recording
   bandwidth can no longer reveal the source or label.
2. **Clipping:** drop clips with > 0.1% of samples at |x| ≥ 0.999 (native audio).
3. **Silence:** drop clips where > 50% of 25-ms frames have RMS < 1e-3 (−60 dBFS).
4. **UJM SNR:** drop UJM clips whose published `SNR` < 10 dB.
5. Everything else is unchanged from v2 (same models, 5 × 3 CV, DBL groups, primary
   family H1–H4 with Holm over 36 tests, decision rule). Results go to `results/v3/`.

Pre-declared extra diagnostic (exploratory): a DBL classifier that uses only the native
sample rate (one-hot), to quantify how much label information the bandwidth cue carries.

## Deviations
1. PCA dimension is capped at n_train − 1 when a (inner) training split has fewer than
   65 samples. Only DBL embedding runs are affected (inner splits of ~54 clips). Found as
   a crash on the first DBL embedding run, before any embedding result existed.
2. DBL cleaning (applied exactly as specified) left 103 clips in 86 groups: 1 byte-identical
   duplicate and 133 cross-corpus matches were removed (107 of them with cosine ≥ 0.999,
   i.e. copies: 41 of Tier-1 Dunstan clips, 66 of CryCeleb clips). This is not a protocol
   change, but it makes DBL very small (heh: 6 clips); DBL results are low-powered.
