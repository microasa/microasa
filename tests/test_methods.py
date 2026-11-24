"""Unit tests for v2 fusion and statistics (supervisor findings M1-M3, S2)."""
import numpy as np
import pytest
from scipy import stats

from infantcry.fusion import combine, fit_bank, sample_weights
from infantcry.stats import holm, nb_test

Y = np.array(["a"] * 121 + ["b"] * 46 + ["c"] * 19)


@pytest.mark.parametrize("scheme", ["none", "balanced", "effective"])
def test_sample_weights_sum_to_n(scheme):
    w = sample_weights(Y, scheme)
    assert np.isclose(w.sum(), len(Y))


def test_balanced_weights_equalise_classes():
    w = sample_weights(Y, "balanced")
    per_class = [w[Y == c].sum() for c in "abc"]
    assert np.allclose(per_class, per_class[0])


def test_nb_variance_larger_than_naive():
    rng = np.random.default_rng(0)
    d = rng.normal(0.01, 0.02, 15)
    naive_p = stats.ttest_1samp(d, 0).pvalue
    assert nb_test(d)["p"] > naive_p
    r = nb_test(d)
    assert r["ci_low"] < r["mean"] < r["ci_high"]


def test_holm_known_values():
    assert np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


def test_bank_and_combiners_shapes_and_selection():
    rng = np.random.default_rng(1)
    n = 120
    y = np.repeat(np.array(["x", "y"]), n // 2)
    g = np.arange(n).astype(str)
    informative = (y == "y")[:, None] * 2.0 + rng.normal(size=(n, 3))
    X = {"good": informative, "noise1": rng.normal(size=(n, 3)), "noise2": rng.normal(size=(n, 3))}
    tr, te = np.arange(0, n, 2), np.arange(1, n, 2)
    classes = np.unique(y)
    bank = fit_bank({k: v[tr] for k, v in X.items()}, y[tr], g[tr], {k: v[te] for k, v in X.items()}, classes)
    out, diag = combine(bank, y[tr], classes)
    assert diag["best_single"] == "good"
    assert diag["tau"] > 0  # with one clearly better expert, uniform weighting must not win
    for P in out.values():
        assert P.shape == (len(te), 2) and np.allclose(P.sum(1), 1)
    acc = (classes[out["stacking"].argmax(1)] == y[te]).mean()
    assert acc > 0.8
