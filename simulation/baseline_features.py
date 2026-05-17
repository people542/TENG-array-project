"""Simple feature extraction and NumPy baselines for TENG datasets."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from simulation.dataset_generator import DatasetSplit


@dataclass(frozen=True)
class BaselineResult:
    """Metrics for simple material and force baselines."""

    material_accuracy: float
    force_mae: float
    force_rmse: float

    def as_dict(self) -> dict[str, float]:
        """Return result metrics as plain scalars."""
        return {
            "material_accuracy": self.material_accuracy,
            "force_mae": self.force_mae,
            "force_rmse": self.force_rmse,
        }


@dataclass(frozen=True)
class BaselineModel:
    """Fitted nearest-centroid classifier and ridge regressor."""

    centroids: np.ndarray
    material_classes: np.ndarray
    feature_mean: np.ndarray
    feature_std: np.ndarray
    force_weights: np.ndarray
    feature_mode: str = "full"
    ridge_lambda: float = 1e-3


def extract_handcrafted_features(signal: np.ndarray, mode: str = "full") -> np.ndarray:
    """Extract compact per-sample features from ``(N, 8, 8, 200)`` signals."""
    if signal.ndim != 4:
        raise ValueError(f"signal must have shape (N, 8, 8, 200), got {signal.shape!r}")

    peak_map = signal.max(axis=-1)
    mean_map = signal.mean(axis=-1)
    energy_map = np.mean(np.square(signal), axis=-1)
    temporal_stats = _temporal_shape_features(signal, peak_map)
    global_stats = np.stack(
        [
            peak_map.max(axis=(1, 2)),
            peak_map.mean(axis=(1, 2)),
            peak_map.std(axis=(1, 2)),
            mean_map.mean(axis=(1, 2)),
            energy_map.mean(axis=(1, 2)),
            energy_map.max(axis=(1, 2)),
        ],
        axis=1,
    )
    summary = np.concatenate([global_stats, temporal_stats], axis=1)
    if mode == "summary":
        return summary
    if mode != "full":
        raise ValueError(f"Unknown feature mode {mode!r}. Valid modes: full, summary")
    return np.concatenate(
        [
            peak_map.reshape(signal.shape[0], -1),
            mean_map.reshape(signal.shape[0], -1),
            energy_map.reshape(signal.shape[0], -1),
            summary,
        ],
        axis=1,
    )


def fit_baseline(
    train: DatasetSplit,
    ridge_lambda: float = 1e-3,
    feature_mode: str = "full",
) -> BaselineModel:
    """Fit baseline models on a training split."""
    features = extract_handcrafted_features(train.signal, mode=feature_mode)
    feature_mean = features.mean(axis=0)
    feature_std = features.std(axis=0)
    feature_std = np.where(feature_std == 0.0, 1.0, feature_std)
    x = (features - feature_mean) / feature_std

    classes = np.unique(train.material_index)
    centroids = np.stack([x[train.material_index == cls].mean(axis=0) for cls in classes])

    x_with_bias = np.concatenate([x, np.ones((x.shape[0], 1))], axis=1)
    penalty = ridge_lambda * np.eye(x_with_bias.shape[1])
    penalty[-1, -1] = 0.0
    force_weights = np.linalg.solve(
        x_with_bias.T @ x_with_bias + penalty,
        x_with_bias.T @ train.force,
    )

    return BaselineModel(
        centroids=centroids,
        material_classes=classes,
        feature_mean=feature_mean,
        feature_std=feature_std,
        force_weights=force_weights,
        feature_mode=feature_mode,
        ridge_lambda=ridge_lambda,
    )


def predict_material(model: BaselineModel, signal: np.ndarray) -> np.ndarray:
    """Predict material class indices with nearest centroids."""
    x = _transform(model, signal)
    distances = np.linalg.norm(x[:, np.newaxis, :] - model.centroids[np.newaxis, :, :], axis=2)
    return model.material_classes[np.argmin(distances, axis=1)]


def predict_force(model: BaselineModel, signal: np.ndarray) -> np.ndarray:
    """Predict total force with a linear ridge regressor."""
    x = _transform(model, signal)
    x_with_bias = np.concatenate([x, np.ones((x.shape[0], 1))], axis=1)
    return x_with_bias @ model.force_weights


def evaluate_baseline(model: BaselineModel, split: DatasetSplit) -> BaselineResult:
    """Evaluate material classification and force regression."""
    material_pred = predict_material(model, split.signal)
    force_pred = predict_force(model, split.signal)
    force_error = force_pred - split.force
    return BaselineResult(
        material_accuracy=float(np.mean(material_pred == split.material_index)),
        force_mae=float(np.mean(np.abs(force_error))),
        force_rmse=float(np.sqrt(np.mean(np.square(force_error)))),
    )


def select_baseline(
    train: DatasetSplit,
    val: DatasetSplit,
    ridge_lambdas: tuple[float, ...] = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0),
    feature_modes: tuple[str, ...] = ("summary", "full"),
) -> tuple[BaselineModel, BaselineResult]:
    """Select the best baseline configuration on a validation split."""
    best_model: BaselineModel | None = None
    best_result: BaselineResult | None = None
    best_score: float | None = None

    force_scale = float(max(np.std(train.force), 1e-6))
    for mode in feature_modes:
        for ridge_lambda in ridge_lambdas:
            model = fit_baseline(train, ridge_lambda=ridge_lambda, feature_mode=mode)
            result = evaluate_baseline(model, val)
            score = (1.0 - result.material_accuracy) + result.force_mae / force_scale
            if best_score is None or score < best_score:
                best_score = score
                best_model = model
                best_result = result

    if best_model is None or best_result is None:
        raise ValueError("No baseline configuration was evaluated.")
    return best_model, best_result


def _transform(model: BaselineModel, signal: np.ndarray) -> np.ndarray:
    features = extract_handcrafted_features(signal, mode=model.feature_mode)
    return (features - model.feature_mean) / model.feature_std


def _temporal_shape_features(signal: np.ndarray, peak_map: np.ndarray) -> np.ndarray:
    sample_count = signal.shape[-1]
    flat_signal = signal.reshape(signal.shape[0], -1, sample_count)
    flat_peaks = peak_map.reshape(signal.shape[0], -1)
    active_index = np.argmax(flat_peaks, axis=1)
    representative = flat_signal[np.arange(signal.shape[0]), active_index]

    peak = np.max(representative, axis=1, keepdims=True)
    peak = np.where(peak <= 0.0, 1.0, peak)
    normalized = representative / peak

    sample_indices = np.linspace(0, sample_count - 1, 20).round().astype(int)
    coarse_shape = normalized[:, sample_indices]
    early_area = normalized[:, : sample_count // 3].mean(axis=1)
    mid_area = normalized[:, sample_count // 3 : 2 * sample_count // 3].mean(axis=1)
    late_area = normalized[:, 2 * sample_count // 3 :].mean(axis=1)
    time_to_peak = np.argmax(normalized, axis=1) / max(sample_count - 1, 1)
    ratios = np.stack([early_area, mid_area, late_area, time_to_peak], axis=1)
    return np.concatenate([coarse_shape, ratios], axis=1)
