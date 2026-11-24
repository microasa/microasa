"""Protocol v2 fusion methods (supervisor findings M1-M4).

Design: per outer training fold, ONE bank of per-group experts is fitted; every fusion
rule is then derived from the same bank, so methods differ only in the combiner.

Expert (per feature group / encoder layer):
    median-imputer -> StandardScaler -> [PCA(d, whiten=True)] -> LogisticRegression
    C chosen from C_GRID by inner group-aware CV (macro-F1); class weights normalised so
    the total sample weight equals n for every scheme (fixes M3).

Combiners (all fitted on inner out-of-fold probabilities only):
    equal        mean of expert probabilities (linear pool)
    best_single  hard argmax of inner OOF macro-F1 (pure selection, no softmax)
    softmax_tau  w_g = softmax(tau * F1_g); tau tuned on inner OOF fused macro-F1 (fixes M1)
    stacking     multinomial LR on all experts' OOF log-probabilities: learns class-aware
                 expert weights coherently in one model (replaces the incoherent
                 per-class softmax fusion; fixes M2)  <- PROPOSED (v2)
Extra baselines: last layer, concatenation, duration-only, SUPERB learnable weighted sum.
"""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler

C_GRID = (0.01, 0.1, 1.0)
TAU_GRID = (0.0, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0)
INNER_SPLITS = 3
EPS = 1e-6


def sample_weights(y, scheme, beta=0.999):
    """Per-sample weights with sum == n for every scheme (so C means the same thing)."""
    if scheme == "none":
        return np.ones(len(y))
    classes, inv, counts = np.unique(y, return_inverse=True, return_counts=True)
    if scheme == "balanced":
        wc = 1.0 / counts
    elif scheme == "effective":  # Cui et al. 2019
        wc = (1 - beta) / (1 - beta ** counts)
    else:
        raise ValueError(scheme)
    w = wc[inv]
    return w * len(y) / w.sum()


class Prep:
    """Imputer -> scaler -> optional whitened PCA, fitted on the given rows only."""

    def __init__(self, pca=None, seed=0):
        self.pca, self.seed = pca, seed

    def fit(self, X):
        self.imp = SimpleImputer(strategy="median", keep_empty_features=True).fit(X)
        Z = self.imp.transform(X)
        self.sc = StandardScaler().fit(Z)
        Z = self.sc.transform(Z)
        self.p = None
        if self.pca and Z.shape[1] > self.pca:
            self.p = PCA(self.pca, whiten=True, random_state=self.seed).fit(Z)
        return self

    def transform(self, X):
        Z = self.sc.transform(self.imp.transform(X))
        return self.p.transform(Z) if self.p is not None else Z


def macro_f1(y, P, classes):
    return f1_score(y, classes[P.argmax(1)], average="macro", labels=classes, zero_division=0)


def _lr(C, Z, y, w):
    return LogisticRegression(C=C, max_iter=3000).fit(Z, y, sample_weight=w)


def fit_expert(Xtr, ytr, gtr, Xte, classes, scheme="balanced", pca=None, seed=0, Cs=C_GRID):
    """Returns OOF probs on the training fold (best C), test probs, chosen C, OOF macro-F1."""
    cv = StratifiedGroupKFold(INNER_SPLITS, shuffle=True, random_state=seed)
    oof = {C: np.zeros((len(ytr), len(classes))) for C in Cs}
    for tr, va in cv.split(Xtr, ytr, gtr):
        prep = Prep(pca, seed).fit(Xtr[tr])
        Ztr, Zva = prep.transform(Xtr[tr]), prep.transform(Xtr[va])
        w = sample_weights(ytr[tr], scheme)
        for C in Cs:
            m = _lr(C, Ztr, ytr[tr], w)
            oof[C][np.ix_(va, np.searchsorted(classes, m.classes_))] = m.predict_proba(Zva)
    scores = {C: macro_f1(ytr, oof[C], classes) for C in Cs}
    Cbest = max(Cs, key=lambda c: (scores[c], -c))  # ties -> stronger regularisation
    prep = Prep(pca, seed).fit(Xtr)
    m = _lr(Cbest, prep.transform(Xtr), ytr, sample_weights(ytr, scheme))
    Pte = np.zeros((len(Xte), len(classes)))
    Pte[:, np.searchsorted(classes, m.classes_)] = m.predict_proba(prep.transform(Xte))
    return oof[Cbest], Pte, Cbest, scores[Cbest]


