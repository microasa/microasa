"""Buku IMRaD + defense Paper 4. Run from the repo root:  python3 reports/defense/build_book4_defense.py
All result numbers are read from results/v2 and results/v3; minimum detectable effects (MDE) are derived from the
corrected confidence intervals of the primary tests."""
import sys
from pathlib import Path

import pandas as pd
from reportlab.lib.units import cm
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from defense_common import Book  # noqa: E402
from learning_resources import add_learning_path  # noqa: E402

p2, p3 = pd.read_csv("results/v2/primary_tests.csv"), pd.read_csv("results/v3/primary_tests.csv")
s2, s3 = pd.read_csv("results/v2/summary.csv"), pd.read_csv("results/v3/summary.csv")
e2 = pd.read_csv("results/v2/exploratory_tests.csv")
dg = pd.concat([pd.read_csv(f"results/v2/{r}_{t}_diag.csv") for r in ["hand", "w2v2", "hubert"]
                for t in ["cryceleb", "infantcry_dbl", "ujm_sex", "ujm_age"]])
n2, n3 = int((p2.verdict != "no evidence").sum()), int((p3.verdict != "no evidence").sum())
unadj = p2[(p2.ci_low > 0) | (p2.ci_high < 0)]
T975, T80 = stats.t.ppf(0.975, 14), stats.t.ppf(0.80, 14)
p2["se"] = (p2.ci_high - p2["mean"]) / T975
p2["mde"] = (T975 + T80) * p2.se
keep = ["equal", "best_single", "softmax_tau", "stacking", "superb_wsum", "last_layer", "concat_balanced"]
best2 = s2[s2.method.isin(keep)].groupby(["task", "rep"]).macro_f1.max()
best3 = s3[s3.method.isin(keep)].groupby(["task", "rep"]).macro_f1.max()
eb = e2[e2.hypothesis == "E2"]
TASK = {"cryceleb": "CryCeleb", "infantcry_dbl": "DBL", "ujm_sex": "UJM-sex", "ujm_age": "UJM-age",
        "ujm_axa": "UJM-delivery"}
REP = {"hand": "handcrafted", "w2v2": "wav2vec2", "hubert": "HuBERT"}
mde_nd = p2[p2.task != "infantcry_dbl"].mde
mde_d = p2[p2.task == "infantcry_dbl"].mde

bk = Book("Paper 4 · pembobotan pada klasifikasi tangis bayi · buku IMRaD dan pertahanan disertasi")
bk.cover("Paper 4 dalam Bentuk IMRaD",
         "Does Weighting Help Infant Cry Classification? A Leakage-Controlled Evaluation of Class, Feature-Group "
         "and Layer Weighting, with a Provenance Audit of a Public Cry Corpus",
         ["Teori, aplikasi, hasil, pembahasan, dan jawaban atas pertanyaan penguji serta asesor yang kritis",
          "Semua angka hasil dibaca langsung dari results/v2 dan results/v3",
          "Pendamping teknis: reports/book/paper4_buku.pdf", "November 2026"])

# =============================================================== Pengantar
bk.CH("Cara Memakai Buku Ini")
bk.P("Struktur IMRaD: <b>I</b>ntroduction (pendahuluan dan landasan teori), <b>M</b>ethods, <b>R</b>esults, "
     "<b>a</b>nd <b>D</b>iscussion. Kotak abu-abu berisi <b>Teori</b> (definisi, rumus, turunan). Kotak hijau berisi "
     "<b>Aplikasi</b> (bagaimana teori dipakai di Paper 4, dengan angka). Bagian akhir berisi bank pertanyaan penguji dan "
     "asesor yang kritis.")
bk.H2("Ringkasan eksekutif")
bk.BOX(f"Tiga tingkat pembobotan (kelas, enam grup fitur akustik, 13 lapisan wav2vec2/HuBERT) diuji pada tiga korpus "
       f"publik (CryCeleb2023, BABYCRY-UJM-AXA, InfantCry-DBL yang dibersihkan) dengan CV berkelompok per bayi 5-fold × 3. "
       f"Semua bobot dan hyperparameter dipilih di dalam fold. Dari 36 hipotesis pra-registrasi (uji Nadeau–Bengio, Holm), "
       f"{n2} menunjukkan bukti; analisis sensitivitas pembersihan data memberi {n3}/36. Efek terkecil yang terdeteksi "
       f"dengan daya 80% pada CryCeleb dan UJM adalah {mde_nd.min():.3f}–{mde_nd.max():.3f} macro-F1, jadi efek "
       f"pembobotan yang besar dapat dikesampingkan. Audit provenance: 107 dari 236 klip DBL 'online/volunteer' adalah "
       f"salinan klip Dunstan (41) atau CryCeleb (66).")

# =============================================================== I
bk.CH("I. Introduction — Pendahuluan")
bk.H2("I.1 Latar belakang dan masalah")
bk.P("Sistem klasifikasi tangis bayi biasanya menggabungkan banyak deskriptor akustik atau encoder pretrained, lalu "
     "menambahkan tahap pembobotan: bobot kelas untuk ketimpangan label, bobot grup fitur, atau bobot lapisan encoder. "
     "Korpus kecil, klip berulang dari bayi yang sama, dan desain evaluasi yang membocorkan informasi uji membuat "
     "peningkatan dari pembobotan mudah terlihat lebih besar dari kenyataannya.")
bk.P("Paper 1 disertasi ini menemukan pembobotan tidak membantu (rincian di buku Paper 1, yang tidak disimpan di "
     "repositori publik ini). Paper 4 menguji apakah kegagalan itu khas data Paper 1, dengan tiga korpus lain dan "
     "evaluasi yang ketat.")
