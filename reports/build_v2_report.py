"""Build the v2 follow-up report (fixes + rerun results) as a PDF.
Run from the repo root after scripts/analyze_v2.py:  python3 reports/build_v2_report.py"""
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", F + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")

INK, GRY, LINE, FILL = (colors.HexColor(c) for c in ("#1f2328", "#667085", "#d0d5dd", "#f2f4f7"))
RED, AMB, GRN = (colors.HexColor(c) for c in ("#b42318", "#b54708", "#067647"))
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="DV", fontSize=9.5, leading=13.5, textColor=INK,
                      spaceAfter=5)
small = ParagraphStyle("s", parent=body, fontSize=8, leading=10.5, spaceAfter=0)
smallb = ParagraphStyle("sb", parent=small, fontName="DVB")
h1 = ParagraphStyle("h1", parent=body, fontName="DVB", fontSize=17, leading=21, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=body, fontName="DVB", fontSize=12.5, leading=16, spaceBefore=12, spaceAfter=5)
sub = ParagraphStyle("sub", parent=body, textColor=GRY, fontSize=9)
box = ParagraphStyle("v", parent=body, fontName="DVB", fontSize=10.3, leading=14.5, textColor=RED,
                     borderColor=RED, borderWidth=1, borderPadding=7, spaceBefore=6, spaceAfter=12)
bullet = ParagraphStyle("bl", parent=body, leftIndent=12, bulletIndent=2, spaceAfter=3)
STAT = {"SELESAI": GRN, "SEBAGIAN": AMB, "TERBUKA": RED}


def P(t, s=body):
    return Paragraph(t, s)


def table(rows, widths, status_col=None):
    data = [[Paragraph(str(c), smallb if i == 0 else small) for c in r] for i, r in enumerate(rows)]
    st = [("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("BACKGROUND", (0, 0), (-1, 0), FILL), ("LEFTPADDING", (0, 0), (-1, -1), 4),
          ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if status_col is not None:
        for i, r in enumerate(rows[1:], start=1):
            c = STAT.get(r[status_col])
            if c:
                data[i][status_col] = Paragraph(f'<font color="{c.hexval()}"><b>{r[status_col]}</b></font>', small)
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle(st))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(GRY)
    canvas.drawString(2 * cm, 1.2 * cm, "Laporan perbaikan dan hasil v2 · Paper 4 · protokol v2 dibekukan di commit 27ae932")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"hal. {doc.page}")
    canvas.restoreState()


prim = pd.read_csv("results/v2/primary_tests.csv")
expl = pd.read_csv("results/v2/exploratory_tests.csv")
summ = pd.read_csv("results/v2/summary.csv")

S = [P("Laporan Perbaikan dan Hasil v2", h1),
     P("Tindak lanjut laporan supervisi kritis (reports/supervisor_review.pdf) · Paper 4, klasifikasi tangis bayi", sub),
     P("Semua temuan FATAL dan MAYOR sudah ditangani di kode, lalu seluruh eksperimen dijalankan ulang di bawah "
       "protokol v2 (PROTOCOL.md). Protokol itu di-commit (27ae932) SEBELUM hasil v2 pertama ada. Kode eksperimen "
       "identik di semua commit yang tercatat pada file hasil (diverifikasi dengan git diff).", sub)]
n_ev = int((prim.verdict != "no evidence").sum())
S.append(P(f"HASIL UTAMA: {n_ev} dari {len(prim)} hipotesis primer menunjukkan bukti. Setelah data dibersihkan, fitur "
           "diperbaiki, hyperparameter dituning, dan statistik dikoreksi, tidak ada metode pembobotan atau fusi "
           "(termasuk metode usulan v2, stacking) yang terbukti lebih baik dari rata-rata sederhana, pemilihan satu "
           "grup/lapisan terbaik, atau baseline SUPERB. Pembobotan kelas juga tidak terbukti membantu. Klaim metode "
           "untuk Paper 4 tidak didukung data.", box))

