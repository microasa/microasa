"""Buku defense Paper 4. Run from the repo root:  python3 reports/defense/build_book4_defense.py
Key numbers are read from results/v2 and results/v3."""
import sys
from pathlib import Path

import pandas as pd
from reportlab.lib.units import cm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from defense_common import Book  # noqa: E402

p2, p3 = pd.read_csv("results/v2/primary_tests.csv"), pd.read_csv("results/v3/primary_tests.csv")
s2 = pd.read_csv("results/v2/summary.csv")
e2 = pd.read_csv("results/v2/exploratory_tests.csv")
n2, n3 = int((p2.verdict != "no evidence").sum()), int((p3.verdict != "no evidence").sum())
unadj = p2[(p2.ci_low > 0) | (p2.ci_high < 0)]
keep = ["equal", "best_single", "softmax_tau", "stacking", "superb_wsum", "last_layer", "concat_balanced"]
best = s2[s2.method.isin(keep)].groupby(["task", "rep"]).macro_f1.max()
hw = ((p2.ci_high - p2.ci_low) / 2).groupby(p2.task == "infantcry_dbl").agg(["min", "max"])
eb = e2[e2.hypothesis == "E2"]


def r(t):
    return f"{best[t].min():.2f}–{best[t].max():.2f}"


bk = Book("Buku Defense Paper 4 · pembobotan pada klasifikasi tangis bayi")
bk.cover("Buku Defense Paper 4",
         "Does Weighting Help Infant Cry Classification? A Leakage-Controlled Evaluation of Class, Feature-Group "
         "and Layer Weighting, with a Provenance Audit of a Public Cry Corpus",
         ["Panduan mempertahankan Paper 4 di depan penguji disertasi",
          "Pendamping: reports/book/paper4_buku.pdf (buku teknis lengkap)",
          "Semua angka hasil dibaca langsung dari results/v2 dan results/v3", "November 2026"])

bk.CH("Bab 1. Ringkasan Tiga Menit")
bk.BOX("<b>Masalah.</b> Pembobotan (kelas, grup fitur, lapisan encoder) sering dilaporkan meningkatkan klasifikasi "
       "tangis bayi, tetapi biasanya pada data kecil, pembagian per klip, dan bobot yang dipilih tanpa memisahkan data "
       "uji.<br/><br/>"
       "<b>Pertanyaan.</b> Apakah pembobotan membantu jika evaluasinya bebas kebocoran?<br/><br/>"
       "<b>Desain.</b> Tiga korpus publik (CryCeleb2023, BABYCRY-UJM-AXA, InfantCry-DBL yang dibersihkan), fitur "
       "akustik dan embedding wav2vec2/HuBERT, lima cara menggabungkan, CV 5-fold × 3 berkelompok per bayi, semua bobot "
       "dan hyperparameter dipilih di dalam fold, 36 hipotesis pra-registrasi, uji Nadeau–Bengio dan koreksi Holm."
       "<br/><br/>"
       f"<b>Hasil.</b> {n2} dari 36 hipotesis menunjukkan bukti. Setelah pembersihan data (v3), tetap {n3}/36. Audit "
       "provenance menemukan 107 dari 236 klip DBL 'online/volunteer' adalah salinan klip Dunstan atau CryCeleb.<br/><br/>"
       "<b>Makna.</b> Di bawah evaluasi yang benar, pembobotan tidak menambah nilai di atas rata-rata sederhana atau "
       "pemilihan satu lapisan. Dataset publik harus diaudit asal-usulnya sebelum klaim peningkatan dibuat.")
bk.H2("Lima kalimat yang wajib hafal")
bk.B([f"'Dari 36 perbandingan yang ditetapkan di muka, {n2} menunjukkan bukti, dan hasil ini bertahan setelah data "
      "dibersihkan.'",
      "'Semua bobot, termasuk suhu softmax dan C, dipilih hanya dari data latih setiap fold.'",
      "'Hampir separuh klip DBL yang diklaim independen ternyata salinan dari korpus lain.'",
      "'Skor DBL turun dari 0,85 ke 0,77, lalu 0,67, setiap kali satu celah evaluasi ditutup.'",
      "'Yang konsisten hanya satu pola eksploratif: satu lapisan awal yang dipilih lewat CV cenderung mengungguli "
      "lapisan terakhir.'"])

