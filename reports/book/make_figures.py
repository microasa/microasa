"""Figures for the Paper 4 book (static print figures, light theme).
Run from the repo root:  python3 reports/book/make_figures.py
Palette: reference categorical slots 1-2 (validated light mode); text/grid neutrals."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

BLUE, ORANGE = "#257de0", "#f47230"
INK, INK2, GRID = "#191919", "#666666", "#e3e5e8"
TASK = {"cryceleb": "CryCeleb", "infantcry_dbl": "DBL", "ujm_sex": "UJM-sex", "ujm_age": "UJM-age",
        "ujm_axa": "UJM-delivery"}
REP = {"hand": "handcrafted", "w2v2": "wav2vec2", "hubert": "HuBERT"}
HYP = {"H1": "H1  stacking − equal", "H2": "H2  stacking − best single", "H3": "H3  stacking − SUPERB",
       "H4": "H4  concat balanced − concat tanpa bobot"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK, "axes.spines.top": False,
                     "axes.spines.right": False})


def forest():
    p = pd.read_csv("results/v2/primary_tests.csv")
    fig, ax = plt.subplots(figsize=(6.6, 8.6), dpi=200)
    y, ticks, labels, heads = 0, [], [], []
    for h in ["H1", "H2", "H3", "H4"]:
        heads.append((y, HYP[h]))
        y -= 1
        for _, r in p[p.hypothesis == h].iterrows():
            ax.plot([r.ci_low, r.ci_high], [y, y], color=BLUE, lw=2, solid_capstyle="round", zorder=2)
            ax.plot(r["mean"], y, "o", ms=5, color=BLUE, mec="white", mew=1.2, zorder=3)
            ticks.append(y)
            labels.append(f"{TASK[r.task]} · {REP[r.rep]}")
            y -= 1
        y -= 0.6
    ax.axvline(0, color=INK2, lw=1, zorder=1)
    ax.set_yticks(ticks, labels, fontsize=7)
    for yy, t in heads:
        ax.text(-0.42, yy, t, fontsize=8.2, fontweight="bold", color=INK, va="center", ha="left")
    ax.set_xlim(-0.42, 0.32)
    ax.set_ylim(y + 0.6, 0.8)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Selisih macro-F1 (rata-rata 15 fold) dengan CI 95% terkoreksi Nadeau–Bengio")
    ax.text(0.005, 0.35, "← metode pembanding lebih baik   |   metode usulan lebih baik →", transform=ax.transData,
            fontsize=7, color=INK2, ha="center")
    fig.tight_layout()
    fig.savefig("reports/book/fig_forest.png")


def dumbbell():
    keep = ["equal", "best_single", "softmax_tau", "stacking", "superb_wsum", "last_layer", "concat_balanced"]
    best = lambda d: d[d.method.isin(keep)].groupby(["task", "rep"]).macro_f1.max()  # noqa: E731
    a = best(pd.read_csv("results/v2/summary.csv"))
    b = best(pd.read_csv("results/v3/summary.csv"))
    order = [(t, r) for t in ["cryceleb", "ujm_sex", "ujm_age", "ujm_axa", "infantcry_dbl"]
             for r in ["hand", "w2v2", "hubert"] if (t, r) in a.index]
    fig, ax = plt.subplots(figsize=(6.6, 4.6), dpi=200)
    for i, k in enumerate(order):
        yy = -i
        ax.plot([a[k], b[k]], [yy, yy], color="#b8bcc2", lw=1.5, zorder=1)
        ax.plot(a[k], yy, "o", ms=6.5, color=BLUE, mec="white", mew=1.5, zorder=3)
        ax.plot(b[k], yy, "s", ms=6, color=ORANGE, mec="white", mew=1.5, zorder=3)
        d = b[k] - a[k]
        if abs(d) >= 0.03:
            ax.text(min(a[k], b[k]) - 0.006, yy, f"{d:+.2f}", fontsize=7, color=INK, va="center", ha="right")
    ax.set_yticks([-i for i in range(len(order))], [f"{TASK[t]} · {REP[r]}" for t, r in order], fontsize=7)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_xlabel("Macro-F1 metode terbaik per tugas")
    ax.plot([], [], "o", color=BLUE, label="v2 (data apa adanya)")
    ax.plot([], [], "s", color=ORANGE, label="v3 (band-limit + filter kualitas)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=2, frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig("reports/book/fig_v2_v3.png")


def inflation():
    """How the DBL estimate moved as each evaluation flaw was fixed (proposed method)."""
    steps = [("v1: subset 'bersih', 1 klip = 1 grup", 0.852),
             ("v1: klip mirip (cos > 0,85) satu grup", 0.818),
             ("v2: salinan lintas korpus dibuang (103 klip)", 0.768),
             ("v3: band-limit 0–4 kHz + filter kualitas", 0.665)]
    fig, ax = plt.subplots(figsize=(6.6, 2.4), dpi=200)
    for i, (lab, v) in enumerate(steps):
        ax.barh(-i, v, height=0.55, color=BLUE, zorder=2)
        ax.text(v + 0.008, -i, f"{v:.3f}", va="center", fontsize=7.5, color=INK)
    ax.set_yticks([-i for i in range(len(steps))], [s[0] for s in steps], fontsize=7)
    ax.axvline(0.2, color=INK2, lw=1, ls=(0, (3, 2)), zorder=3)
    ax.text(0.205, 0.45, "acak (5 kelas)", fontsize=6.5, color=INK2)
    ax.set_xlim(0, 1)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_xlabel("Macro-F1 handcrafted terbaik pada DBL")
    fig.tight_layout()
    fig.savefig("reports/book/fig_dbl_inflation.png")


forest()
dumbbell()
inflation()
print("figures written")
