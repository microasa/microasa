"""Curated learning path (videos, readings, exercises) shared by the dissertation books.

Every YouTube link below was found through a web search on 26 Nov 2026 and points to a video whose title matches the
listed topic. Channel attribution is given only where the search result confirmed it. Videos can be removed or
renamed by their owners; if a link breaks, search YouTube for the title shown.
Readings are standard textbooks and the primary papers cited in the manuscripts."""
from reportlab.lib.units import cm


def yt(vid):
    return f"https://www.youtube.com/watch?v={vid}"


V = {
    "fourier": ("But what is the Fourier Transform? A visual introduction (3Blue1Brown)", yt("spUNpyF58BY")),
    "asp": ("Audio Signal Processing for Machine Learning (Valerio Velardo, The Sound of AI)", yt("iCwMQJnKk2c")),
    "stft": ("Short-Time Fourier Transform Explained Easily", yt("-Yxj3yfvY-4")),
    "mel": ("Mel Spectrograms Explained Easily", yt("9GHCiiDLHQ4")),
    "mfcc": ("Mel Frequency Cepstral Coefficients (MFCC) Explained (Valerio Velardo)", yt("SJo7vPgRlBQ")),
    "sincnet": ("Speaker Recognition from raw waveform with SincNet (penjelasan paper)", yt("sendxu-rHlY")),
    "softmax": ("Neural Networks Part 5: ArgMax and SoftMax (StatQuest)", yt("KpKog-L9veg")),
    "xent": ("Neural Networks Part 6: Cross Entropy (StatQuest)", yt("6ArSys5qHAU")),
    "adam": ("ADAM Optimization Algorithm Explained Visually", yt("MWZakqZDgfQ")),
    "cv": ("Machine Learning Fundamentals: Cross Validation (StatQuest)", yt("fSytzGwwBVw")),
    "confusion": ("Machine Learning Fundamentals: The Confusion Matrix (StatQuest)", yt("Kdsp6soqA7o")),
    "logreg": ("StatQuest: Logistic Regression", yt("yIYKR4sgzI8")),
    "odds": ("Odds and Log(Odds), Clearly Explained!!! (StatQuest)", yt("ARfXDSkQf1Y")),
    "pca": ("StatQuest: PCA main ideas in only 5 minutes!!!", yt("HMOI_lkzW08")),
    "boot": ("Bootstrapping Main Ideas!!! (StatQuest)", yt("Xz0x-8-cgaQ")),
    "bootp": ("Using Bootstrapping to Calculate p-values!!! (StatQuest)", yt("N4ZQQqyIf6k")),
    "ci": ("Confidence Intervals, Clearly Explained!!! (StatQuest)", yt("TqOeMYtOc1w")),
    "se": ("The standard error, Clearly Explained!!! (StatQuest)", yt("XNgt7F6FqDU")),
    "power": ("Statistical Power, Clearly Explained!!! (StatQuest)", yt("Rsc5znwR5FA")),
    "poweran": ("Power Analysis, Clearly Explained!!! (StatQuest)", yt("VX_M3tIyiYk")),
    "holm": ("Holm-Bonferroni Correction — Smarter Multiple Testing Explained in 2 Minutes", yt("LJrVsYHVVck")),
    "fdr": ("False Discovery Rates, FDR, clearly explained (StatQuest)", yt("K8LQSvtjcEo")),
    "phack": ("p-hacking: What it is and how to avoid it!", yt("HDCOUXE3HMM")),
    "w2v2": ("wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations (penjelasan paper)",
             yt("aUSXvoWfy3w")),
    "hubert": ("HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units "
               "(penjelasan paper)", yt("p5M7CYZAqfA")),
    "ssl": ("Self-supervised Learning and its applications to Human Language Processing (1) — Hung-yi Lee, OAMLS",
            yt("QTlsNoV7MQM")),
    "leak1": ("Reproducibility Crisis in Machine Learning Based Science — Sayash Kapoor (2022 Virtual Event, Part 3)",
              yt("hfK-fMGTI3M")),
    "prisma": ("The PRISMA 2020 flow diagram: what is it all about?", yt("IgYqlv71l6g")),
    "kappa": ("Cohen's Kappa: Measuring Agreement", yt("aUxlxrPKyxY")),
    "conv": ("But what is a convolution? (3Blue1Brown)", yt("KuXjwB4LzSA")),
    "rnn": ("Recurrent Neural Networks (RNNs), Clearly Explained!!! (StatQuest)", yt("AsNTP8Kwu80")),
    "lstm": ("Long Short-Term Memory (LSTM), Clearly Explained (StatQuest)", yt("YCzL96nL7j0")),
    "transformer": ("Transformer Neural Networks, ChatGPT's foundation, Clearly Explained!!! (StatQuest)",
                    yt("zxQyTK8quyY")),
    "wavelet": ("Wavelets: a mathematical microscope (Artem Kirsanov)", yt("jnxqHcObNK4")),
    "leak2": ("The Reproducibility Crisis in Machine Learning Based Science — Arvind Narayanan (Hariri Institute)",
              yt("icJFr9TYmD4")),
}

