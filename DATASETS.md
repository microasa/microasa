# Paper 4 datasets (infant cry weighting study)

Paper 4 must use datasets disjoint from Paper 1 (Donate-a-Cry, Baby Chillanto, Dunstan/Kaggle).

| Dataset | Source | License | Local path | Status |
|---|---|---|---|---|
| CryCeleb2023 | huggingface.co/datasets/Ubenwa/CryCeleb2023 (gated, token required) | CC BY-NC-ND 4.0 | data/raw/cryceleb | downloading |
| BABYCRY-UJM-AXA | zenodo.org/records/19205929 (81 GB zip; partial range download) | CC BY 4.0 | data/raw/ujm_axa | not started |
| InfantCry-DBL | data.mendeley.com/datasets/x493z8nmwc | CC BY 4.0 | data/raw/infantcry_dbl | downloaded |

## Overlap caveats
- InfantCry-DBL Tier 1 (337 clips) comes from Dunstan instructional videos, overlapping Paper 1's Dunstan data.
- InfantCry-DBL Tier 2 is partly derived from CryCeleb. Only non-CryCeleb Tier 2 clips (see `source` column) may be used.
- ICSD: download location not yet found.

## Evaluation rules
Subject-independent splits only; report macro-F1 and balanced accuracy.