S.append(P("1. Status setiap temuan", h2))
S.append(table([
    ["Kode", "Temuan", "Tindakan", "Bukti setelah perbaikan", "Status"],
    ["S1", "Klaim metode tak didukung", "Keluarga hipotesis primer ditetapkan di muka (36 uji)",
     f"{n_ev}/36 bukti; klaim metode dinyatakan tidak didukung", "SELESAI"],
    ["S2", "Wilcoxon pada fold dependen", "stats.py: Nadeau–Bengio + CI 95% + Holm", "Unit test: varians NB &gt; naif; Holm sesuai acuan", "SELESAI"],
    ["D1", "Duplikat DBL", "prepare_dbl.py: hapus identik byte, cluster cos ≥ 0,90 jadi satu grup",
     "1 duplikat dihapus; 103 klip dalam 86 grup", "SELESAI"],
    ["M1", "Bobot τ = 10 nyaris seragam", "τ dituning di CV dalam (0–1000)",
     "τ terpilih (median) 10–300; bobot maks rata-rata 0,22–0,71 (dulu 0,14)", "SELESAI"],
    ["D2", "Shortcut durasi CryCeleb", "Durasi dihapus dari fitur; baseline durasi-saja di semua tugas",
     "Semua model mengungguli durasi-saja (CryCeleb +0,05…+0,09). Confound kondisi rekaman tetap tak terukur",
     "SEBAGIAN"],
    ["D3", "Sumber DBL tak terverifikasi", "sha256 + pencocokan silang ke Tier-1 Dunstan dan 26.093 klip CryCeleb",
     "133 klip dibuang (107 salinan identik). Tumpang tindih dengan berkas Paper 1 belum bisa dicek tanpa data Paper 1",
     "SEBAGIAN"],
    ["F1", "MFCC-mean = DCT(mel-mean)", "Grup mel diganti std log-mel", "R² MFCC-mean dari grup mel: 1,000 → 0,300", "SELESAI"],
    ["F2", "Estimator F0 salah", "ACF terkoreksi jendela, puncak lokal, aturan puncak mayor pertama, interpolasi, 150–2000 Hz",
     "18 unit test lolos; 1.200 Hz → 1.200,3 Hz (dulu 400); derau low-pass 1% bersuara", "SELESAI"],
    ["M2", "Fusi classwise tak koheren", "Diganti stacking (LR multinomial atas log-prob OOF)", "Unit test combiner lolos", "SELESAI"],
    ["M3", "Bobot effective ubah regularisasi", "Semua skema dinormalisasi Σw = n", "Unit test: Σw = n untuk 3 skema", "SELESAI"],
    ["M4", "Baseline lemah / C tak dituning", "Baseline SUPERB, best-single argmax keras, C ∈ {0,01; 0,1; 1} dituning untuk semua model, PCA whitened",
     "Kapasitas fusi vs model tunggal tetap berbeda (melekat pada desain)", "SEBAGIAN"],
    ["E1", "Protokol tak seragam", "5 fold × 3 seed untuk semua 13 run", "15 fold per metode per run (dicek)", "SELESAI"],
    ["E2", "Forking paths", "PROTOCOL.md dibekukan sebelum hasil; deviasi dicatat", "2 deviasi tercatat (batas PCA, ukuran DBL)", "SELESAI"],
], [1.2 * cm, 2.9 * cm, 4.5 * cm, 6.2 * cm, 2.2 * cm], status_col=4))

S.append(P("2. Temuan baru dari perbaikan: kontaminasi InfantCry-DBL", h2))
S.append(P("Pencocokan silang menemukan bahwa dari 236 klip Tier-2 berlabel <i>online_or_volunteer</i>, <b>107 adalah "
           "salinan</b> (kemiripan fitur ≥ 0,999): 41 salinan klip Dunstan Tier-1 dan 66 salinan klip CryCeleb. Sebanyak "
           "26 klip lain sangat mirip (0,95–0,999), kebanyakan dengan klip Dunstan. Konsekuensinya:", body))
S += [Paragraph(t, bullet, bulletText="•") for t in [
    "Hasil DBL versi v1 (macro-F1 ≈ 0,85) tidak sah: sebagian besar klipnya adalah data Dunstan, sumber yang sama "
    "dengan Paper 1, dan sebagian lagi data CryCeleb yang juga dipakai sebagai dataset lain di Paper 4.",
    "Metadata sumber dataset publik ini tidak bisa dipercaya. Temuan ini sendiri layak dilaporkan, misalnya sebagai "
    "catatan kualitas data.",
    "DBL bersih tinggal 103 klip (kelas heh: 6 klip), sehingga semua hasil DBL bertenaga statistik rendah "
    "(CI selisih ±0,1–0,2)."]]

S.append(PageBreak())
S.append(P("3. Hipotesis primer (Nadeau–Bengio, koreksi Holm atas 36 uji)", h2))
S.append(P("H1: stacking − equal · H2: stacking − best_single · H3: stacking − SUPERB · H4: concat balanced − concat "
           "tanpa bobot. Nilai = rata-rata selisih macro-F1 per fold dengan CI 95%.", body))
rows = [["Hipotesis", "Representasi", "Tugas", "Selisih", "CI 95%", "p", "p Holm", "Vonis"]]
for _, r in prim.iterrows():
    rows.append([r.hypothesis, r.rep, r.task, f"{r['mean']:+.3f}", f"[{r.ci_low:+.3f}, {r.ci_high:+.3f}]",
                 f"{r.p:.3f}", f"{r.p_holm:.2f}", "tidak ada bukti" if r.verdict == "no evidence" else r.verdict])
S.append(table(rows, [1.6 * cm, 2.0 * cm, 2.5 * cm, 1.6 * cm, 3.2 * cm, 1.4 * cm, 1.5 * cm, 3.2 * cm]))

