"""Dataset generation utilities for TENG tactile-array learning tasks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from simulation.array_generator import ArraySample, sample_random_array
from simulation.material_params import DEFAULT_ARRAY_CONFIG, ArrayConfig, material_index_map, material_keys
from simulation.perturbations import PerturbationConfig, apply_perturbations


@dataclass(frozen=True)
class DatasetSplit:
    """In-memory generated dataset split."""

    signal: np.ndarray
    pressure_map: np.ndarray
    material_key: np.ndarray
    material_index: np.ndarray
    force: np.ndarray
    position: np.ndarray
    radius: np.ndarray

    def as_dict(self) -> dict[str, np.ndarray]:
        """Return NPZ-ready arrays."""
        return {
            "signal": self.signal,
            "pressure_map": self.pressure_map,
            "material_key": self.material_key,
            "material_index": self.material_index,
            "force": self.force,
            "position": self.position,
            "radius": self.radius,
        }


def generate_dataset_split(
    count: int,
    *,
    rng: np.random.Generator | int | None = None,
    config: ArrayConfig = DEFAULT_ARRAY_CONFIG,
    perturbation: PerturbationConfig | None = None,
    stochastic_waveform: bool = True,
) -> DatasetSplit:
    """Generate one dataset split with balanced material cycling."""
    if count <= 0:
        raise ValueError(f"count must be positive, got {count!r}")
    rng = _as_rng(rng)
    keys = material_keys()
    index_map = material_index_map()

    samples: list[ArraySample] = []
    signals: list[np.ndarray] = []
    for index in range(count):
        material_key = keys[index % len(keys)]
        sample = sample_random_array(
            rng,
            material_key=material_key,
            config=config,
            stochastic_waveform=stochastic_waveform,
        )
        signal = sample.signal
        if perturbation is not None:
            signal, _ = apply_perturbations(signal, perturbation, rng)
        samples.append(sample)
        signals.append(signal)

    material_key_array = np.array([sample.material_key for sample in samples])
    return DatasetSplit(
        signal=np.stack(signals, axis=0),
        pressure_map=np.stack([sample.pressure_map_n for sample in samples], axis=0),
        material_key=material_key_array,
        material_index=np.array([index_map[key] for key in material_key_array], dtype=np.int64),
        force=np.array([sample.force_n for sample in samples], dtype=float),
        position=np.array(
            [[sample.position_x_mm, sample.position_y_mm] for sample in samples],
            dtype=float,
        ),
        radius=np.array([sample.radius_mm for sample in samples], dtype=float),
    )


def save_dataset_split(split: DatasetSplit, output_path: str | Path) -> None:
    """Save a dataset split to a compressed NPZ file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_path, **split.as_dict())


def load_dataset_split(input_path: str | Path) -> DatasetSplit:
    """Load a dataset split saved by ``save_dataset_split``."""
    data = np.load(input_path)
    return DatasetSplit(
        signal=data["signal"],
        pressure_map=data["pressure_map"],
        material_key=data["material_key"],
        material_index=data["material_index"],
        force=data["force"],
        position=data["position"],
        radius=data["radius"],
    )


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)

