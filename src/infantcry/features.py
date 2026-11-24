"""Handcrafted acoustic features, organised in named feature groups (protocol v2).

Feature groups are the unit of weighting in Paper 4. v2 changes (supervisor review):
  * F1  `mel` group is now the temporal STD of log-mel bands. The old `mel` (mean) was an
        exact linear transform of the MFCC means (MFCC = orthonormal DCT of log-mel).
  * F2  F0 estimator rewritten: window-corrected autocorrelation (Boersma 1993), local-peak
        requirement, first-major-peak rule against subharmonic errors, parabolic
        interpolation, search range 150-2000 Hz (covers hyperphonation).
  * F3  delta-MFCC means (~0 by construction) dropped; only their STD is kept.
  * F4  voicing energy is computed on exactly the same frames as F0.
  * F5  clip duration is no longer a feature (shortcut, see D2); it is stored separately
        for the duration-only baseline. Missing pitch statistics stay NaN (imputed inside
        the model pipeline on the training fold) instead of being silently zeroed.
"""
import librosa
import numpy as np
import soundfile as sf

SR = 16000
MAX_SECONDS = 8.0
N_MFCC = 20
N_MELS = 32
GROUPS = ("mfcc", "delta", "spectral", "pitch", "energy", "mel")
FEATURE_VERSION = "v2"

F0_MIN, F0_MAX = 150.0, 2000.0
F0_FRAME, F0_HOP = 1024, 160
VOICING_THRESHOLD = 0.45
MAJOR_PEAK_RATIO = 0.9


def _ms(a: np.ndarray) -> list[float]:
    return list(a.mean(axis=-1)) + list(a.std(axis=-1))


