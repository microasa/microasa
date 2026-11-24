"""Build the critical supervisor review of the Paper 4 code base as a PDF.

Run from the repo root:  python3 reports/build_supervisor_review.py
Numbers quoted in the report were measured in the audit session of 24 Nov 2026;
the significance table is read from reports/audit_significance.csv.
"""
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", F + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")

ss = getSampleStyleSheet()
INK = colors.HexColor("#1f2328")
RED = colors.HexColor("#b42318")
AMB = colors.HexColor("#b54708")
GRN = colors.HexColor("#067647")
GRY = colors.HexColor("#667085")
LINE = colors.HexColor("#d0d5dd")
FILL = colors.HexColor("#f2f4f7")

body = ParagraphStyle("b", parent=ss["Normal"], fontName="DV", fontSize=9.5, leading=13.5,
                      textColor=INK, alignment=TA_LEFT, spaceAfter=5)
small = ParagraphStyle("s", parent=body, fontSize=8.2, leading=11, spaceAfter=0)
smallb = ParagraphStyle("sb", parent=small, fontName="DVB")
h1 = ParagraphStyle("h1", parent=body, fontName="DVB", fontSize=17, leading=21, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=body, fontName="DVB", fontSize=12.5, leading=16,
                    spaceBefore=12, spaceAfter=5)
h3 = ParagraphStyle("h3", parent=body, fontName="DVB", fontSize=10.2, leading=13.5,
                    spaceBefore=7, spaceAfter=3)
sub = ParagraphStyle("sub", parent=body, textColor=GRY, fontSize=9)
mono = ParagraphStyle("m", parent=body, fontName="DVM", fontSize=8.2, leading=11,
                      backColor=FILL, borderPadding=4, spaceBefore=3, spaceAfter=7)
verdict = ParagraphStyle("v", parent=body, fontName="DVB", fontSize=10.5, leading=14.5,
                         textColor=RED, borderColor=RED, borderWidth=1, borderPadding=7,
                         spaceBefore=6, spaceAfter=12)
bullet = ParagraphStyle("bl", parent=body, leftIndent=12, bulletIndent=2, spaceAfter=3)

SEV = {"FATAL": RED, "MAYOR": AMB, "MINOR": GRY, "OK": GRN}


def P(t, s=body):
    return Paragraph(t, s)


def bl(items):
    return [Paragraph(t, bullet, bulletText="•") for t in items]


def table(rows, widths, header=True, sev_col=None, font=small):
    data = [[c if not isinstance(c, str) else Paragraph(c, smallb if (header and i == 0) else font)
             for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), FILL))
    if sev_col is not None:
        for i, r in enumerate(rows[1:], start=1):
            c = SEV.get(r[sev_col])
            if c:
                st.append(("TEXTCOLOR", (sev_col, i), (sev_col, i), c))
                data[i][sev_col] = Paragraph(f'<font color="{c.hexval()}"><b>{r[sev_col]}</b></font>', small)
    t.setStyle(TableStyle(st))
    return t


def finding(code, sev, title, where, what, evidence, fix):
    c = SEV[sev].hexval()
    head = P(f'<font color="{c}"><b>[{code} · {sev}]</b></font> <b>{title}</b>', h3)
    rows = [["Lokasi", where], ["Masalah", what], ["Bukti", evidence], ["Perbaikan wajib", fix]]
    t = Table([[Paragraph(a, smallb), Paragraph(b, small)] for a, b in rows],
              colWidths=[3.0 * cm, 14.0 * cm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (0, -1), FILL),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return KeepTogether([head, t, Spacer(1, 4)])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(GRY)
    canvas.drawString(2 * cm, 1.2 * cm, "Laporan supervisi kritis · Paper 4 (infant cry weighting) · repo microasa, "
                      "branch claude/repo-harnes-connection-rbg5g8")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"hal. {doc.page}")
    canvas.restoreState()


