"""Build the Paper 4 manuscript draft (negative-result study + data-quality finding) as a PDF.
Run from the repo root after scripts/analyze_v2.py has been run for results/v2 and results/v3:
    python3 reports/build_manuscript.py
All result numbers in tables are read from results/v2 and results/v3."""
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

F = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("S", "DejaVuSerif.ttf"), ("SB", "DejaVuSerif-Bold.ttf"), ("SS", "DejaVuSans.ttf"),
             ("SSB", "DejaVuSans-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(n, F + f))
pdfmetrics.registerFontFamily("S", normal="S", bold="SB", italic="S", boldItalic="SB")

LINE, FILL, GRY = colors.HexColor("#c8ccd2"), colors.HexColor("#f2f4f7"), colors.HexColor("#555b66")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="S", fontSize=10, leading=14.2, alignment=TA_JUSTIFY,
                      spaceAfter=6)
title = ParagraphStyle("t", parent=body, fontName="SB", fontSize=15.5, leading=20, alignment=TA_CENTER,
                       spaceAfter=8)
center = ParagraphStyle("c", parent=body, alignment=TA_CENTER, textColor=GRY, fontSize=9.5)
h1 = ParagraphStyle("h1", parent=body, fontName="SB", fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=5,
                    alignment=0)
h2 = ParagraphStyle("h2", parent=body, fontName="SB", fontSize=10.2, leading=14, spaceBefore=6, spaceAfter=3,
                    alignment=0)
absb = ParagraphStyle("ab", parent=body, fontSize=9.5, leading=13.2, leftIndent=0.8 * cm, rightIndent=0.8 * cm)
cap = ParagraphStyle("cap", parent=body, fontSize=8.8, leading=11.8, textColor=GRY, spaceBefore=3, spaceAfter=8)
cell = ParagraphStyle("cell", parent=body, fontName="SS", fontSize=7.6, leading=9.6, alignment=0, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="SSB")
ref = ParagraphStyle("ref", parent=body, fontSize=8.8, leading=11.8, leftIndent=0.6 * cm, firstLineIndent=-0.6 * cm,
                     alignment=0, spaceAfter=3)
note = ParagraphStyle("n", parent=body, fontSize=8.8, textColor=GRY, alignment=0)


def P(t, s=body):
    return Paragraph(t, s)