bk.H2("I.2 Pertanyaan riset dan hipotesis")
bk.TBL([["Kode", "Hipotesis primer (ditetapkan sebelum hasil v2)", "Run"],
        ["H1", "stacking ≠ equal (rata-rata sederhana)", "12"],
        ["H2", "stacking ≠ best single (satu grup/lapisan terbaik lewat CV dalam)", "12"],
        ["H3", "stacking ≠ SUPERB weighted sum", "8 (embedding)"],
        ["H4", "concat dengan bobot kelas balanced ≠ concat tanpa bobot", "4 (handcrafted)"]],
       [1.6 * cm, 11.4 * cm, 3.6 * cm], "Tabel I.1. Keluarga 36 hipotesis primer (Holm atas seluruhnya).")
bk.H2("I.3 Kontribusi")
bk.B(["Perbandingan pra-registrasi pembobotan kelas, grup fitur, dan lapisan pada tiga korpus dengan pembagian per bayi "
      "dan estimasi nested untuk setiap bobot.",
      "Hasil negatif yang jelas dan tahan terhadap analisis sensitivitas kualitas data.",
      "Audit provenance yang menemukan duplikasi substansial antar-tier dan antar-korpus pada InfantCry-DBL.",
      "Kode terbuka, termasuk estimator F0 untuk tangis yang divalidasi dengan unit test."])

# --------------------------------------------------------------- Teori
bk.CH("I (lanjutan). Landasan Teori")
bk.H2("T.1 Fitur akustik dan redundansi")
bk.T("MFCC sebagai transformasi linear",
     "MFCC per frame adalah c(t) = D·L(t), dengan L log-mel dan D matriks DCT-II ortonormal. Karena D linear, rata-rata "
     "waktunya mean<sub>t</sub> c(t) = D · mean<sub>t</sub> L(t). Jadi rata-rata MFCC adalah transformasi linear persis "
     "dari rata-rata log-mel. Simpangan baku tidak bersifat demikian: std(D·L) ≠ D·std(L).")
bk.APP("Versi awal memakai rata-rata log-mel sebagai grup 'mel', sehingga R² MFCC-mean dari grup mel = 1,000000. "
       "Versi final memakai simpangan baku log-mel, dan R² turun ke 0,300. Grup fitur menjadi benar-benar berbeda "
       "informasinya, syarat agar 'membobot grup' bermakna.")
bk.T("delta",
     "Δc(t) ≈ c(t+1) − c(t−1). Rata-rata sepanjang T frame mendekati (c<sub>akhir</sub> − c<sub>awal</sub>)/T, mendekati "
     "nol untuk klip panjang.")
bk.APP("Rasio |rata-rata delta| / simpangan baku delta = 0,087, jadi hanya simpangan baku delta yang disimpan "
       "(20 fitur).")
bk.H2("T.2 Estimasi F0")
bk.T("autokorelasi dan koreksi jendela",
     "Untuk sinyal periodik x(t) = x(t + T), autokorelasi r(l) memuncak di l = T, 2T, … Teorema Wiener–Khinchin: "
     "r = IFFT(|X|²), dengan zero-padding 2N untuk menghindari aliasing sirkular. Jendela w membuat r<sub>xw</sub>(l) ≈ "
     "r<sub>x</sub>(l)·r<sub>w</sub>(l), sehingga bias ke lag pendek. Boersma (1993): r(l) = r<sub>xw</sub>(l)/r<sub>w</sub>(l).")
bk.T("kesalahan oktaf dan interpolasi",
     "Puncak di 2T dan 3T hampir setinggi puncak di T. Memilih maksimum global bisa jatuh ke subharmonik. Aturan: ambil "
     "puncak lokal dengan lag terpendek yang tingginya ≥ 0,9 × puncak tertinggi. Lag diperhalus dengan parabola lewat tiga "
     "titik (a, b, c): δ = ½(a − c)/(a − 2b + c), F0 = f<sub>s</sub>/(l + δ).")
bk.APP("Rentang 150–2.000 Hz (lag 8–107 sampel pada 16 kHz) agar hyperphonation tertangkap; frame 64 ms, langkah 10 ms; "
       "bersuara jika tinggi puncak ≥ 0,45 dan RMS frame ≥ 10% RMS maksimum (frame yang sama). Delapan belas unit test: "
       "nada 160–1.800 Hz dan sinyal harmonik akurat ≤ 2%; 1.200 Hz terbaca 1.200,3 Hz (versi awal: 400 Hz); derau "
       "low-pass 1% bersuara.")
bk.H2("T.3 Encoder ucapan self-supervised")
bk.T("wav2vec 2.0 dan HuBERT",
     "Keduanya: encoder CNN mengubah gelombang menjadi frame laten setiap 20 ms (stride 320 sampel pada 16 kHz), lalu "
     "Transformer 12 lapisan berdimensi 768 (versi base). wav2vec 2.0 dilatih dengan loss kontrastif pada frame yang "
     "di-mask: memilih representasi terkuantisasi yang benar di antara distraktor. HuBERT dilatih memprediksi label "
     "klaster k-means pada frame yang di-mask. Lapisan awal cenderung menyimpan informasi akustik; lapisan akhir lebih "
     "khusus untuk tugas pretraining.")
bk.APP("13 hidden state (keluaran proyeksi CNN + 12 lapisan Transformer), dirata-rata sepanjang waktu, maksimal 6 s audio. "
       "Input dinormalisasi (do_normalize = True untuk kedua model, sesuai konfigurasi resmi). Tidak ada fine-tuning.")
bk.H2("T.4 PCA whitening dan regresi logistik")
bk.T("PCA whitening",
     "z = Λ<super>−1/2</super>U<super>T</super>(x − μ), dengan U vektor eigen dan Λ nilai eigen kovarians data latih. "
     "Hasilnya komponen tak berkorelasi bervarians 1, sehingga penalti L2 berlaku merata ke semua arah.")