S = []
S += [P("Laporan Supervisi Kritis", h1),
      P("Paper 4 — pembobotan kelas, grup fitur, dan lapisan embedding untuk klasifikasi tangis bayi", sub),
      P("Cakupan: seluruh kode di <font face='DVM'>src/infantcry/</font> dan <font face='DVM'>scripts/</font> "
        "(637 baris), semua hasil di <font face='DVM'>results/</font>, serta matematika fitur, metode, dan uji "
        "statistik. Tanggal audit: 24 November 2026. Setiap temuan di bawah diverifikasi dengan eksekusi kode atau "
        "uji numerik, bukan dugaan.", sub)]

S.append(P("VONIS: Belum layak dikirim ke jurnal mana pun. Metode yang diusulkan tidak terbukti lebih baik dari "
           "pembanding mana pun setelah uji statistik yang benar. Dari 78 perbandingan, hanya 1 yang bertahan "
           "koreksi Nadeau–Bengio + Holm, dan itu efek pembobotan KELAS, bukan kontribusi metode. Ada kebocoran "
           "data terukur di DBL, shortcut durasi di CryCeleb, fitur yang redundan secara matematis, dan estimator "
           "F0 yang salah dengan keyakinan tinggi.", verdict))

S.append(P("1. Ringkasan temuan", h2))
S.append(table([
    ["Kode", "Tingkat", "Temuan", "Lokasi"],
    ["S1", "FATAL", "Klaim metode tidak didukung statistik: 1/78 perbandingan lolos NB + Holm, dan bukan untuk "
                    "pembobotan grup/lapisan", "scripts/run_*experiments.py"],
    ["S2", "FATAL", "Wilcoxon pada fold CV berulang yang saling bergantung; p-value terlalu optimistis", "run_*.py:31/35"],
    ["D1", "FATAL", "Duplikat dan near-duplicate di DBL; skor usulan turun 0,852 → 0,818 saat dikelompokkan",
     "data.py:91"],
    ["M1", "FATAL", "Bobot 'usulan' (τ = 10) nyaris seragam: secara praktis = fusi sama rata", "weighting.py:108-110"],
    ["D2", "MAYOR", "CryCeleb: durasi saja memberi macro-F1 0,550 (acak 0,50); label B/D tercampur kondisi rekaman",
     "data.py:16-33"],
    ["D3", "MAYOR", "Subset DBL 'bersih' bergantung pada label sumber yang 100% tidak terkonfirmasi", "data.py:86"],
    ["F1", "MAYOR", "MFCC-mean = DCT(mel-mean) persis (R² = 1): grup fitur tidak independen", "features.py:42-43, 69-74"],
    ["F2", "MAYOR", "Estimator F0: 1.200 Hz terbaca 400 Hz (keyakinan 0,99); derau terbaca 1.000 Hz", "features.py:19-32"],
    ["M2", "MAYOR", "Fusi classwise tidak koheren secara probabilistik (campuran berbeda per kelas)", "weighting.py:110, 116-119"],
    ["M3", "MAYOR", "Bobot 'effective' mengubah regularisasi (total bobot 0,64 n)", "weighting.py:28-30"],
    ["M4", "MAYOR", "Baseline standar (learnable weighted-sum ala SUPERB) tidak ada; kapasitas model tidak setara",
     "run_embedding_experiments.py:19-27"],
    ["E1", "MAYOR", "Protokol tidak seragam (3/2/1 seed); CryCeleb 1 seed tak bisa signifikan dengan Wilcoxon",
     "run_emb_exp.sh, evaluate.py:49"],
    ["E2", "MAYOR", "Keputusan desain diubah setelah melihat hasil (forking paths) tanpa pra-registrasi", "riwayat commit"],
    ["F3", "MINOR", "Rata-rata delta-MFCC ≈ 0 (20 fitur nyaris tanpa informasi)", "features.py:44, 70"],
    ["F4", "MINOR", "Mask voicing bergeser 32 ms terhadap frame F0", "features.py:56-59"],
    ["F5", "MINOR", "Normalisasi puncak, durasi sebagai fitur, nan_to_num membungkam error, 8 s vs 6 s", "features.py, extract_embeddings.py"],
    ["R1", "MINOR", "Tanpa test, tanpa pin versi, tanpa README, hasil tanpa jejak commit; cek HTTP 206 & sha256 tidak ada",
     "repo"],
], [1.3 * cm, 1.9 * cm, 9.4 * cm, 4.4 * cm], sev_col=1))

