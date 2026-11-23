"""Handcrafted acoustic features, organised in named feature groups.

Feature groups are the unit of weighting in Paper 4.
"""
import librosa
import numpy as np

SR = 16000
MAX_SECONDS = 8.0
N_MFCC = 20
N_MELS = 32
GROUPS = ("mfcc", "delta", "spectral", "pitch", "energy", "mel")


def _ms(a: np.ndarray) -> list[float]:
    return list(a.mean(axis=-1)) + list(a.std(axis=-1))


def _f0_autocorr(y, fmin=150.0, fmax=1000.0, frame=1024, hop=160):
    """Frame-wise F0 by normalised autocorrelation (pure numpy; librosa.yin's numba
    kernel segfaults in this environment). Returns (f0_hz, peak_confidence)."""
    if len(y) < frame:
        y = np.pad(y, (0, frame - len(y)))
    idx = np.arange(frame)[None, :] + hop * np.arange(1 + (len(y) - frame) // hop)[:, None]
    fr = y[idx] * np.hanning(frame)[None, :]
    spec = np.fft.rfft(fr, n=2 * frame, axis=1)
    acf = np.fft.irfft(np.abs(spec) ** 2, axis=1)[:, :frame]
    acf = acf / (acf[:, :1] + 1e-9)
    lo, hi = int(SR / fmax), int(SR / fmin)
    seg = acf[:, lo:hi]
    lag = seg.argmax(axis=1) + lo
    return SR / lag, seg.max(axis=1)


def extract(path: str) -> dict[str, np.ndarray]:
    y, _ = librosa.load(path, sr=SR, mono=True, duration=MAX_SECONDS)
    if len(y) < SR // 4:
        y = np.pad(y, (0, SR // 4 - len(y)))
    y = y / (np.abs(y).max() + 1e-9)
    S = np.abs(librosa.stft(y, n_fft=512, hop_length=160)) ** 2
    mel = librosa.feature.melspectrogram(S=S, sr=SR, n_mels=N_MELS)
    logmel = librosa.power_to_db(mel)
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
    rms = librosa.feature.rms(S=mag, frame_length=512)[0]
    f0, conf = _f0_autocorr(y)
    n = min(len(f0), len(rms))
    voiced = (rms[:n] > 0.1 * rms.max()) & (conf[:n] > 0.3)
    f0v = f0[:n][voiced] if voiced.sum() > 2 else f0[:n]
    pitch = [f0v.mean(), f0v.std(), np.median(f0v), f0v.min(), f0v.max(), float(voiced.mean())]
    t = np.arange(len(rms))
    energy = [
        rms.mean(), rms.std(), rms.max(), len(y) / SR,
        (t * rms).sum() / (rms.sum() + 1e-9) / len(rms),
        20 * np.log10((rms.max() + 1e-9) / (np.median(rms) + 1e-9)),
    ]
    out = {
        "mfcc": np.array(_ms(mfcc)),
        "delta": np.array(_ms(delta)),
        "spectral": np.array(_ms(spec)),
        "pitch": np.array(pitch),
        "energy": np.array(energy),
        "mel": logmel.mean(axis=1),
    }
    return {k: np.nan_to_num(v.astype(np.float32)) for k, v in out.items()}