bk.T("regresi logistik multinomial berbobot",
     "P(c|x) = softmax(Wx + b)<sub>c</sub>. Parameter meminimalkan C·Σ<sub>i</sub> w<sub>i</sub>(−log P(y<sub>i</sub>|x<sub>i</sub>)) "
     "+ ½‖W‖². C kecil berarti regularisasi kuat.")
bk.APP("PCA 64 komponen, dipasang hanya pada data latih fold (dibatasi n − 1 jika fold kecil). C ∈ {0,01; 0,1; 1} dipilih "
       "per pakar lewat CV dalam 3-fold berkelompok berdasarkan macro-F1; jika seri, C terkecil.")
bk.H2("T.5 Bobot kelas")
bk.T("balanced dan effective number",
     "Balanced: w<sub>c</sub> ∝ 1/n<sub>c</sub>. Effective number (Cui et al., 2019): sampel yang tumpang tindih memberi "
     "informasi menurun, dengan jumlah efektif E<sub>n</sub> = (1 − β<super>n</super>)/(1 − β), sehingga w<sub>c</sub> ∝ "
     "1/E<sub>n<sub>c</sub></sub> = (1 − β)/(1 − β<super>n<sub>c</sub></super>). Karena bobot sampel mengalikan suku loss, "
     "total bobot Σw<sub>i</sub> berinteraksi dengan C: mengubah total bobot sama dengan mengubah C.")
bk.APP("Semua skema dinormalisasi agar Σw<sub>i</sub> = n. Tanpa ini, skema 'effective' (β = 0,999) pada DBL versi awal "
       "memberi total 0,64n, setara regularisasi ±1,6 kali lebih kuat.")
bk.H2("T.6 Teori penggabungan (fusion)")
bk.T("linear pool",
     "P(c|x) = Σ<sub>g</sub> w<sub>g</sub>P<sub>g</sub>(c|x), Σw<sub>g</sub> = 1. Dengan bobot sama, ini rata-rata "
     "pakar. Linear pool tetap terkalibrasi bila pakar terkalibrasi, tetapi tidak bisa memberi bobot berbeda per kelas "
     "secara koheren.")
bk.T("softmax bersuhu",
     "w<sub>g</sub> = exp(τF1<sub>g</sub>)/Σ<sub>h</sub>exp(τF1<sub>h</sub>). Untuk τ → 0 bobot seragam (equal); untuk "
     "τ → ∞ bobot terpusat ke pakar terbaik (best single). τ menginterpolasi keduanya.")
bk.T("stacking (Wolpert, 1992)",
     "Model tingkat dua dilatih pada prediksi pakar. Syaratnya: prediksi itu harus out-of-fold (OOF), yaitu dibuat oleh "
     "model yang tidak melihat sampel tersebut. Jika memakai prediksi in-sample, meta-model belajar mempercayai pakar yang "
     "overfit. Regresi logistik multinomial pada log-peluang semua pakar mempelajari bobot per pakar × kelas di dalam satu "
     "model yang koheren.")
bk.T("SUPERB weighted sum",
     "z = Σ<sub>l</sub> softmax(a)<sub>l</sub> · x̃<sub>l</sub> (x̃ lapisan yang distandardisasi), lalu kepala linear; a "
     "dan kepala dilatih bersama dengan cross-entropy. Ini baseline standar untuk probing lapisan encoder.")
bk.APP("Satu bank pakar per fold luar; semua combiner dibangun dari prediksi OOF bank yang sama. τ ∈ {0, 1, 3, 10, 30, "
       "100, 300, 1.000} dipilih dari macro-F1 fusi OOF. Stacking: regresi logistik (C = 1, balanced) pada log-peluang OOF "
       "yang distandardisasi. SUPERB: Adam lr 0,01, 300 langkah full-batch, weight decay kepala dipilih dari {10⁻⁴, 10⁻³, "
       f"10⁻²}} di satu split dalam. Hasilnya, τ terpilih (median per run) 10–300 dan bobot terbesar rata-rata "
       f"{dg.w_max.mean():.2f}, jadi bobot benar-benar tidak seragam.")
bk.H2("T.7 Kebocoran, pengelompokan, dan provenance")
bk.T("kebocoran",
     "Generalisasi diukur dengan asumsi sampel uji independen dari data latih. Tiga jalur kebocoran utama: (1) subjek "
     "yang sama di latih dan uji; (2) salinan atau hampir-salinan audio di kedua sisi; (3) bobot atau hyperparameter yang "
     "dipilih dengan melihat data uji. Ketiganya menggelembungkan skor.")
bk.T("deteksi hampir-salinan",
     "Dua klip dianggap salinan jika vektor fitur ringkasnya, setelah z-score, punya kosinus sangat tinggi. Kosinus ≥ 0,999 "
     "praktis identik. Metode ini bisa menghasilkan positif palsu (klip berbeda yang mirip secara akustik) dan negatif palsu "
     "(klip yang disunting). Konfirmasi paling kuat adalah korelasi silang gelombang.")
bk.APP("Pembagian per bayi (CryCeleb, UJM) atau per klaster hampir-salinan (DBL, kosinus ≥ 0,90). ID anonim CryCeleb "
       "dibuang karena dua periode bayi yang sama diberi ID berbeda. Pencocokan DBL terhadap 337 klip Tier 1 dan 26.093 "
       "klip CryCeleb. Semua pemilihan bobot nested di dalam fold.")
bk.H2("T.8 Statistik: uji, koreksi, dan daya")
bk.T("Nadeau–Bengio",
     "Untuk k selisih fold yang berkorelasi dengan korelasi ρ, Var(d̄) ≈ σ²(1/k + ρ/(1 − ρ)). Nadeau dan Bengio "
     "mengaproksimasi ρ ≈ n<sub>uji</sub>/n, sehingga ρ/(1 − ρ) = n<sub>uji</sub>/n<sub>latih</sub>. Statistik: "
     "t = d̄/√((1/k + n<sub>uji</sub>/n<sub>latih</sub>)s²), df = k − 1.")