S.append(PageBreak())
S.append(P("2. Statistik: inti masalahnya", h2))
S.append(finding(
    "S2", "FATAL", "Uji Wilcoxon diterapkan pada fold CV berulang",
    "scripts/run_experiments.py:31, scripts/run_embedding_experiments.py:35",
    "Setiap pasangan (seed, fold) diperlakukan sebagai sampel independen. Padahal set latih antar-fold tumpang tindih "
    "75%, dan tiga repetisi memakai data yang sama. Varians selisih jadi terlalu kecil dan p-value terlalu optimistis "
    "(Nadeau &amp; Bengio, 2003; Bouckaert &amp; Frank, 2004). Juga tidak ada koreksi perbandingan berganda.",
    "Dengan n = 5 pasangan (CryCeleb, 1 seed), p dua-sisi terkecil yang MUNGKIN adalah 0,0625. Uji ini secara "
    "matematis tidak bisa signifikan. Untuk n = 10: 0,0020; n = 15: 0,00006.",
    "Pakai corrected resampled t-test: t = d̄ / √((1/k + n<sub>uji</sub>/n<sub>latih</sub>) · s²), df = k − 1, "
    "dengan n<sub>uji</sub>/n<sub>latih</sub> = 1/4 untuk 5-fold. Lalu koreksi Holm atas semua perbandingan. "
    "Laporkan interval kepercayaan, bukan hanya p."))

st = pd.read_csv("reports/audit_significance.csv")
S.append(P("Hasil hitung ulang (macro-F1, usulan dikurangi pembanding; d̄ positif = usulan lebih baik). "
           "Ringkasan seluruh 78 perbandingan:", body))
S.append(table([
    ["Kriteria", "Jumlah signifikan (p < 0,05)"],
    ["Wilcoxon apa adanya (yang dipakai di laporan sebelumnya)", f"{int((st.p_wilcoxon < .05).sum())} / {len(st)}"],
    ["Nadeau–Bengio corrected t-test", f"{int((st.p_nb < .05).sum())} / {len(st)}"],
    ["Nadeau–Bengio + koreksi Holm", f"{int((st.p_nb_holm < .05).sum())} / {len(st)}"],
], [11 * cm, 6 * cm]))
S.append(Spacer(1, 6))

key = st[st.baseline.isin(["last_layer+balanced", "mean_layers+balanced", "best_layer(inner-CV)+balanced",
                           "layers_equal+balanced", "concat+balanced", "fusion_equal+balanced", "fusion_equal+none"])]
key = key[~key.run.isin(["ujm_axa"])]
rows = [["Run", "Pembanding", "k", "d̄", "p Wilcoxon", "p NB", "p NB+Holm"]]
for _, r in key.iterrows():
    rows.append([r.run, r.baseline, str(r.k), f"{r.delta:+.3f}", f"{r.p_wilcoxon:.4f}", f"{r.p_nb:.4f}",
                 f"{r.p_nb_holm:.3f}"])
S.append(table(rows, [4.0 * cm, 4.8 * cm, 0.8 * cm, 1.4 * cm, 2.0 * cm, 1.8 * cm, 2.2 * cm]))
S.append(Spacer(1, 6))
S.append(finding(
    "S1", "FATAL", "Klaim kontribusi metode tidak didukung",
    "Seluruh results/*_folds.csv (dihitung ulang di reports/audit_significance.csv)",
    "Satu-satunya perbandingan yang bertahan adalah CryCeleb handcrafted: usulan vs fusion_equal+none "
    "(d̄ = +0,047, p<sub>Holm</sub> = 0,008). Itu efek class weighting 'balanced' vs 'none', bukan efek "
    "pembobotan grup. Usulan vs pembobotan global: d̄ = 0,000 persis di 7 dari 8 run biner.",
    "Lihat tabel di atas. Termasuk klaim saya sendiri di laporan sebelumnya ('banyak lapisan signifikan lebih baik "
    "dari lapisan terakhir di DBL, p ≤ 0,004'): setelah koreksi, p<sub>Holm</sub> = 0,12 (HuBERT) dan 1,00 (w2v2). "
    "Klaim itu salah dan harus ditarik.",
    "Jangan menulis 'metode usulan lebih baik'. Paling jauh: 'pembobotan kelas membantu fusi pada data timpang' "
    "(1 dataset) dan 'agregasi multi-lapisan cenderung lebih baik dari lapisan terakhir' (tren, tidak signifikan)."))