def fit_bank(Xtr: dict, ytr, gtr, Xte: dict, classes, scheme="balanced", pca=None, seed=0):
    return {k: fit_expert(Xtr[k], ytr, gtr, Xte[k], classes, scheme, pca, seed) for k in Xtr}


def _softmax(a):
    a = a - a.max()
    e = np.exp(a)
    return e / e.sum()


def combine(bank: dict, ytr, classes, seed=0):
    """All combiners from one bank. Returns {method: test_probs}, diagnostics."""
    keys = list(bank)
    Poof = np.stack([bank[k][0] for k in keys])  # G, Ntr, K
    Pte = np.stack([bank[k][1] for k in keys])   # G, Nte, K
    f1 = np.array([bank[k][3] for k in keys])
    out, diag = {}, {}
    out["equal"] = Pte.mean(0)
    b = int(np.argmax(f1))
    out["best_single"] = Pte[b]
    diag["best_single"] = keys[b]
    best = None
    for tau in TAU_GRID:
        w = _softmax(tau * f1)
        s = macro_f1(ytr, np.tensordot(w, Poof, 1), classes)
        if best is None or s > best[0] + 1e-12:
            best = (s, tau, w)
    out["softmax_tau"] = np.tensordot(best[2], Pte, 1)
    diag["tau"], diag["w_max"] = best[1], float(best[2].max())
    Zoof = np.log(np.clip(Poof, EPS, 1)).transpose(1, 0, 2).reshape(len(ytr), -1)
    Zte = np.log(np.clip(Pte, EPS, 1)).transpose(1, 0, 2).reshape(Pte.shape[1], -1)
    sc = StandardScaler().fit(Zoof)
    meta = _lr(1.0, sc.transform(Zoof), ytr, sample_weights(ytr, "balanced"))
    P = np.zeros((len(Zte), len(classes)))
    P[:, np.searchsorted(classes, meta.classes_)] = meta.predict_proba(sc.transform(Zte))
    out["stacking"] = P
    diag["C"] = {k: bank[k][2] for k in keys}
    return out, diag


def superb_weighted_sum(Ltr, ytr, gtr, Lte, classes, seed=0, wds=(1e-4, 1e-3, 1e-2), steps=300):
    """SUPERB-style baseline: softmax-weighted sum of per-layer standardised features with a
    linear head, trained end-to-end (Yang et al., 2021). Weight decay chosen on one inner
    group-aware split; then refit on the whole training fold. L*: (N, L, D) arrays."""
    import torch

    torch.set_num_threads(1)

    def train(Xa, ya, wd):
        torch.manual_seed(seed)
        mu, sd = Xa.mean(0, keepdims=True), Xa.std(0, keepdims=True) + 1e-6
        X = torch.tensor((Xa - mu) / sd, dtype=torch.float32)
        yi = torch.tensor(np.searchsorted(classes, ya))
        cw = torch.tensor(np.bincount(yi.numpy(), minlength=len(classes)), dtype=torch.float32)
        cw = torch.where(cw > 0, len(ya) / (len(classes) * cw.clamp(min=1)), torch.zeros_like(cw))
        a = torch.zeros(X.shape[1], requires_grad=True)
        head = torch.nn.Linear(X.shape[2], len(classes))
        opt = torch.optim.Adam([{"params": [a], "weight_decay": 0.0},
                                {"params": head.parameters(), "weight_decay": wd}], lr=1e-2)
        lossf = torch.nn.CrossEntropyLoss(weight=cw)
        for _ in range(steps):
            opt.zero_grad()
            z = torch.einsum("l,nld->nd", torch.softmax(a, 0), X)
            lossf(head(z), yi).backward()
            opt.step()

        def predict(Xb):
            with torch.no_grad():
                Xb = torch.tensor((Xb - mu) / sd, dtype=torch.float32)
                z = torch.einsum("l,nld->nd", torch.softmax(a, 0), Xb)
                return torch.softmax(head(z), 1).numpy()

        return predict, torch.softmax(a, 0).detach().numpy()

    tr, va = next(StratifiedGroupKFold(INNER_SPLITS, shuffle=True, random_state=seed).split(Ltr[:, 0], ytr, gtr))
    scores = {wd: macro_f1(ytr[va], train(Ltr[tr], ytr[tr], wd)[0](Ltr[va]), classes) for wd in wds}
    wd = max(wds, key=lambda v: (scores[v], v))
    predict, lw = train(Ltr, ytr, wd)
    return predict(Lte), {"wd": wd, "layer_w_max": float(lw.max()), "layer_argmax": int(lw.argmax())}
