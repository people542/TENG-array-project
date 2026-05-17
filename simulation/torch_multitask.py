"""Lightweight PyTorch multi-task model for TENG tactile arrays."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset

from simulation.dataset_generator import DatasetSplit


@dataclass(frozen=True)
class TargetScaler:
    """Mean/std normalization for force, position x/y, and radius."""

    mean: np.ndarray
    std: np.ndarray

    @classmethod
    def from_split(cls, split: DatasetSplit) -> "TargetScaler":
        targets = regression_targets(split)
        mean = targets.mean(axis=0)
        std = targets.std(axis=0)
        std = np.where(std == 0.0, 1.0, std)
        return cls(mean=mean.astype(np.float32), std=std.astype(np.float32))

    def transform(self, targets: np.ndarray) -> np.ndarray:
        return ((targets - self.mean) / self.std).astype(np.float32)

    def inverse_transform(self, targets: np.ndarray) -> np.ndarray:
        return targets * self.std + self.mean


class TENGDataset(Dataset):
    """Torch dataset wrapper for generated NPZ splits."""

    def __init__(self, split: DatasetSplit, scaler: TargetScaler) -> None:
        self.signal = split.signal.astype(np.float32)
        self.material = split.material_index.astype(np.int64)
        self.raw_targets = regression_targets(split)
        self.targets = scaler.transform(regression_targets(split))

    def __len__(self) -> int:
        return int(self.signal.shape[0])

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        return (
            torch.from_numpy(self.signal[index]),
            torch.tensor(self.material[index], dtype=torch.long),
            torch.from_numpy(self.targets[index]),
            torch.from_numpy(self.raw_targets[index]),
        )


class TENGMultiTaskNet(nn.Module):
    """Compact spatial-temporal network for material and regression tasks."""

    def __init__(self, material_classes: int = 6) -> None:
        super().__init__()
        self.spatial = nn.Sequential(
            nn.Conv2d(5, 24, kernel_size=3, padding=1),
            nn.BatchNorm2d(24),
            nn.ReLU(),
            nn.Conv2d(24, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(32 * 8 * 8, 96),
            nn.ReLU(),
        )
        self.temporal = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=7, padding=3),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
        )
        self.shared = nn.Sequential(
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.15),
        )
        self.material_head = nn.Linear(128, material_classes)
        self.regression_head = nn.Linear(128, 4)

    def forward(self, signal: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        spatial_input = spatial_summary(signal)
        temporal_input = representative_waveform(signal).unsqueeze(1)
        features = torch.cat([self.spatial(spatial_input), self.temporal(temporal_input)], dim=1)
        shared = self.shared(features)
        return self.material_head(shared), self.regression_head(shared)


def regression_targets(split: DatasetSplit) -> np.ndarray:
    """Return regression targets as ``force, x, y, radius``."""
    return np.column_stack([split.force, split.position, split.radius]).astype(np.float32)


def spatial_summary(signal: torch.Tensor) -> torch.Tensor:
    """Return peak/mean/energy and coordinate maps with shape ``(B, 5, 8, 8)``."""
    peak = signal.max(dim=-1).values
    mean = signal.mean(dim=-1)
    energy = signal.square().mean(dim=-1)
    batch, rows, cols = peak.shape
    y_coord = torch.linspace(0.0, 1.0, rows, device=signal.device).view(1, rows, 1)
    x_coord = torch.linspace(0.0, 1.0, cols, device=signal.device).view(1, 1, cols)
    y_map = y_coord.expand(batch, rows, cols)
    x_map = x_coord.expand(batch, rows, cols)
    return torch.stack([peak, mean, energy, x_map, y_map], dim=1)


def representative_waveform(signal: torch.Tensor) -> torch.Tensor:
    """Return peak-normalized waveform of the most active channel."""
    batch, rows, cols, samples = signal.shape
    flat = signal.reshape(batch, rows * cols, samples)
    peaks = flat.max(dim=-1).values
    index = peaks.argmax(dim=1)
    waveform = flat[torch.arange(batch, device=signal.device), index]
    peak = waveform.max(dim=1, keepdim=True).values.clamp_min(1e-6)
    return waveform / peak