S.append(finding(
    "E1", "MAYOR", "Protokol evaluasi tidak seragam antar-dataset",
    "evaluate.py:49 (seeds), skrip run_emb_exp.sh",
    "Handcrafted dan DBL-embedding: 5 fold × 3 seed. UJM-embedding: 2 seed. CryCeleb-embedding: 1 seed (diubah demi "
    "waktu). Macro-F1 dihitung per fold lalu dirata-rata; di DBL fold uji berisi ±4 klip untuk heh/eairh, jadi F1 "
    "per kelas sangat berisik.",
    "SD fold DBL 0,05–0,10; CryCeleb-embedding hanya 5 nilai.",
    "Satu protokol untuk semua: mis. 5 × 5 fold atau nested CV; laporkan macro-F1 gabungan (pooled) dan CI bootstrap per bayi."))

S.append(finding(
    "E2", "MAYOR", "Garden of forking paths",
    "Riwayat commit 8cf2b4f → 6a0d961",
    "Setelah melihat hasil: tugas UJM diganti (persalinan → jenis kelamin/usia), PCA-64 ditambahkan, jumlah seed "
    "dikurangi, ID anonim CryCeleb dibuang. Sebagian beralasan kuat (ID anonim), tapi semuanya terjadi pasca-hasil "
    "dan tidak terdokumentasi sebagai deviasi.",
    "Hasil persalinan (≈ acak) tetap tersimpan, bagus; tapi tidak ada catatan pra-registrasi.",
    "Tulis bagian 'Deviations from plan' di paper; bekukan protokol, lalu jalankan ulang semuanya sekali."))

S.append(PageBreak())
S.append(P("3. Data dan desain eksperimen", h2))
S.append(finding(
    "D1", "FATAL", "Kebocoran lewat duplikat di InfantCry-DBL",
    "data.py:91 (group = satu klip satu grup)",
    "DBL tidak punya ID bayi, lalu tiap klip dijadikan grupnya sendiri. Klip dari rekaman yang sama bisa jatuh di "
    "fold latih dan uji.",
    "Dari 237 klip: 1 pasang identik byte demi byte; 10 pasang dengan kosinus fitur &gt; 0,95, semuanya berlabel sama. "
    "Jika klip mirip dipaksa satu grup, skor turun: usulan 0,852 → 0,846 (&gt;0,95) → 0,837 (&gt;0,90) → 0,818 "
    "(&gt;0,85); keunggulan atas concat menyusut dari +1,6 ke +0,5 poin.",
    "Deduplikasi wajib (hash audio + kemiripan akustik), kelompokkan klip berdasarkan cluster, laporkan skor DBL "
    "sebagai batas atas yang optimistis."))
S.append(finding(
    "D3", "MAYOR", "Subset DBL 'bersih' tidak terverifikasi",
    "data.py:86",
    "Kriteria 'bukan turunan CryCeleb/Dunstan' bergantung pada kolom source = online_or_volunteer.",
    "Seluruh 1.214 klip Tier-2 memiliki source_confirmed = False. Klip 'online' bisa berasal dari video YouTube yang "
    "juga menjadi sumber dataset Dunstan/Kaggle di Paper 1.",
    "Klaim 'disjoint dari Paper 1' harus dilemahkan, atau buktikan dengan pencocokan audio silang terhadap data "
    "Paper 1 (fingerprint/hash)."))