def tbl(rows, widths, caption):
    data = [[Paragraph(str(c), cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
                           ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                           ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                           ("BACKGROUND", (0, 0), (-1, 0), FILL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return KeepTogether([P(caption, cap), t, Spacer(1, 8)])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("SS", 7.5)
    canvas.setFillColor(GRY)
    canvas.drawString(2.2 * cm, 1.2 * cm, "Manuscript draft — not peer reviewed")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, str(doc.page))
    canvas.restoreState()


TASK = {"cryceleb": "CryCeleb (B vs D)", "infantcry_dbl": "DBL (5 classes)", "ujm_sex": "UJM sex",
        "ujm_age": "UJM age", "ujm_axa": "UJM delivery*"}
REP = {"hand": "Handcrafted", "w2v2": "wav2vec2", "hubert": "HuBERT"}
s2 = pd.read_csv("results/v2/summary.csv")
s3 = pd.read_csv("results/v3/summary.csv")
p2 = pd.read_csv("results/v2/primary_tests.csv")
p3 = pd.read_csv("results/v3/primary_tests.csv")
e2 = pd.read_csv("results/v2/exploratory_tests.csv")
n_sig2, n_sig3 = int((p2.verdict != "no evidence").sum()), int((p3.verdict != "no evidence").sum())
e2_bl = e2[e2.hypothesis == "E2"]

S = []
S += [P("Does Weighting Help Infant Cry Classification? A Leakage-Controlled Evaluation of Class, "
        "Feature-Group and Layer Weighting, with a Provenance Audit of a Public Cry Corpus", title),
      P("[Author names and affiliations]", center),
      P("Draft prepared for submission · target: Signal, Image and Video Processing (Springer)", center),
      Spacer(1, 6)]

S.append(P(
    "<b>Abstract.</b> Weighting is routinely proposed to improve infant cry classification: class weights for "
    "imbalanced labels, weights over acoustic feature groups, and weights over the layers of self-supervised speech "
    "encoders. We test whether any of these help when evaluation is controlled for the usual sources of optimism. "
    "We use three public corpora (CryCeleb2023, a 300-infant subset of BABYCRY-UJM-AXA, and a cleaned subset of "
    "InfantCry-DBL), handcrafted acoustic features and layer-wise wav2vec 2.0 and HuBERT embeddings, and compare "
    "equal-weight fusion, inner-validated single-expert selection, temperature-tuned softmax weighting, stacking, "
    "and a SUPERB-style learnable weighted sum. All weights and hyperparameters are estimated inside the training "
    "folds, splits are infant-grouped, and 36 pre-registered comparisons are tested with the Nadeau–Bengio "
    f"corrected resampled t-test and Holm correction. None of the 36 comparisons shows evidence of a difference "
    f"({n_sig2}/36). The conclusion is unchanged in a data-quality sensitivity analysis with band-limited audio and "
    f"quality filtering ({n_sig3}/36). Selecting one inner-validated encoder layer tends to beat the last layer, "
    "but this was not a pre-registered test. A provenance audit of InfantCry-DBL showed that 107 of 236 Tier-2 clips "
    "labelled as online or volunteer recordings are copies of clips from the Dunstan-derived tier or from CryCeleb2023. "
    "Under naive evaluation, our own preliminary analysis of the uncleaned subset reported macro-F1 ≈ 0.85; the "
    "cleaned, cluster-grouped estimate is 0.69–0.77. We argue that weighting gains reported on such data should be "
    "re-examined, and we release the protocol and code.", absb))
S.append(P("<b>Keywords:</b> infant cry classification; fusion; class imbalance; self-supervised speech "
           "representations; data leakage; negative result; reproducibility", absb))

S.append(P("1. Introduction", h1))
S.append(P(
    "Automatic analysis of infant crying is studied for parental support and neonatal monitoring. Typical systems "
    "combine heterogeneous acoustic descriptors or pretrained encoders with a classifier, and many add a weighting "
    "stage: class weights to counter label imbalance, learned weights over feature groups, or weights over encoder "
    "layers. Small corpora, repeated clips from the same infant, and evaluation designs that let information flow "
    "from test to training data make such gains easy to overstate."))
S.append(P(
    "This paper asks a narrow question: under a leakage-controlled protocol, does any of these weighting schemes "
    "outperform simple baselines on public infant cry data? Our contributions are: (i) a pre-registered comparison "
    "of class, feature-group and layer weighting on three corpora with infant-grouped cross-validation, nested "
    "estimation of every weight and hyperparameter, and corrected statistics; (ii) a clear negative result that is "
    "robust to a data-quality sensitivity analysis; (iii) a provenance audit showing substantial duplication between "
    "tiers and corpora in InfantCry-DBL; and (iv) open code, including a validated F0 tracker for cry signals."))

S.append(P("2. Related work", h1))
S.append(P(
    "Self-supervised speech encoders such as wav2vec 2.0 [1] and HuBERT [2] expose a stack of hidden layers whose "
    "usefulness varies by task. The SUPERB benchmark popularised a learnable softmax-weighted sum of layers as a "
    "standard probing baseline [3]. For imbalanced labels, inverse-frequency and effective-number class weights [4] "
    "are common. Combining per-expert predictions by a trained meta-learner is known as stacking [5]. For comparing "
    "learners evaluated by repeated cross-validation, naive paired tests are anti-conservative because training sets "
    "overlap; the corrected resampled t-test addresses this [6, 7], and Holm's procedure [8] controls the "
    "family-wise error over many comparisons. Public infant cry resources used here are CryCeleb2023 [9], "
    "BABYCRY-UJM-AXA [10] and InfantCry-DBL [11]."))

S.append(P("3. Data", h1))
S.append(P(
    "<b>CryCeleb2023</b> [9] contains cry expirations of 786 newborns recorded either within the first hours of life "
    "(B) or at hospital discharge (D). We use only infants with persistent identifiers (626 infants, at most five "
    "clips per infant and period), because the competition test split anonymises each infant's two periods under "
    "different identifiers, which would defeat grouping. The task is B vs D. <b>BABYCRY-UJM-AXA</b> [10] contains "
    "107,312 cry sequences from about 1,000 full-term newborns in an 81 GB archive; we draw a deterministic subset of "
    "300 infants (100 per delivery method, up to six clips each) by HTTP range requests. We define two tasks before "
    "seeing results: newborn sex, and recording age (lowest vs highest tertile of hours since birth); delivery "
    "method is reported as a supplementary task. <b>InfantCry-DBL</b> [11] labels cries with five Dunstan Baby "
    "Language categories; we use only Tier-2 clips whose metadata source is <i>online_or_volunteer</i>, after the "
    "audit in Section 3.1. Table 1 summarises the tasks."))
rows = [["Task", "Clips", "CV groups", "Class counts"]]
for t, n, g, c in [("CryCeleb (B vs D)", 4954, "626 infants", "B 2815, D 2139"),
                   ("DBL (5 classes)", 103, "86 clusters", "owh 40, eh 26, neh 18, eairh 13, heh 6"),
                   ("UJM sex", 1762, "300 infants", "F 882, M 880"),
                   ("UJM age (tertiles)", 1176, "247 infants", "young 588, old 588"),
                   ("UJM delivery*", 1762, "300 infants", "Assisted 594, C-section 592, Vaginal 576")]:
    rows.append([t, n, g, c])
S.append(tbl(rows, [3.6 * cm, 1.5 * cm, 2.4 * cm, 8.1 * cm],
             "<b>Table 1.</b> Tasks in the primary analysis (* supplementary). CV groups are the units that never "
             "straddle training and test folds."))

S.append(P("3.1 Provenance audit of InfantCry-DBL", h2))
S.append(P(
    "All 1,551 DBL files matched the publisher's SHA-256 hashes. Of the 237 Tier-2 <i>online_or_volunteer</i> "
    "candidates, one was a byte-identical duplicate. We then compared every candidate with all 337 Tier-1 clips "
    "(derived from Dunstan instructional videos) and all 26,093 CryCeleb2023 clips using the cosine similarity of "
    "z-scored acoustic summary vectors. A total of 107 candidates were effectively copies (cosine ≥ 0.999): 41 of "
    "Tier-1 clips and 66 of CryCeleb clips. Another 26 had cosine between 0.95 and 0.999, mostly with Tier-1 clips. "
    "Applying a threshold fixed in advance (0.95), we removed 133 candidates. The remaining 103 clips were grouped "
    "into 86 clusters (cosine ≥ 0.90 within DBL), so that near-duplicates never straddle folds. The metadata field "
    "<i>source_confirmed</i> is false for all 1,214 Tier-2 clips, so the source labels cannot be relied on."))

S.append(P("4. Methods", h1))
S.append(P("4.1 Representations", h2))
S.append(P(
    "<b>Handcrafted features</b> are organised in six groups computed on peak-normalised 16 kHz audio (first 8 s): "
    "MFCC mean and standard deviation (40), delta-MFCC standard deviation (20), spectral descriptors (22), pitch (7), "
    "energy dynamics (5) and log-mel band standard deviations (32). We deliberately avoid mel-band means: MFCC means "
    "are an exact orthonormal DCT of log-mel means, which would make two groups linearly redundant. Pitch comes "
    "from an autocorrelation tracker corrected for the window autocorrelation [12]. It takes the shortest major "
    "local peak (≥ 0.9 × the best) to avoid sub-harmonic errors, refines it by parabolic interpolation, and searches "
    "150–2000 Hz to cover hyperphonated cries. On synthetic signals it is within 2% for 160–1800 Hz tones and "
    "harmonic complexes, and leaves white and low-pass noise unvoiced (unit tests in the repository). Clip duration "
    "is never a model input. <b>Encoder embeddings</b> are the 13 hidden states of wav2vec 2.0 base [1] and HuBERT "
    "base [2], mean-pooled over time, from at most 6 s of input."))
S.append(P("4.2 Experts and combiners", h2))
S.append(P(
    "In every outer training fold we fit one expert per feature group or layer: median imputation, standardisation, "
    "whitened PCA to 64 dimensions (embeddings only, capped at n − 1), and logistic regression with class-balanced "
    "sample weights normalised to sum to n. The inverse regularisation C ∈ {0.01, 0.1, 1} is chosen by inner 3-fold "
    "group-aware cross-validation on macro-F1. All combiners are derived from the same experts and use only the "
    "inner out-of-fold probabilities: <b>equal</b> (mean of probabilities); <b>best single</b> (hard selection of "
    "the expert with the highest inner macro-F1); <b>softmax-τ</b> (weights softmax(τ·F1<sub>g</sub>) with "
    "τ ∈ {0, 1, 3, 10, 30, 100, 300, 1000} tuned on inner fused macro-F1); and <b>stacking</b> (multinomial logistic "
    "regression on all experts' out-of-fold log-probabilities, which learns class-specific expert weights within one "
    "model [5]). Baselines are the last encoder layer, a SUPERB-style learnable weighted sum of layers with a linear "
    "head [3] (weight decay chosen on an inner split), feature concatenation without, with balanced and with "
    "effective-number class weights [4], and a duration-only classifier that measures a known shortcut."))

S.append(P("5. Evaluation protocol", h1))
S.append(P(
    "Every task–representation pair is evaluated by stratified group 5-fold cross-validation repeated with three "
    "seeds (15 outer folds), with an assertion that no group appears in both training and test data. The primary "
    "metric is macro-F1 per outer fold. The protocol and a family of 36 primary hypotheses were committed to the "
    "repository before any result of this protocol existed: H1 stacking vs equal and H2 stacking vs best single "
    "(12 runs each); H3 stacking vs SUPERB (8 embedding runs); and H4 balanced vs unweighted concatenation "
    "(4 handcrafted runs). Each is tested with the corrected resampled t-test (n<sub>test</sub>/n<sub>train</sub> = "
    "1/4, 14 degrees of freedom) [6, 7], with Holm correction over all 36 tests [8]. A difference is declared only if "
    "the Holm-adjusted p &lt; 0.05 and the 95% confidence interval excludes zero. Two deviations are recorded in "
    "the protocol: the PCA cap for tiny folds, and the small size of the cleaned DBL subset."))

S.append(P("6. Results", h1))
methods = [("equal", "Equal"), ("best_single", "Best single"), ("softmax_tau", "Softmax-τ"),
           ("stacking", "Stack."), ("superb_wsum", "SUPERB"), ("last_layer", "Last layer"),
           ("concat_balanced", "Concat (bal.)"), ("duration_only", "Duration")]
piv = s2.pivot_table(index=["task", "rep"], columns="method", values="macro_f1")
order = [(t, r) for t in ["cryceleb", "infantcry_dbl", "ujm_sex", "ujm_age", "ujm_axa"]
         for r in ["hand", "w2v2", "hubert"] if (t, r) in piv.index]
rows = [["Task", "Features"] + [m[1] for m in methods]]
for t, r in order:
    v = piv.loc[(t, r)]
    rows.append([TASK[t], REP[r]] + ["–" if pd.isna(v.get(m)) else f"{v[m]:.3f}" for m, _ in methods])
S.append(tbl(rows, [2.6 * cm, 1.9 * cm] + [1.48 * cm] * 8,
             "<b>Table 2.</b> Mean macro-F1 over 15 outer folds (primary analysis). Chance: 0.50 for binary tasks, "
             "0.20 for DBL, 0.33 for delivery. Fold standard deviations: 0.01–0.05 (CryCeleb, UJM), 0.08–0.16 (DBL)."))
S.append(P(
    f"<b>Primary hypotheses.</b> None of the 36 pre-registered comparisons shows evidence of a difference "
    f"({n_sig2}/36; Table 3). Stacking does not beat equal averaging (H1), selection of the best single expert "
    "(H2) or the SUPERB weighted sum (H3), and class weighting does not change concatenation results (H4). "
    "Confidence intervals are narrow for CryCeleb and UJM (half-widths 0.003–0.06), so effects larger than a few points are excluded "
    "there. For DBL they are wide (half-widths 0.08–0.21), so DBL is uninformative either way. Before "
    "correction, 3 of the 36 intervals exclude zero (stacking +0.015 over best single on handcrafted CryCeleb; "
    "+0.043 and +0.023 over SUPERB on wav2vec2 UJM sex and HuBERT CryCeleb; unadjusted p 0.03–0.05). About two "
    "such results are expected by chance among 36 tests, and none survives Holm correction."))
cols = ["H1", "H2", "H3", "H4"]
rows = [["Task", "Features"] + [f"{h}: Δ [95% CI]" for h in cols]]
for t, r in [(t, r) for t in ["cryceleb", "infantcry_dbl", "ujm_sex", "ujm_age"] for r in ["hand", "w2v2", "hubert"]]:
    row = [TASK[t], REP[r]]
    for h in cols:
        x = p2[(p2.hypothesis == h) & (p2.task == t) & (p2.rep == r)]
        row.append("–" if x.empty else f"{x['mean'].iat[0]:+.3f} [{x.ci_low.iat[0]:+.3f}, {x.ci_high.iat[0]:+.3f}]")
    rows.append(row)
S.append(tbl(rows, [2.6 * cm, 1.9 * cm] + [2.85 * cm] * 4,
             "<b>Table 3.</b> Primary comparisons: mean macro-F1 difference and corrected 95% CI. H1 stacking − "
             "equal; H2 stacking − best single; H3 stacking − SUPERB; H4 balanced − unweighted concatenation. All "
             "Holm-adjusted p-values are 1.00."))
S.append(P(
    f"<b>Exploratory observations</b> (unadjusted, not pre-registered). Selecting one inner-validated encoder layer "
    f"beat the last layer in {int((e2_bl.ci_low > 0).sum())} of {len(e2_bl)} embedding runs. The selected layer was "
    "usually one of the earliest (L0–L1), whereas the SUPERB weights peaked in middle layers (L3–L8); both reached "
    "similar scores. Tuned softmax weights were far from uniform (largest weight 0.22–0.71 on average), so the null "
    "result does not come from degenerate weights. All fusion methods exceeded the duration-only shortcut, but on "
    "CryCeleb duration alone reached 0.55 macro-F1 against a best of 0.64, which warns that B vs D labels partly "
    "reflect recording circumstances."))

S.append(P("6.1 Data-quality sensitivity analysis", h2))
S.append(P(
    "After the primary analysis, a quality scan found a sample-rate/label association in DBL (χ<super>2</super> "
    "p = 0.0001), clipping in DBL and low-SNR clips in UJM. We therefore fixed sensitivity criteria in advance: "
    "band-limit all audio to 0–4 kHz, and drop clips with more than 0.1% clipped samples, more than 50% silent "
    "frames, or (UJM) published SNR below 10 dB. This removed 497 clips (CryCeleb 101, DBL 9, UJM 387). The whole "
    f"pipeline was re-run unchanged. Again none of the 36 primary comparisons showed evidence ({n_sig3}/36). Best "
    "scores moved by at most 0.02 on CryCeleb and UJM, while DBL dropped by 0.02–0.10 (Table 4). A classifier using "
    "only the native sample rate was at chance on DBL (macro-F1 0.197), so the DBL drop cannot be attributed to a "
    "simple sample-rate shortcut. It may reflect lost high-frequency harmonics, bandwidth artefacts, or the smaller "
    "sample, and these cannot be separated with the available data."))
keep = ["equal", "best_single", "softmax_tau", "stacking", "superb_wsum", "last_layer", "concat_balanced"]
best = lambda d: d[d.method.isin(keep)].groupby(["task", "rep"]).macro_f1.max()  # noqa: E731
cmp_ = pd.concat([best(s2).rename("v2"), best(s3).rename("v3")], axis=1)
rows = [["Task", "Features", "Best macro-F1, primary", "Best macro-F1, cleaned", "Change"]]
for (t, r) in order:
    if (t, r) in cmp_.index:
        a, b = cmp_.loc[(t, r)]
        rows.append([TASK[t], REP[r], f"{a:.3f}", f"{b:.3f}", f"{b - a:+.3f}"])
S.append(tbl(rows, [3.0 * cm, 2.4 * cm, 3.6 * cm, 3.6 * cm, 2.2 * cm],
             "<b>Table 4.</b> Sensitivity analysis: best method per task before and after band-limiting and quality "
             "filtering."))

S.append(P("7. Discussion", h1))
S.append(P(
    "Once weights are estimated without access to test folds, splits respect infant identity, and comparisons are "
    "corrected for overlapping training sets and multiplicity, none of the weighting schemes adds measurable value "
    "over averaging calibrated per-group experts or picking one good layer. We see three plausible reasons. First, "
    "the per-group experts are strongly correlated, so reweighting them changes little. Second, inner validation "
    "sets are small, so data-driven weights are noisy estimates of small true differences. Third, the tasks with "
    "enough data to detect small effects (CryCeleb, UJM) carry weak signal overall (best macro-F1 0.56–0.64)."))
S.append(P(
    "The DBL audit is a cautionary result in its own right. Nearly half of the clips labelled as independent online or "
    "volunteer recordings were copies of clips from another tier or another public corpus. Studies that combine "
    "Dunstan-derived material with other cry corpora, or that split such data at clip level, can therefore leak "
    "identical audio across training and test sets. Our own preliminary analysis on the uncleaned subset with "
    "per-clip grouping reported macro-F1 ≈ 0.85, compared with 0.69–0.77 after cleaning and cluster grouping. "
    "Earlier stages of this project also showed how optimistic statistics can mislead. A naive Wilcoxon test over "
    "repeated folds declared 19 of 78 comparisons significant; after correction and Holm adjustment, one remained."))
S.append(P(
    "<b>Limitations.</b> The cleaned DBL subset is small (103 clips), and its overlap with other Dunstan-derived "
    "collections beyond Tier 1 could not be checked. UJM is a 300-infant subset. CryCeleb B/D labels are confounded "
    "with recording circumstances. We study linear experts and mean-pooled embeddings; fine-tuned encoders might "
    "behave differently. Task definitions for UJM were changed once during exploratory work before the protocol was "
    "frozen, and this is documented in the repository history."))

S.append(P("8. Conclusion", h1))
S.append(P(
    "Under a leakage-controlled, pre-registered evaluation on three public corpora, class weighting, feature-group "
    "weighting and layer weighting (including stacking and a SUPERB-style weighted sum) did not outperform equal "
    "averaging or inner-validated selection of a single expert, and this held after data-quality filtering. Public "
    "cry corpora should be audited for cross-tier and cross-corpus duplication before reporting weighting gains. "
    "Infant-grouped, nested evaluation with corrected statistics should be the default."))

S.append(P("Data and code availability", h1))
S.append(P(
    "All corpora are public (DOIs in the references; CryCeleb2023 requires accepting its non-commercial licence). "
    "Code, the frozen protocol (PROTOCOL.md), per-fold results, predictions, the DBL cleaning manifest and the "
    "quality manifest are available in the project repository [repository URL to be added]."))
S.append(P("Declarations", h1))
S.append(P("Funding: [to be completed]. Competing interests: [to be completed]. Ethics: only public, de-identified "
           "corpora were used; no new recordings were collected. Author contributions: [to be completed]. "
           "Use of AI tools: [to be completed by the authors, as required by the journal].", body))

S.append(P("References", h1))
for r in [
    "[1] Baevski A, Zhou Y, Mohamed A, Auli M (2020) wav2vec 2.0: A framework for self-supervised learning of "
    "speech representations. Advances in Neural Information Processing Systems 33.",
    "[2] Hsu W-N, Bolte B, Tsai Y-HH, Lakhotia K, Salakhutdinov R, Mohamed A (2021) HuBERT: Self-supervised speech "
    "representation learning by masked prediction of hidden units. IEEE/ACM Trans Audio Speech Lang Process "
    "29:3451–3460.",
    "[3] Yang S-W et al. (2021) SUPERB: Speech processing Universal PERformance Benchmark. Proc. Interspeech 2021.",
    "[4] Cui Y, Jia M, Lin T-Y, Song Y, Belongie S (2019) Class-balanced loss based on effective number of samples. "
    "Proc. IEEE/CVF CVPR 2019.",
    "[5] Wolpert DH (1992) Stacked generalization. Neural Networks 5(2):241–259.",
    "[6] Nadeau C, Bengio Y (2003) Inference for the generalization error. Machine Learning 52:239–281.",
    "[7] Bouckaert RR, Frank E (2004) Evaluating the replicability of significance tests for comparing learning "
    "algorithms. Proc. PAKDD 2004, LNCS 3056.",
    "[8] Holm S (1979) A simple sequentially rejective multiple test procedure. Scand J Stat 6(2):65–70.",
    "[9] Budaghyan D et al. (2023) CryCeleb: A speaker verification dataset based on infant cry sounds. "
    "arXiv:2305.00969. Dataset: huggingface.co/datasets/Ubenwa/CryCeleb2023.",
    "[10] BABYCRY-UJM-AXA: A sound library of cries from 1,000 full-term babies aged between 1 and 3 days (2026). "
    "Zenodo. doi:10.5281/zenodo.19205929. [author list to be completed from the record]",
    "[11] Tawfik M. InfantCry-DBL: A two-tier annotated corpus of infant cries labelled with Dunstan Baby Language "
    "categories, version 2. Mendeley Data. doi:10.17632/x493z8nmwc.2. Associated article: IEEE Access 14 (2026), "
    "doi:10.1109/ACCESS.2026.3733522.",
    "[12] Boersma P (1993) Accurate short-term analysis of the fundamental frequency and the harmonics-to-noise "
    "ratio of a sampled sound. Proc. Institute of Phonetic Sciences, University of Amsterdam 17:97–110."]:
    S.append(P(r, ref))
S.append(Spacer(1, 6))
S.append(P("Note for the authors: verify every reference against the publisher's record before submission (in "
           "particular the author list of [9] and the dataset record [10]), complete the bracketed fields, and "
           "add the relationship to Paper 1 if required by the journal's overlap policy.", note))

doc = SimpleDocTemplate("reports/paper4_manuscript_draft.pdf", pagesize=A4, leftMargin=2.2 * cm,
                        rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Does Weighting Help Infant Cry Classification? (draft)", author="[Authors]")
doc.build(S, onFirstPage=footer, onLaterPages=footer)
print("written reports/paper4_manuscript_draft.pdf")
