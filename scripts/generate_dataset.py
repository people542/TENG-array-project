"""Generate train/validation/test NPZ splits for the TENG tactile project."""

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
    parser.add_argument("--train", type=int, default=600)
    parser.add_argument("--val", type=int, default=120)
    parser.add_argument("--test", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260517)
    parser.add_argument("--out-dir", type=Path, default=Path("data/datasets/v1"))
    parser.add_argument("--snr-db", type=float, default=40.0)
    parser.add_argument("--gain-variation", type=float, default=0.10)
    parser.add_argument("--crosstalk-ratio", type=float, default=0.05)
    parser.add_argument("--fault-ratio", type=float, default=0.03)
    parser.add_argument("--baseline-drift-ratio", type=float, default=0.02)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    perturbation = PerturbationConfig(
        snr_db=args.snr_db,
        gain_variation=args.gain_variation,
        crosstalk_ratio=args.crosstalk_ratio,
        fault_ratio=args.fault_ratio,
        baseline_drift_ratio=args.baseline_drift_ratio,
    )

    split_specs = {
        "train": (args.train, args.seed),
        "val": (args.val, args.seed + 1),
        "test_random": (args.test, args.seed + 2),
    }
    for name, (count, seed) in split_specs.items():
        split = generate_dataset_split(count, rng=seed, perturbation=perturbation)
        output_path = args.out_dir / f"{name}.npz"
        save_dataset_split(split, output_path)
        print(f"{name}: count={count} signal_shape={split.signal.shape} path={output_path}")


if __name__ == "__main__":
    main()