bk.T("Holm",
     "Urutkan p-value; tolak H<sub>(i)</sub> selama p<sub>(i)</sub> ≤ α/(m − i + 1). Mengendalikan family-wise error ≤ α "
     "tanpa asumsi independensi.")
bk.T("efek terkecil yang terdeteksi (MDE)",
     "Dengan galat baku SE, efek yang terdeteksi dengan daya 1 − β pada α dua sisi kira-kira MDE = (t<sub>1−α/2</sub> + "
     "t<sub>1−β</sub>) · SE. SE diperoleh dari CI: SE = setengah-lebar CI / t<sub>0,975</sub>.")
bk.APP(f"k = 15, n<sub>uji</sub>/n<sub>latih</sub> = 1/4, df = 14, t<sub>0,975</sub> = {T975:.3f}, t<sub>0,80</sub> = "
       f"{T80:.3f}. Jadi MDE<sub>80%</sub> = {T975 + T80:.3f} × SE. Holm atas 36 uji primer. MDE dihitung untuk setiap uji "
       "di bab Hasil (R.3). Catatan: MDE ini untuk α = 0,05 per uji; dengan koreksi Holm, efek yang diperlukan sedikit lebih "
       "besar.")
bk.H2("T.9 Pra-registrasi dan forking paths")
bk.T("garden of forking paths",
     "Jika peneliti mencoba banyak pilihan analisis dan melaporkan yang 'berhasil', p-value kehilangan maknanya walaupun "
     "setiap uji tampak sah. Pra-registrasi menetapkan hipotesis, analisis, dan aturan keputusan sebelum melihat hasil, "
     "dan setiap deviasi dicatat.")
bk.APP("PROTOCOL.md v2 di-commit pada 27ae932 dan v3 pada 228d42b, masing-masing sebelum hasilnya ada. Deviasi dicatat "
       "(batas PCA, ukuran DBL). Keputusan yang dipicu hasil di fase v1 (pergantian tugas UJM, beralih ke embedding) "
       "diungkapkan terbuka.")

# =============================================================== M
bk.CH("M. Methods — Metode")
bk.H2("M.1 Data dan tugas")
bk.TBL([["Tugas", "Korpus dan pemilihan", "Klip", "Grup", "Kelas"],
        ["CryCeleb", "CryCeleb2023; hanya ID asli; durasi ≥ 0,5 s; ≤ 5 klip per bayi per periode", "4.954", "626 bayi",
         "B 2.815 · D 2.139"],
        ["UJM-sex", "BABYCRY-UJM-AXA; subset deterministik 100 bayi per cara persalinan, ≤ 6 klip per bayi", "1.762",
         "300 bayi", "F 882 · M 880"],
        ["UJM-age", "subset yang sama; tertil bawah vs atas usia rekam (jam)", "1.176", "247 bayi", "muda 588 · tua 588"],
        ["DBL", "InfantCry-DBL Tier 2 online/volunteer setelah audit", "103", "86 klaster",
         "owh 40 · eh 26 · neh 18 · eairh 13 · heh 6"],
        ["UJM-delivery*", "tugas tambahan (awal)", "1.762", "300 bayi", "3 kelas ±590"]],
       [2.2 * cm, 6.6 * cm, 1.4 * cm, 2.0 * cm, 4.4 * cm], "Tabel M.1. Data analisis utama (v2).")
bk.H2("M.2 Audit DBL")
bk.B(["SHA-256 semua 1.551 berkas cocok dengan penerbit.", "1 duplikat identik byte dibuang.",
      "107 salinan (kosinus ≥ 0,999): 41 dari Tier 1 Dunstan, 66 dari CryCeleb; 26 hampir salinan (0,95–0,999).",
      "Ambang 0,95 ditetapkan di muka: 133 dibuang; sisa 103 klip dalam 86 klaster (kosinus ≥ 0,90).",
      "source_confirmed = False untuk seluruh 1.214 klip Tier 2."])
bk.H2("M.3 Representasi, model, dan evaluasi")
bk.B(["Handcrafted: enam grup, total 126 fitur; durasi bukan fitur.", "Embedding: 13 lapisan × 768, PCA 64 dalam fold.",
      "Pakar per grup/lapisan + combiner (equal, best single, softmax-τ, stacking) + baseline (last layer, SUPERB, "
      "concat none/balanced/effective, durasi saja).",
      "StratifiedGroupKFold 5-fold × seed {0, 1, 2}; assertion tanpa irisan grup di setiap fold.",
      "Metrik primer macro-F1 per fold; uji Nadeau–Bengio dua sisi; Holm atas 36 uji; aturan keputusan: p Holm &lt; 0,05 "
      "dan CI 95% tidak memuat nol."])
bk.H2("M.4 Analisis sensitivitas v3")
bk.P("Kriteria dibekukan di 228d42b sebelum hasil v3: audio dipotong ke 0–4 kHz (resample 8 kHz lalu kembali ke 16 kHz); "
     "klip dengan clipping &gt; 0,1% atau &gt; 50% frame 25 ms sunyi (&lt; −60 dBFS) dibuang; klip UJM dengan SNR resmi "
     "&lt; 10 dB dibuang. Total 497 klip dibuang (CryCeleb 101, DBL 9, UJM 387). Diagnostik yang ditetapkan di muka: "
     "classifier sample-rate saja pada DBL.")

# =============================================================== R
bk.CH("R. Results — Hasil")
bk.H2("R.1 Skor semua metode")
methods = [("equal", "Equal"), ("best_single", "Best"), ("softmax_tau", "Softm.-τ"), ("stacking", "Stack."),
           ("superb_wsum", "SUPERB"), ("last_layer", "Last"), ("concat_balanced", "Concat"), ("duration_only", "Durasi")]
