# Paper 4 datasets (infant cry weighting study)

Paper 4 must use datasets disjoint from Paper 1 (Donate-a-Cry, Baby Chillanto, Dunstan/Kaggle).

| Dataset | Source | License | Local path | Status |
|---|---|---|---|---|
| CryCeleb2023 | huggingface.co/datasets/Ubenwa/CryCeleb2023 (gated, token required) | CC BY-NC-ND 4.0 | data/raw/cryceleb | downloaded + extracted (anonymous test ids dropped: 626 babies, 4,954 clips) |
| BABYCRY-UJM-AXA | zenodo.org/records/19205929 (81 GB zip; partial range download) | CC BY 4.0 | data/raw/ujm_axa | subset downloaded: 300 babies x <=6 clips = 1,762 clips (balanced 100 babies/delivery class) |
| InfantCry-DBL | data.mendeley.com/datasets/x493z8nmwc | CC BY 4.0 | data/raw/infantcry_dbl | downloaded; only 237 Tier-2 `online_or_volunteer` clips used |

## Overlap caveats
- InfantCry-DBL Tier 1 (337 clips) comes from Dunstan instructional videos, overlapping Paper 1's Dunstan data.
- InfantCry-DBL Tier 2 is partly derived from CryCeleb. Only non-CryCeleb Tier 2 clips (see `source` column) may be used.
- ICSD: download location not yet found.

## Evaluation rules
Subject-independent splits only; report macro-F1 and balanced accuracy.

## Preliminary results (macro-F1, 5-fold x 3 seeds, group-aware; see results/*_summary.csv)
| Dataset (task) | concat+balanced | fusion_equal+balanced | proposed classwise+balanced |
|---|---|---|---|
| InfantCry-DBL clean (5 Dunstan classes, no infant id) | 0.836 | 0.832 | 0.852 |
| CryCeleb2023 (birth vs discharge, 626 babies) | 0.611 | 0.606 | 0.605 |
| BABYCRY-UJM-AXA (delivery method, balanced, 300 babies) | 0.345 | 0.355 | 0.356 (chance = 0.333) |

Feature-group weighting gave no significant gain over equal-weight fusion on any dataset.
Class weighting mattered only for fusion on imbalanced data (DBL, CryCeleb).
CryCeleb: the `anonymousNNN` test ids must be excluded (same infant can appear under two ids).
