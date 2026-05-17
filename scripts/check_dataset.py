"""Inspect generated TENG dataset splits."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset_generator import load_dataset_split


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="NPZ split files to inspect.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for path in args.paths:
        inspect_split(path)


def inspect_split(path: Path) -> None:
    split = load_dataset_split(path)
    material_keys, material_counts = np.unique(split.material_key, return_counts=True)
    force_error = np.abs(split.pressure_map.sum(axis=(1, 2)) - split.force)

    print(f"\n{path}")
    print(f"  signal: {split.signal.shape} {split.signal.dtype}")
    print(f"  pressure_map: {split.pressure_map.shape}")
    print(f"  material_index: {split.material_index.shape}")
    print(f"  force range: {split.force.min():.3f} to {split.force.max():.3f} N")
    print(
        "  position range: "
        f"x {split.position[:, 0].min():.3f} to {split.position[:, 0].max():.3f} mm, "
        f"y {split.position[:, 1].min():.3f} to {split.position[:, 1].max():.3f} mm"
    )
    print(f"  radius range: {split.radius.min():.3f} to {split.radius.max():.3f} mm")
    print(f"  signal range: {split.signal.min():.6f} to {split.signal.max():.6f}")
    print(f"  max force conservation error: {force_error.max():.6e}")
    print("  material counts:")
    for key, count in zip(material_keys, material_counts):
        print(f"    {key}: {count}")

    if split.signal.ndim != 4 or split.signal.shape[1:] != (8, 8, 200):
        raise ValueError(f"{path} has invalid signal shape {split.signal.shape!r}")
    if force_error.max() > 1e-8:
        raise ValueError(f"{path} pressure map does not conserve force.")
    if not np.all(np.isfinite(split.signal)):
        raise ValueError(f"{path} contains non-finite signal values.")


if __name__ == "__main__":
    main()