S.append(finding(
    "D2", "MAYOR", "CryCeleb: tugas B vs D kemungkinan besar mengukur kondisi rekaman",
    "data.py:16-33",
    "Label 'period' (sesaat lahir vs saat pulang) berkorelasi dengan lokasi, waktu, perangkat, dan prosedur rekam. "
    "Klasifikator bisa belajar artefak, bukan fisiologi tangis.",
    "Fitur durasi SAJA memberi macro-F1 0,550 ± 0,028 (acak 0,50; terbaik 0,64). Median durasi B = 0,87 s, D = 0,95 s. "
    "Hampir separuh jarak dari acak ke model terbaik dapat dijelaskan oleh durasi.",
    "Kendalikan durasi (hapus fitur durasi, normalisasi panjang), laporkan baseline 'durasi saja', dan bahas "
    "confound kondisi rekaman secara eksplisit."))
S.append(finding(
    "D4", "MINOR", "UJM-AXA: sinyal lemah dan desain sampling",
    "download_ujm_subset.py:23-28, data.py:66-74",
    "Subset disampling seimbang per cara persalinan, lalu dipakai untuk tugas lain (jenis kelamin, usia); distribusi "
    "tidak representatif. Ambang tertil usia dihitung di level klip, bukan bayi.",
    "Semua model UJM: 0,51–0,61 (acak 0,50). Tugas persalinan ≈ acak (0,35 vs 0,33).",
    "Jika dipertahankan, ambil sampel acak per bayi untuk tiap tugas; atau tempatkan UJM sebagai hasil negatif."))

S.append(P("4. Matematika fitur handcrafted", h2))
S.append(finding(
    "F1", "MAYOR", "Grup 'mfcc' dan 'mel' tidak independen secara matematis",
    "features.py:42-43 dan 69-74",
    "MFCC = DCT-II ortonormal dari log-mel. Karena DCT linear, rata-rata waktu dari MFCC = DCT dari rata-rata log-mel. "
    "Jadi 20 fitur 'mfcc-mean' adalah transformasi linear persis dari 32 fitur grup 'mel'. Pembobotan grup "
    "menghitung bukti yang sama dua kali dan bobot grup tidak bisa ditafsirkan.",
    "max |MFCC-mean − DCT(mel-mean)| = 4,6 × 10<super>−5</super>; R² regresi linear = 1,000000.",
    "Gabungkan atau ganti salah satu grup (mis. mel-std, GFCC, atau fitur prosodi), lalu definisikan grup yang "
    "benar-benar berbeda informasinya."))
S.append(finding(
    "F2", "MAYOR", "Estimator F0 autokorelasi salah pada kasus penting",
    "features.py:19-32",
    "(a) argmax global dalam rentang lag tanpa syarat puncak lokal → bisa menempel di batas lag 16 (1.000 Hz); "
    "(b) rentang 150–1.000 Hz membuang hyperphonation tangis (&gt; 1 kHz) dan justru memetakannya ke subharmonik; "
    "(c) ACF berjendela tidak dikoreksi autokorelasi jendela (Boersma 1993) → bias ke lag pendek; "
    "(d) tanpa interpolasi parabolik → kuantisasi kasar.",
    "Sinus 1.200 Hz → 400 Hz (keyakinan 0,99); 1.500 Hz → 500 Hz (0,99); 100 Hz → 1.000 Hz; derau low-pass → "
    "1.000 Hz dengan keyakinan 0,64 (&gt; ambang 0,3, jadi lolos sebagai 'bersuara'). Langkah kuantisasi: 5,6 Hz "
    "(300 Hz), 12,7 Hz (450 Hz), 22,8 Hz (600 Hz), 52,3 Hz (900 Hz). Untuk sinus 160–900 Hz hasilnya akurat dalam "
    "±12 Hz.",
    "Pakai estimator yang tervalidasi (pYIN/CREPE/Praat), naikkan fmax ke ≥ 2 kHz untuk tangis bayi, wajibkan "
    "puncak lokal, interpolasi parabolik, dan validasi pada sinyal sintetis sebagai unit test."))
S.append(finding(
    "F3", "MINOR", "Rata-rata delta-MFCC hampir nol",
    "features.py:44, 70",
    "Rata-rata waktu dari turunan lokal ≈ (akhir − awal)/T, jadi mendekati nol dan hanya mencerminkan efek tepi.",
    "Rata-rata |mean delta| = 0,114 vs rata-rata std delta = 1,317 (rasio 0,087).",
    "Simpan hanya std delta (atau statistik lain yang informatif)."))