def _frames(y: np.ndarray, frame: int, hop: int) -> np.ndarray:
    if len(y) < frame:
        y = np.pad(y, (0, frame - len(y)))
    idx = np.arange(frame)[None, :] + hop * np.arange(1 + (len(y) - frame) // hop)[:, None]
    return y[idx]


def _norm_acf(x: np.ndarray) -> np.ndarray:
    """Normalised autocorrelation of each row via zero-padded FFT (no circular aliasing)."""
    n = x.shape[-1]
    spec = np.fft.rfft(x, n=2 * n, axis=-1)
    acf = np.fft.irfft(np.abs(spec) ** 2, axis=-1)[..., :n]
    return acf / (acf[..., :1] + 1e-12)


def f0_track(y: np.ndarray, sr: int = SR, fmin: float = F0_MIN, fmax: float = F0_MAX,
             frame: int = F0_FRAME, hop: int = F0_HOP):
    """Frame-wise F0 (Hz, NaN where unvoiced), periodicity strength and voiced mask.

    r(l) = r_x(l) / r_w(l): autocorrelation of the Hann-windowed frame divided by the
    autocorrelation of the window itself, which removes the taper bias towards short
    lags. Candidates are local maxima of r in [sr/fmax, sr/fmin]; the chosen period is
    the SHORTEST candidate whose height is >= MAJOR_PEAK_RATIO x the best candidate
    (prevents picking a subharmonic multiple of the true period). The lag is refined
    by parabolic interpolation. A frame is voiced if its periodicity >= threshold AND
    its RMS >= 10% of the clip's maximum frame RMS (same frames as F0).
    """
    fr = _frames(y, frame, hop)
    win = np.hanning(frame)
    r = _norm_acf(fr * win[None, :]) / np.maximum(_norm_acf(win[None, :]), 1e-3)
    lo, hi = int(np.floor(sr / fmax)), int(np.ceil(sr / fmin))
    hi = min(hi, frame // 2 - 2)
    n = len(fr)
    f0 = np.full(n, np.nan)
    strength = np.zeros(n)
    seg = r[:, lo - 1: hi + 2]  # one guard sample on each side
    is_peak = (seg[:, 1:-1] > seg[:, :-2]) & (seg[:, 1:-1] >= seg[:, 2:])
    for i in range(n):
        cand = np.flatnonzero(is_peak[i]) + lo
        if cand.size == 0:
            continue
        h = r[i, cand]
        if h.max() <= 0:  # no positive periodicity: clearly aperiodic frame
            continue
        l = cand[np.flatnonzero(h >= MAJOR_PEAK_RATIO * h.max())[0]]
        a, b, c = r[i, l - 1], r[i, l], r[i, l + 1]
        den = a - 2 * b + c
        delta = 0.5 * (a - c) / den if den < 0 else 0.0
        f0[i] = sr / (l + np.clip(delta, -0.5, 0.5))
        strength[i] = b
    rms = np.sqrt((fr ** 2).mean(axis=1))
    voiced = (strength >= VOICING_THRESHOLD) & (rms >= 0.1 * rms.max()) & np.isfinite(f0)
    f0[~voiced] = np.nan
    return f0, strength, voiced, rms


def clip_duration(path: str) -> float:
    return float(sf.info(path).duration)


BANDLIMIT_SR = 8000  # protocol v3: keep only 0-4 kHz


def load_audio(path: str, max_seconds: float = MAX_SECONDS, bandlimit: bool = False) -> np.ndarray:
    """Mono 16 kHz audio. With bandlimit=True the signal is resampled to 8 kHz
    (anti-aliased) and back, removing all content above 4 kHz (protocol v3)."""
    y, _ = librosa.load(path, sr=SR, mono=True, duration=max_seconds)
    if bandlimit:
        y = librosa.resample(librosa.resample(y, orig_sr=SR, target_sr=BANDLIMIT_SR),
                             orig_sr=BANDLIMIT_SR, target_sr=SR)
    return y.astype(np.float32)


def extract(path: str, bandlimit: bool = False) -> dict[str, np.ndarray]:
    y = load_audio(path, MAX_SECONDS, bandlimit)
    if len(y) < SR // 4:
        y = np.pad(y, (0, SR // 4 - len(y)))
    y = y / (np.abs(y).max() + 1e-9)  # peak-normalised: loudness is NOT comparable across corpora
    S = np.abs(librosa.stft(y, n_fft=512, hop_length=160)) ** 2
    logmel = librosa.power_to_db(librosa.feature.melspectrogram(S=S, sr=SR, n_mels=N_MELS))
    mfcc = librosa.feature.mfcc(S=logmel, n_mfcc=N_MFCC)
    delta = librosa.feature.delta(mfcc)
    mag = np.sqrt(S)
    spec = np.vstack(
        [
            librosa.feature.spectral_centroid(S=mag, sr=SR),
            librosa.feature.spectral_bandwidth(S=mag, sr=SR),
            librosa.feature.spectral_rolloff(S=mag, sr=SR),
            librosa.feature.spectral_flatness(S=mag),
            librosa.feature.zero_crossing_rate(y, frame_length=512, hop_length=160),
            librosa.feature.spectral_contrast(S=mag, sr=SR, n_bands=5),
        ]
    )
    f0, strength, voiced, frms = f0_track(y)
    if voiced.sum() >= 3:
        fv = f0[voiced]
        pitch = [fv.mean(), fv.std(), np.median(fv), np.percentile(fv, 5), np.percentile(fv, 95)]
    else:
        pitch = [np.nan] * 5
    pitch += [float(voiced.mean()), float(strength[voiced].mean()) if voiced.any() else 0.0]
    t = np.arange(len(frms))
    energy = [
        frms.mean(), frms.std(), frms.max(),
        (t * frms).sum() / (frms.sum() + 1e-9) / max(len(frms), 1),
        20 * np.log10((frms.max() + 1e-9) / (np.median(frms) + 1e-9)),
    ]
    out = {
        "mfcc": np.array(_ms(mfcc)),
        "delta": delta.std(axis=1),
        "spectral": np.array(_ms(spec)),
        "pitch": np.array(pitch, dtype=float),
        "energy": np.array(energy),
        "mel": logmel.std(axis=1),
    }
    return {k: v.astype(np.float32) for k, v in out.items()}