bk.CH("Bab 2. Posisi Paper 4 dalam Disertasi")
bk.P("Paper 4 melanjutkan Paper 1, yang pembobotannya gagal (rinciannya di Buku Defense Paper 1, yang sengaja tidak "
     "disimpan di repositori publik ini). Paper 4 bertanya apakah pembobotan gagal hanya karena data Paper 1, dengan "
     "menguji tiga korpus lain di bawah evaluasi yang ketat.")
bk.BOX("<b>Benang merah disertasi:</b> peningkatan yang dilaporkan dalam klasifikasi tangis bayi tidak terulang di bawah "
       "evaluasi yang mengendalikan kebocoran. Hambatan utamanya adalah data dan label, bukan arsitektur atau skema "
       "pembobotan. Paper 1 membuktikannya dengan kontrol positif; Paper 4 dengan pra-registrasi lintas korpus dan audit "
       "provenance.")
bk.P("Jika Paper 1 memakai pendekatan statistik yang berbeda dari Paper 4 (lihat Buku Defense Paper 1), tonjolkan bahwa "
     "kesimpulan yang konsisten di bawah dua pendekatan berbeda justru memperkuat tesis.")

bk.CH("Bab 3. Konsep Teknis yang Wajib Dikuasai")
bk.P("Penjelasan rinci ada di buku teknis (paper4_buku.pdf, Bab 4–7). Berikut versi ringkas untuk sidang.")
bk.H2("3.1 Tiga tingkat pembobotan")
bk.B(["<b>Kelas:</b> bobot sampel ∝ 1/n<sub>c</sub> (balanced) atau (1−β)/(1−β<super>n<sub>c</sub></super>) "
      "(effective number), selalu dinormalisasi agar total = n.",
      "<b>Grup fitur:</b> enam grup handcrafted (MFCC, delta, spektral, pitch, energi, simpangan baku log-mel).",
      "<b>Lapisan:</b> 13 hidden state wav2vec2 dan HuBERT, dirata-rata sepanjang waktu, PCA whitening 64 di dalam fold."])
bk.H2("3.2 Lima cara menggabungkan")
bk.TBL([["Metode", "Rumus atau cara", "Peran"],
        ["Equal", "P = (1/G) Σ P<sub>g</sub>", "baseline paling sederhana"],
        ["Best single", "pilih pakar dengan macro-F1 OOF tertinggi", "pemilihan keras"],
        ["Softmax-τ", "w<sub>g</sub> ∝ exp(τ F1<sub>g</sub>), τ dituning", "versi pembobotan yang diperbaiki"],
        ["Stacking (usulan v2)", "regresi logistik pada log-peluang OOF semua pakar", "bobot per pakar × kelas yang koheren"],
        ["SUPERB", "bobot softmax lapisan + kepala linear, dilatih end-to-end", "baseline standar literatur"]],
       [3.0 * cm, 8.4 * cm, 5.2 * cm], "Tabel 3.1. Metode yang dibandingkan.")
bk.H2("3.3 Uji Nadeau–Bengio")
bk.EQ("t = d̄ / √((1/k + n<sub>uji</sub>/n<sub>latih</sub>) · s²),   k = 15,   n<sub>uji</sub>/n<sub>latih</sub> = 1/4")
bk.P("Suku 1/4 mengoreksi varians karena set latih antar-fold tumpang tindih 75%. Tanpa koreksi ini, 19 dari 78 "
     "perbandingan di versi awal tampak 'signifikan'. Setelah koreksi dan Holm, tinggal 1.")
bk.H2("3.4 Estimator F0")
bk.P("Autokorelasi dibagi autokorelasi jendela (Boersma, 1993), puncak lokal dengan lag terpendek ≥ 0,9 × tertinggi, "
     "interpolasi parabolik, rentang 150–2.000 Hz. Diuji dengan unit test pada sinyal sintetis. Versi awal membaca "
     "1.200 Hz sebagai 400 Hz; versi final membacanya 1.200,3 Hz.")