piv = s2.pivot_table(index=["task", "rep"], columns="method", values="macro_f1")
order = [(t, r) for t in ["cryceleb", "infantcry_dbl", "ujm_sex", "ujm_age", "ujm_axa"]
         for r in ["hand", "w2v2", "hubert"] if (t, r) in piv.index]
rows = [["Tugas", "Fitur"] + [m[1] for m in methods]]
for t, r in order:
    v = piv.loc[(t, r)]
    rows.append([TASK[t], REP[r]] + ["–" if pd.isna(v.get(m)) else f"{v[m]:.3f}" for m, _ in methods])
bk.TBL(rows, [2.3 * cm, 2.0 * cm] + [1.54 * cm] * 8,
       "Tabel R.1. Macro-F1 rata-rata 15 fold (v2). Acak: 0,50 biner; 0,20 DBL; 0,33 delivery.")
bk.H2("R.2 Hipotesis primer")
rows = [["Hip.", "Fitur", "Tugas", "Δ", "CI 95%", "p", "p Holm"]]
for _, x in p2.iterrows():
    rows.append([x.hypothesis, REP[x.rep], TASK[x.task], f"{x['mean']:+.3f}", f"[{x.ci_low:+.3f}, {x.ci_high:+.3f}]",
                 f"{x.p:.3f}", f"{x.p_holm:.2f}"])
bk.TBL(rows, [1.3 * cm, 2.3 * cm, 2.3 * cm, 1.7 * cm, 4.2 * cm, 1.6 * cm, 1.6 * cm],
       f"Tabel R.2. 36 uji primer v2: {n2} menunjukkan bukti.")
bk.P(f"Tanpa koreksi, {len(unadj)} interval tidak memuat nol, semuanya kecil dan berpihak ke stacking "
     + "; ".join(f"{x.hypothesis} {REP[x.rep]} {TASK[x.task]} {x['mean']:+.3f}" for _, x in unadj.iterrows())
     + ". Sekitar dua hasil seperti itu diharapkan muncul secara kebetulan dari 36 uji; tidak satu pun bertahan setelah Holm.")
bk.H2("R.3 Efek terkecil yang terdeteksi (MDE)")
rows = [["Tugas", "Fitur", "MDE H1", "MDE H2", "MDE H3", "MDE H4"]]
for t in ["cryceleb", "ujm_sex", "ujm_age", "infantcry_dbl"]:
    for rr in ["hand", "w2v2", "hubert"]:
        row = [TASK[t], REP[rr]]
        for h in ["H1", "H2", "H3", "H4"]:
            x = p2[(p2.hypothesis == h) & (p2.task == t) & (p2.rep == rr)]
            row.append("–" if x.empty else f"{x.mde.iat[0]:.3f}")
        rows.append(row)
bk.TBL(rows, [2.4 * cm, 2.4 * cm, 2.9 * cm, 2.9 * cm, 2.9 * cm, 2.9 * cm],
       "Tabel R.3. Selisih macro-F1 yang terdeteksi dengan daya 80% (α = 0,05 per uji), diturunkan dari CI terkoreksi.")
bk.P(f"Pada CryCeleb dan UJM, MDE berkisar {mde_nd.min():.3f}–{mde_nd.max():.3f} macro-F1. Efek pembobotan sebesar itu "
     f"atau lebih besar seharusnya terdeteksi, tetapi tidak terdeteksi. Pada DBL, MDE {mde_d.min():.2f}–{mde_d.max():.2f}, "
     "sehingga DBL tidak informatif untuk uji metode.")
bk.H2("R.4 Temuan eksploratif")
bk.B([f"Satu lapisan terbaik (CV dalam) vs lapisan terakhir: lebih baik di {int((eb.ci_low > 0).sum())} dari {len(eb)} "
      "run, tanpa koreksi. Lapisan terpilih paling sering L00–L01; bobot SUPERB terpusat di L03–L08.",
      "Semua metode mengungguli durasi saja; di CryCeleb durasi saja 0,55 dari maksimum 0,64.",
      "Satu-satunya run v2 yang diulang memberi hasil identik sampai digit terakhir."])
bk.H2("R.5 Analisis sensitivitas v3")
rows = [["Tugas", "Fitur", "Terbaik v2", "Terbaik v3", "Selisih"]]
for t, rr in order:
    if (t, rr) in best3.index:
        rows.append([TASK[t], REP[rr], f"{best2[(t, rr)]:.3f}", f"{best3[(t, rr)]:.3f}",
                     f"{best3[(t, rr)] - best2[(t, rr)]:+.3f}"])
bk.TBL(rows, [3.0 * cm, 2.6 * cm, 3.4 * cm, 3.4 * cm, 2.6 * cm], f"Tabel R.4. v2 vs v3; hipotesis primer v3: {n3}/36.")
bk.P("CryCeleb dan UJM bergeser ±0,02; DBL turun 0,02–0,10. Classifier sample-rate saja pada DBL: 0,197 (acak 0,20).")
bk.H2("R.6 Skor DBL per tahap perbaikan")
bk.TBL([["Tahap", "Macro-F1 handcrafted terbaik"],
        ["v1: subset 'bersih', satu klip satu grup", "0,852"], ["v1: klip mirip (kosinus &gt; 0,85) satu grup", "0,818"],
        ["v2: salinan lintas korpus dibuang (103 klip)", "0,768"], ["v3: band-limit 0–4 kHz + filter kualitas", "0,665"]],
       [11 * cm, 5.6 * cm], "Tabel R.5. Antara v1 dan v2 fitur dan metode juga berubah.")

