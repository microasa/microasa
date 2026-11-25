"""Buku panduan Paper 4 (bahasa Indonesia) -> reports/book/paper4_buku.pdf
Run from the repo root after make_figures.py:  python3 reports/book/build_book.py
All result tables are generated from results/v2 and results/v3."""
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

F = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("S", "DejaVuSerif.ttf"), ("SB", "DejaVuSerif-Bold.ttf"), ("SS", "DejaVuSans.ttf"),
             ("SSB", "DejaVuSans-Bold.ttf"), ("M", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(n, F + f))
pdfmetrics.registerFontFamily("S", normal="S", bold="SB", italic="S", boldItalic="SB")
pdfmetrics.registerFontFamily("SS", normal="SS", bold="SSB", italic="SS", boldItalic="SSB")

INK, GRY, LINE, FILL = (colors.HexColor(c) for c in ("#191919", "#666666", "#c8ccd2", "#f2f4f7"))
ACC = colors.HexColor("#1d5fa8")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="S", fontSize=10.2, leading=15, alignment=TA_JUSTIFY,
                      textColor=INK, spaceAfter=7)
ch = ParagraphStyle("ch", parent=body, fontName="SSB", fontSize=20, leading=25, spaceBefore=0, spaceAfter=14,
                    textColor=ACC, alignment=0)
h2 = ParagraphStyle("h2", parent=body, fontName="SSB", fontSize=12.5, leading=16, spaceBefore=12, spaceAfter=5,
                    alignment=0, keepWithNext=1)
h3 = ParagraphStyle("h3", parent=body, fontName="SSB", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=3,
                    alignment=0, keepWithNext=1)
eq = ParagraphStyle("eq", parent=body, fontName="S", alignment=TA_CENTER, spaceBefore=4, spaceAfter=9, fontSize=10.5)
cap = ParagraphStyle("cap", parent=body, fontName="SS", fontSize=8.6, leading=11.5, textColor=GRY, spaceAfter=10)
cell = ParagraphStyle("cell", parent=body, fontName="SS", fontSize=8, leading=10.2, alignment=0, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="SSB")
code = ParagraphStyle("code", parent=body, fontName="M", fontSize=8, leading=10.5, alignment=0, backColor=FILL,
                      borderPadding=5, spaceBefore=4, spaceAfter=10)
bul = ParagraphStyle("bul", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=4)
box = ParagraphStyle("box", parent=body, fontName="SS", fontSize=9.4, leading=13.5, backColor=colors.HexColor("#eef4fb"),
                     borderColor=ACC, borderWidth=0.8, borderPadding=8, spaceBefore=6, spaceAfter=12, alignment=0)
title = ParagraphStyle("t", parent=body, fontName="SSB", fontSize=28, leading=34, alignment=TA_CENTER, textColor=ACC)
subt = ParagraphStyle("st", parent=body, fontName="SS", fontSize=13, leading=18, alignment=TA_CENTER, textColor=INK)
small = ParagraphStyle("sm", parent=body, fontName="SS", fontSize=9, alignment=TA_CENTER, textColor=GRY)

S = []


def P(t, s=body):
    S.append(Paragraph(t, s))


def B(items):
    for t in items:
        S.append(Paragraph(t, bul, bulletText="•"))


def EQ(t):
    S.append(Paragraph(t, eq))


def CODE(t):
    S.append(Paragraph(t.replace("\n", "<br/>").replace("  ", "&nbsp;&nbsp;"), code))


def BOX(t):
    S.append(Paragraph(t, box))


def CH(t):
    S.append(PageBreak())
    S.append(Paragraph(t, ch))


