"""Statistics for repeated k-fold CV (supervisor finding S2).

Corrected resampled t-test (Nadeau & Bengio, 2003; Bouckaert & Frank, 2004):
    d_j = score_A - score_B on outer fold j (j = 1..k, k = folds x repetitions)
    t   = mean(d) / sqrt((1/k + n_test/n_train) * var(d)),   df = k - 1
The n_test/n_train term inflates the variance to account for overlapping training sets,
which the naive paired tests (t, Wilcoxon) ignore. With 5-fold CV, n_test/n_train = 1/4.
"""
import numpy as np
from scipy import stats

TEST_TRAIN_RATIO = 0.25  # 5-fold CV


def nb_test(d, ratio=TEST_TRAIN_RATIO, alpha=0.05):
    d = np.asarray(d, dtype=float)
    k = len(d)
    mean, var = d.mean(), d.var(ddof=1)
    if var == 0:
        return dict(k=k, mean=mean, t=np.nan, p=1.0 if mean == 0 else 0.0, ci_low=mean, ci_high=mean)
    se = np.sqrt((1 / k + ratio) * var)
    t = mean / se
    q = stats.t.ppf(1 - alpha / 2, k - 1)
    return dict(k=k, mean=mean, t=t, p=float(2 * stats.t.sf(abs(t), k - 1)),
                ci_low=mean - q * se, ci_high=mean + q * se)


def holm(pvals):
    """Holm-Bonferroni adjusted p-values (monotone, capped at 1)."""
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj
