"""Run structural ablation experiments for the TENG multi-task model."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


VARIANTS = ["full", "no_temporal", "no_spatial"]
METRICS = ["material_acc", "force_mae", "position_mae_mm", "radius_mae_mm"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=Path("data/datasets/v2_augmented/train.npz"))
    parser.add_argument("--val", type=Path, default=Path("data/datasets/v2_augmented/val.npz"))
    parser.add_argument("--test", type=Path, default=Path("data/datasets/v2_augmented/test_random.npz"))
    parser.add_argument("--epochs", type=int, default=18)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--material-loss-weight", type=float, default=2.0)
    parser.add_argument("--out", type=Path, default=Path("results/ablation_structural_v1.csv"))
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("checkpoints/ablation_structural"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for variant in VARIANTS:
        checkpoint = args.checkpoint_dir / f"{variant}.pt"
        metrics_path = args.checkpoint_dir / f"{variant}_metrics.json"
        train_variant(args, variant, checkpoint, metrics_path)
        metrics = load_metrics(metrics_path)
        for split_name, split_metrics in metrics["metrics"].items():
            row = {"variant": variant, "split": split_name}
            row.update({metric: split_metrics[metric] for metric in METRICS})
            rows.append(row)
        test_metrics = metrics["metrics"]["test_random"]
        print(
            f"{variant}: "
            f"acc={test_metrics['material_acc']:.4f} "
            f"force={test_metrics['force_mae']:.4f} "
            f"pos={test_metrics['position_mae_mm']:.4f} "
            f"radius={test_metrics['radius_mae_mm']:.4f}"
        )

    write_rows(args.out, rows)
    print(f"saved={args.out}")


def train_variant(args: argparse.Namespace, variant: str, checkpoint: Path, metrics_path: Path) -> None:
    command = [
        sys.executable,
        "scripts/train_torch_multitask.py",
        "--train",
        str(args.train),
        "--val",
        str(args.val),
        "--test",
        str(args.test),
        "--epochs",
        str(args.epochs),
        "--batch-size",
        str(args.batch_size),
        "--material-loss-weight",
        str(args.material_loss_weight),
        "--model-variant",
        variant,
        "--model-out",
        str(checkpoint),
        "--metrics-out",
        str(metrics_path),
    ]
    subprocess.run(command, check=True)


def load_metrics(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_rows(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["variant", "split", *METRICS])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
