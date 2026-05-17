"""Grid-search force-loss weights using default and high-force validation splits."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=Path("data/datasets/v2_augmented/train.npz"))
    parser.add_argument("--val", type=Path, default=Path("data/datasets/v2_augmented/val.npz"))
    parser.add_argument("--test", type=Path, default=Path("data/datasets/v2_augmented/test_random.npz"))
    parser.add_argument("--high-force", type=Path, default=Path("data/generalization/v1/force_high_20_30n.npz"))
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--force-dim-weights", default="1.0,1.5,2.0")
    parser.add_argument("--high-force-sample-weights", default="1.0,1.5,2.0")
    parser.add_argument("--out", type=Path, default=Path("results/force_weight_grid.csv"))
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("checkpoints/grid_force_weights"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    force_dim_weights = parse_float_list(args.force_dim_weights)
    high_force_sample_weights = parse_float_list(args.high_force_sample_weights)
    rows = []
    for force_dim_weight in force_dim_weights:
        for sample_weight in high_force_sample_weights:
            tag = f"fdw{force_dim_weight:g}_hsw{sample_weight:g}".replace(".", "p")
            checkpoint = args.checkpoint_dir / f"{tag}.pt"
            metrics_json = args.checkpoint_dir / f"{tag}.json"
            train_candidate(args, force_dim_weight, sample_weight, checkpoint, metrics_json)
            default_metrics = evaluate_checkpoint(checkpoint, args.val)
            high_metrics = evaluate_checkpoint(checkpoint, args.high_force)
            score = selection_score(default_metrics, high_metrics)
            row = {
                "tag": tag,
                "force_dim_loss_weight": force_dim_weight,
                "high_force_loss_weight": sample_weight,
                "score": score,
                **prefix_metrics("default_val", default_metrics),
                **prefix_metrics("high_force", high_metrics),
                "checkpoint": str(checkpoint),
            }
            rows.append(row)
            print(
                f"{tag}: score={score:.4f} "
                f"default_force={default_metrics['force_mae']:.4f} "
                f"high_force={high_metrics['force_mae']:.4f}"
            )

    rows.sort(key=lambda item: float(item["score"]))
    write_rows(args.out, rows)
    print(f"best={rows[0]['tag']} score={rows[0]['score']:.4f} checkpoint={rows[0]['checkpoint']}")
    print(f"saved={args.out}")


def train_candidate(
    args: argparse.Namespace,
    force_dim_weight: float,
    sample_weight: float,
    checkpoint: Path,
    metrics_json: Path,
) -> None:
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
        "2.0",
        "--force-dim-loss-weight",
        str(force_dim_weight),
        "--high-force-loss-weight",
        str(sample_weight),
        "--model-out",
        str(checkpoint),
        "--metrics-out",
        str(metrics_json),
    ]
    subprocess.run(command, check=True)


def evaluate_checkpoint(checkpoint: Path, split: Path) -> dict[str, float]:
    command = [
        sys.executable,
        "scripts/evaluate_torch_checkpoint.py",
        "--checkpoint",
        str(checkpoint),
        str(split),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    line = completed.stdout.strip().splitlines()[-1]
    metrics: dict[str, float] = {}
    for token in line.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if key.endswith(":"):
            continue
        metrics[key] = float(value)
    return metrics


def selection_score(default_metrics: dict[str, float], high_metrics: dict[str, float]) -> float:
    """Lower is better. Balance ordinary validation and high-force extrapolation."""
    return (
        (1.0 - default_metrics["material_acc"])
        + default_metrics["force_mae"] / 6.0
        + default_metrics["position_mae_mm"] / 12.0
        + default_metrics["radius_mae_mm"] / 3.0
        + high_metrics["force_mae"] / 10.0
    )


def prefix_metrics(prefix: str, metrics: dict[str, float]) -> dict[str, float]:
    return {f"{prefix}_{key}": value for key, value in metrics.items()}


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
