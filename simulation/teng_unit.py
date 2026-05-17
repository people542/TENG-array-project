"""Single-cell TENG voltage waveform simulation.

This module implements the first simplified, literature-guided waveform model:

    V(t) = A_m * S_m(F) * W(t) * exp(-t / tau_m)

The model is intended for algorithm pre-research. It preserves material,
force, frequency, and decay trends without claiming experimental calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from simulation.material_params import (
    DEFAULT_ARRAY_CONFIG,
    ArrayConfig,
    MaterialConfig,
    get_material_config,
    midpoint,
)


@dataclass(frozen=True)
class UnitWaveformParams:
    """Concrete parameters used to generate one single-cell waveform."""

    material_key: str
    material_label: str
    force_n: float
    frequency_hz: float
    sigma_uc_m2: float
    tau_s: float
    alpha_n: float
    epsilon_r: float
    amplitude_v: float
    phase_cycle: float = 0.0

    def as_dict(self) -> dict[str, float | str]:
        """Return metadata suitable for dataset records."""
        return {
            "material_key": self.material_key,
            "material_label": self.material_label,
            "force_n": self.force_n,
            "frequency_hz": self.frequency_hz,
            "sigma_uc_m2": self.sigma_uc_m2,
            "tau_s": self.tau_s,
            "alpha_n": self.alpha_n,
            "epsilon_r": self.epsilon_r,
            "amplitude_v": self.amplitude_v,
            "phase_cycle": self.phase_cycle,
        }


def pressure_saturation(force_n: float, alpha_n: float) -> float:
    """Return nonlinear pressure saturation S(F) = 1 - exp(-F / alpha)."""
    if force_n < 0:
        raise ValueError(f"force_n must be non-negative, got {force_n!r}")
    if alpha_n <= 0:
        raise ValueError(f"alpha_n must be positive, got {alpha_n!r}")
    return float(1.0 - np.exp(-force_n / alpha_n))


def time_axis(config: ArrayConfig = DEFAULT_ARRAY_CONFIG) -> np.ndarray:
    """Return a fixed-length time axis for one waveform sample."""
    return np.arange(config.sample_count, dtype=float) / config.sample_rate_hz


def contact_separation_waveform(
    t_s: np.ndarray,
    frequency_hz: float,
    phase_cycle: float = 0.0,
) -> np.ndarray:
    """Return a non-negative half-cosine contact-separation carrier."""
    if frequency_hz <= 0:
        raise ValueError(f"frequency_hz must be positive, got {frequency_hz!r}")
    phase_rad = 2.0 * np.pi * phase_cycle
    return 0.5 * (1.0 - np.cos(2.0 * np.pi * frequency_hz * t_s + phase_rad))


def deterministic_unit_params(
    material_key: str,
    force_n: float,
    frequency_hz: float | None = None,
    voltage_scale: float = 10.0,
) -> UnitWaveformParams:
    """Build deterministic midpoint parameters for reproducible demos/tests."""
    material = get_material_config(material_key)
    if frequency_hz is None:
        frequency_hz = midpoint(DEFAULT_ARRAY_CONFIG.contact_frequency_range_hz)
    return _build_params(
        material=material,
        force_n=force_n,
        frequency_hz=frequency_hz,
        sigma_uc_m2=midpoint(material.sigma_range_uc_m2),
        tau_s=midpoint(material.tau_range_s),
        alpha_n=midpoint(material.alpha_range_n),
        epsilon_r=midpoint(material.epsilon_r_range),
        voltage_scale=voltage_scale,
        phase_cycle=0.0,
    )


def sample_unit_params(
    material_key: str,
    force_n: float,
    rng: np.random.Generator | None = None,
    config: ArrayConfig = DEFAULT_ARRAY_CONFIG,
    voltage_scale: float = 10.0,
    phase_jitter_cycle: float = 0.05,
    amplitude_jitter: float = 0.10,
) -> UnitWaveformParams:
    """Sample concrete material and contact parameters from configured ranges."""
    if rng is None:
        rng = np.random.default_rng()

    material = get_material_config(material_key)
    sigma = _uniform_range(rng, material.sigma_range_uc_m2)
    tau = _uniform_range(rng, material.tau_range_s)
    alpha = _uniform_range(rng, material.alpha_range_n)
    epsilon = _uniform_range(rng, material.epsilon_r_range)
    frequency = _uniform_range(rng, config.contact_frequency_range_hz)
    phase = float(rng.uniform(-phase_jitter_cycle, phase_jitter_cycle))
    jitter = float(rng.uniform(1.0 - amplitude_jitter, 1.0 + amplitude_jitter))

    params = _build_params(
        material=material,
        force_n=force_n,
        frequency_hz=frequency,
        sigma_uc_m2=sigma,
        tau_s=tau,
        alpha_n=alpha,
        epsilon_r=epsilon,
        voltage_scale=voltage_scale,
        phase_cycle=phase,
    )
    return UnitWaveformParams(
        **{
            **params.as_dict(),
            "amplitude_v": params.amplitude_v * jitter,
        }
    )


def generate_unit_waveform(
    material_key: str,
    force_n: float,
    *,
    frequency_hz: float | None = None,
    config: ArrayConfig = DEFAULT_ARRAY_CONFIG,
    voltage_scale: float = 10.0,
    rng: np.random.Generator | int | None = None,
    stochastic: bool = False,
    return_params: bool = False,
) -> np.ndarray | tuple[np.ndarray, UnitWaveformParams]:
    """Generate one TENG unit voltage waveform.

    Args:
        material_key: Key from ``simulation.material_params.MATERIAL_CONFIGS``.
        force_n: Local force applied to this unit, in Newtons.
        frequency_hz: Contact frequency. If omitted, use the default midpoint.
        config: Sampling and duration configuration.
        voltage_scale: Empirical scale factor converting normalized material
            response into voltage-like values.
        rng: Optional random generator or seed. Used only in stochastic mode.
        stochastic: If true, sample parameters inside material ranges and add
            small phase/amplitude jitter.
        return_params: If true, also return the concrete parameters used.

    Returns:
        A ``(sample_count,)`` voltage waveform, optionally with metadata.
    """
    if isinstance(rng, int):
        rng = np.random.default_rng(rng)

    if stochastic:
        params = sample_unit_params(
            material_key=material_key,
            force_n=force_n,
            rng=rng,
            config=config,
            voltage_scale=voltage_scale,
        )
    else:
        params = deterministic_unit_params(
            material_key=material_key,
            force_n=force_n,
            frequency_hz=frequency_hz,
            voltage_scale=voltage_scale,
        )

    t_s = time_axis(config)
    carrier = contact_separation_waveform(t_s, params.frequency_hz, params.phase_cycle)
    decay = np.exp(-t_s / params.tau_s)
    waveform = params.amplitude_v * carrier * decay

    if return_params:
        return waveform.astype(float), params
    return waveform.astype(float)


def _build_params(
    material: MaterialConfig,
    force_n: float,
    frequency_hz: float,
    sigma_uc_m2: float,
    tau_s: float,
    alpha_n: float,
    epsilon_r: float,
    voltage_scale: float,
    phase_cycle: float,
) -> UnitWaveformParams:
    if force_n < 0:
        raise ValueError(f"force_n must be non-negative, got {force_n!r}")
    if tau_s <= 0:
        raise ValueError(f"tau_s must be positive, got {tau_s!r}")
    if epsilon_r <= 0:
        raise ValueError(f"epsilon_r must be positive, got {epsilon_r!r}")

    saturation = pressure_saturation(force_n, alpha_n)
    material_factor = (sigma_uc_m2 / 100.0) / epsilon_r
    amplitude_v = voltage_scale * material_factor * saturation

    return UnitWaveformParams(
        material_key=material.key,
        material_label=material.label,
        force_n=float(force_n),
        frequency_hz=float(frequency_hz),
        sigma_uc_m2=float(sigma_uc_m2),
        tau_s=float(tau_s),
        alpha_n=float(alpha_n),
        epsilon_r=float(epsilon_r),
        amplitude_v=float(amplitude_v),
        phase_cycle=float(phase_cycle),
    )


def _uniform_range(rng: np.random.Generator, value_range: tuple[float, float]) -> float:
    low, high = value_range
    return float(rng.uniform(low, high))


def params_from_mapping(values: dict[str, Any]) -> UnitWaveformParams:
    """Recreate ``UnitWaveformParams`` from saved metadata."""
    return UnitWaveformParams(
        material_key=str(values["material_key"]),
        material_label=str(values["material_label"]),
        force_n=float(values["force_n"]),
        frequency_hz=float(values["frequency_hz"]),
        sigma_uc_m2=float(values["sigma_uc_m2"]),
        tau_s=float(values["tau_s"]),
        alpha_n=float(values["alpha_n"]),
        epsilon_r=float(values["epsilon_r"]),
        amplitude_v=float(values["amplitude_v"]),
        phase_cycle=float(values.get("phase_cycle", 0.0)),
    )