bk.CH("Bab 4. Angka yang Wajib Hafal")
bk.TBL([["Hal", "Angka"],
        ["Tugas dan data", "CryCeleb 4.954 klip / 626 bayi; UJM-sex 1.762 / 300; UJM-age 1.176 / 247; DBL 103 klip / 86 klaster"],
        ["Hipotesis primer", f"v2: {n2}/36 bukti; v3: {n3}/36 bukti; semua p setelah Holm = 1,00"],
        ["Tanpa koreksi", f"{len(unadj)} dari 36 CI tidak memuat nol (selisih +0,015 sampai +0,043)"],
        ["Lebar CI (setengah)", f"CryCeleb/UJM {hw.loc[False, 'min']:.3f}–{hw.loc[False, 'max']:.2f}; "
                                f"DBL {hw.loc[True, 'min']:.2f}–{hw.loc[True, 'max']:.2f}"],
        ["Skor terbaik v2", f"CryCeleb {r('cryceleb')}; UJM-sex {r('ujm_sex')}; UJM-age {r('ujm_age')}; DBL {r('infantcry_dbl')}"],
        ["Durasi saja (CryCeleb)", "0,55 (acak 0,50)"],
        ["Kontaminasi DBL", "107 salinan (41 Dunstan, 66 CryCeleb) + 26 hampir salinan; 133 dibuang"],
        ["Skor DBL per tahap", "0,852 → 0,818 → 0,768 → 0,665"],
        ["Pembersihan v3", "497 klip dibuang (CryCeleb 101, DBL 9, UJM 387)"],
        ["Satu lapisan vs terakhir", f"lebih baik di {int((eb.ci_low > 0).sum())} dari {len(eb)} run (eksploratif)"],
        ["Sample rate saja (DBL)", "0,197 (acak 0,20)"]],
       [4.6 * cm, 12.0 * cm], "Tabel 4.1. Lembar contekan angka kunci.")

bk.CH("Bab 5. Bank Pertanyaan Penguji")
bk.H2("5.1 Kebaruan dan kontribusi")
bk.QA("Hasil Anda negatif lagi, sama seperti Paper 1. Apa kontribusi positifnya?",
      "Tiga hal: (1) bukti terkendali bahwa pembobotan tidak menambah nilai di tiga korpus dengan 36 uji pra-registrasi; "
      "(2) audit provenance yang menemukan 107 salinan di dataset publik, temuan yang relevan bagi siapa pun yang "
      "memakai InfantCry-DBL; (3) protokol dan kode terbuka yang bisa dipakai ulang. Bersama Paper 1, ini membentuk "
      "satu argumen: hambatan bidang ini adalah data, bukan model.",
      "hasil negatif yang sahih adalah kontribusi ilmiah, terutama di bidang dengan klaim yang menggelembung.")
bk.QA("Kenapa memilih stacking sebagai metode usulan?",
      "Versi awal memakai fusi per kelas dengan softmax, yang tidak koheren secara probabilistik dan bobotnya nyaris "
      "seragam. Stacking adalah cara yang benar untuk mempelajari bobot per pakar dan per kelas di dalam satu model. "
      "Pergantian ini ditetapkan di protokol v2 sebelum hasil v2 ada.")
bk.QA("Apakah metode Anda gagal karena salah implementasi?",
      "Ada tiga hal yang menepis kemungkinan itu: unit test untuk combiner menunjukkan pakar yang informatif dipilih "
      "dengan benar; bobot softmax yang dituning sudah tidak seragam (bobot terbesar 0,22–0,71); dan semua metode "
      "mengungguli baseline durasi saja dan peluang acak. Jadi pipeline bekerja, tetapi pembobotan tidak menambah apa-apa.")
bk.H2("5.2 Data")
bk.QA("Bagaimana Anda tahu 107 klip DBL itu salinan?",
      "Setiap kandidat dibandingkan dengan 337 klip Tier 1 dan 26.093 klip CryCeleb memakai kosinus vektor fitur yang "
      "di-z-score. 107 klip punya kosinus ≥ 0,999, praktis identik. Kolom source_confirmed juga False untuk seluruh "
      "1.214 klip Tier 2.",
      "sebutkan bahwa ambang 0,95 ditetapkan sebelum hasil v2.")
