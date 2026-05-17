"""Generate out-of-distribution generalization splits for TENG evaluation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.array_generator import generate_array_sample
from simulation.dataset_generator import DatasetSplit, save_dataset_split
from simulation.material_params import DEFAULT_ARRAY_CONFIG, material_index_map, material_keys
from simulation.perturbations import PerturbationConfig, apply_perturbations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260701)
    parser.add_argument("--out-dir", type=Path, default=Path("data/generalization/v1"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    specs = {
        "force_high_20_30n": {"force": (20.0, 30.0)},
        "radius_small_1_3mm": {"radius": (1.0, 3.0)},
        "radius_large_12_18mm": {"radius": (12.0, 18.0)},
        "position_edges": {"position_mode": "edges"},
        "combined_hard": {
            "force": (20.0, 30.0),
            "radius": (12.0, 18.0),
            "position_mode": "edges",
            "perturbation": PerturbationConfig(snr_db=20.0, fault_ratio=0.2, baseline_drift_ratio=0.1),
        },
    }
    for index, (name, spec) in enumerate(specs.items()):
        split = generate_split(args.count, args.seed + index, spec)
        output_path = args.out_dir / f"{name}.npz"
        save_dataset_split(split, output_path)
        print(f"{name}: count={args.count} path={output_path}")


def generate_split(count: int, seed: int, spec: dict) -> DatasetSplit:
    rng = np.random.default_rng(seed)
    keys = material_keys()
    index_map = material_index_map()
    x_range, y_range = DEFAULT_ARRAY_CONFIG.coordinate_range_mm
    perturbation = spec.get("perturbation")

    signals = []
    pressure_maps = []
    material_key_values = []
    forces = []
    positions = []
    radii = []

    for index in range(count):
        material_key = keys[index % len(keys)]
        force_n = sample_range(rng, spec.get("force", DEFAULT_ARRAY_CONFIG.force_range_n))
        radius_mm = sample_range(rng, spec.get("radius", DEFAULT_ARRAY_CONFIG.radius_range_mm))
        position_x_mm, position_y_mm = sample_position(rng, spec.get("position_mode", "uniform"), x_range, y_range)
        sample = generate_array_sample(
            material_key,
            force_n=force_n,
            position_x_mm=position_x_mm,
            position_y_mm=position_y_mm,
            radius_mm=radius_mm,
            stochastic=True,
            rng=rng,
        )
        signal = sample.signal
        if perturbation is not None:
            signal, _ = apply_perturbations(signal, perturbation, rng)

        signals.append(signal)
        pressure_maps.append(sample.pressure_map_n)
        material_key_values.append(material_key)
        forces.append(force_n)
        positions.append([position_x_mm, position_y_mm])
        radii.append(radius_mm)

    material_key_array = np.array(material_key_values)
    return DatasetSplit(
        signal=np.stack(signals, axis=0),
        pressure_map=np.stack(pressure_maps, axis=0),
        material_key=material_key_array,
        material_index=np.array([index_map[key] for key in material_key_array], dtype=np.int64),
        force=np.array(forces, dtype=float),
        position=np.array(positions, dtype=float),
        radius=np.array(radii, dtype=float),
    )


def sample_range(rng: np.random.Generator, value_range: tuple[float, float]) -> float:
    return float(rng.uniform(value_range[0], value_range[1]))


def sample_position(
    rng: np.random.Generator,
    mode: str,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
) -> tuple[float, float]:
    if mode == "uniform":
        return sample_range(rng, x_range), sample_range(rng, y_range)
    if mode == "edges":
        edge_width = 5.0
        side = int(rng.integers(0, 4))
        if side == 0:
            return sample_range(rng, x_range), sample_range(rng, (y_range[0], y_range[0] + edge_width))
        if side == 1:
            return sample_range(rng, x_range), sample_range(rng, (y_range[1] - edge_width, y_range[1]))
        if side == 2:
            return sample_range(rng, (x_range[0], x_range[0] + edge_width)), sample_range(rng, y_range)
        return sample_range(rng, (x_range[1] - edge_width, x_range[1])), sample_range(rng, y_range)
    raise ValueError(f"Unknown position mode {mode!r}")


if __name__ == "__main__":
    main()