# =============================================================== D
bk.CH("D. Discussion — Pembahasan")
bk.H2("D.1 Temuan utama")
bk.P("Ketika bobot diestimasi tanpa akses ke fold uji, pembagian menghormati identitas bayi, dan perbandingan dikoreksi "
     "untuk set latih yang tumpang tindih dan banyaknya uji, tidak ada skema pembobotan yang menambah nilai terukur di atas "
     "rata-rata pakar atau pemilihan satu lapisan yang baik. Analisis MDE menunjukkan ini bukan sekadar kurang daya: pada "
     f"CryCeleb dan UJM, efek sebesar {mde_nd.min():.3f}–{mde_nd.max():.3f} macro-F1 (tergantung run dan hipotesis) "
     "seharusnya terdeteksi dengan daya 80%.")
bk.H2("D.2 Mengapa pembobotan tidak membantu")
bk.B(["<b>Pakar sangat berkorelasi.</b> Grup fitur dan lapisan berdekatan membawa informasi yang tumpang tindih, sehingga "
      "mengubah bobot hanya sedikit mengubah prediksi gabungan.",
      "<b>Set validasi dalam kecil.</b> Bobot yang dipilih dari data adalah estimasi berisik dari selisih kecil, sehingga "
      "keuntungannya hilang di data uji (variance vs bias dalam pemilihan model).",
      "<b>Sinyal tugas lemah.</b> Pada tugas yang cukup data untuk mendeteksi efek kecil (CryCeleb, UJM), macro-F1 terbaik "
      "hanya 0,56–0,64. Tidak banyak informasi yang bisa ditata ulang oleh pembobotan."])
bk.H2("D.3 Audit DBL sebagai temuan tersendiri")
bk.P("Hampir separuh klip yang diberi label sebagai rekaman online atau sukarelawan independen adalah salinan klip dari tier "
     "lain atau korpus publik lain. Studi yang menggabungkan materi turunan Dunstan dengan korpus lain, atau membagi data "
     "per klip, bisa membocorkan audio identik ke data latih dan uji. Skor DBL turun dari 0,852 ke 0,665 sepanjang "
     "perbaikan.")
bk.H2("D.4 Hubungan dengan Paper 1")
bk.P("Paper 1 dan Paper 4 sampai pada kesimpulan yang sejalan dari arah berbeda: hambatan klasifikasi tangis bayi ada pada "
     "data dan label, bukan pada arsitektur atau pembobotan. Kesamaan kesimpulan di bawah desain yang berbeda memperkuat "
     "tesis disertasi.")
bk.H2("D.5 Ancaman validitas")
bk.TBL([["Jenis", "Ancaman", "Mitigasi"],
        ["Internal", "forking paths di fase v1; pemilihan C/τ yang berisik", "pra-registrasi v2/v3; nested; deviasi dicatat"],
        ["Konstruk", "label CryCeleb B/D tercampur kondisi rekam; deteksi salinan berbasis fitur",
         "baseline durasi; kosinus ≥ 0,999 untuk salinan; disarankan korelasi silang gelombang"],
        ["Eksternal", "UJM subset 300 bayi; tanpa fine-tuning; tiga korpus saja", "klaim dibatasi pada pengaturan ini"],
        ["Kesimpulan statistik", "DBL kecil; NB hanya aproksimasi untuk split berkelompok; Holm konservatif",
         "MDE dilaporkan; CI dilaporkan; hasil tanpa koreksi diungkapkan"]],
       [3.0 * cm, 7.0 * cm, 6.6 * cm], "Tabel D.1. Ancaman validitas.")
bk.H2("D.6 Kesimpulan")
bk.BOX("Di bawah evaluasi pra-registrasi yang mengendalikan kebocoran pada tiga korpus publik, pembobotan kelas, grup fitur, "
       "dan lapisan (termasuk stacking dan SUPERB) tidak mengungguli rata-rata sederhana atau pemilihan satu pakar, dan "
       "hasil ini bertahan setelah pembersihan data. Korpus tangis publik perlu diaudit duplikasi antar-tier dan antar-korpus "
       "sebelum peningkatan dari pembobotan dilaporkan.")

# =============================================================== Q&A
bk.CH("Bank Pertanyaan Penguji dan Asesor yang Kritis")
bk.H2("Q-I. Pendahuluan dan kebaruan")
bk.QA("Dua paper Anda sama-sama negatif. Apa kontribusi positif disertasi ini?",
      "Disertasi ini memberi bukti terkendali bahwa peningkatan yang dilaporkan di bidang ini tidak terulang di bawah "
      "evaluasi yang benar, dan menunjukkan sebabnya: kualitas data dan label. Kontribusi konkretnya protokol evaluasi yang "
      "bisa dipakai ulang, audit provenance yang menemukan 107 salinan di dataset publik, estimator F0 tervalidasi, dan "
      "rekomendasi pelaporan.",
      "hasil negatif yang sahih mencegah bidang ini membangun di atas klaim yang menggelembung.")
bk.QA("Apa bedanya stacking dengan metode yang sudah ada? Di mana kebaruan metodenya?",
      "Kebaruan Paper 4 bukan pada metode baru, melainkan pada pengujian terkendali metode yang sudah dipakai luas. Stacking "
      "dipilih sebagai versi paling koheren dari ide pembobotan per kelas di versi awal. Pertanyaannya 'apakah ini membantu', "
      "dan jawabannya tidak.")
bk.QA("Mengapa memakai korpus dengan tugas yang aneh, seperti lahir vs pulang atau jenis kelamin?",
      "Karena hanya tugas itu yang tersedia dengan ID bayi untuk pembagian berkelompok. Pertanyaan risetnya tentang "
      "pembobotan, bukan tentang tugas klinis tertentu. Tugas yang berbeda justru menguji apakah kesimpulan tergeneralisasi.")