S.append(finding(
    "F4", "MINOR", "Mask voicing tidak sejajar dengan frame F0",
    "features.py:56-59",
    "librosa.rms memakai frame center=True (frame i berpusat di i·160), sedangkan F0 tanpa padding (berpusat di "
    "i·160 + 512). Lalu dipotong ke panjang minimum dari awal.",
    "Offset 512 sampel = 32 ms = 3,2 frame. Jika voiced ≤ 2 frame, kode diam-diam memakai SEMUA frame F0 (termasuk sunyi).",
    "Samakan pemusatan frame; jika tidak ada frame bersuara, isi NaN eksplisit dan tangani di model."))
S.append(finding(
    "F5", "MINOR", "Pilihan pra-pemrosesan yang mengaburkan tafsiran",
    "features.py:36-39, 63-67, 76; extract_embeddings.py:18",
    "Normalisasi puncak menghapus informasi kenyaringan, padahal grup 'energy' seolah mengukurnya. Durasi menjadi "
    "fitur (jalur shortcut, lihat D2). np.nan_to_num membungkam kegagalan ekstraksi. Fitur dipotong 8 s, "
    "embedding 6 s.",
    "Diperiksa di kode; durasi terbukti informatif di CryCeleb (D2).",
    "Dokumentasikan atau hapus; log jumlah NaN per fitur; samakan panjang potongan."))

S.append(PageBreak())
S.append(P("5. Matematika metode pembobotan", h2))
S.append(P("Definisi di kode: untuk grup/lapisan g dan kelas c, skor F1<sub>gc</sub> diperoleh dari CV dalam. "
           "Global: w<sub>g</sub> = softmax<sub>g</sub>(τ · mean<sub>c</sub> F1<sub>gc</sub>). "
           "Classwise: w<sub>gc</sub> = softmax<sub>g</sub>(τ · F1<sub>gc</sub>). "
           "Fusi: s<sub>c</sub>(x) = Σ<sub>g</sub> w<sub>gc</sub> · P<sub>g</sub>(c|x), lalu dinormalisasi atas c.", mono))
S.append(finding(
    "M1", "FATAL", "Dengan τ = 10, bobot usulan praktis seragam",
    "weighting.py:74 (tau=10.0), 108-110",
    "Selisih F1 antar-lapisan berkisar beberapa poin persen. Dengan τ = 10, selisih 0,05 hanya menjadi rasio bobot "
    "e<super>0,5</super> ≈ 1,65. Nilai τ tidak pernah dituning atau dijustifikasi.",
    "Contoh nyata (DBL, w2v2, satu fold): bobot terbesar 0,140 (seragam = 0,077); entropi 3,54 bit dari maksimum "
    "3,70. Classwise: bobot maksimum per kelas 0,115–0,200. Karena itu usulan ≈ fusi sama rata, dan usulan vs global "
    "memberi d̄ = 0,000 persis di 7 dari 8 run biner. Dengan τ = 100 bobot terbesar 0,736; dengan τ = 1.000 menjadi "
    "pemilihan satu lapisan.",
    "Tuning τ di CV dalam (nested), atau ganti dengan bobot yang dipelajari (stacking/meta-LR atau weighted-sum "
    "yang dilatih end-to-end)."))
S.append(finding(
    "M2", "MAYOR", "Fusi classwise tidak koheren secara probabilistik",
    "weighting.py:110, 116-119",
    "Tiap kelas memakai campuran pakar yang berbeda, lalu argmax membandingkan skor dari campuran berbeda. Kelas yang "
    "pakar terbaiknya terlalu yakin (overconfident) akan dimenangkan. Normalisasi ulang atas c tidak memulihkan "
    "kalibrasi. Selain itu, bobot diturunkan dari F1 prediksi KERAS tetapi diterapkan pada probabilitas LUNAK.",
    "Analisis matematis; tidak ada kalibrasi (Platt/temperature) sebelum fusi.",
    "Kalibrasi tiap pakar dulu, lalu pakai satu bobot per pakar atau meta-classifier pada log-probabilitas."))
