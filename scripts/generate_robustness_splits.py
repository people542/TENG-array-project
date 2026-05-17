"""Generate robustness-test splits for the TENG tactile model."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset_generator import generate_dataset_split, save_dataset_split
from simulation.perturbations import PerturbationConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260601)
    parser.add_argument("--out-dir", type=Path, default=Path("data/robustness/v1"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    specs = build_specs()
    group_seed_offsets = {
        "snr": 0,
        "fault": 1000,
        "crosstalk": 2000,
        "drift": 3000,
    }
    for name, group, perturbation in specs:
        split = generate_dataset_split(
            args.count,
            rng=args.seed + group_seed_offsets[group],
            perturbation=perturbation,
        )
        output_path = args.out_dir / f"{name}.npz"
        save_dataset_split(split, output_path)
        print(f"{name}: count={args.count} path={output_path}")


def build_specs() -> list[tuple[str, str, PerturbationConfig]]:
    specs: list[tuple[str, str, PerturbationConfig]] = []
    for snr_db in (50.0, 40.0, 30.0, 20.0, 10.0):
        specs.append((f"snr_{int(snr_db)}db", "snr", PerturbationConfig(snr_db=snr_db)))
    for fault_ratio in (0.0, 0.1, 0.2, 0.3, 0.4):
        specs.append((f"fault_{int(fault_ratio * 100)}pct", "fault", PerturbationConfig(fault_ratio=fault_ratio)))
    for crosstalk_ratio in (0.0, 0.05, 0.1, 0.2):
        specs.append((f"crosstalk_{int(crosstalk_ratio * 100)}pct", "crosstalk", PerturbationConfig(crosstalk_ratio=crosstalk_ratio)))
    for drift_ratio in (0.0, 0.05, 0.1, 0.2, 0.3):
        specs.append((f"drift_{int(drift_ratio * 100)}pct", "drift", PerturbationConfig(baseline_drift_ratio=drift_ratio)))
    return specs


if __name__ == "__main__":
    main()