bk.QA("Kenapa tugas UJM diganti di tengah jalan?",
      "Tugas cara persalinan setara acak (0,35 untuk tiga kelas). Penggantian ke jenis kelamin dan usia adalah keputusan "
      "yang dipicu hasil, dan saya akui terbuka. Tugas baru ditetapkan sebelum hasilnya dilihat, dan hasil persalinan "
      "tetap dilaporkan sebagai tugas tambahan.",
      "jangan menyembunyikan; keterbukaan meredam kecurigaan forking paths.")
bk.QA("Label B vs D di CryCeleb bukankah lebih tentang kondisi rekaman?",
      "Bisa jadi, dan itu kami ukur: durasi saja memberi 0,55. Durasi sudah dihapus dari fitur, dan semua metode "
      "mengungguli baseline durasi. Confound kondisi rekaman tetap tidak bisa dikendalikan dengan metadata yang ada, "
      "dan ini kami tulis sebagai keterbatasan.")
bk.QA("Kenapa ID anonim CryCeleb dibuang?",
      "Split uji kompetisi memberi ID berbeda untuk dua periode bayi yang sama, sehingga pengelompokan per ID tidak "
      "mencegah kebocoran. Tersisa 626 bayi ber-ID asli.")
bk.H2("5.3 Metode dan statistik")
bk.QA("Kenapa Nadeau–Bengio, bukan uji permutasi atau bootstrap?",
      "Keduanya sah untuk CV berkelompok. Nadeau–Bengio dipilih karena membandingkan banyak metode pada fold yang sama "
      "dengan biaya rendah dan memperhitungkan tumpang tindih set latih. Uji permutasi berbasis grup bisa ditambahkan "
      "sebagai analisis sensitivitas bila penguji memintanya.")
bk.QA("Dengan 36 uji, bukankah Holm terlalu konservatif?",
      f"Bahkan tanpa Holm, hanya {len(unadj)} dari 36 CI yang tidak memuat nol. Ini sesuai yang diharapkan dari kebetulan "
      "(sekitar 2 dari 36). Kesimpulan tidak bergantung pada pilihan koreksi.")
bk.QA("DBL hanya 103 klip. Apa gunanya?",
      f"Untuk uji metode, DBL memang tidak informatif: setengah lebar CI-nya {hw.loc[True, 'min']:.2f}–"
      f"{hw.loc[True, 'max']:.2f}. Kesimpulan utama bertumpu pada CryCeleb dan UJM, yang CI-nya sempit. Nilai DBL ada "
      "pada audit provenance dan pada ilustrasi bagaimana skor menggelembung.")
bk.QA("Kenapa encoder tidak di-fine-tune?",
      "Studi ini menguji praktik paling umum (fitur beku + model linear). Fine-tuning pada data sekecil ini rawan "
      "overfitting dan membutuhkan nested CV yang jauh lebih mahal. Ini keterbatasan yang kami nyatakan.")
bk.QA("Kenapa ada PCA 64 dimensi? Bukankah itu membuang informasi?",
      "768 dimensi terlalu banyak untuk ratusan bayi. PCA dipasang hanya pada data latih fold, dengan whitening agar "
      "penalti L2 merata. Di DBL, jumlah komponen dibatasi n−1, dan ini dicatat sebagai deviasi protokol.")
bk.H2("5.4 Integritas proses")
bk.QA("Apakah Anda mengulang eksperimen sampai hasilnya bagus?",
      "Tidak. Protokol v2 di-commit (27ae932) sebelum hasil v2 ada, dan v3 (228d42b) sebelum hasil v3 ada. Satu-satunya "
      "run v2 yang diulang memberi hasil identik sampai digit terakhir. Semua hasil v1 diarsipkan, tidak dibuang. "
      "Setiap file hasil menyimpan hash commit kode yang menghasilkannya.",
      "tunjukkan riwayat git sebagai bukti.")
bk.QA("Apa peran AI dalam pekerjaan ini?",
      "Kode dan eksperimen dikerjakan oleh agen AI di bawah arahan saya, termasuk audit kritis yang menemukan "
      "kesalahan versi awal. Keputusan riset dan interpretasi adalah tanggung jawab saya. [Lengkapi sesuai praktik "
      "Anda.]",
      "Anda harus bisa menjelaskan setiap rumus dan keputusan tanpa bantuan.")
