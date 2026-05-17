"""Run validation-selected sklearn baselines on TENG dataset splits."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset_generator import load_dataset_split
from simulation.sklearn_baseline import evaluate_sklearn_baseline, fit_select_sklearn_baseline


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
    model, val_metrics = fit_select_sklearn_baseline(train, val)

    print(
        "selected: "
        f"feature_mode={model.feature_mode} "
        f"classifier={model.classifier_name} "
        f"regressor={model.regressor_name} "
        f"val_material_acc={val_metrics.material_accuracy:.4f} "
        f"val_force_mae={val_metrics.force_mae:.4f} "
        f"val_position_mae_mm={val_metrics.position_mae_mm:.4f} "
        f"val_radius_mae_mm={val_metrics.radius_mae_mm:.4f}"
    )

    for name, path in [("train", args.train), ("val", args.val), ("test_random", args.test)]:
        split = load_dataset_split(path)
        metrics = evaluate_sklearn_baseline(model, split)
        print(
            f"{name}: "
            f"material_acc={metrics.material_accuracy:.4f} "
            f"force_mae={metrics.force_mae:.4f} "
            f"force_rmse={metrics.force_rmse:.4f} "
            f"position_mae_mm={metrics.position_mae_mm:.4f} "
            f"position_rmse_mm={metrics.position_rmse_mm:.4f} "
            f"radius_mae_mm={metrics.radius_mae_mm:.4f} "
            f"radius_rmse_mm={metrics.radius_rmse_mm:.4f}"
        )


if __name__ == "__main__":
    main()
