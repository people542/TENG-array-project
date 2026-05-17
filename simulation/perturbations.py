"""Non-ideal perturbations for simulated TENG array signals."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PerturbationConfig:
    """Configuration for array-signal perturbations."""

    snr_db: float | None = None
    gain_variation: float = 0.0
    crosstalk_ratio: float = 0.0
    fault_ratio: float = 0.0
    baseline_drift_ratio: float = 0.0


def add_awgn(signal: np.ndarray, snr_db: float, rng: np.random.Generator | int | None = None) -> np.ndarray:
    """Add white Gaussian noise at the requested signal-to-noise ratio."""
    rng = _as_rng(rng)
    signal_power = float(np.mean(np.square(signal)))
    if signal_power <= 0:
        return signal.copy()

    noise_power = signal_power / (10.0 ** (snr_db / 10.0))
    noise = rng.normal(loc=0.0, scale=np.sqrt(noise_power), size=signal.shape)
    return signal + noise


def apply_channel_gain(
    signal: np.ndarray,
    gain_variation: float,
    rng: np.random.Generator | int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply fixed per-channel multiplicative gain variation."""
    if gain_variation < 0:
        raise ValueError(f"gain_variation must be non-negative, got {gain_variation!r}")
    rng = _as_rng(rng)
    rows, cols = _array_shape(signal)
    gains = rng.uniform(1.0 - gain_variation, 1.0 + gain_variation, size=(rows, cols))
    return signal * gains[..., np.newaxis], gains


def add_baseline_drift(
    signal: np.ndarray,
    drift_ratio: float,
    rng: np.random.Generator | int | None = None,
) -> np.ndarray:
    """Add low-frequency sinusoidal baseline drift to each channel."""
    if drift_ratio < 0:
        raise ValueError(f"drift_ratio must be non-negative, got {drift_ratio!r}")
    if drift_ratio == 0:
        return signal.copy()

    rng = _as_rng(rng)
    rows, cols, samples = _signal_shape(signal)
    peak = float(np.max(np.abs(signal)))
    if peak <= 0:
        return signal.copy()

    t = np.linspace(0.0, 1.0, samples, endpoint=False)
    phases = rng.uniform(0.0, 2.0 * np.pi, size=(rows, cols))
    freqs = rng.uniform(0.2, 1.0, size=(rows, cols))
    amplitudes = rng.uniform(0.0, drift_ratio * peak, size=(rows, cols))
    drift = amplitudes[..., np.newaxis] * np.sin(
        2.0 * np.pi * freqs[..., np.newaxis] * t + phases[..., np.newaxis]
    )
    return signal + drift


def apply_neighbor_crosstalk(signal: np.ndarray, crosstalk_ratio: float) -> np.ndarray:
    """Mix each channel with its four-neighbor average."""
    if not 0.0 <= crosstalk_ratio <= 1.0:
        raise ValueError(f"crosstalk_ratio must be in [0, 1], got {crosstalk_ratio!r}")
    if crosstalk_ratio == 0:
        return signal.copy()

    rows, cols, _ = _signal_shape(signal)
    neighbor_sum = np.zeros_like(signal)
    neighbor_count = np.zeros((rows, cols, 1), dtype=float)

    neighbor_sum[1:, :, :] += signal[:-1, :, :]
    neighbor_count[1:, :, :] += 1.0
    neighbor_sum[:-1, :, :] += signal[1:, :, :]
    neighbor_count[:-1, :, :] += 1.0
    neighbor_sum[:, 1:, :] += signal[:, :-1, :]
    neighbor_count[:, 1:, :] += 1.0
    neighbor_sum[:, :-1, :] += signal[:, 1:, :]
    neighbor_count[:, :-1, :] += 1.0

    neighbor_avg = neighbor_sum / neighbor_count
    return (1.0 - crosstalk_ratio) * signal + crosstalk_ratio * neighbor_avg


def apply_faulty_channels(
    signal: np.ndarray,
    fault_ratio: float,
    rng: np.random.Generator | int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Set a random subset of channels to zero and return the fault mask."""
    if not 0.0 <= fault_ratio <= 1.0:
        raise ValueError(f"fault_ratio must be in [0, 1], got {fault_ratio!r}")

    rng = _as_rng(rng)
    rows, cols = _array_shape(signal)
    channel_count = rows * cols
    fault_count = int(round(channel_count * fault_ratio))
    mask = np.zeros((rows, cols), dtype=bool)
    output = signal.copy()

    if fault_count == 0:
        return output, mask

    indices = rng.choice(channel_count, size=fault_count, replace=False)
    mask.flat[indices] = True
    output[mask, :] = 0.0
    return output, mask


def apply_perturbations(
    signal: np.ndarray,
    config: PerturbationConfig,
    rng: np.random.Generator | int | None = None,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Apply configured perturbations in a fixed order."""
    rng = _as_rng(rng)
    output = signal.copy()
    metadata: dict[str, np.ndarray] = {}

    if config.gain_variation:
        output, gains = apply_channel_gain(output, config.gain_variation, rng)
        metadata["channel_gains"] = gains
    if config.crosstalk_ratio:
        output = apply_neighbor_crosstalk(output, config.crosstalk_ratio)
    if config.baseline_drift_ratio:
        output = add_baseline_drift(output, config.baseline_drift_ratio, rng)
    if config.snr_db is not None:
        output = add_awgn(output, config.snr_db, rng)
    if config.fault_ratio:
        output, fault_mask = apply_faulty_channels(output, config.fault_ratio, rng)
        metadata["fault_mask"] = fault_mask

    return output, metadata


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)


def _array_shape(signal: np.ndarray) -> tuple[int, int]:
    rows, cols, _ = _signal_shape(signal)
    return rows, cols


def _signal_shape(signal: np.ndarray) -> tuple[int, int, int]:
    if signal.ndim != 3:
        raise ValueError(f"signal must have shape (rows, cols, samples), got {signal.shape!r}")
    return signal.shape