S.append(finding(
    "M3", "MAYOR", "Skema 'effective number' mengubah kekuatan regularisasi",
    "weighting.py:28-30",
    "Rumus Cui et al. benar: w<sub>c</sub> = (1−β)/(1−β<super>n<sub>c</sub></super>), dinormalisasi Σ<sub>c</sub> w<sub>c</sub> = K. "
    "Tetapi pada LogisticRegression, bobot sampel mengalikan suku loss, sehingga total bobot ≠ n setara dengan "
    "mengubah C.",
    "DBL: 'balanced' total bobot = 237,0 (= n), 'effective' total = 151,4 (0,64 n). Perbandingan effective vs "
    "balanced tercampur dengan regularisasi ≈ 1,6× lebih kuat.",
    "Normalisasi agar Σ<sub>i</sub> w<sub>y<sub>i</sub></sub> = n untuk semua skema."))
S.append(finding(
    "M4", "MAYOR", "Pembanding lemah dan kapasitas tidak setara",
    "run_embedding_experiments.py:17-27, run_experiments.py:15-23",
    "(a) Baseline baku literatur, yaitu learnable weighted-sum lapisan ala SUPERB (Yang et al., 2021), tidak ada. "
    "(b) 'last_layer' dari wav2vec2 pretrained memang dikenal buruk, jadi lawan yang lemah. (c) Fusi = 13 model × "
    "64 dimensi vs mean_layers = 1 × 64: kapasitas tidak setara. (d) C = 0,05 dan PCA = 64 dipilih tanpa tuning, "
    "PCA tanpa whitening membuat penalti L2 tidak merata. (e) 'best_layer' memakai softmax τ = 1.000, bukan argmax "
    "keras (aman di fold yang diperiksa, tapi rapuh jika F1 nyaris seri).",
    "Konfigurasi di kode.",
    "Tambahkan weighted-sum terlatih dan best-layer argmax keras; tuning C di CV dalam untuk SEMUA model; samakan anggaran parameter."))

S.append(P("6. Rekayasa perangkat lunak dan reprodusibilitas", h2))
S.append(finding(
    "R1", "MINOR", "Infrastruktur riset belum memadai",
    "Seluruh repo",
    "Tidak ada unit test (estimator F0 dan rumus bobot seharusnya diuji). Tidak ada requirements/lockfile. Versi "
    "torch, transformers, sklearn, dan librosa tidak dicatat. Tidak ada README. Path relatif bergantung pada direktori "
    "kerja. CSV hasil tidak menyimpan hash commit yang menghasilkannya. remote_zip.read tidak memeriksa status 206, "
    "sehingga server yang mengabaikan Range akan mengirim 81 GB ke memori. Unduhan Mendeley tidak diverifikasi dengan "
    "sha256 yang tersedia di metadata. Dua bug dtype pandas 3 baru ditemukan saat runtime.",
    "Diperiksa di kode.",
    "Tambah tests/, requirements.lock, README, cek status 206, verifikasi sha256, dan tulis git SHA ke setiap hasil."))

S.append(P("7. Yang diperiksa dan ternyata benar", h2))
S.append(P("Supervisor yang adil juga mencatat apa yang tidak bermasalah. Hal-hal berikut sudah diverifikasi:", body))
S.append(table([
    ["Aspek", "Status", "Catatan"],
    ["Pemisahan subjek di fold luar", "OK", "assert tanpa irisan grup di evaluate.py:33; berlaku jika ID grup benar"],
    ["Bobot fusi hanya dari CV dalam", "OK", "Fold uji luar tidak menyentuh bobot (weighting.py:83-114)"],
    ["StandardScaler/PCA di dalam pipeline", "OK", "Dipasang ulang per fold latih, tanpa kebocoran"],
    ["Rumus class weight 'balanced'", "OK", "n / (K · n<sub>c</sub>), identik dengan sklearn; total bobot = n"],
    ["Rumus 'effective number'", "OK", "Sesuai Cui et al. (2019); masalahnya hanya normalisasi (M3)"],
    ["ACF via FFT", "OK", "Zero-padding 2× mencegah aliasing sirkular"],
    ["Skala antar-lapisan embedding", "OK", "Norma rata-rata 4,3–7,4 (rasio 1,7); mean_layers tidak didominasi satu lapisan"],
    ["Normalisasi input HuBERT", "OK", "Konfigurasi resmi do_normalize = True untuk kedua model"],
    ["Pembuangan ID anonim CryCeleb", "OK", "Perlu dan benar; mencegah kebocoran bayi yang sama"],
    ["Integritas unduhan zip", "OK", "zipfile memverifikasi CRC-32 saat membaca anggota"],
], [5.2 * cm, 1.3 * cm, 10.5 * cm], sev_col=1))