R = {
    "fmp": "Müller, M. Fundamentals of Music Processing (Springer) dan notebook FMP gratis (audiolabs-erlangen.de/FMP): "
           "bab Fourier, STFT, dan estimasi F0/melodi.",
    "sasp": "Smith, J. O. Spectral Audio Signal Processing (gratis daring, CCRMA Stanford): jendela, resolusi, STFT.",
    "slp": "Jurafsky & Martin, Speech and Language Processing, edisi ke-3 draf (gratis): bab fitur akustik dan ASR.",
    "islr": "James, Witten, Hastie & Tibshirani, An Introduction to Statistical Learning (gratis, statlearning.com): "
            "bab klasifikasi (regresi logistik), resampling (CV, bootstrap), regularisasi, dan PCA.",
    "esl": "Hastie, Tibshirani & Friedman, The Elements of Statistical Learning (gratis): model averaging dan stacking, "
           "seleksi dan penilaian model.",
    "d2l": "Zhang et al., Dive into Deep Learning (gratis, d2l.ai): softmax, optimisasi, Adam.",
    "kapoor": "Kapoor & Narayanan (2023), Leakage and the reproducibility crisis in machine-learning-based science, "
              "Patterns 4:100804.",
    "saeb": "Saeb et al. (2017), The need to approximate the use-case in clinical machine learning, GigaScience 6(5).",
    "varo": "Varoquaux (2018), Cross-validation failure: small sample sizes lead to large error bars, NeuroImage 180.",
    "nb": "Nadeau & Bengio (2003), Inference for the generalization error, Machine Learning 52; Bouckaert & Frank (2004).",
    "perm": "Ojala & Garriga (2010), Permutation tests for studying classifier performance, JMLR 11; "
            "Field & Welsh (2007), Bootstrapping clustered data, JRSS-B 69.",
    "holm": "Holm (1979), A simple sequentially rejective multiple test procedure, Scand J Stat 6.",
    "lakens": "Lakens (2017), Equivalence tests: a practical primer, Social Psychological and Personality Science 8(4).",
    "sincleaf": "Ravanelli & Bengio (2018) SincNet; Zeghidour et al. (2021) LEAF; Anderson et al. (2023) Learnable "
                "frontends that do not learn; Schlüter & Gutenbrunner (2022) EfficientLEAF.",
    "pcen": "Wang et al. (2017) Trainable frontend (PCEN); Lostanlen et al. (2019) PCEN: why and how, IEEE SPL 26.",
    "boersma": "Boersma (1993), Accurate short-term analysis of the fundamental frequency and the harmonics-to-noise "
               "ratio, IFA Proceedings 17.",
    "ssl": "Baevski et al. (2020) wav2vec 2.0; Hsu et al. (2021) HuBERT; Mohamed, Lee et al. (2022) Self-supervised "
           "speech representation learning: a review (arXiv 2205.10643); Yang et al. (2021) SUPERB.",
    "wolpert": "Wolpert (1992), Stacked generalization, Neural Networks 5(2).",
    "prisma": "Page et al. (2021), The PRISMA 2020 statement, BMJ 372:n71, beserta dokumen Explanation and "
              "Elaboration; Rethlefsen et al. (2021), PRISMA-S (pelaporan pencarian).",
    "kitch": "Kitchenham & Charters (2007), Guidelines for performing systematic literature reviews in software "
             "engineering (EBSE Technical Report); Cochrane Handbook for Systematic Reviews of Interventions.",
    "biblio": "Donthu et al. (2021), How to conduct a bibliometric analysis: an overview and guidelines, Journal of "
              "Business Research 133.",
    "kappa": "Cohen (1960), A coefficient of agreement for nominal scales; Landis & Koch (1977), The measurement of "
             "observer agreement for categorical data, Biometrics 33.",
    "swim": "Campbell et al. (2020), Synthesis without meta-analysis (SWiM) in systematic reviews: reporting "
            "guideline, BMJ 368:l6890.",
    "probast": "Wolff et al. (2019), PROBAST: a tool to assess the risk of bias and applicability of prediction model "
               "studies, Annals of Internal Medicine 170; Collins et al. (2024), TRIPOD+AI, BMJ 385.",
    "dlbook": "Goodfellow, Bengio & Courville, Deep Learning (MIT Press, gratis daring): CNN, RNN, regularisasi; "
              "Zhang et al., Dive into Deep Learning (d2l.ai): attention dan Transformer.",
    "arch": "Hochreiter & Schmidhuber (1997) LSTM; Vaswani et al. (2017) Attention is all you need; Gong et al. "
            "(2021) AST: Audio Spectrogram Transformer (arXiv 2104.01778).",
    "wavecqt": "Mallat, A Wavelet Tour of Signal Processing (Academic Press); Brown (1991), Calculation of a constant "
               "Q spectral transform, JASA 89(1).",
    "cryrev": "Ji et al. (2021), A review of infant cry analysis and classification, EURASIP J. Audio Speech Music "
              "Process.; Owino & Shibwabo (2025), systematic review infant cry paralinguistic classification, JMIR "
              "Rehabil Assist Technol.",
    "cui": "Cui et al. (2019), Class-balanced loss based on effective number of samples, CVPR.",
}


