"""Generate an augmented training dataset for harder TENG generalization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_generalization_splits import generate_split
from simulation.dataset_generator import DatasetSplit, generate_dataset_split, save_dataset_split
from simulation.perturbations import PerturbationConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=int, default=1200)
    parser.add_argument("--val", type=int, default=240)
    parser.add_argument("--test", type=int, default=240)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--out-dir", type=Path, default=Path("data/datasets/v2_augmented"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    train = generate_augmented_train(args.train, args.seed)
    val = generate_dataset_split(
        args.val,
        rng=args.seed + 100,
        perturbation=default_perturbation(),
    )
    test = generate_dataset_split(
        args.test,
        rng=args.seed + 200,
        perturbation=default_perturbation(),
    )

    save_dataset_split(train, args.out_dir / "train.npz")
    save_dataset_split(val, args.out_dir / "val.npz")
    save_dataset_split(test, args.out_dir / "test_random.npz")

    print(f"train: count={args.train} signal_shape={train.signal.shape} path={args.out_dir / 'train.npz'}")
    print(f"val: count={args.val} signal_shape={val.signal.shape} path={args.out_dir / 'val.npz'}")
    print(f"test_random: count={args.test} signal_shape={test.signal.shape} path={args.out_dir / 'test_random.npz'}")


def generate_augmented_train(count: int, seed: int) -> DatasetSplit:
    """Build a mixed training distribution targeting known weak cases."""
    if count < 6:
        raise ValueError("count should be at least 6 for mixed augmentation.")

    base_count = count // 3
    hard_count = count - base_count
    per_case = hard_count // 5
    remainder = hard_count - per_case * 5

    splits = [
        generate_dataset_split(
            base_count,
            rng=seed,
            perturbation=default_perturbation(),
        ),
        generate_split(per_case + remainder, seed + 1, {"force": (18.0, 30.0), "perturbation": default_perturbation()}),
        generate_split(per_case, seed + 2, {"radius": (1.0, 4.0), "perturbation": default_perturbation()}),
        generate_split(per_case, seed + 3, {"radius": (10.0, 18.0), "perturbation": default_perturbation()}),
        generate_split(per_case, seed + 4, {"position_mode": "edges", "perturbation": default_perturbation()}),
        generate_split(
            per_case,
            seed + 5,
            {
                "force": (18.0, 30.0),
                "radius": (10.0, 18.0),
                "position_mode": "edges",
                "perturbation": PerturbationConfig(snr_db=25.0, fault_ratio=0.15, baseline_drift_ratio=0.08),
            },
        ),
    ]
    return concatenate_splits(splits, seed + 99)


def default_perturbation() -> PerturbationConfig:
    """Use the same mild training perturbation as v1 plus enough noise for robustness."""
    return PerturbationConfig(
        snr_db=40.0,
        gain_variation=0.10,
        crosstalk_ratio=0.05,
        fault_ratio=0.03,
        baseline_drift_ratio=0.02,
    )


def concatenate_splits(splits: list[DatasetSplit], seed: int) -> DatasetSplit:
    """Concatenate and shuffle several dataset splits."""
    rng = np.random.default_rng(seed)
    signal = np.concatenate([split.signal for split in splits], axis=0)
    pressure_map = np.concatenate([split.pressure_map for split in splits], axis=0)
    material_key = np.concatenate([split.material_key for split in splits], axis=0)
    material_index = np.concatenate([split.material_index for split in splits], axis=0)
    force = np.concatenate([split.force for split in splits], axis=0)
    position = np.concatenate([split.position for split in splits], axis=0)
    radius = np.concatenate([split.radius for split in splits], axis=0)
    order = rng.permutation(signal.shape[0])
    return DatasetSplit(
        signal=signal[order],
        pressure_map=pressure_map[order],
        material_key=material_key[order],
        material_index=material_index[order],
        force=force[order],
        position=position[order],
        radius=radius[order],
    )


if __name__ == "__main__":
    main()
