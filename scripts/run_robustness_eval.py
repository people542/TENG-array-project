"""Evaluate saved checkpoint on all robustness splits and write a CSV table."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset_generator import load_dataset_split
from simulation.torch_multitask import TENGDataset, TENGMultiTaskNet, TargetScaler
from scripts.train_torch_multitask import evaluate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/torch_multitask_best.pt"))
    parser.add_argument("--split-dir", type=Path, default=Path("data/robustness/v1"))
    parser.add_argument("--out", type=Path, default=Path("results/robustness_v1.csv"))
    parser.add_argument("--batch-size", type=int, default=128)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    scaler = TargetScaler(
        mean=np.asarray(checkpoint["target_mean"], dtype=np.float32),
        std=np.asarray(checkpoint["target_std"], dtype=np.float32),
    )
    variant = checkpoint.get("model_variant", checkpoint.get("args", {}).get("model_variant", "full"))
    model = TENGMultiTaskNet(material_classes=6, variant=variant)
    model.load_state_dict(checkpoint["model_state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    rows = []
    for path in sorted(args.split_dir.glob("*.npz")):
        split = load_dataset_split(path)
        loader = DataLoader(TENGDataset(split, scaler), batch_size=args.batch_size)
        metrics = evaluate(model, loader, scaler, device)
        group, level = parse_split_name(path.stem)
        row = {"split": path.stem, "group": group, "level": level, **metrics}
        rows.append(row)
        print(
            f"{path.stem}: "
            f"material_acc={metrics['material_acc']:.4f} "
            f"force_mae={metrics['force_mae']:.4f} "
            f"position_mae_mm={metrics['position_mae_mm']:.4f} "
            f"radius_mae_mm={metrics['radius_mae_mm']:.4f}"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "split",
                "group",
                "level",
                "material_acc",
                "force_mae",
                "position_mae_mm",
                "radius_mae_mm",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved={args.out}")


def parse_split_name(name: str) -> tuple[str, float]:
    match = re.match(r"([a-z]+)_(\d+)(db|pct)", name)
    if not match:
        return name, 0.0
    group, value, unit = match.groups()
    level = float(value)
    if unit == "pct":
        level /= 100.0
    return group, level


if __name__ == "__main__":
    main()
