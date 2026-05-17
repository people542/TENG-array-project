"""Train a lightweight PyTorch multi-task TENG model."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset_generator import load_dataset_split
from simulation.torch_multitask import TENGDataset, TENGMultiTaskNet, TargetScaler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=Path("data/datasets/v1/train.npz"))
    parser.add_argument("--val", type=Path, default=Path("data/datasets/v1/val.npz"))
    parser.add_argument("--test", type=Path, default=Path("data/datasets/v1/test_random.npz"))
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--material-loss-weight", type=float, default=1.5)
    parser.add_argument("--regression-loss-weight", type=float, default=1.0)
    parser.add_argument("--force-dim-loss-weight", type=float, default=1.0)
    parser.add_argument("--position-dim-loss-weight", type=float, default=1.0)
    parser.add_argument("--radius-dim-loss-weight", type=float, default=1.0)
    parser.add_argument("--high-force-threshold", type=float, default=20.0)
    parser.add_argument("--high-force-loss-weight", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=20260517)
    parser.add_argument("--model-variant", choices=["full", "no_temporal", "no_spatial"], default="full")
    parser.add_argument("--model-out", type=Path, default=Path("checkpoints/torch_multitask_best.pt"))
    parser.add_argument("--metrics-out", type=Path, default=Path("results/torch_multitask_metrics.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    train_split = load_dataset_split(args.train)
    val_split = load_dataset_split(args.val)
    test_split = load_dataset_split(args.test)
    scaler = TargetScaler.from_split(train_split)

    train_loader = DataLoader(
        TENGDataset(train_split, scaler),
        batch_size=args.batch_size,
        shuffle=True,
    )
    val_loader = DataLoader(TENGDataset(val_split, scaler), batch_size=args.batch_size)
    test_loader = DataLoader(TENGDataset(test_split, scaler), batch_size=args.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TENGMultiTaskNet(material_classes=6, variant=args.model_variant).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    ce_loss = nn.CrossEntropyLoss()
    mse_loss = nn.MSELoss()

    best_state = None
    best_val_score = None
    best_epoch = None
    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(
            model,
            train_loader,
            optimizer,
            ce_loss,
            mse_loss,
            device,
            args.material_loss_weight,
            args.regression_loss_weight,
            args.force_dim_loss_weight,
            args.position_dim_loss_weight,
            args.radius_dim_loss_weight,
            args.high_force_threshold,
            args.high_force_loss_weight,
        )
        val_metrics = evaluate(model, val_loader, scaler, device)
        val_score = validation_score(val_metrics)
        if best_val_score is None or val_score < best_val_score:
            best_val_score = val_score
            best_epoch = epoch
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        print(
            f"epoch={epoch:03d} train_loss={train_loss:.4f} "
            f"val_acc={val_metrics['material_acc']:.4f} "
            f"val_force_mae={val_metrics['force_mae']:.4f} "
            f"val_position_mae_mm={val_metrics['position_mae_mm']:.4f} "
            f"val_radius_mae_mm={val_metrics['radius_mae_mm']:.4f}"
        )

    if best_state is not None:
        model.load_state_dict(best_state)

    all_metrics = {}
    for name, loader in [("train", train_loader), ("val", val_loader), ("test_random", test_loader)]:
        metrics = evaluate(model, loader, scaler, device)
        all_metrics[name] = metrics
        print(
            f"{name}: "
            f"material_acc={metrics['material_acc']:.4f} "
            f"force_mae={metrics['force_mae']:.4f} "
            f"position_mae_mm={metrics['position_mae_mm']:.4f} "
            f"radius_mae_mm={metrics['radius_mae_mm']:.4f}"
        )

    save_checkpoint(args.model_out, model, scaler, args, best_epoch, best_val_score)
    save_metrics(args.metrics_out, all_metrics, args, best_epoch, best_val_score)
    print(f"saved_model={args.model_out}")
    print(f"saved_metrics={args.metrics_out}")


def train_one_epoch(
    model: TENGMultiTaskNet,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    ce_loss: nn.Module,
    mse_loss: nn.Module,
    device: torch.device,
    material_loss_weight: float,
    regression_loss_weight: float,
    force_dim_loss_weight: float,
    position_dim_loss_weight: float,
    radius_dim_loss_weight: float,
    high_force_threshold: float,
    high_force_loss_weight: float,
) -> float:
    model.train()
    total_loss = 0.0
    total = 0
    dim_weights = torch.tensor(
        [
            force_dim_loss_weight,
            position_dim_loss_weight,
            position_dim_loss_weight,
            radius_dim_loss_weight,
        ],
        dtype=torch.float32,
        device=device,
    )
    for signal, material, targets, raw_targets in loader:
        signal = signal.to(device)
        material = material.to(device)
        targets = targets.to(device)
        raw_targets = raw_targets.to(device)

        optimizer.zero_grad()
        logits, regression = model(signal)
        per_dim_regression_loss = torch.square(regression - targets) * dim_weights
        per_sample_regression_loss = torch.mean(per_dim_regression_loss, dim=1)
        sample_weights = torch.ones_like(per_sample_regression_loss)
        if high_force_loss_weight != 1.0:
            sample_weights = torch.where(
                raw_targets[:, 0] >= high_force_threshold,
                torch.full_like(sample_weights, high_force_loss_weight),
                sample_weights,
            )
        loss = (
            material_loss_weight * ce_loss(logits, material)
            + regression_loss_weight * torch.mean(sample_weights * per_sample_regression_loss)
        )
        loss.backward()
        optimizer.step()

        batch_size = signal.shape[0]
        total_loss += float(loss.item()) * batch_size
        total += batch_size
    return total_loss / max(total, 1)


@torch.no_grad()
def evaluate(
    model: TENGMultiTaskNet,
    loader: DataLoader,
    scaler: TargetScaler,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    material_true = []
    material_pred = []
    target_true = []
    target_pred = []
    for signal, material, targets, _raw_targets in loader:
        signal = signal.to(device)
        logits, regression = model(signal)
        material_true.append(material.numpy())
        material_pred.append(logits.argmax(dim=1).cpu().numpy())
        target_true.append(targets.numpy())
        target_pred.append(regression.cpu().numpy())

    y_true_norm = np.concatenate(target_true, axis=0)
    y_pred_norm = np.concatenate(target_pred, axis=0)
    y_true = scaler.inverse_transform(y_true_norm)
    y_pred = scaler.inverse_transform(y_pred_norm)
    mat_true = np.concatenate(material_true, axis=0)
    mat_pred = np.concatenate(material_pred, axis=0)

    position_error = np.linalg.norm(y_pred[:, 1:3] - y_true[:, 1:3], axis=1)
    return {
        "material_acc": float(np.mean(mat_pred == mat_true)),
        "force_mae": float(np.mean(np.abs(y_pred[:, 0] - y_true[:, 0]))),
        "position_mae_mm": float(np.mean(position_error)),
        "radius_mae_mm": float(np.mean(np.abs(y_pred[:, 3] - y_true[:, 3]))),
    }


def validation_score(metrics: dict[str, float]) -> float:
    return (
        (1.0 - metrics["material_acc"])
        + metrics["force_mae"] / 6.0
        + metrics["position_mae_mm"] / 12.0
        + metrics["radius_mae_mm"] / 3.0
    )


def save_checkpoint(
    path: Path,
    model: TENGMultiTaskNet,
    scaler: TargetScaler,
    args: argparse.Namespace,
    best_epoch: int | None,
    best_val_score: float | None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "target_mean": scaler.mean,
            "target_std": scaler.std,
            "best_epoch": best_epoch,
            "best_val_score": best_val_score,
            "args": vars(args),
            "model_variant": args.model_variant,
        },
        path,
    )


def save_metrics(
    path: Path,
    metrics: dict[str, dict[str, float]],
    args: argparse.Namespace,
    best_epoch: int | None,
    best_val_score: float | None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "best_epoch": best_epoch,
        "best_val_score": best_val_score,
        "args": {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
        "metrics": metrics,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