bk.QA("Versi awal Anda melaporkan 0,85 di DBL. Bukankah itu berarti ada kesalahan?",
      "Ya, dan itu ditemukan lewat audit sendiri sebelum dikirim. Skor itu hasil duplikat dan kontaminasi lintas korpus. "
      "Kami menjadikannya ilustrasi di paper: skor turun setiap kali satu celah ditutup.")

bk.CH("Bab 6. Kelemahan yang Pasti Ditanyakan")
bk.TBL([["Kelemahan", "Cara mengakui"],
        ["DBL kecil (103 klip)", "'DBL tidak dipakai untuk menyimpulkan efek metode; nilainya ada di audit.'"],
        ["Overlap DBL dengan data Paper 1 belum dicek langsung", "'Kami membuang salinan Tier 1 Dunstan; pencocokan dengan "
         "berkas Paper 1 akan dilakukan dengan data asli Paper 1.'"],
        ["Confound kondisi rekaman CryCeleb", "'Diukur lewat baseline durasi; tidak bisa dihilangkan dengan metadata yang ada.'"],
        ["UJM hanya subset 300 bayi", "'Subset deterministik; ukuran cukup untuk CI sempit (±0,06).'"],
        ["Tugas UJM diganti setelah hasil", "'Diungkapkan terbuka; tugas baru ditetapkan di muka.'"],
        ["Encoder tidak di-fine-tune", "'Praktik paling umum; fine-tuning di luar cakupan.'"],
        ["Penurunan DBL di v3 tidak bisa dijelaskan", "'Kami tidak mengklaim penyebabnya; tiga kemungkinan disebutkan.'"]],
       [5.6 * cm, 11.0 * cm], "Tabel 6.1. Kelemahan dan cara mengakuinya.")
bk.H2("Kalimat yang jangan pernah diucapkan")
bk.B(["'Metode usulan lebih baik.'", "'Multi-lapisan signifikan lebih baik dari lapisan terakhir.'",
      "'DBL mencapai 0,85.'", "'Pembobotan tidak pernah berguna.' (Yang benar: tidak terbukti di tiga korpus ini.)",
      "'Dataset DBL palsu.' (Yang benar: metadata sumbernya tidak bisa dipercaya untuk 133 klip.)"])

bk.CH("Bab 7. Alur Presentasi 15 Menit")
bk.TBL([["Menit", "Slide", "Isi"],
        ["0–1", "Judul", "pertanyaan riset; hubungan dengan Paper 1"],
        ["1–3", "Masalah", "klaim pembobotan di literatur; celah evaluasi yang umum"],
        ["3–5", "Data", "tiga korpus; audit DBL (107 salinan)"],
        ["5–7", "Metode", "tiga tingkat pembobotan; lima combiner; semua di dalam fold"],
        ["7–8", "Protokol", "pra-registrasi; 36 hipotesis; Nadeau–Bengio + Holm"],
        ["8–11", "Hasil", "forest plot 36 hipotesis; v2 vs v3"],
        ["11–13", "Pelajaran", "grafik skor DBL yang turun; 10 pelajaran"],
        ["13–15", "Penutup", "kontribusi bagi tesis; keterbatasan; saran untuk bidang ini"]],
       [1.6 * cm, 3.0 * cm, 12.0 * cm], "Tabel 7.1. Rencana slide (gambar tersedia di reports/book/).")

bk.CH("Bab 8. Daftar Periksa Sebelum Sidang")
bk.B(["Lengkapi nama penulis, afiliasi, pendanaan, konflik kepentingan, kontribusi penulis, dan pernyataan AI di draf "
      "manuskrip.",
      "Verifikasi semua referensi ke sumber asli.",
      "Publikasikan repositori atau arsip Zenodo, dan siapkan tautannya untuk ditunjukkan.",
      "Siapkan riwayat git (commit 27ae932 dan 228d42b) untuk membuktikan pra-registrasi.",
      "Samakan pernyataan penggunaan AI antara Paper 1 dan Paper 4.",
      "Cocokkan DBL dengan data asli Paper 1 jika memungkinkan, untuk menutup keterbatasan overlap.",
      "Latih penjelasan rumus Nadeau–Bengio dan estimator F0 di papan tulis."])

bk.build("reports/defense/Buku_Defense_Paper4.pdf", "Buku Defense Paper 4")
print("ok")