def module(bk, title, goal, prereq, theory_ref, videos, readings, exercises, checks):
    bk.H2(title)
    bk.P(f"<b>Tujuan:</b> {goal}")
    bk.P(f"<b>Prasyarat:</b> {prereq} <b>Bab terkait di buku ini:</b> {theory_ref}.")
    if videos:
        rows = [["Video", "Tautan"]] + [[V[k][0], V[k][1]] for k in videos]
        bk.TBL(rows, [8.6 * cm, 8.0 * cm], "Video yang disarankan (judul terverifikasi lewat pencarian web).")
    bk.P("<b>Bacaan:</b>")
    bk.B([R[k] for k in readings])
    bk.P("<b>Latihan:</b>")
    bk.B(exercises)
    bk.P("<b>Cek diri (harus bisa dijawab tanpa catatan):</b>")
    bk.B(checks)


def plan(bk, rows):
    bk.TBL([["Minggu", "Modul", "Target akhir minggu"]] + rows, [1.8 * cm, 5.4 * cm, 9.4 * cm],
           "Rencana belajar empat minggu menjelang sidang.")


def add_learning_path(bk, paper):
    bk.CH("Jalur Belajar Mendalam")
    bk.P("Bab ini mengubah isi paper menjadi kurikulum. Setiap modul punya tujuan, prasyarat, video, bacaan, latihan "
         "langsung, dan pertanyaan cek diri. Urutannya mengikuti alur paper: sinyal → representasi → model → evaluasi "
         "→ statistik → integritas. Video dipilih karena menjelaskan intuisi; bacaan dipilih karena memberi rumus dan "
         "bukti. Untuk sidang, intuisi dari video belum cukup: Anda harus bisa menurunkan rumusnya sendiri.")
    bk.WARN("Semua tautan YouTube ditemukan lewat pencarian web pada 26 November 2026, dan judulnya cocok dengan topik. "
            "Video bisa dihapus atau diganti namanya oleh pemiliknya; jika tautan rusak, cari judulnya di YouTube. "
            "Untuk estimasi F0 berbasis autokorelasi, tidak ditemukan tutorial video yang bisa diverifikasi, jadi "
            "modul itu memakai bacaan saja.")
    if paper == "p1":
        module(bk, "Modul 1. Sinyal, Fourier, dan STFT",
               "memahami spektrum, resolusi frekuensi, dan trade-off waktu–frekuensi yang menentukan Δf = 31,25 Hz.",
               "aljabar kompleks dasar; sinus dan kosinus.", "T.2",
               ["fourier", "asp", "stft"], ["fmp", "sasp"],
               ["Hitung STFT satu klip tangis dengan N = 512 dan N = 1.024; bandingkan bagaimana harmonik terpisah.",
                "Buktikan bahwa Δf = f<sub>s</sub>/N dan main-lobe Hann = 4 bin."],
               ["Mengapa FFT 1.024 tidak mengubah hasil Donate-a-Cry?", "Berapa Δf dan main-lobe di paper ini?"])
        module(bk, "Modul 2. Skala mel, filterbank, dan MFCC",
               "memahami filterbank sebagai matriks 40 × 257 dan hubungan log-mel dengan MFCC.",
               "Modul 1.", "T.3", ["mel", "mfcc"], ["fmp", "slp"],
               ["Bangun filterbank mel 40 pita secara manual dan bandingkan dengan librosa.",
                "Tunjukkan secara numerik bahwa rata-rata MFCC = DCT dari rata-rata log-mel."],
               ["Mengapa log-mel dan SAFB berbiaya sama?", "Apa yang hilang ketika MFCC memotong koefisien tinggi?"])
        module(bk, "Modul 3. Front-end yang dapat dipelajari",
               "memahami SincNet, LEAF/PCEN, Gaussian, dan SAFB, serta kritik bahwa front-end learnable sering tidak "
               "benar-benar belajar.", "Modul 2; kalkulus turunan.", "T.4–T.6",
               ["sincnet"], ["sincleaf", "pcen"],
               ["Implementasikan satu pita SAFB di PyTorch dan bandingkan gradien autograd dengan rumus ∂H/∂c, ∂H/∂w, "
                "∂H/∂s di buku ini.",
                "Plot ∂H/∂s sepanjang frekuensi untuk s = 0,3 bin dan s = 3 bin; jelaskan mengapa yang pertama nyaris nol."],
               ["Mengapa normalisasi luas penting?", "Apa arti 'movement is not adaptation'?"])
        module(bk, "Modul 4. Pelatihan jaringan",
               "memahami softmax, cross-entropy berbobot, AdamW, dan early stopping.", "kalkulus; probabilitas dasar.",
               "T.7", ["softmax", "xent", "adam"], ["d2l"],
               ["Latih classifier kecil pada data timpang dengan dan tanpa bobot kelas; bandingkan porsi prediksi "
                "mayoritas.", "Turunkan gradien cross-entropy terhadap logit (p − y)."],
               ["Mengapa AdamW memisahkan weight decay?", "Mengapa early stopping berhenti di epoch 2–5 di Donate-a-Cry?"])
        module(bk, "Modul 5. Evaluasi dan kebocoran",
               "memahami mengapa pembagian per kontributor wajib dan bagaimana kebocoran menggelembungkan skor.",
               "Modul 4.", "T.8", ["cv", "leak1", "leak2"], ["kapoor", "saeb", "varo", "islr"],
               ["Bandingkan pembagian acak per klip dengan pembagian per UUID pada Donate-a-Cry; catat selisih skornya.",
                "Daftar semua jalur kebocoran yang mungkin di pipeline Anda (pengelompokan, augmentasi, duplikat)."],
               ["Ke arah mana kebocoran membiaskan skor?", "Mengapa UUID bukan jaminan independensi bayi?"])
        module(bk, "Modul 6. Metrik dan rujukan peluang acak",
               "menguasai Macro-F1, classifier mayoritas, dan acak bertingkat.", "Modul 5.", "T.9",
               ["confusion"], ["islr"],
               ["Simulasikan 10.000 classifier acak bertingkat pada distribusi Donate-a-Cry; bandingkan dengan 0,196.",
                "Turunkan Macro-F1 mayoritas 2p/(K(1 + p)) dan hitung untuk S1 dan S2."],
               ["Mengapa akurasi 83,6% tidak berarti apa-apa?", "Di mana posisi model Anda relatif terhadap dua rujukan?"])
        module(bk, "Modul 7. Inferensi: bootstrap, permutasi, Holm, daya",
               "menguasai bootstrap klaster, uji randomisasi berpasangan, Holm, corrected t-test, dan konsep daya.",
               "statistik dasar (p-value, distribusi normal).", "T.10",
               ["boot", "bootp", "ci", "se", "holm", "fdr", "power"], ["perm", "holm", "nb"],
               ["Implementasikan bootstrap klaster dan bandingkan lebarnya dengan bootstrap per klip.",
                "Implementasikan uji randomisasi yang menukar prediksi per grup; tunjukkan p minimum = 1/(B + 1).",
                "Terapkan Holm pada 12 p-value Tabel R.3 secara manual."],
               ["Apa asumsi keterpertukaran uji randomisasi?", "Mengapa Holm lebih kuat dari Bonferroni?"])
        module(bk, "Modul 8. Integritas riset",
               "memahami p-hacking, pra-spesifikasi versus pra-registrasi, dan uji ekuivalensi.", "Modul 7.",
               "M.5 dan D.7", ["phack", "poweran"], ["lakens", "kapoor"],
               ["Tulis ulang protokol ReCANVo Anda dalam format pra-registrasi publik (misalnya OSF).",
                "Lakukan TOST dengan margin ±0,02 pada SAFB vs Gaussian, dan jelaskan mengapa itu tetap post-hoc."],
               ["Apa beda pre-specified dan pre-registered?", "Mengapa 'tidak berbeda' bukan 'setara'?"])
        plan(bk, [["1", "Modul 1–2", "bisa menggambar pipeline STFT → mel → log → DCT dan menghitung Δf"],
                  ["2", "Modul 3–4", "bisa menurunkan gradien SAFB dan menjelaskan pelatihan"],
                  ["3", "Modul 5–6", "bisa menjelaskan kebocoran dan menurunkan rujukan peluang acak"],
                  ["4", "Modul 7–8 + simulasi sidang", "bisa menjawab seluruh bank pertanyaan tanpa catatan"]])
    elif paper in ("p2", "p3"):
        _slr_modules(bk, paper)
    else:
        module(bk, "Modul 1. Sinyal, mel, dan MFCC",
               "memahami representasi akustik dan bukti bahwa rata-rata MFCC redundan dengan rata-rata log-mel.",
               "aljabar linear dasar.", "T.1", ["fourier", "asp", "stft", "mel", "mfcc"], ["fmp", "sasp", "slp"],
               ["Regresikan rata-rata MFCC pada grup mel versi lama (rata-rata, file v1 data/interim/cryceleb.npz) dan "
                "versi baru (simpangan baku, data/interim/hand_cryceleb.npz); reproduksi R² 1,000 vs 0,300.",
                "Buktikan secara aljabar bahwa std(D·L) ≠ D·std(L)."],
               ["Mengapa grup fitur harus tidak redundan sebelum dibobot?", "Mengapa rata-rata delta mendekati nol?"])
        module(bk, "Modul 2. Estimasi F0",
               "memahami autokorelasi, koreksi jendela Boersma, kesalahan oktaf, dan interpolasi parabolik.",
               "Modul 1.", "T.2", [], ["boersma", "fmp"],
               ["Jalankan tests/test_features.py; ubah MAJOR_PEAK_RATIO menjadi 1,0 dan amati test 1.200 Hz gagal.",
                "Turunkan rumus interpolasi parabolik δ = ½(a − c)/(a − 2b + c)."],
               ["Mengapa maksimum global menghasilkan subharmonik?", "Mengapa batas atas harus 2.000 Hz untuk tangis?"])
        module(bk, "Modul 3. Encoder self-supervised",
               "memahami wav2vec 2.0, HuBERT, dan mengapa lapisan berbeda menyimpan informasi berbeda.",
               "Modul 1; dasar Transformer.", "T.3", ["w2v2", "hubert", "ssl"], ["ssl"],
               ["Dari data/interim/emb_w2v2_*.npz, latih satu regresi logistik per lapisan dan plot macro-F1 per lapisan.",
                "Bandingkan pola itu dengan lapisan yang dipilih best-single di results/v2/*_diag.csv."],
               ["Apa beda tujuan pretraining wav2vec 2.0 dan HuBERT?", "Mengapa lapisan terakhir sering paling buruk?"])
        module(bk, "Modul 4. Regresi logistik, regularisasi, dan PCA",
               "memahami model pakar, peran C, dan PCA whitening.", "aljabar linear; probabilitas.", "T.4",
               ["logreg", "odds", "pca"], ["islr"],
               ["Ulangi satu run dengan C tetap 1,0 dan bandingkan dengan C yang dituning.",
                "Turunkan PCA whitening dari dekomposisi eigen kovarians."],
               ["Mengapa PCA harus dipasang di dalam fold?", "Apa efek C kecil?"])
        module(bk, "Modul 5. Bobot kelas dan fusi",
               "memahami balanced vs effective number, linear pool, softmax-τ, stacking, dan SUPERB.",
               "Modul 4.", "T.5–T.6", ["softmax", "xent"], ["cui", "wolpert", "esl", "ssl"],
               ["Ubah fusion.combine agar stacking memakai prediksi in-sample (bukan OOF) dan ukur kenaikan skor palsu "
                "di data latih vs penurunan di data uji.",
                "Hitung total bobot sampel skema effective tanpa normalisasi untuk kelas DBL."],
               ["Mengapa stacking wajib OOF?", "Apa batas τ → 0 dan τ → ∞?"])
        module(bk, "Modul 6. Kebocoran dan provenance data",
               "memahami tiga jalur kebocoran dan cara mengaudit duplikasi antar-korpus.", "Modul 4.", "T.7",
               ["cv", "leak1", "leak2"], ["kapoor", "saeb", "varo"],
               ["Jalankan scripts/prepare_dbl.py dengan ambang 0,90 dan 0,98; catat jumlah klip yang dibuang.",
                "Verifikasi 10 dari 107 salinan dengan korelasi silang gelombang (scipy.signal.correlate)."],
               ["Mengapa kosinus fitur bukan bukti salinan yang final?", "Mengapa ID anonim CryCeleb dibuang?"])
        module(bk, "Modul 7. Statistik CV berulang, koreksi, dan daya",
               "menguasai uji Nadeau–Bengio, Holm, CI, dan MDE.", "statistik dasar.", "T.8",
               ["se", "ci", "boot", "holm", "fdr", "power", "poweran"], ["nb", "holm", "perm"],
               ["Dari results/v2/*_folds.csv, hitung p naif (t-test biasa) dan p Nadeau–Bengio untuk H1; bandingkan.",
                "Reproduksi Tabel R.3 (MDE) dari primary_tests.csv."],
               ["Dari mana suku 1/4?", "Apa beda 'efek besar dikesampingkan' dan 'tidak ada efek'?"])
        module(bk, "Modul 8. Integritas riset",
               "memahami forking paths, pra-registrasi, dan pelaporan deviasi.", "Modul 7.", "T.9",
               ["phack"], ["kapoor", "lakens"],
               ["Baca PROTOCOL.md dan riwayat git (27ae932, 228d42b); jelaskan urutan protokol → hasil kepada teman.",
                "Tulis paragraf 'Deviations from plan' untuk manuskrip."],
               ["Mengapa forking paths tidak bisa menjelaskan hasil negatif?", "Apa yang membuktikan pra-registrasi Anda?"])
        plan(bk, [["1", "Modul 1–3", "bisa menjelaskan fitur, F0, dan encoder dari dasar"],
                  ["2", "Modul 4–5", "bisa menurunkan model pakar dan semua combiner"],
                  ["3", "Modul 6–7", "bisa menjelaskan kebocoran, audit, Nadeau–Bengio, dan MDE"],
                  ["4", "Modul 8 + simulasi sidang", "bisa menjawab seluruh bank pertanyaan tanpa catatan"]])