def TBL(rows, widths, caption):
    data = [[Paragraph(str(c), cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, LINE), ("BACKGROUND", (0, 0), (-1, 0), FILL),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    S.append(KeepTogether([Paragraph(caption, cap), t, Spacer(1, 8)]))


def FIG(path, w, caption):
    from reportlab.lib.utils import ImageReader

    iw, ih = ImageReader(path).getSize()
    S.append(KeepTogether([Image(path, width=w, height=w * ih / iw), Paragraph(caption, cap)]))


class Doc(SimpleDocTemplate):
    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("ch", "h2"):
            self.notify("TOCEntry", (0 if f.style.name == "ch" else 1, f.getPlainText(), self.page))


def footer(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("SS", 7.5)
    canvas.setFillColor(GRY)
    canvas.drawString(2.2 * cm, 1.2 * cm, "Paper 4 dalam satu buku · pembobotan pada klasifikasi tangis bayi")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, str(doc.page))
    canvas.restoreState()


TASK = {"cryceleb": "CryCeleb", "infantcry_dbl": "DBL", "ujm_sex": "UJM-sex", "ujm_age": "UJM-age",
        "ujm_axa": "UJM-delivery"}
REP = {"hand": "handcrafted", "w2v2": "wav2vec2", "hubert": "HuBERT"}
s2, s3 = pd.read_csv("results/v2/summary.csv"), pd.read_csv("results/v3/summary.csv")
p2, p3 = pd.read_csv("results/v2/primary_tests.csv"), pd.read_csv("results/v3/primary_tests.csv")
e2 = pd.read_csv("results/v2/exploratory_tests.csv")
d2 = pd.concat([pd.read_csv(f"results/v2/{r}_{t}_diag.csv") for r in ["hand", "w2v2", "hubert"]
                for t in ["cryceleb", "infantcry_dbl", "ujm_sex", "ujm_age"]])
n2, n3 = int((p2.verdict != "no evidence").sum()), int((p3.verdict != "no evidence").sum())

# ---------------------------------------------------------------- cover + TOC
S += [Spacer(1, 5 * cm), Paragraph("Paper 4 dalam Satu Buku", title), Spacer(1, 0.6 * cm),
      Paragraph("Pembobotan kelas, grup fitur, dan lapisan embedding pada klasifikasi tangis bayi: "
                "data, matematika, evaluasi, hasil, dan pelajarannya", subt),
      Spacer(1, 1.2 * cm),
      Paragraph("Disusun dari kode, data, dan hasil di repositori microasa "
                "(branch claude/repo-harnes-connection-rbg5g8)", small),
      Paragraph("Semua angka hasil dibaca langsung dari results/v2 dan results/v3", small),
      Paragraph("November 2026", small), PageBreak()]
S.append(Paragraph("Daftar Isi", ch))
toc = TableOfContents()
toc.levelStyles = [ParagraphStyle("t0", fontName="SSB", fontSize=10.5, leading=15, leftIndent=0),
                   ParagraphStyle("t1", fontName="SS", fontSize=9, leading=12.5, leftIndent=16, textColor=GRY)]
S.append(toc)

# ---------------------------------------------------------------- Bab 1
CH("Bab 1. Gambaran Besar")
P("Buku ini menjelaskan Paper 4 dari awal sampai akhir: pertanyaan risetnya, data yang dipakai, setiap langkah "
  "matematika di dalam kode, cara mengevaluasi secara jujur, hasilnya, serta kesalahan yang ditemukan dan diperbaiki "
  "di sepanjang jalan. Tujuannya agar Anda bisa mempertahankan paper ini di depan reviewer, menjawab pertanyaan "
  "teknis apa pun, dan mereproduksi semuanya sendiri.")
S.append(Paragraph("1.1 Pertanyaan riset", h2))
P("Paper 1 (dikirim ke BSPC) mencoba pembobotan dan hasilnya gagal. Paper 4 menanyakan pertanyaan yang lebih "
  "mendasar: <b>apakah pembobotan memang membantu klasifikasi tangis bayi, jika evaluasinya dibuat bebas "
  "kebocoran?</b> Pembobotan diuji di tiga tingkat:")
B(["<b>Tingkat kelas:</b> memberi bobot lebih pada kelas yang jarang (class weighting).",
   "<b>Tingkat grup fitur:</b> menggabungkan beberapa kelompok fitur akustik (MFCC, pitch, spektral, dan "
   "seterusnya) dengan bobot berbeda.",
   "<b>Tingkat lapisan:</b> menggabungkan 13 lapisan tersembunyi encoder suara pretrained (wav2vec2, HuBERT) "
   "dengan bobot berbeda."])
S.append(Paragraph("1.2 Jawaban singkat", h2))
BOX(f"<b>Tidak.</b> Dari 36 perbandingan utama yang ditetapkan sebelum eksperimen, {n2} menunjukkan bukti "
    f"perbedaan. Setelah data dibersihkan (analisis sensitivitas v3), hasilnya tetap {n3}/36. Tidak ada metode "
    "pembobotan atau fusi, termasuk stacking yang diusulkan, yang mengungguli rata-rata sederhana, pemilihan satu "
    "grup/lapisan terbaik, atau baseline SUPERB. Pembobotan kelas juga tidak terbukti membantu.")
P("Selain hasil negatif itu, ada satu temuan sampingan yang kuat: <b>dataset publik InfantCry-DBL terkontaminasi</b>. "
  "Dari 236 klip yang diklaim sebagai rekaman online atau sukarelawan, 107 ternyata salinan klip lain, yaitu 41 dari "
  "video Dunstan dan 66 dari CryCeleb. Akibatnya, angka DBL sekitar 0,85 dari analisis awal kami tidak sah.")
S.append(Paragraph("1.3 Kenapa hasil negatif tetap bernilai", h2))
P("Banyak paper melaporkan peningkatan dari pembobotan, tetapi sering pada data kecil, dengan split per klip (bukan "
  "per bayi), bobot yang dipilih memakai data uji, dan uji statistik yang terlalu optimistis. Paper 4 menunjukkan "
  "bahwa ketika semua celah itu ditutup, peningkatannya hilang. Ini informasi yang berguna bagi peneliti lain, "
  "asalkan metodologinya terbukti kuat. Itulah sebabnya sebagian besar buku ini membahas metodologi.")
S.append(Paragraph("1.4 Peta buku", h2))
B(["Bab 2–3: latar belakang dan data, termasuk audit kontaminasi DBL.",
   "Bab 4–6: fitur akustik, embedding, dan metode pembobotan beserta matematikanya.",
   "Bab 7: protokol evaluasi dan statistik.",
   "Bab 8: hasil lengkap.",
   "Bab 9: perjalanan riset, yaitu kesalahan yang ditemukan dan pelajarannya.",
   "Bab 10–11: cara menulis, mengirim, dan mempertahankan paper, serta cara mereproduksinya.",
   "Lampiran: glosarium dan daftar berkas."])

# ---------------------------------------------------------------- Bab 2
CH("Bab 2. Latar Belakang")
S.append(Paragraph("2.1 Analisis tangis bayi", h2))
P("Tangis adalah satu-satunya sarana komunikasi bayi baru lahir. Analisis otomatis tangis dipelajari untuk "
  "membantu orang tua (misalnya menebak penyebab tangis) dan untuk pemantauan klinis di ruang neonatal. Sinyal "
  "tangis punya ciri khas: frekuensi dasar (F0) tinggi, umumnya 300–600 Hz, dan pada kondisi tertentu bisa melonjak "
  "di atas 1 kHz (hyperphonation); harmonik yang kuat; serta pola napas yang membagi tangis menjadi segmen-segmen "
  "ekspirasi.")
S.append(Paragraph("2.2 Mengapa pembobotan begitu populer", h2))
P("Data tangis biasanya kecil dan timpang. Peneliti lalu menggabungkan banyak jenis fitur dan berharap kombinasi yang "
  "tepat akan lebih baik dari fitur tunggal. Pembobotan adalah cara alami untuk 'memilih' kombinasi itu. Masalahnya, "
  "semakin banyak bobot yang dipilih dari data, semakin besar risiko bobot itu hanya menyesuaikan diri dengan "
  "kebetulan pada data tertentu (overfitting), terutama bila data uji ikut memengaruhi pemilihan.")
S.append(Paragraph("2.3 Tiga tingkat pembobotan", h2))
P("<b>Pembobotan kelas</b> mengubah fungsi loss supaya kesalahan pada kelas jarang dihukum lebih berat. "
  "<b>Pembobotan grup fitur</b> melatih satu model per kelompok fitur lalu menggabungkan prediksinya dengan bobot. "
  "<b>Pembobotan lapisan</b> memanfaatkan fakta bahwa tiap lapisan encoder self-supervised menyimpan informasi yang "
  "berbeda: lapisan awal lebih dekat ke akustik, lapisan akhir lebih dekat ke tugas pretraining (pengenalan ucapan). "
  "Benchmark SUPERB mempopulerkan jumlahan berbobot lapisan yang dipelajari sebagai baseline standar.")
S.append(Paragraph("2.4 Posisi terhadap Paper 1", h2))
P("Paper 1 memakai Donate-a-Cry, Baby Chillanto, dan Dunstan/Kaggle, dan pembobotannya gagal. Paper 4 sengaja memakai "
  "dataset yang berbeda agar tidak tumpang tindih. Ironisnya, audit di Paper 4 menemukan bahwa salah satu dataset "
  "'baru' (InfantCry-DBL) justru berisi salinan video Dunstan. Bagian yang terkontaminasi itu sudah dibuang. "
  "Kegagalan pembobotan di Paper 1 kini punya konteks: di bawah evaluasi yang ketat, pembobotan memang tidak "
  "terbukti membantu di tiga korpus lain sekalipun.")

# ---------------------------------------------------------------- Bab 3
CH("Bab 3. Data")
P("Tiga korpus publik dipakai. Prinsip utamanya: setiap tugas didefinisikan sebelum melihat hasil, dan setiap "
  "'kelompok CV' (unit yang tidak boleh terbelah antara data latih dan uji) ditetapkan dengan hati-hati.")
TBL([["Tugas", "Korpus", "Klip", "Kelompok CV", "Kelas"],
     ["CryCeleb (B vs D)", "CryCeleb2023 (Hugging Face, CC BY-NC-ND)", "4.954", "626 bayi", "B 2.815 · D 2.139"],
     ["UJM-sex", "BABYCRY-UJM-AXA (Zenodo, CC BY)", "1.762", "300 bayi", "F 882 · M 880"],
     ["UJM-age", "sama", "1.176", "247 bayi", "muda 588 · tua 588"],
     ["UJM-delivery (tambahan)", "sama", "1.762", "300 bayi", "Assisted 594 · C-section 592 · Vaginal 576"],
     ["DBL (5 kelas)", "InfantCry-DBL (Mendeley, CC BY)", "103", "86 klaster", "owh 40 · eh 26 · neh 18 · eairh 13 · heh 6"]],
    [3.0 * cm, 4.4 * cm, 1.3 * cm, 2.1 * cm, 5.8 * cm], "Tabel 3.1. Tugas pada analisis utama (protokol v2).")
S.append(Paragraph("3.1 CryCeleb2023", h2))
P("CryCeleb2023 berisi potongan ekspirasi tangis dari 786 bayi yang direkam pada dua periode: sesaat setelah lahir "
  "(B) dan saat pulang dari rumah sakit (D). Dataset ini dibuat untuk verifikasi identitas bayi, tetapi labelnya bisa "
  "dipakai untuk tugas B vs D. Akses memerlukan token Hugging Face dan persetujuan lisensi non-komersial.")
P("<b>Jebakan yang ditemukan:</b> split uji kompetisi memakai ID <i>anonymousNNN</i>, dan dua periode dari bayi yang "
  "sama diberi ID berbeda. Jika dipakai, bayi yang sama bisa muncul di data latih dan uji tanpa terdeteksi. Karena "
  "itu hanya bayi ber-ID asli yang dipakai (626 bayi), dengan klip berdurasi minimal 0,5 detik dan paling banyak 5 "
  "klip per bayi per periode.")
P("<b>Confound:</b> label B/D juga berarti perbedaan waktu, lokasi, dan prosedur rekam. Fitur durasi saja sudah "
  "memberi macro-F1 0,55 (acak 0,50). Jadi sebagian 'sinyal' B vs D bisa jadi berasal dari kondisi rekaman.")
S.append(Paragraph("3.2 BABYCRY-UJM-AXA", h2))
P("Korpus ini berisi 107.312 rekaman tangis dari sekitar 1.000 bayi cukup bulan, beserta metadata klinis, dalam "
  "satu file zip 81 GB. Ruang disk tidak cukup, jadi hanya sebagian yang diunduh lewat <i>HTTP range request</i>: "
  "daftar isi zip dibaca dari ujung file, lalu hanya klip terpilih yang diambil. Subsetnya deterministik (seed 0): "
  "100 bayi per cara persalinan, paling banyak 6 klip per bayi, total 1.762 klip.")
P("Tugas awal (cara persalinan) ternyata setara tebakan acak, lalu diganti dengan dua tugas yang ditetapkan sebelum "
  "hasilnya dilihat: <b>jenis kelamin</b> dan <b>usia rekaman</b>. Usia dibagi menjadi tertil bawah ('muda') dan "
  "tertil atas ('tua') dari jam sejak lahir, sedangkan tertil tengah dibuang. Penggantian ini dicatat sebagai "
  "keputusan yang dipicu hasil (lihat Bab 9).")
S.append(Paragraph("3.3 InfantCry-DBL dan auditnya", h2))
P("InfantCry-DBL memberi label lima kategori 'Dunstan Baby Language' (eairh, eh, heh, neh, owh). Tier 1 berasal dari "
  "video instruksional Dunstan, dan Tier 2 diklaim berasal dari tiga sumber, salah satunya turunan CryCeleb. "
  "Yang kita pakai hanya Tier 2 berlabel <i>online_or_volunteer</i>. Audit berlapis:")
B(["Semua 1.551 berkas cocok dengan hash SHA-256 resmi penerbit, jadi unduhan utuh.",
   "Satu klip adalah duplikat identik byte demi byte.",
   "Setiap kandidat dibandingkan dengan seluruh 337 klip Tier 1 dan seluruh 26.093 klip CryCeleb, memakai kemiripan "
   "kosinus vektor fitur yang sudah di-z-score. Hasilnya, <b>107 klip adalah salinan</b> (kosinus ≥ 0,999): 41 dari "
   "Tier 1 dan 66 dari CryCeleb. Ada 26 klip lain yang sangat mirip (0,95–0,999), kebanyakan dengan Tier 1.",
   "Dengan ambang 0,95 yang sudah ditetapkan sebelumnya, 133 klip dibuang. Sisanya 103 klip.",
   "Klip yang saling mirip di dalam DBL (kosinus ≥ 0,90) digabung menjadi satu kelompok CV (86 klaster), karena DBL "
   "tidak punya ID bayi.",
   "Kolom <i>source_confirmed</i> bernilai False untuk seluruh 1.214 klip Tier 2, jadi metadata sumbernya memang tidak "
   "bisa dipercaya."])
BOX("<b>Pelajaran:</b> label sumber di metadata dataset publik tidak boleh diterima mentah-mentah. Pencocokan audio "
    "silang antar-korpus murah dilakukan, dan di sini ia mengubah kesimpulan secara drastis.")

# ---------------------------------------------------------------- Bab 4
CH("Bab 4. Fitur Akustik Handcrafted")
P("Semua audio diubah ke 16 kHz mono, diambil 8 detik pertama, lalu dinormalisasi puncak (dibagi nilai absolut "
  "maksimum). Normalisasi puncak berarti kenyaringan absolut tidak dipakai, karena kenyaringan tidak sebanding antar "
  "perangkat rekam. Spektrogram dihitung dengan STFT (jendela 512 sampel = 32 ms, langkah 160 sampel = 10 ms).")
TBL([["Grup", "Isi", "Dimensi"],
     ["mfcc", "rata-rata dan simpangan baku 20 MFCC dari 32 pita log-mel", "40"],
     ["delta", "simpangan baku delta-MFCC (laju perubahan MFCC)", "20"],
     ["spectral", "centroid, bandwidth, rolloff, flatness, zero-crossing rate, kontras spektral 6 pita; "
      "rata-rata dan simpangan baku", "22"],
     ["pitch", "F0 rata-rata, simpangan baku, median, persentil 5 dan 95; porsi frame bersuara; "
      "kekuatan periodisitas rata-rata", "7"],
     ["energy", "RMS rata-rata, simpangan baku, maksimum; pusat waktu energi; rentang dinamis", "5"],
     ["mel", "simpangan baku tiap 32 pita log-mel sepanjang waktu", "32"]],
    [2.0 * cm, 13.0 * cm, 1.6 * cm], "Tabel 4.1. Enam grup fitur (total 126 dimensi). Grup adalah unit pembobotan.")
S.append(Paragraph("4.1 MFCC dan mengapa grup 'mel' memakai simpangan baku", h2))
P("Log-mel adalah energi spektrum pada 32 pita frekuensi berskala mel, dalam desibel. MFCC adalah transformasi "
  "kosinus diskret (DCT-II ortonormal) dari log-mel pada setiap frame:")
EQ("c<sub>k</sub>(t) = Σ<sub>m</sub> α<sub>k</sub> · L<sub>m</sub>(t) · cos(π k (m + ½) / M),  k = 0, …, 19")
P("Karena DCT bersifat linear, rata-rata MFCC sepanjang waktu sama persis dengan DCT dari rata-rata log-mel. Versi "
  "awal memakai rata-rata log-mel sebagai grup 'mel', sehingga 20 fitur MFCC-mean hanyalah transformasi linear grup "
  "'mel'. Audit membuktikannya: R² = 1,000000. Dua grup yang seharusnya 'berbeda' ternyata memuat informasi yang "
  "sama. Di versi final, grup 'mel' memakai <b>simpangan baku</b> log-mel (seberapa banyak tiap pita berfluktuasi), "
  "dan R² turun ke 0,300.")
S.append(Paragraph("4.2 Delta-MFCC", h2))
P("Delta adalah turunan lokal MFCC terhadap waktu. Rata-rata turunan sepanjang klip kira-kira (nilai akhir − nilai "
  "awal) / panjang klip, sehingga mendekati nol dan hanya mencerminkan efek tepi. Rasio |rata-rata| terhadap "
  "simpangan bakunya hanya 0,087. Karena itu hanya simpangan baku delta yang disimpan.")
S.append(Paragraph("4.3 Estimator F0 (pitch)", h2))
P("Estimator F0 ditulis sendiri karena <i>librosa.yin</i> mengalami segmentation fault di lingkungan ini. Versi "
  "pertamanya salah secara serius: nada 1.200 Hz terbaca 400 Hz dengan keyakinan 0,99, dan derau terbaca 1.000 Hz. "
  "Versi final bekerja per frame 64 ms (1.024 sampel, langkah 10 ms) dengan langkah berikut.")
P("<b>Langkah 1, autokorelasi terkoreksi jendela.</b> Frame dikalikan jendela Hann, lalu autokorelasinya dihitung "
  "lewat FFT dengan zero-padding dua kali (agar tidak terjadi aliasing sirkular). Jendela membuat autokorelasi mengecil "
  "untuk lag panjang, sehingga hasilnya bias ke lag pendek. Bias ini dikoreksi dengan membaginya dengan autokorelasi "
  "jendela itu sendiri (Boersma, 1993):")
EQ("r(l) = r<sub>x·w</sub>(l) / r<sub>w</sub>(l)")
P("<b>Langkah 2, cari kandidat.</b> Kandidat periode adalah puncak lokal r(l) pada rentang lag 8 sampai 107 sampel, "
  "yaitu 2.000 Hz sampai 150 Hz. Batas atas 2.000 Hz penting supaya hyperphonation tertangkap.")
P("<b>Langkah 3, aturan puncak mayor pertama.</b> Untuk sinyal periodik, r(l) punya puncak di T, 2T, 3T, dan "
  "seterusnya dengan tinggi hampir sama. Memilih puncak tertinggi bisa jatuh ke 2T atau 3T (kesalahan subharmonik, "
  "seperti 1.200 Hz menjadi 400 Hz). Karena itu dipilih puncak dengan <b>lag terpendek</b> yang tingginya minimal "
  "0,9 × puncak tertinggi.")
P("<b>Langkah 4, interpolasi parabolik.</b> Lag hanya berupa bilangan bulat, sehingga resolusinya kasar pada F0 "
  "tinggi (di 900 Hz, satu langkah lag ≈ 52 Hz). Tiga titik di sekitar puncak (a, b, c) dipasangkan ke parabola:")
EQ("δ = ½ (a − c) / (a − 2b + c),   F0 = f<sub>s</sub> / (l + δ)")
P("<b>Langkah 5, keputusan bersuara.</b> Frame dianggap bersuara jika tinggi puncak ≥ 0,45 dan RMS frame ≥ 10% dari "
  "RMS frame terbesar. RMS dihitung pada frame yang sama dengan F0; versi awal meleset 32 ms karena memakai frame "
  "yang berbeda.")
P("Estimator ini diuji dengan 18 unit test pada sinyal sintetis: nada murni 160–1.800 Hz dan sinyal harmonik akurat "
  "dalam 2%, nada 100 Hz (di bawah rentang) ditandai tidak bersuara, dan derau putih maupun derau low-pass hampir "
  "seluruhnya tidak bersuara (1%).")
S.append(Paragraph("4.4 Energi dan durasi", h2))
P("Pusat waktu energi adalah Σ t · RMS(t) / Σ RMS(t), dinormalisasi ke 0–1. Rentang dinamis adalah "
  "20 log<sub>10</sub>(RMS maks / RMS median) dalam dB. <b>Durasi klip sengaja tidak menjadi fitur</b>, karena terbukti "
  "menjadi jalan pintas di CryCeleb. Durasi hanya dipakai oleh baseline 'durasi saja' untuk mengukur besarnya jalan "
  "pintas itu.")

# ---------------------------------------------------------------- Bab 5
CH("Bab 5. Representasi Encoder Pretrained")
P("Dua encoder suara self-supervised dipakai tanpa fine-tuning: <b>wav2vec 2.0 base</b> (facebook/wav2vec2-base) dan "
  "<b>HuBERT base</b> (facebook/hubert-base-ls960). Keduanya dilatih pada ucapan orang dewasa berbahasa Inggris, "
  "bukan tangis bayi, sehingga pertanyaannya adalah lapisan mana yang masih berguna untuk tangis.")
S.append(Paragraph("5.1 Dari audio ke vektor per lapisan", h2))
B(["Audio 16 kHz, paling panjang 6 detik; klip yang lebih pendek dari 0,4 detik di-pad.",
   "Gelombang dinormalisasi: dikurangi rata-rata lalu dibagi simpangan baku. Ini sesuai konfigurasi resmi kedua model "
   "(<i>do_normalize = True</i>).",
   "Model menghasilkan 13 <i>hidden state</i>: keluaran proyeksi fitur CNN (L00) dan 12 lapisan transformer "
   "(L01–L12), masing-masing berdimensi 768 per frame (20 ms).",
   "Setiap lapisan dirata-rata sepanjang waktu (<i>mean pooling</i>), menghasilkan 13 vektor × 768 dimensi per klip."])
S.append(Paragraph("5.2 PCA whitening", h2))
P("768 dimensi terlalu banyak untuk data kecil. Di dalam setiap fold, data latih dipakai untuk memasang PCA ke 64 "
  "komponen dengan <i>whitening</i> (setiap komponen diskalakan ke varians 1, agar penalti L2 berlaku merata). "
  "Jika fold latih kurang dari 65 sampel (terjadi di DBL), jumlah komponen dibatasi n − 1. PCA tidak pernah melihat "
  "data uji.")

# ---------------------------------------------------------------- Bab 6
CH("Bab 6. Metode Pembobotan dan Fusi")
P("Semua metode dibangun dari satu 'bank pakar' yang sama di setiap fold. Akibatnya, perbedaan antar-metode murni "
  "berasal dari cara menggabungkan, bukan dari model dasar yang berbeda.")
S.append(Paragraph("6.1 Pakar per grup atau lapisan", h2))
P("Untuk setiap grup fitur atau lapisan g dibuat satu pipeline: imputasi median (untuk nilai pitch yang hilang) → "
  "standardisasi → (PCA whitening 64, khusus embedding) → regresi logistik multinomial. Regresi logistik memodelkan "
  "peluang kelas c sebagai:")
EQ("P(c | x) = exp(w<sub>c</sub>·x + b<sub>c</sub>) / Σ<sub>c'</sub> exp(w<sub>c'</sub>·x + b<sub>c'</sub>)")
P("Parameter dilatih dengan meminimalkan cross-entropy berbobot ditambah penalti L2 ||w||² / (2C). Nilai C dipilih dari "
  "{0,01; 0,1; 1} lewat CV dalam 3-fold yang menghormati kelompok, berdasarkan macro-F1. Jika seri, dipilih C "
  "terkecil (regularisasi terkuat).")
S.append(Paragraph("6.2 Bobot kelas", h2))
P("Bobot per sampel bergantung pada kelasnya. Untuk skema 'balanced', w<sub>c</sub> ∝ 1/n<sub>c</sub>. Untuk skema "
  "'effective number' (Cui et al., 2019) dengan β = 0,999:")
EQ("w<sub>c</sub> ∝ (1 − β) / (1 − β<super>n<sub>c</sub></super>)")
P("Satu detail penting: <b>total bobot selalu dinormalisasi menjadi n</b> (jumlah sampel). Tanpa normalisasi ini, "
  "mengganti skema bobot diam-diam juga mengubah kekuatan regularisasi. Pada versi awal, skema 'effective' "
  "menghasilkan total bobot hanya 0,64 n, setara regularisasi 1,6 kali lebih kuat, sehingga perbandingannya tidak adil.")
S.append(Paragraph("6.3 Prediksi out-of-fold", h2))
P("Agar bobot fusi tidak dipilih dengan melihat data uji, setiap pakar juga menghasilkan prediksi <i>out-of-fold</i> "
  "(OOF) pada data latih: data latih dibagi 3, model dilatih pada 2 bagian dan memprediksi bagian ketiga, bergiliran. "
  "Semua penggabung (combiner) di bawah ini hanya belajar dari prediksi OOF tersebut.")
S.append(Paragraph("6.4 Empat cara menggabungkan", h2))
P("<b>Equal (rata-rata sederhana):</b> P(c|x) = (1/G) Σ<sub>g</sub> P<sub>g</sub>(c|x). Tidak ada yang dipelajari.")
P("<b>Best single:</b> pilih satu pakar dengan macro-F1 OOF tertinggi; pakar lain diabaikan.")
P("<b>Softmax-τ:</b> setiap pakar diberi bobot sesuai performanya, dengan suhu τ yang dituning:")
EQ("w<sub>g</sub> = exp(τ · F1<sub>g</sub>) / Σ<sub>h</sub> exp(τ · F1<sub>h</sub>),   τ ∈ {0, 1, 3, 10, 30, 100, 300, 1000}")
P("τ = 0 setara equal; τ besar setara best single. Versi awal memakai τ = 10 tetap, dan ternyata bobotnya nyaris "
  "seragam (bobot terbesar 0,14, padahal bobot seragam 0,077), sehingga 'metode usulan' sebenarnya sama saja dengan "
  "rata-rata. Di versi final, τ dipilih lewat macro-F1 gabungan OOF. τ terpilih berkisar 10–300, dan bobot terbesar "
  f"rata-rata {d2.w_max.mean():.2f}.")
P("<b>Stacking (metode usulan v2):</b> regresi logistik kedua (meta-learner) dilatih pada log-peluang OOF semua pakar, "
  "yaitu vektor berdimensi G × K. Meta-learner ini belajar bobot yang berbeda untuk tiap pasangan pakar dan kelas, "
  "tetapi secara koheren di dalam satu model probabilistik. Ia menggantikan 'fusi classwise' versi awal yang tidak "
  "koheren, karena di sana tiap kelas memakai campuran pakar yang berbeda lalu skornya dibandingkan begitu saja.")
S.append(Paragraph("6.5 Baseline", h2))
TBL([["Baseline", "Cara kerja", "Untuk apa"],
     ["Last layer", "pakar dari lapisan terakhir encoder (L12)", "praktik paling umum dan paling naif"],
     ["SUPERB weighted sum", "bobot softmax per lapisan + kepala linear, dilatih end-to-end dengan Adam (300 langkah); "
      "weight decay dipilih di split dalam", "baseline standar literatur untuk pembobotan lapisan"],
     ["Concat (none/balanced/effective)", "126 fitur handcrafted digabung, satu model", "menguji pembobotan kelas (H4)"],
     ["Durasi saja", "regresi logistik pada durasi klip", "mengukur jalan pintas durasi"]],
    [3.6 * cm, 8.0 * cm, 5.0 * cm], "Tabel 6.1. Baseline pembanding.")

# ---------------------------------------------------------------- Bab 7
CH("Bab 7. Protokol Evaluasi dan Statistik")
S.append(Paragraph("7.1 Validasi silang berkelompok", h2))
P("Setiap pasangan tugas dan representasi dievaluasi dengan <i>StratifiedGroupKFold</i> 5 fold, diulang dengan 3 seed "
  "(0, 1, 2), sehingga ada 15 fold luar. 'Group' berarti semua klip dari satu bayi (atau satu klaster DBL) selalu "
  "berada di sisi yang sama, latih atau uji. Kode memeriksa hal ini dengan assertion di setiap fold.")
P("Metrik utama adalah <b>macro-F1</b>: F1 dihitung per kelas lalu dirata-rata tanpa bobot, sehingga kelas jarang "
  "sama pentingnya dengan kelas besar. F1 kelas c adalah 2 · presisi · recall / (presisi + recall).")
S.append(Paragraph("7.2 Semua yang dipelajari ada di dalam fold", h2))
P("Pemilihan C, τ, weight decay, PCA, standardisasi, imputasi, dan bobot fusi semuanya dilakukan hanya pada data latih "
  "fold tersebut (nested). Data uji fold luar hanya dipakai sekali, untuk menghitung skor akhir.")
S.append(Paragraph("7.3 Uji statistik yang benar untuk CV berulang", h2))
P("Pada CV 5-fold, dua set latih saling tumpang tindih 75%. Skor antar-fold karena itu saling bergantung, dan uji "
  "berpasangan biasa (t-test, Wilcoxon) menganggap variansnya lebih kecil dari yang sebenarnya, sehingga terlalu "
  "mudah menyatakan 'signifikan'. Uji yang dipakai adalah <b>corrected resampled t-test</b> (Nadeau dan Bengio, 2003):")
EQ("t = d̄ / √((1/k + n<sub>uji</sub>/n<sub>latih</sub>) · s²),   derajat bebas k − 1")
P("Di sini d<sub>j</sub> adalah selisih skor dua metode pada fold j, d̄ rata-ratanya, s² variansnya, k = 15, dan "
  "n<sub>uji</sub>/n<sub>latih</sub> = 1/4. Suku 1/4 inilah koreksinya. Interval kepercayaan 95% adalah "
  "d̄ ± t<sub>0,975; 14</sub> · √((1/k + 1/4) · s²).")
S.append(Paragraph("7.4 Banyak uji, koreksi Holm", h2))
P("Dengan 36 uji pada α = 0,05, rata-rata hampir 2 uji akan 'signifikan' secara kebetulan walaupun tidak ada efek. "
  "Koreksi Holm mengurutkan p-value dari terkecil, lalu membandingkan p ke-i dengan α / (m − i + 1). Ini mengendalikan "
  "peluang setidaknya satu kesimpulan palsu dalam keluarga uji.")
S.append(Paragraph("7.5 Pra-registrasi", h2))
P("Protokol, termasuk 36 hipotesis utama dan aturan keputusan, ditulis di PROTOCOL.md dan di-commit (27ae932) "
  "sebelum satu pun hasil v2 ada. Hipotesis utamanya:")
B(["<b>H1</b> (12 run): stacking vs equal.", "<b>H2</b> (12 run): stacking vs best single.",
   "<b>H3</b> (8 run embedding): stacking vs SUPERB.", "<b>H4</b> (4 run handcrafted): concat balanced vs concat tanpa bobot."])
P("Aturan keputusan: sebuah metode baru disebut lebih baik jika p setelah Holm &lt; 0,05 <b>dan</b> interval "
  "kepercayaan 95% tidak memuat nol. Semua perbandingan lain dilabeli eksploratif.")

# ---------------------------------------------------------------- Bab 8
CH("Bab 8. Hasil")
S.append(Paragraph("8.1 Skor semua metode", h2))
methods = [("equal", "Equal"), ("best_single", "Best"), ("softmax_tau", "Softmax-τ"), ("stacking", "Stacking"),
           ("superb_wsum", "SUPERB"), ("last_layer", "Last"), ("concat_balanced", "Concat"),
           ("duration_only", "Durasi")]
piv = s2.pivot_table(index=["task", "rep"], columns="method", values="macro_f1")
order = [(t, r) for t in ["cryceleb", "infantcry_dbl", "ujm_sex", "ujm_age", "ujm_axa"]
         for r in ["hand", "w2v2", "hubert"] if (t, r) in piv.index]
rows = [["Tugas", "Fitur"] + [m[1] for m in methods]]
for t, r in order:
    v = piv.loc[(t, r)]
    rows.append([TASK[t], REP[r]] + ["–" if pd.isna(v.get(m)) else f"{v[m]:.3f}" for m, _ in methods])
TBL(rows, [2.2 * cm, 2.0 * cm] + [1.55 * cm] * 8,
    "Tabel 8.1. Macro-F1 rata-rata 15 fold (v2). Acak: 0,50 untuk tugas biner, 0,20 untuk DBL, 0,33 untuk delivery.")
P("Ada tiga hal yang terlihat. Pertama, skor tugas biner rendah (0,55–0,64), jadi sinyal yang bisa ditangkap memang "
  "lemah. Kedua, kolom Equal, Best, Softmax-τ, dan Stacking hampir selalu berdekatan. Ketiga, lapisan terakhir hampir "
  "selalu lebih buruk dari metode lain.")
S.append(Paragraph("8.2 Hipotesis utama", h2))
FIG("reports/book/fig_forest.png", 15.5 * cm,
    "Gambar 8.1. Selisih macro-F1 untuk 36 hipotesis utama (titik = rata-rata, garis = CI 95% terkoreksi). Garis "
    "vertikal di nol berarti tidak ada perbedaan. Semua interval DBL sangat lebar karena datanya kecil.")
x = p2[(p2.ci_low > 0) | (p2.ci_high < 0)]
P(f"<b>Hasil: {n2} dari 36 hipotesis menunjukkan bukti.</b> Seluruh p setelah koreksi Holm bernilai 1,00. Untuk "
  "CryCeleb dan UJM, setengah lebar interval kepercayaannya hanya 0,003–0,06, jadi efek yang lebih besar dari "
  "beberapa poin bisa dikesampingkan. Untuk DBL, setengah lebarnya 0,08–0,21, sehingga DBL tidak bisa memberi "
  "kesimpulan ke arah mana pun.")
P(f"Tanpa koreksi, {len(x)} interval tidak memuat nol, semuanya kecil dan berpihak ke stacking:")
B([f"{r.hypothesis} {TASK[r.task]} {REP[r.rep]}: {r['mean']:+.3f} [{r.ci_low:+.3f}, {r.ci_high:+.3f}], p = {r.p:.3f}"
   for _, r in x.iterrows()])
P("Dari 36 uji, sekitar dua hasil seperti ini memang diharapkan muncul karena kebetulan, dan tidak satu pun bertahan "
  "setelah koreksi. Hal ini harus disebut terbuka di paper.")
S.append(Paragraph("8.3 Temuan eksploratif", h2))
eb = e2[e2.hypothesis == "E2"]
B([f"<b>Satu lapisan terbaik vs lapisan terakhir:</b> lebih baik di {int((eb.ci_low > 0).sum())} dari {len(eb)} run "
   "(tanpa koreksi). Lapisan yang terpilih hampir selalu L00–L01, yaitu lapisan paling awal dan paling 'akustik'.",
   "<b>SUPERB</b> memberi bobot terbesar pada lapisan tengah (L03–L08), tetapi skornya mirip best single.",
   "<b>Softmax-τ tidak lebih baik dari equal</b> walaupun bobotnya sekarang jelas tidak seragam. Jadi kegagalan "
   "metode bukan karena τ yang salah.",
   "<b>Semua metode mengungguli durasi saja</b>, tetapi di CryCeleb durasi saja sudah mencapai 0,55 dari skor "
   "terbaik 0,64."])
S.append(Paragraph("8.4 Analisis sensitivitas: pembersihan data (v3)", h2))
P("Setelah v2, pemindaian kualitas audio menemukan hubungan antara sample rate dan label di DBL (χ² p = 0,0001), "
  "clipping di DBL, dan klip ber-SNR rendah di UJM. Kriteria pembersihan dibekukan dulu (commit 228d42b), lalu "
  "seluruh pipeline dijalankan ulang tanpa perubahan lain:")
B(["semua audio dipotong ke pita 0–4 kHz (resample ke 8 kHz lalu kembali ke 16 kHz);",
   "klip dibuang jika lebih dari 0,1% sampelnya clipping, atau lebih dari 50% frame 25 ms-nya sunyi (di bawah −60 dBFS);",
   "klip UJM dengan SNR resmi di bawah 10 dB dibuang.",
   "Total 497 klip dibuang: CryCeleb 101, DBL 9, UJM 387."])
FIG("reports/book/fig_v2_v3.png", 15 * cm,
    "Gambar 8.2. Skor metode terbaik sebelum (lingkaran biru) dan sesudah pembersihan (kotak oranye). Label angka "
    "hanya untuk perubahan ≥ 0,03; nilai lengkap ada di Tabel 8.2.")
keep = ["equal", "best_single", "softmax_tau", "stacking", "superb_wsum", "last_layer", "concat_balanced"]
best = lambda d: d[d.method.isin(keep)].groupby(["task", "rep"]).macro_f1.max()  # noqa: E731
cmp_ = pd.concat([best(s2).rename("v2"), best(s3).rename("v3")], axis=1)
rows = [["Tugas", "Fitur", "Terbaik v2", "Terbaik v3", "Selisih"]]
for t, r in order:
    if (t, r) in cmp_.index:
        a, b = cmp_.loc[(t, r)]
        rows.append([TASK[t], REP[r], f"{a:.3f}", f"{b:.3f}", f"{b - a:+.3f}"])
TBL(rows, [3.2 * cm, 2.6 * cm, 3.2 * cm, 3.2 * cm, 2.6 * cm], "Tabel 8.2. Skor terbaik v2 vs v3.")
P(f"Hasil v3: {n3} dari 36 hipotesis menunjukkan bukti, sama seperti v2. CryCeleb dan UJM hanya bergeser ±0,02, "
  "jadi skor rendah bukan disebabkan kualitas audio. DBL turun 0,02–0,10. Penyebabnya bisa harmonik di atas 4 kHz yang "
  "ikut terbuang, artefak lebar pita rekaman, atau data yang makin kecil, dan ketiganya tidak bisa dipisahkan. Sample "
  "rate saja tidak bisa menebak kelas (macro-F1 0,197, acak 0,20), jadi penurunannya bukan sekadar jalan pintas "
  "sample rate.")

# ---------------------------------------------------------------- Bab 9
CH("Bab 9. Perjalanan Riset dan Pelajarannya")
P("Paper 4 tidak lahir lurus. Bab ini mencatat apa yang salah, bagaimana ketahuan, dan apa pelajarannya. Bagian ini "
  "penting justru karena jujur: reviewer menghargai peneliti yang tahu kelemahan versi awalnya.")
S.append(Paragraph("9.1 Versi 1: hasil yang terlihat menjanjikan", h2))
P("Versi awal memakai DBL 'bersih' versi metadata (237 klip, satu klip satu grup), fitur dengan estimator F0 lama, "
  "bobot τ = 10, dan uji Wilcoxon. Hasilnya terlihat bagus: macro-F1 DBL 0,852, dan banyak perbandingan 'signifikan'.")
S.append(Paragraph("9.2 Audit supervisor", h2))
P("Seluruh kode lalu diaudit dengan sikap supervisor yang kritis, dan setiap dugaan diuji secara numerik. Temuan "
  "utamanya:")
TBL([["Temuan", "Bukti", "Perbaikan"],
     ["Wilcoxon pada fold yang saling bergantung", "19/78 'signifikan'; setelah koreksi + Holm tinggal 1",
      "Nadeau–Bengio + Holm + CI"],
     ["Duplikat DBL", "skor turun 0,852 → 0,818 saat klip mirip dikelompokkan", "deduplikasi + klaster"],
     ["Kontaminasi DBL", "107 salinan dari Dunstan dan CryCeleb", "133 klip dibuang"],
     ["Bobot τ = 10 nyaris seragam", "bobot maks 0,14 (seragam 0,077)", "τ dituning; stacking"],
     ["MFCC = DCT(mel)", "R² = 1,000000", "grup mel diganti simpangan baku"],
     ["F0 salah", "1.200 Hz → 400 Hz, keyakinan 0,99", "estimator baru + 18 unit test"],
     ["Jalan pintas durasi", "durasi saja 0,55 di CryCeleb", "durasi bukan fitur; baseline durasi"],
     ["Bobot 'effective' ubah regularisasi", "total bobot 0,64 n", "normalisasi Σw = n"],
     ["Baseline lemah", "tidak ada SUPERB; C tidak dituning", "SUPERB + tuning C untuk semua"],
     ["Protokol tidak seragam", "1, 2, atau 3 seed", "5 fold × 3 seed untuk semua"]],
    [4.4 * cm, 6.4 * cm, 5.8 * cm], "Tabel 9.1. Temuan audit dan perbaikannya.")
FIG("reports/book/fig_dbl_inflation.png", 15 * cm,
    "Gambar 9.1. Skor DBL turun setiap kali satu celah evaluasi ditutup. Antara v1 dan v2, fitur dan metodenya juga "
    "berubah, jadi tiap langkah bukan efek data murni. Polanya tetap jelas: sebagian besar skor awal adalah ilusi "
    "evaluasi.")
S.append(Paragraph("9.3 Keputusan yang dipicu hasil (forking paths)", h2))
P("Ada dua keputusan di v1 yang diambil <b>setelah</b> melihat hasil jelek: tugas UJM diganti (persalinan → jenis "
  "kelamin/usia), dan pendekatan beralih ke embedding. Keduanya disetujui, tetapi tetap termasuk 'garden of forking "
  "paths', yaitu banyak jalan yang dicoba sampai ada yang terlihat berhasil. Penangkalnya adalah pra-registrasi v2 "
  "dan v3, serta pengungkapan terbuka di paper. Satu-satunya run v2 yang pernah diulang memberi hasil identik sampai "
  "digit terakhir, dan tidak ada run yang dibuang.")
S.append(Paragraph("9.4 Sepuluh pelajaran", h2))
B(["Bagi data per subjek (bayi), bukan per klip.",
   "Audit duplikat di dalam dan antar-korpus sebelum menghitung skor.",
   "Jangan percaya metadata sumber tanpa verifikasi audio.",
   "Semua bobot dan hyperparameter harus dipilih di dalam fold latih.",
   "Pakai uji statistik yang sesuai untuk CV berulang, dan koreksi untuk banyak uji.",
   "Uji estimator sinyal (seperti F0) pada sinyal sintetis yang jawabannya diketahui.",
   "Periksa redundansi matematis antar-grup fitur sebelum 'membobot' grup.",
   "Selalu sertakan baseline jalan pintas (durasi, sample rate).",
   "Bekukan protokol sebelum melihat hasil, lalu catat setiap deviasi.",
   "Laporkan hasil negatif dengan jujur, karena itu juga kontribusi ilmiah."])

# ---------------------------------------------------------------- Bab 10
CH("Bab 10. Menulis, Mengirim, dan Mempertahankan Paper 4")
S.append(Paragraph("10.1 Bingkai paper", h2))
P("Paper 4 adalah <b>paper hasil negatif dengan evaluasi bebas kebocoran</b>, ditambah <b>audit provenance</b> sebuah "
  "dataset publik. Judul draf: <i>Does Weighting Help Infant Cry Classification? A Leakage-Controlled Evaluation of "
  "Class, Feature-Group and Layer Weighting, with a Provenance Audit of a Public Cry Corpus</i>. Drafnya ada di "
  "reports/paper4_manuscript_draft.pdf.")
S.append(Paragraph("10.2 Klaim yang boleh dan tidak boleh", h2))
TBL([["Boleh ditulis", "Jangan ditulis"],
     ["Tidak ada bukti bahwa pembobotan/fusi mengungguli rata-rata sederhana (0/36, setelah koreksi)",
      "'Metode usulan lebih baik'"],
     ["Kesimpulan kokoh terhadap pembersihan data (v3)", "Macro-F1 DBL ≈ 0,85"],
     ["107/236 klip DBL online/volunteer adalah salinan", "'Multi-lapisan signifikan lebih baik dari lapisan terakhir'"],
     ["Satu lapisan awal terpilih cenderung lebih baik dari lapisan terakhir (eksploratif)",
      "Klaim generalisasi ke semua dataset tangis"]],
    [8.3 * cm, 8.3 * cm], "Tabel 10.1. Batas klaim.")
S.append(Paragraph("10.3 Target jurnal dan biaya", h2))
P("Draf menargetkan <i>Signal, Image and Video Processing</i> (Springer, Q2). Jalur subscription tidak memungut biaya "
  "publikasi (APC). Alternatifnya <i>Circuits, Systems, and Signal Processing</i>. Paper hasil negatif dengan "
  "metodologi kuat bisa diterima, tetapi peluangnya tidak bisa dijamin. Pastikan memilih opsi non-open-access saat "
  "submit agar tidak muncul APC.")
S.append(Paragraph("10.4 Pertanyaan reviewer yang mungkin muncul", h2))
for q, a in [
    ("Mengapa tidak fine-tuning encoder? Mungkin pembobotan baru membantu di sana.",
     "Benar, ini keterbatasan yang diakui. Studi ini menguji praktik paling umum (fitur beku + model linear). "
     "Fine-tuning pada data sekecil ini juga rawan overfitting, dan evaluasinya memerlukan nested CV yang jauh lebih "
     "mahal."),
    ("Dengan data sekecil DBL, wajar tidak ada yang signifikan.",
     "Setuju untuk DBL, dan paper menyatakannya. Namun CryCeleb (626 bayi) dan UJM (300 bayi) punya interval "
     "kepercayaan sempit (±0,003–0,06), sehingga efek besar memang tidak ada di sana."),
    ("Apakah koreksi Nadeau–Bengio terlalu konservatif?",
     "Bahkan tanpa koreksi Holm, hanya 3 dari 36 interval yang tidak memuat nol, sesuai yang diharapkan dari kebetulan. "
     "Kesimpulannya tidak bergantung pada pilihan koreksi."),
    ("Ambang kosinus 0,95 untuk deteksi salinan terasa arbitrer.",
     "107 klip memiliki kosinus ≥ 0,999, jadi praktis identik. Ambang 0,95 hanya menambah 26 klip, dan ditetapkan "
     "sebelum hasil v2 ada."),
    ("Mengapa tugas UJM diganti?",
     "Diungkapkan terbuka: tugas persalinan setara acak, lalu diganti. Tugas baru ditetapkan sebelum hasilnya dilihat, "
     "dan hasil tugas persalinan tetap dilaporkan sebagai tugas tambahan."),
    ("Apa hubungannya dengan Paper 1?",
     "Paper 4 memakai korpus berbeda; bagian DBL yang ternyata berasal dari Dunstan sudah dibuang. Sebutkan relasinya "
     "sesuai kebijakan tumpang tindih jurnal.")]:
    P(f"<b>T:</b> {q}<br/><b>J:</b> {a}")
S.append(Paragraph("10.5 Daftar periksa sebelum submit", h2))
B(["Lengkapi nama penulis, afiliasi, pendanaan, konflik kepentingan, dan kontribusi penulis.",
   "Tulis pernyataan penggunaan AI sesuai kebijakan jurnal.",
   "Verifikasi setiap referensi ke sumber aslinya, terutama daftar penulis CryCeleb dan record Zenodo UJM.",
   "Publikasikan repositori (atau arsip Zenodo) dan cantumkan URL-nya.",
   "Pastikan lisensi CryCeleb (non-komersial) dipatuhi: jangan sebarkan audio, cukup kode dan hasil.",
   "Pilih jalur subscription agar bebas APC."])

# ---------------------------------------------------------------- Bab 11
CH("Bab 11. Panduan Reproduksi")
P("Semua langkah dijalankan dari akar repositori. Data mentah tidak ikut di-commit dan harus diunduh ulang.")
CODE("pip install -r requirements.lock   # Python 3.13\n"
     "export PYTHONPATH=src HF_HUB_DISABLE_XET=1\n"
     "python -m pytest -q tests          # 26 test harus lolos\n"
     "python scripts/download_ujm_subset.py\n"
     "python scripts/prepare_dbl.py      # audit + manifest DBL\n"
     "for t in infantcry_dbl ujm_sex ujm_age ujm_axa cryceleb; do\n"
     "  python scripts/extract_features.py $t; done\n"
     "for m in w2v2 hubert; do for p in infantcry_dbl ujm_axa cryceleb; do\n"
     "  python scripts/extract_embeddings.py $m $p; done; done\n"
     "for r in hand w2v2 hubert; do for t in infantcry_dbl ujm_age ujm_sex cryceleb; do\n"
     "  python scripts/run_v2.py $t $r; done; done\n"
     "python scripts/analyze_v2.py results/v2\n"
     "# sensitivitas v3: scripts/quality_v3.py, lalu argumen tambahan 'v3' pada ekstraksi dan run")
S.append(Paragraph("11.1 Catatan lingkungan", h2))
B(["CryCeleb memerlukan token Hugging Face dan persetujuan lisensi.",
   "Di balik proxy sesi ini, unduhan Hugging Face memerlukan HF_HUB_DISABLE_XET=1.",
   "librosa.yin mengalami segfault di lingkungan ini, jadi estimator F0 ditulis murni dengan numpy.",
   "Zenodo membatasi laju unduhan (HTTP 429); pembaca zip jarak jauh sudah memakai backoff.",
   "Waktu jalan: run handcrafted beberapa detik, run embedding CryCeleb sekitar 8 menit (4 core)."])
S.append(Paragraph("11.2 Struktur repositori", h2))
TBL([["Lokasi", "Isi"],
     ["src/infantcry/", "data.py, features.py, fusion.py, stats.py, evaluate.py, remote_zip.py"],
     ["scripts/", "unduh, prepare_dbl, quality_v3, extract_features, extract_embeddings, run_v2, analyze_v2"],
     ["tests/", "unit test F0, band-limit, bobot, statistik, combiner"],
     ["results/v2, results/v3", "hasil per fold, prediksi, diagnostik, uji hipotesis, ringkasan"],
     ["results/v1", "hasil lama yang sudah digantikan (arsip)"],
     ["reports/", "laporan supervisi, laporan perbaikan, draf manuskrip, buku ini"],
     ["PROTOCOL.md", "protokol v2 dan v3 yang dibekukan, beserta deviasinya"]],
    [4.4 * cm, 12.2 * cm], "Tabel 11.1. Peta repositori.")

# ---------------------------------------------------------------- Lampiran
CH("Lampiran A. Glosarium")
for k, v in [
    ("Macro-F1", "rata-rata F1 semua kelas tanpa bobot; adil untuk kelas jarang."),
    ("Kelompok CV (group)", "unit yang tidak boleh terbelah antara data latih dan uji, di sini bayi atau klaster klip."),
    ("Kebocoran (leakage)", "informasi data uji yang ikut masuk ke pelatihan, sehingga skor tampak lebih bagus."),
    ("Nested CV", "CV di dalam CV: lapisan dalam untuk memilih hyperparameter, lapisan luar untuk menilai."),
    ("Out-of-fold (OOF)", "prediksi untuk sampel yang tidak dipakai melatih model yang memprediksinya."),
    ("Stacking", "model kedua yang belajar menggabungkan prediksi beberapa model pertama."),
    ("Softmax-τ", "bobot berbentuk softmax dari skor, dengan suhu τ yang mengatur seberapa tajam pilihannya."),
    ("SUPERB weighted sum", "jumlahan berbobot lapisan encoder yang dipelajari bersama kepala klasifikasi."),
    ("Hidden state / lapisan", "representasi antara di dalam encoder; wav2vec2 dan HuBERT base punya 13."),
    ("PCA whitening", "proyeksi ke komponen utama dengan varians tiap komponen disamakan menjadi 1."),
    ("Corrected resampled t-test", "uji t dengan varians dikoreksi untuk set latih yang tumpang tindih."),
    ("Holm", "koreksi untuk banyak uji yang mengendalikan peluang setidaknya satu kesimpulan palsu."),
    ("Pra-registrasi", "menetapkan hipotesis dan analisis sebelum melihat hasil."),
    ("Forking paths", "mencoba banyak jalur analisis lalu melaporkan yang 'berhasil'."),
    ("F0", "frekuensi dasar, persepsi tinggi-rendahnya nada."),
    ("Hyperphonation", "tangis dengan F0 sangat tinggi, di atas sekitar 1 kHz."),
    ("Band-limiting", "membuang isi frekuensi di atas batas tertentu (di sini 4 kHz)."),
    ("SNR", "rasio sinyal terhadap derau, dalam dB."),
    ("Provenance", "asal-usul data; audit provenance memeriksa apakah sumbernya benar.")]:
    P(f"<b>{k}</b> — {v}")
S.append(Paragraph("Lampiran B. Dokumen terkait", ch))
B(["reports/supervisor_review.pdf — audit kritis versi 1.",
   "reports/v2_fixes_and_results.pdf — status perbaikan, hasil v2, dan sensitivitas v3.",
   "reports/paper4_manuscript_draft.pdf — draf manuskrip bahasa Inggris.",
   "PROTOCOL.md — protokol yang dibekukan.",
   "DATASETS.md — catatan dataset dan lisensi."])
S.append(Paragraph("Lampiran C. Referensi utama", ch))
for r in ["Baevski dkk. (2020) wav2vec 2.0. NeurIPS 33.",
          "Hsu dkk. (2021) HuBERT. IEEE/ACM TASLP 29:3451–3460.",
          "Yang dkk. (2021) SUPERB. Interspeech 2021.",
          "Cui dkk. (2019) Class-balanced loss based on effective number of samples. CVPR 2019.",
          "Wolpert (1992) Stacked generalization. Neural Networks 5(2):241–259.",
          "Nadeau &amp; Bengio (2003) Inference for the generalization error. Machine Learning 52:239–281.",
          "Bouckaert &amp; Frank (2004) Evaluating the replicability of significance tests. PAKDD 2004.",
          "Holm (1979) A simple sequentially rejective multiple test procedure. Scand J Stat 6(2):65–70.",
          "Boersma (1993) Accurate short-term analysis of the fundamental frequency. IFA Proceedings 17:97–110.",
          "CryCeleb2023: arXiv:2305.00969.", "BABYCRY-UJM-AXA: doi:10.5281/zenodo.19205929.",
          "InfantCry-DBL: doi:10.17632/x493z8nmwc.2."]:
    S.append(Paragraph(r, bul, bulletText="•"))
P("Verifikasi detail setiap referensi ke sumber aslinya sebelum dikutip di paper.", cap)

doc = Doc("reports/book/paper4_buku.pdf", pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
          topMargin=2 * cm, bottomMargin=2 * cm, title="Paper 4 dalam Satu Buku", author="microasa")
doc.multiBuild(S, onFirstPage=footer, onLaterPages=footer)
print("written reports/book/paper4_buku.pdf")
