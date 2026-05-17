"""Evaluate a saved PyTorch TENG multi-task checkpoint on NPZ splits."""

from __future__ import annotations

import argparse
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
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("splits", nargs="+", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    scaler = TargetScaler(
        mean=np.asarray(checkpoint["target_mean"], dtype=np.float32),
        std=np.asarray(checkpoint["target_std"], dtype=np.float32),
    )
    model = TENGMultiTaskNet(material_classes=6)
    model.load_state_dict(checkpoint["model_state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    for split_path in args.splits:
        split = load_dataset_split(split_path)
        loader = DataLoader(TENGDataset(split, scaler), batch_size=args.batch_size)
        metrics = evaluate(model, loader, scaler, device)
        print(
            f"{split_path}: "
            f"material_acc={metrics['material_acc']:.4f} "
            f"force_mae={metrics['force_mae']:.4f} "
            f"position_mae_mm={metrics['position_mae_mm']:.4f} "
            f"radius_mae_mm={metrics['radius_mae_mm']:.4f}"
        )


if __name__ == "__main__":
    main()
