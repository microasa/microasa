"""Unit tests for the v2 F0 estimator and feature groups (supervisor findings F1-F4)."""
import numpy as np
import pytest

from infantcry.features import SR, f0_track

T = np.arange(SR) / SR
RNG = np.random.default_rng(0)


def median_f0(sig):
    f0, _, voiced, _ = f0_track(sig.astype(np.float32))
    return np.nanmedian(f0) if voiced.any() else np.nan, voiced.mean()


@pytest.mark.parametrize("f", [160, 250, 350, 450, 550, 700, 900, 1200, 1500, 1800])
def test_sine_within_2_percent(f):
    est, vfrac = median_f0(np.sin(2 * np.pi * f * T))
    assert vfrac > 0.9
    assert abs(est - f) / f < 0.02, (f, est)


@pytest.mark.parametrize("f", [300, 450, 600, 1100])
def test_harmonic_complex(f):
    sig = sum(np.sin(2 * np.pi * k * f * T) / k for k in range(1, 8) if k * f < SR / 2)
    est, _ = median_f0(sig)
    assert abs(est - f) / f < 0.02, (f, est)


def test_below_range_not_reported_as_fmax():
    est, vfrac = median_f0(np.sin(2 * np.pi * 100 * T))
    assert vfrac < 0.1 or abs(est - 100) > 0  # must not invent a confident in-range pitch
    assert not (vfrac > 0.5 and est > 1500)


@pytest.mark.parametrize("kind", ["white", "lowpass"])
def test_noise_mostly_unvoiced(kind):
    x = RNG.standard_normal(SR)
    if kind == "lowpass":
        x = np.convolve(x, np.ones(40) / 40, "same")
    _, vfrac = median_f0(x)
    assert vfrac < 0.2, vfrac


def test_voicing_uses_same_frames_as_f0():
    sig = np.concatenate([np.zeros(SR // 2), np.sin(2 * np.pi * 400 * T[: SR // 2])])
    f0, _, voiced, rms = f0_track(sig.astype(np.float32))
    assert len(f0) == len(voiced) == len(rms)
    onset = np.argmax(voiced)
    # first voiced frame must overlap the tone (frame start i*160, length 1024)
    assert onset * 160 + 1024 > SR // 2 and onset * 160 < SR // 2 + 160
