"""Run simple NumPy baselines on generated TENG dataset splits."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.baseline_features import evaluate_baseline, select_baseline
from simulation.dataset_generator import load_dataset_split


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=Path("data/datasets/v1/train.npz"))
    parser.add_argument("--val", type=Path, default=Path("data/datasets/v1/val.npz"))
    parser.add_argument("--test", type=Path, default=Path("data/datasets/v1/test_random.npz"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train = load_dataset_split(args.train)
    val = load_dataset_split(args.val)
    model, val_result = select_baseline(train, val)
    print(
        "selected: "
        f"feature_mode={model.feature_mode} "
        f"ridge_lambda={model.ridge_lambda:g} "
        f"val_material_acc={val_result.material_accuracy:.4f} "
        f"val_force_mae={val_result.force_mae:.4f}"
    )

    for name, path in [("train", args.train), ("val", args.val), ("test_random", args.test)]:
        split = load_dataset_split(path)
        result = evaluate_baseline(model, split)
        print(
            f"{name}: "
            f"material_acc={result.material_accuracy:.4f} "
            f"force_mae={result.force_mae:.4f} "
            f"force_rmse={result.force_rmse:.4f}"
        )


if __name__ == "__main__":
    main()