S.append(PageBreak())
S.append(P("4. Macro-F1 per metode (rata-rata 15 fold)", h2))
methods = ["equal", "best_single", "softmax_tau", "stacking", "superb_wsum", "last_layer", "concat_none",
           "concat_balanced", "duration_only"]
piv = summ.pivot_table(index=["task", "rep"], columns="method", values="macro_f1")
rows = [["Tugas", "Rep."] + ["equal", "best", "softmax τ", "stacking", "SUPERB", "last", "concat", "concat bal.", "durasi"]]
for (task, rep), r in piv.iterrows():
    rows.append([task, rep] + ["–" if pd.isna(r.get(m)) else f"{r[m]:.3f}" for m in methods])
S.append(table(rows, [2.4 * cm, 1.3 * cm] + [1.48 * cm] * 9))
S.append(Spacer(1, 6))
S.append(P("Acak: CryCeleb, UJM-sex, UJM-age = 0,50; DBL (5 kelas) = 0,20; UJM-delivery (3 kelas) = 0,33.", sub))

S.append(P("5. Analisis eksploratif (tanpa koreksi, hanya indikatif)", h2))
e2 = expl[expl.hypothesis == "E2"]
e4 = expl[expl.hypothesis == "E4"]
S += [Paragraph(t, bullet, bulletText="•") for t in [
    f"<b>Satu lapisan terbaik (via CV dalam) vs lapisan terakhir:</b> lebih baik di {int((e2.ci_low > 0).sum())} dari "
    f"{len(e2)} run (CI tidak memuat 0, tanpa koreksi). Lapisan awal (L00–L01) paling sering terpilih. Ini satu-satunya "
    "pola yang konsisten, tapi bukan hipotesis primer.",
    "<b>Bobot τ sudah tidak seragam lagi</b> (bobot maks 0,22–0,71), tapi tetap tidak lebih baik dari rata-rata "
    "sederhana. Jadi kegagalan metode bukan artefak τ = 10 seperti di v1.",
    f"<b>Shortcut durasi:</b> metode stacking mengungguli durasi-saja di {int((e4.ci_low > 0).sum())} dari {len(e4)} "
    "run. Tidak ada tugas yang memenuhi kriteria 'didominasi shortcut' (selisih &lt; 0,02), tetapi di CryCeleb durasi "
    "saja sudah 0,55 dari maksimum 0,64.",
    "<b>Bobot lapisan SUPERB</b> terkonsentrasi di lapisan tengah (argmax L03–L08), berbeda dari pilihan best-single "
    "(L00–L01); keduanya berkinerja serupa."]]

S.append(P("6. Yang masih terbuka", h2))
S += [Paragraph(t, bullet, bulletText="•") for t in [
    "Tumpang tindih dengan berkas Paper 1 hanya bisa dipastikan jika data Paper 1 (Donate-a-Cry, Baby Chillanto, "
    "Dunstan/Kaggle) tersedia untuk pencocokan silang.",
    "Confound kondisi rekaman pada CryCeleb (lahir vs pulang) tidak bisa dikendalikan dengan metadata yang ada.",
    "DBL terlalu kecil setelah dibersihkan; UJM hanya subset 300 bayi; embedding memakai 6 s, fitur 8 s.",
    "Temuan minor yang belum disentuh: normalisasi puncak tetap dipakai (didokumentasikan)."]]

S.append(P("7. Vonis supervisor (v2)", h2))
S.append(P("Perbaikan sudah benar dan menyeluruh, tapi justru membuktikan bahwa <b>tidak ada efek metode yang bisa "
           "diklaim</b>. Paper 4 tidak bisa ditulis sebagai paper metode. Dua arah yang jujur dan masih layak:", body))
S += [Paragraph(t, bullet, bulletText="•") for t in [
    "<b>Paper hasil negatif / benchmark terkontrol kebocoran:</b> 'pembobotan kelas, grup fitur, dan lapisan tidak "
    "mengungguli rata-rata sederhana pada tiga korpus tangis bayi di bawah evaluasi yang benar'. Kontribusinya protokol, "
    "kode terbuka, dan bukti negatif yang kuat.",
    "<b>Catatan kualitas data:</b> kontaminasi InfantCry-DBL (107 dari 236 klip berlabel online/volunteer adalah salinan "
    "Dunstan/CryCeleb). Ini temuan yang paling orisinal dari seluruh pekerjaan ini.",
    "Klaim lama yang harus dicabut: macro-F1 DBL ≈ 0,85, 'metode usulan lebih baik', dan 'multi-lapisan signifikan "
    "lebih baik dari lapisan terakhir'."]]

doc = SimpleDocTemplate("reports/v2_fixes_and_results.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=2 * cm, title="Laporan Perbaikan dan Hasil v2",
                        author="Audit kode microasa")
doc.build(S, onFirstPage=footer, onLaterPages=footer)
print("written reports/v2_fixes_and_results.pdf")