bk.H2("Q-T. Teori")
bk.QA("Turunkan mengapa rata-rata MFCC redundan dengan rata-rata log-mel.",
      "MFCC = D·L dengan D matriks DCT. Rata-rata waktu: (1/T)Σ<sub>t</sub> D·L(t) = D·(1/T)Σ<sub>t</sub> L(t). Jadi rata-rata "
      "MFCC = D × rata-rata log-mel, transformasi linear persis (R² = 1). Simpangan baku tidak linear, sehingga versi final "
      "memakai simpangan baku log-mel.")
bk.QA("Jelaskan mengapa stacking harus memakai prediksi out-of-fold.",
      "Jika meta-model dilatih pada prediksi in-sample, pakar yang overfit tampak sempurna di data latih, sehingga meta-model "
      "memberinya bobot besar, lalu gagal di data uji. Prediksi OOF meniru kondisi data yang belum dilihat, sehingga bobotnya "
      "mencerminkan performa generalisasi.")
bk.QA("Dari mana suku 1/4 di uji Nadeau–Bengio?",
      "Selisih antar-fold berkorelasi karena set latih tumpang tindih. Var(d̄) ≈ σ²(1/k + ρ/(1 − ρ)). Nadeau dan Bengio "
      "mengaproksimasi ρ ≈ n<sub>uji</sub>/n; untuk 5-fold, n<sub>uji</sub>/n = 1/5, sehingga ρ/(1 − ρ) = 1/4.")
bk.QA("Bagaimana estimator F0 Anda menghindari kesalahan oktaf?",
      "Autokorelasi sinyal periodik memuncak di T, 2T, 3T dengan tinggi hampir sama. Memilih maksimum global bisa jatuh ke "
      "2T atau 3T (subharmonik). Saya memilih puncak lokal dengan lag terpendek yang tingginya ≥ 0,9 × tertinggi, setelah "
      "koreksi bias jendela. Versi awal yang memakai maksimum global membaca 1.200 Hz sebagai 400 Hz; versi final 1.200,3 Hz.")
bk.QA("Apa batas τ → 0 dan τ → ∞ pada softmax-τ?",
      "τ → 0 memberi bobot seragam (equal). τ → ∞ memberi seluruh bobot ke pakar terbaik (best single). Jadi softmax-τ "
      "menginterpolasi dua baseline itu; jika keduanya tidak kalah, softmax-τ pun tidak diharapkan menang jauh.")
bk.H2("Q-M. Metode")
bk.QA("Kosinus fitur ringkas bukan bukti salinan. Bagaimana Anda tahu 107 klip itu salinan, bukan sekadar mirip?",
      "Kosinus ≥ 0,999 pada 126 fitur ter-z-score sangat sulit dicapai oleh dua rekaman berbeda. Ambang yang dipakai "
      "membuang klip adalah 0,95, ditetapkan di muka. Saya akui verifikasi terkuat, yaitu korelasi silang gelombang atau "
      "mendengarkan sampel, belum dilakukan untuk semua klip, dan itu langkah berikut sebelum publikasi.",
      "akui batas metode deteksi; usulkan verifikasi gelombang.")
bk.QA("Ambang klaster 0,90 dan pembuangan 0,95 terasa arbitrer.",
      "Keduanya ditetapkan sebelum hasil v2. Sensitivitasnya terhadap skor DBL sudah terlihat di v1: skor turun dari 0,852 "
      "(per klip) ke 0,846, 0,837, dan 0,818 pada ambang 0,95, 0,90, dan 0,85. Arah efeknya konsisten: ambang lebih ketat "
      "memberi skor lebih rendah, yang memang diharapkan bila klip mirip membocorkan informasi.")
bk.QA("Mengapa model linear, bukan deep learning?",
      "Pakar linear di atas fitur beku adalah praktik paling umum dalam probing encoder dan memungkinkan estimasi nested yang "
      "terjangkau. Model yang lebih kompleks dengan data sekecil ini rawan overfitting, dan pembobotan yang diuji adalah "
      "tahap fusi, bukan pakar.")
bk.QA("Mengapa mean pooling, bukan pooling yang lebih kaya?",
      "Mean pooling adalah baseline standar dan sama untuk semua metode, sehingga perbandingan pembobotan adil. Pooling yang "
      "lebih kaya mungkin menaikkan skor absolut semua metode, tetapi tidak jelas mengubah selisih antar-metode.")
bk.QA("Tugas UJM diganti setelah melihat hasil. Bukankah itu p-hacking?",
      "Itu keputusan yang dipicu hasil di fase eksploratif v1, dan saya ungkapkan terbuka. Kesimpulan Paper 4 diambil dari v2, "
      "yang protokolnya dibekukan sebelum hasil v2 ada, dan hasilnya negatif. P-hacking adalah mencari hasil positif; di sini "
      "semua jalur berakhir negatif, jadi forking paths tidak bisa menjelaskan kesimpulan.",
      "forking paths menggelembungkan hasil positif; kesimpulan Anda negatif.")
bk.QA("Kenapa ID anonim CryCeleb dibuang? Bukankah itu mengurangi data?",
      "Split uji kompetisi memberi ID berbeda untuk dua periode bayi yang sama, sehingga pengelompokan per ID tidak mencegah "
      "kebocoran. Membuangnya mengorbankan sebagian data demi validitas; tersisa 626 bayi, cukup untuk CI sempit.")
bk.H2("Q-R. Hasil")
bk.QA("Ketiadaan bukti bukan bukti ketiadaan. Bagaimana Anda tahu ini bukan kurang daya?",
      f"Saya menghitung MDE dari CI terkoreksi. Pada CryCeleb dan UJM, efek {mde_nd.min():.3f}–{mde_nd.max():.3f} macro-F1 "
      "seharusnya terdeteksi dengan daya 80%. Jadi saya bisa menyatakan efek pembobotan yang lebih besar dari itu tidak "
      "ada. Yang tidak bisa saya klaim adalah tidak adanya efek yang lebih kecil, dan DBL memang tidak informatif.",
      "bedakan 'efek besar dikesampingkan' dari 'tidak ada efek sama sekali'.")