S.append(P("8. Perintah kerja (urut prioritas)", h2))
S += bl([
    "<b>Statistik dulu.</b> Ganti Wilcoxon dengan corrected resampled t-test + Holm (atau Bayesian correlated t-test), "
    "laporkan CI. Satu protokol untuk semua dataset.",
    "<b>Bersihkan DBL.</b> Deduplikasi audio, kelompokkan klip mirip, dan jalankan ulang. Lemahkan klaim 'disjoint "
    "dari Paper 1' atau buktikan dengan fingerprint.",
    "<b>Kendalikan shortcut.</b> Hapus durasi dari fitur, tambahkan baseline 'durasi saja' untuk setiap tugas, dan "
    "bahas confound kondisi rekaman CryCeleb.",
    "<b>Perbaiki fitur.</b> Buang redundansi MFCC/mel, ganti estimator F0 yang tervalidasi (fmax ≥ 2 kHz), dan perbaiki "
    "kesejajaran frame.",
    "<b>Perbaiki metode.</b> Tuning τ dan C secara nested; kalibrasi sebelum fusi; tambahkan baseline weighted-sum "
    "ala SUPERB; normalisasi bobot effective.",
    "<b>Reprodusibilitas.</b> Unit test untuk F0 dan bobot, lockfile, README, dan hash commit di setiap file hasil.",
])

S.append(P("9. Klaim yang boleh dan tidak boleh ditulis saat ini", h2))
S.append(table([
    ["Boleh (didukung data)", "Tidak boleh (tidak didukung)"],
    ["Pembobotan kelas 'balanced' membantu fusi pada data timpang (CryCeleb, p<sub>Holm</sub> = 0,008)",
     "'Metode usulan lebih baik dari baseline'"],
    ["Agregasi multi-lapisan cenderung mengungguli lapisan terakhir (tren konsisten, tidak signifikan setelah koreksi)",
     "'Pembobotan per kelas (classwise) bermanfaat'"],
    ["Pembobotan lapisan adaptif tidak mengungguli pemilihan satu lapisan terbaik",
     "'Multi-lapisan signifikan lebih baik' (klaim lama saya, ditarik)"],
    ["Usia, jenis kelamin, dan cara persalinan hampir tidak terprediksi dari tangis (UJM)",
     "Angka DBL 0,85 sebagai performa realistis (terkontaminasi duplikat)"],
], [8.5 * cm, 8.5 * cm]))
S.append(Spacer(1, 8))
S.append(P("Catatan penutup supervisor: kerangka evaluasinya sudah benar di bagian yang paling sering salah "
           "(pemisahan subjek, estimasi bobot di dalam fold). Masalah utamanya ada pada data (duplikat, shortcut), "
           "fitur yang redundan, metode yang secara numerik tidak berbeda dari baseline, dan statistik yang "
           "menggelembungkan signifikansi. Perbaiki urutan 1–3 di atas sebelum menulis satu kalimat pun di bagian "
           "hasil.", body))

doc = SimpleDocTemplate("reports/supervisor_review.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=2 * cm, title="Laporan Supervisi Kritis Paper 4",
                        author="Audit kode microasa")
doc.build(S, onFirstPage=footer, onLaterPages=footer)
print("written reports/supervisor_review.pdf")