def _slr_modules(bk, paper):
    module(bk, "Modul 1. Metodologi tinjauan sistematis dan PRISMA 2020",
           "memahami perbedaan tinjauan naratif, sistematis, dan bibliometrik, serta isi checklist dan diagram alir "
           "PRISMA 2020.", "tidak ada.", "T.1–T.2", ["prisma"], ["prisma", "kitch"],
           ["Isi checklist PRISMA 2020 (27 butir) untuk naskah Anda dan tandai butir yang belum terpenuhi.",
            "Gambar diagram alir PRISMA dengan angka nyata: identified, duplicates removed, screened, excluded, "
            "full-text assessed, included."],
           ["Apa beda record, report, dan study dalam PRISMA 2020?", "Mengapa pra-registrasi (OSF/PROSPERO) penting?"])
    module(bk, "Modul 2. Strategi pencarian dan bibliometrik",
           "merancang string pencarian yang presisi, memahami Crossref/OpenAlex/Scopus, dan analisis bibliometrik.",
           "Modul 1.", "T.3 dan R.2", [], ["prisma", "biblio"],
           ["Jalankan ulang kueri Crossref Anda dan hitung berapa record yang memuat 'crypt' di judul; ulangi dengan "
            "frasa \u201cinfant cry\u201d dalam tanda kutip, atau cry NOT crypt*.",
            "Bandingkan jumlah record Crossref dengan Scopus dan IEEE Xplore untuk kueri yang sama."],
           ["Mengapa 'cry' sebagai substring berbahaya?", "Apa itu precision dan recall sebuah string pencarian?"])
    module(bk, "Modul 3. Penyaringan dan reliabilitas antar-penilai",
           "melakukan screening judul/abstrak dan teks lengkap oleh dua penilai, dan menghitung Cohen's kappa.",
           "Modul 2.", "T.4", ["kappa"], ["kappa", "kitch"],
           ["Saring 50 record secara independen bersama satu rekan, hitung kappa dan persentase kesepakatan.",
            "Tulis aturan penyelesaian ketidaksepakatan (konsensus atau penilai ketiga)."],
           ["Mengapa kappa bisa rendah walau kesepakatan tinggi (kappa paradox)?", "Berapa kappa yang dianggap cukup?"])
    module(bk, "Modul 4. Ekstraksi data, kualitas studi, dan sintesis",
           "membuat tabel ekstraksi, menilai risiko bias, dan melaporkan sintesis tanpa meta-analisis secara benar.",
           "Modul 3.", "T.5 dan D.3", [], ["swim", "probast"],
           ["Rancang tabel ekstraksi: dataset, tugas, split (per subjek/acak), metrik, ada/tidaknya macro-F1, "
            "evaluasi lintas korpus, ablation.",
            "Isi tabel itu untuk 10 studi pertama dan hitung proporsinya."],
           ["Apa beda klaim kualitatif dan klaim yang didukung tabel ekstraksi?", "Kapan meta-analisis tidak layak?"])
    if paper == "p2":
        module(bk, "Modul 5. CNN untuk spektrogram", "memahami konvolusi, receptive field, dan pooling.",
               "aljabar linear.", "T.6", ["conv"], ["dlbook"],
               ["Latih CNN kecil pada log-mel satu korpus tangis dan catat jumlah parameter.",
                "Hitung receptive field tiga lapis konvolusi 3×3 dengan pooling 2×2."],
               ["Mengapa CNN cocok untuk pola lokal waktu–frekuensi?", "Apa kelemahan CNN untuk dinamika panjang?"])
        module(bk, "Modul 6. RNN, LSTM, GRU, dan CRNN", "memahami pemodelan sekuens dan masalah vanishing gradient.",
               "Modul 5.", "T.6", ["rnn", "lstm"], ["dlbook", "arch"],
               ["Tulis persamaan gerbang LSTM dan jelaskan peran tiap gerbang.",
                "Bandingkan CNN dan CRNN pada data yang sama dengan split per bayi."],
               ["Mengapa LSTM mengatasi vanishing gradient?", "Kapan CRNN layak dipakai?"])
        module(bk, "Modul 7. Attention, Transformer, AST, dan self-supervised",
               "memahami self-attention, patch spektrogram, dan representasi pretrained.", "Modul 6.", "T.6",
               ["transformer", "w2v2", "hubert", "ssl"], ["arch", "ssl"],
               ["Turunkan attention(Q, K, V) = softmax(QK<super>T</super>/√d)V dan jelaskan peran √d.",
                "Baca paper AST dan gambarkan bagaimana spektrogram 128 × T dipotong menjadi patch."],
               ["Mengapa Transformer butuh positional embedding?", "Mengapa model pretrained menarik untuk data kecil?"])
        module(bk, "Modul 8. Evaluasi, generalisasi lintas korpus, dan ablation",
               "memahami confounding, split per subjek, domain shift, dan metrik seimbang.", "Modul 4–7.", "T.7",
               ["cv", "confusion", "leak1", "leak2"], ["kapoor", "saeb", "varo"],
               ["Ambil satu klaim 'arsitektur X lebih baik' dari korpus Anda dan daftar semua variabel yang ikut berubah.",
                "Hitung akurasi classifier mayoritas pada salah satu dataset yang sering dipakai."],
               ["Mengapa perbaikan arsitektur tidak bisa diatribusikan tanpa ablation?", "Apa itu domain shift?"])
    else:
        module(bk, "Modul 5. Fourier dan STFT", "memahami spektrum, jendela, dan resolusi waktu–frekuensi.",
               "aljabar kompleks.", "T.6", ["fourier", "stft", "asp"], ["fmp", "sasp"],
               ["Hitung STFT satu klip tangis dengan tiga panjang jendela dan bandingkan.",
                "Buktikan Δf = f<sub>s</sub>/N."], ["Apa trade-off waktu–frekuensi?", "Mengapa jendela Hann dipakai?"])
        module(bk, "Modul 6. Mel, MFCC, wavelet, dan CQT",
               "memahami representasi handcrafted utama dan dasar matematisnya.", "Modul 5.", "T.6–T.7",
               ["mel", "mfcc", "wavelet"], ["fmp", "wavecqt", "slp"],
               ["Turunkan pipeline MFCC dan tunjukkan bahwa rata-rata MFCC adalah DCT dari rata-rata log-mel.",
                "Bandingkan resolusi CQT (Q konstan) dengan STFT pada nada 300 Hz dan 1.200 Hz."],
               ["Mengapa skala mel berasal dari pendengaran dewasa?", "Mengapa wavelet cocok untuk transien?"])
        module(bk, "Modul 7. Front-end yang dapat dipelajari",
               "memahami SincNet, LEAF/PCEN, dan filterbank adaptif, termasuk SAFB dari Paper 1.", "Modul 6.", "T.8",
               ["sincnet"], ["sincleaf", "pcen"],
               ["Ringkas desain dan hasil Paper 1 (SAFB) sebagai contoh benchmark front-end terkendali.",
                "Daftar biaya (parameter, waktu) SincNet dan LEAF dari literatur."],
               ["Mengapa front-end learnable rawan overfitting pada data kecil?", "Apa arti 'movement is not adaptation'?"])
        module(bk, "Modul 8. Benchmark fitur terkendali dan evaluasi",
               "merancang perbandingan fitur yang hanya mengubah satu variabel.", "Modul 4–7.", "T.9",
               ["cv", "leak1", "power"], ["kapoor", "varo"],
               ["Tulis protokol benchmark: satu classifier, satu dataset, split per subjek, macro-F1, uji berpasangan.",
                "Bandingkan protokol Anda dengan desain Paper 1."],
               ["Mengapa perbandingan dengan baseline dari publikasi lain tidak sah?", "Apa itu confounding?"])
    plan(bk, [["1", "Modul 1–2", "bisa menjelaskan PRISMA dan memperbaiki string pencarian"],
              ["2", "Modul 3–4", "menyelesaikan screening ganda, kappa, dan tabel ekstraksi"],
              ["3", "Modul 5–7", "menguasai teori domain yang ditinjau"],
              ["4", "Modul 8 + simulasi sidang", "bisa menjawab seluruh bank pertanyaan tanpa catatan"]])
