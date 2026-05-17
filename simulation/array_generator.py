"""Array-level TENG tactile signal generation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from simulation.material_params import DEFAULT_ARRAY_CONFIG, ArrayConfig
from simulation.teng_unit import generate_unit_waveform


@dataclass(frozen=True)
class ArraySample:
    """One simulated tactile-array sample and its labels."""

    signal: np.ndarray
    pressure_map_n: np.ndarray
    material_key: str
    force_n: float
    position_x_mm: float
    position_y_mm: float
    radius_mm: float

    def peak_map(self) -> np.ndarray:
        """Return per-channel peak voltage with shape ``(rows, cols)``."""
        return self.signal.max(axis=-1)

    def as_label_dict(self) -> dict[str, float | str]:
        """Return labels used by downstream dataset generation."""
        return {
            "material_key": self.material_key,
            "force_n": self.force_n,
            "position_x_mm": self.position_x_mm,
            "position_y_mm": self.position_y_mm,
            "radius_mm": self.radius_mm,
        }


def cell_coordinates(config: ArrayConfig = DEFAULT_ARRAY_CONFIG) -> np.ndarray:
    """Return cell-center coordinates with shape ``(rows, cols, 2)`` in mm."""
    rows, cols = config.array_shape
    y = np.arange(rows, dtype=float) * config.spacing_mm
    x = np.arange(cols, dtype=float) * config.spacing_mm
    xx, yy = np.meshgrid(x, y)
    return np.stack([xx, yy], axis=-1)


def gaussian_pressure_map(
    force_n: float,
    position_x_mm: float,
    position_y_mm: float,
    radius_mm: float,
    config: ArrayConfig = DEFAULT_ARRAY_CONFIG,
) -> np.ndarray:
    """Distribute total contact force over the array using a 2D Gaussian."""
    if force_n < 0:
        raise ValueError(f"force_n must be non-negative, got {force_n!r}")
    if radius_mm <= 0:
        raise ValueError(f"radius_mm must be positive, got {radius_mm!r}")

    coords = cell_coordinates(config)
    dx = coords[..., 0] - position_x_mm
    dy = coords[..., 1] - position_y_mm
    distance_sq = dx * dx + dy * dy
    weights = np.exp(-distance_sq / (2.0 * radius_mm * radius_mm))
    weight_sum = float(weights.sum())
    if weight_sum <= 0:
        raise ValueError("Gaussian pressure weights summed to zero.")
    return weights / weight_sum * force_n


def generate_array_sample(
    material_key: str,
    force_n: float,
    position_x_mm: float,
    position_y_mm: float,
    radius_mm: float,
    *,
    config: ArrayConfig = DEFAULT_ARRAY_CONFIG,
    stochastic: bool = False,
    rng: np.random.Generator | int | None = None,
) -> ArraySample:
    """Generate one ``(rows, cols, sample_count)`` TENG array signal."""
    if isinstance(rng, int):
        rng = np.random.default_rng(rng)

    pressure_map = gaussian_pressure_map(
        force_n=force_n,
        position_x_mm=position_x_mm,
        position_y_mm=position_y_mm,
        radius_mm=radius_mm,
        config=config,
    )

    rows, cols = config.array_shape
    signal = np.empty((rows, cols, config.sample_count), dtype=float)
    for row in range(rows):
        for col in range(cols):
            local_force = float(pressure_map[row, col])
            signal[row, col] = generate_unit_waveform(
                material_key,
                local_force,
                config=config,
                stochastic=stochastic,
                rng=rng,
            )

    return ArraySample(
        signal=signal,
        pressure_map_n=pressure_map,
        material_key=material_key,
        force_n=float(force_n),
        position_x_mm=float(position_x_mm),
        position_y_mm=float(position_y_mm),
        radius_mm=float(radius_mm),
    )


def sample_random_array(
    rng: np.random.Generator | int | None = None,
    *,
    material_key: str,
    config: ArrayConfig = DEFAULT_ARRAY_CONFIG,
    stochastic_waveform: bool = True,
) -> ArraySample:
    """Sample a random valid contact and generate its array signal."""
    if rng is None:
        rng = np.random.default_rng()
    elif isinstance(rng, int):
        rng = np.random.default_rng(rng)

    x_range, y_range = config.coordinate_range_mm
    force_n = float(rng.uniform(*config.force_range_n))
    radius_mm = float(rng.uniform(*config.radius_range_mm))
    position_x_mm = float(rng.uniform(*x_range))
    position_y_mm = float(rng.uniform(*y_range))

    return generate_array_sample(
        material_key=material_key,
        force_n=force_n,
        position_x_mm=position_x_mm,
        position_y_mm=position_y_mm,
        radius_mm=radius_mm,
        config=config,
        stochastic=stochastic_waveform,
        rng=rng,
    )

