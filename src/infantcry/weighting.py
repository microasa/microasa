"""Dual weighting for infant-cry classification.

Two orthogonal weighting levels:
  * class level   - counter label imbalance (`none` | `balanced` | `effective`)
  * feature-group level - fuse one classifier per acoustic feature group with
        `equal`     : w_g = 1/G                         (unweighted fusion baseline)
        `global`    : w_g = softmax(tau * macroF1_g)    (one weight per group)
        `classwise` : w_gc = softmax_g(tau * F1_gc)     (one weight per group AND class)
    Weights are estimated ONLY from inner, group-aware cross-validation on the
    training fold, so the outer test fold never influences them.
"""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def class_weight_dict(y: np.ndarray, scheme: str, beta: float = 0.999):
    if scheme == "none":
        return None
    classes, counts = np.unique(y, return_counts=True)
    if scheme == "balanced":
        w = len(y) / (len(classes) * counts)
    elif scheme == "effective":  # Cui et al. 2019, effective number of samples
        w = (1 - beta) / (1 - beta**counts)
        w = w / w.sum() * len(classes)
    else:
        raise ValueError(scheme)
    return dict(zip(classes, w))


def _softmax(a: np.ndarray, axis: int) -> np.ndarray:
    a = a - a.max(axis=axis, keepdims=True)
    e = np.exp(a)
    return e / e.sum(axis=axis, keepdims=True)


def make_base(class_weight, C: float = 1.0):
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=C, class_weight=class_weight, max_iter=2000),
    )


class ConcatClassifier(BaseEstimator, ClassifierMixin):
    """Baseline: all feature groups concatenated, single logistic regression."""

    def __init__(self, class_scheme="none"):
        self.class_scheme = class_scheme

    def fit(self, X, y, groups=None):  # X: dict[group -> array]
        self.keys_ = list(X)
        self.model_ = make_base(class_weight_dict(y, self.class_scheme))
        self.model_.fit(np.hstack([X[k] for k in self.keys_]), y)
        self.classes_ = self.model_.classes_
        return self

    def predict_proba(self, X):
        return self.model_.predict_proba(np.hstack([X[k] for k in self.keys_]))

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(1)]


class GroupFusionClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, class_scheme="none", fusion="equal", tau=10.0, inner_splits=3, seed=0):
        self.class_scheme = class_scheme
        self.fusion = fusion
        self.tau = tau
        self.inner_splits = inner_splits
        self.seed = seed

    def _inner_scores(self, X, y, groups):
        """Per-group, per-class F1 from inner group-aware CV on the training fold."""
        n_cls = len(self.classes_)
        scores = np.zeros((len(self.keys_), n_cls))
        cw = class_weight_dict(y, self.class_scheme)
        cv = StratifiedGroupKFold(self.inner_splits, shuffle=True, random_state=self.seed)
        for gi, k in enumerate(self.keys_):
            pred = np.empty(len(y), dtype=y.dtype)
            for tr, va in cv.split(X[k], y, groups):
                m = make_base(cw).fit(X[k][tr], y[tr])
                pred[va] = m.predict(X[k][va])
            scores[gi] = f1_score(y, pred, labels=self.classes_, average=None, zero_division=0)
        return scores

    def fit(self, X, y, groups=None):
        self.keys_ = list(X)
        self.classes_ = np.unique(y)
        cw = class_weight_dict(y, self.class_scheme)
        self.models_ = [make_base(cw).fit(X[k], y) for k in self.keys_]
        G, C = len(self.keys_), len(self.classes_)
        if self.fusion == "equal":
            self.w_ = np.full((G, C), 1.0 / G)
        else:
            sc = self._inner_scores(X, y, groups if groups is not None else np.arange(len(y)))
            if self.fusion == "global":
                self.w_ = np.tile(_softmax(self.tau * sc.mean(1), 0)[:, None], (1, C))
            elif self.fusion == "classwise":
                self.w_ = _softmax(self.tau * sc, axis=0)
            else:
                raise ValueError(self.fusion)
            self.inner_scores_ = sc
        return self

    def predict_proba(self, X):
        P = np.stack([m.predict_proba(X[k]) for m, k in zip(self.models_, self.keys_)])  # G,N,C
        out = (P * self.w_[:, None, :]).sum(0)
        return out / out.sum(1, keepdims=True)

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(1)]