bk.QA("Tiga CI tanpa koreksi tidak memuat nol dan semuanya berpihak ke stacking. Bukankah itu sinyal?",
      "Dari 36 uji, sekitar dua hasil seperti itu diharapkan secara kebetulan pada α = 0,05. Besarnya kecil (+0,015 sampai "
      "+0,043), dan tidak satu pun bertahan setelah Holm. Saya melaporkannya terbuka, tidak menyembunyikannya.")
bk.QA("Mengapa DBL turun 0,10 di v3? Bukankah itu berarti model memakai shortcut?",
      "Penyebabnya tidak bisa dipisahkan: harmonik asli di atas 4 kHz ikut terbuang, artefak lebar pita rekaman hilang, dan "
      "datanya mengecil. Sample rate saja tidak menebak kelas di atas acak (0,197). Saya tidak mengklaim penyebabnya.")
bk.QA("Satu lapisan awal mengungguli lapisan terakhir. Kenapa tidak dijadikan hasil utama?",
      "Karena tidak termasuk hipotesis yang ditetapkan di muka. Menjadikannya hasil utama setelah melihat data adalah "
      "forking paths. Saya laporkan sebagai temuan eksploratif yang perlu dikonfirmasi.")
bk.H2("Q-D. Pembahasan dan generalisasi")
bk.QA("Apakah hasil ini berlaku untuk deteksi tangis patologis?",
      "Tidak bisa diklaim. Tugas di sini bukan klinis, dan data patologis berlabel dengan ID bayi tidak tersedia secara "
      "terbuka. Kesimpulan dibatasi pada tiga korpus dan pengaturan fitur beku.")
bk.QA("Apa rekomendasi Anda untuk peneliti yang ingin memakai pembobotan?",
      "Estimasi bobot di dalam fold latih saja, bandingkan dengan rata-rata sederhana dan pemilihan satu pakar, pakai "
      "pembagian per subjek, laporkan MDE atau CI, dan audit duplikasi data sebelum mengklaim peningkatan.")
bk.QA("Apakah temuan kontaminasi DBL berarti dataset itu tidak boleh dipakai?",
      "Tidak. Yang tidak bisa dipercaya adalah metadata sumbernya. Dataset masih bisa dipakai setelah salinan dibuang dan "
      "klip mirip dikelompokkan, seperti yang kami lakukan.")
bk.H2("Q-X. Integritas dan disertasi")
bk.QA("Bagaimana kami tahu Anda tidak mengulang eksperimen sampai hasilnya sesuai?",
      "Protokol v2 dan v3 di-commit sebelum hasilnya ada (27ae932, 228d42b), dan setiap file hasil menyimpan hash commit "
      "yang menghasilkannya. Semua hasil v1 diarsipkan. Satu-satunya run v2 yang diulang memberi hasil identik.",
      "tunjukkan riwayat git.")
bk.QA("Apa peran AI dalam penelitian ini, dan apa kontribusi Anda?",
      "Kode dan eksperimen dikerjakan agen AI di bawah arahan saya, termasuk audit kritis yang menemukan kesalahan versi awal. "
      "Pertanyaan riset, keputusan protokol, dan interpretasi adalah tanggung jawab saya. [Lengkapi sesuai praktik Anda, dan "
      "samakan dengan pernyataan di Paper 1.]",
      "Anda harus bisa menurunkan setiap rumus di bab Teori tanpa bantuan.")
bk.QA("Versi awal melaporkan 0,85 di DBL. Bagaimana kami bisa percaya angka Anda sekarang?",
      "Karena kesalahan itu ditemukan oleh audit saya sendiri sebelum publikasi, dan setiap perbaikan terdokumentasi dengan "
      "bukti numerik (laporan supervisi dan laporan perbaikan di repositori). Skor yang sekarang dilaporkan berasal dari "
      "protokol yang dibekukan, dengan unit test dan hash commit.")

# =============================================================== Lampiran
add_learning_path(bk, "p4")

bk.CH("Lampiran. Notasi dan Daftar Periksa")
bk.TBL([["Simbol", "Arti"],
        ["P<sub>g</sub>(c|x)", "peluang kelas c dari pakar g"], ["w<sub>g</sub>, τ", "bobot pakar; suhu softmax"],
        ["k, n<sub>uji</sub>/n<sub>latih</sub>", "jumlah fold luar (15); rasio uji/latih (1/4)"],
        ["SE, MDE", "galat baku selisih; efek terkecil terdeteksi"],
        ["β (bobot kelas)", "parameter effective number (0,999)"], ["C", "kebalikan kekuatan regularisasi L2"]],
       [4.2 * cm, 12.4 * cm], "Tabel L.1. Notasi.")
bk.H2("Daftar periksa sebelum sidang")
bk.B(["Verifikasi 107 salinan DBL dengan korelasi silang gelombang atau mendengarkan sampel.",
      "Lengkapi data penulis, pendanaan, pernyataan AI, dan semua referensi di draf manuskrip.",
      "Siapkan riwayat git (27ae932, 228d42b) dan PROTOCOL.md untuk ditunjukkan.",
      "Latih menurunkan di papan tulis: redundansi MFCC, suku 1/4 Nadeau–Bengio, MDE, dan aturan puncak F0.",
      "Samakan narasi disertasi dengan Paper 1."])

bk.build("reports/defense/Buku_Defense_Paper4.pdf", "Paper 4 dalam Bentuk IMRaD")
print("ok", bk.nq, "questions")
