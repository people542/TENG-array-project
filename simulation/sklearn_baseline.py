"""Stronger sklearn baselines for TENG multi-task evaluation."""

from __future__ import annotations

from dataclasses import dataclass
import os

import numpy as np

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor, HistGradientBoostingClassifier, RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from simulation.baseline_features import extract_handcrafted_features
from simulation.dataset_generator import DatasetSplit


@dataclass(frozen=True)
class MultiTaskMetrics:
    """Metrics for material, force, position, and radius prediction."""

    material_accuracy: float
    force_mae: float
    force_rmse: float
    position_mae_mm: float
    position_rmse_mm: float
    radius_mae_mm: float
    radius_rmse_mm: float

    def score(self, force_scale: float, position_scale: float, radius_scale: float) -> float:
        """Lower-is-better validation score for model selection."""
        return (
            (1.0 - self.material_accuracy)
            + self.force_mae / force_scale
            + self.position_mae_mm / position_scale
            + self.radius_mae_mm / radius_scale
        )


@dataclass(frozen=True)
class SklearnBaselineModel:
    """Selected sklearn baseline bundle."""

    classifier_name: str
    regressor_name: str
    feature_mode: str
    classifier: object
    regressor: object


def fit_select_sklearn_baseline(
    train: DatasetSplit,
    val: DatasetSplit,
    feature_modes: tuple[str, ...] = ("summary", "full"),
    random_state: int = 20260517,
) -> tuple[SklearnBaselineModel, MultiTaskMetrics]:
    """Fit candidate sklearn baselines and select the best on validation data."""
    candidates_cls = _classifier_candidates(random_state)
    candidates_reg = _regressor_candidates(random_state)

    force_scale = float(max(np.std(train.force), 1e-6))
    position_scale = float(max(np.std(train.position), 1e-6))
    radius_scale = float(max(np.std(train.radius), 1e-6))

    best_model: SklearnBaselineModel | None = None
    best_metrics: MultiTaskMetrics | None = None
    best_score: float | None = None

    y_train_reg = _regression_targets(train)
    for mode in feature_modes:
        x_train = extract_handcrafted_features(train.signal, mode=mode)
        x_val = extract_handcrafted_features(val.signal, mode=mode)
        for cls_name, cls_model in candidates_cls:
            cls_model.fit(x_train, train.material_index)
            for reg_name, reg_model in candidates_reg:
                reg_model.fit(x_train, y_train_reg)
                model = SklearnBaselineModel(
                    classifier_name=cls_name,
                    regressor_name=reg_name,
                    feature_mode=mode,
                    classifier=cls_model,
                    regressor=reg_model,
                )
                metrics = evaluate_sklearn_baseline(model, val)
                score = metrics.score(force_scale, position_scale, radius_scale)
                if best_score is None or score < best_score:
                    best_score = score
                    best_model = model
                    best_metrics = metrics

    if best_model is None or best_metrics is None:
        raise ValueError("No sklearn baseline candidate was evaluated.")
    return best_model, best_metrics


def evaluate_sklearn_baseline(model: SklearnBaselineModel, split: DatasetSplit) -> MultiTaskMetrics:
    """Evaluate selected sklearn baseline on one split."""
    x = extract_handcrafted_features(split.signal, mode=model.feature_mode)
    material_pred = model.classifier.predict(x)
    reg_pred = model.regressor.predict(x)

    force_pred = reg_pred[:, 0]
    position_pred = reg_pred[:, 1:3]
    radius_pred = reg_pred[:, 3]

    force_error = force_pred - split.force
    position_error = np.linalg.norm(position_pred - split.position, axis=1)
    radius_error = radius_pred - split.radius

    return MultiTaskMetrics(
        material_accuracy=float(accuracy_score(split.material_index, material_pred)),
        force_mae=float(mean_absolute_error(split.force, force_pred)),
        force_rmse=float(mean_squared_error(split.force, force_pred) ** 0.5),
        position_mae_mm=float(np.mean(position_error)),
        position_rmse_mm=float(np.sqrt(np.mean(np.square(position_error)))),
        radius_mae_mm=float(mean_absolute_error(split.radius, radius_pred)),
        radius_rmse_mm=float(mean_squared_error(split.radius, radius_pred) ** 0.5),
    )


def _regression_targets(split: DatasetSplit) -> np.ndarray:
    return np.column_stack([split.force, split.position, split.radius])


def _classifier_candidates(random_state: int) -> list[tuple[str, object]]:
    return [
        (
            "extra_trees",
            ExtraTreesClassifier(
                n_estimators=200,
                max_features="sqrt",
                min_samples_leaf=2,
                n_jobs=1,
                random_state=random_state,
            ),
        ),
        (
            "random_forest",
            RandomForestClassifier(
                n_estimators=200,
                max_features="sqrt",
                min_samples_leaf=2,
                n_jobs=1,
                random_state=random_state,
            ),
        ),
        (
            "hist_gradient_boosting",
            make_pipeline(
                StandardScaler(),
                HistGradientBoostingClassifier(
                    max_iter=150,
                    learning_rate=0.08,
                    l2_regularization=0.01,
                    random_state=random_state,
                ),
            ),
        ),
    ]


def _regressor_candidates(random_state: int) -> list[tuple[str, object]]:
    return [
        (
            "extra_trees",
            ExtraTreesRegressor(
                n_estimators=240,
                max_features="sqrt",
                min_samples_leaf=2,
                n_jobs=1,
                random_state=random_state,
            ),
        ),
        (
            "random_forest",
            RandomForestRegressor(
                n_estimators=240,
                max_features="sqrt",
                min_samples_leaf=2,
                n_jobs=1,
                random_state=random_state,
            ),
        ),
        (
            "hist_gradient_boosting",
            make_pipeline(
                StandardScaler(),
                MultiOutputRegressor(
                    HistGradientBoostingClassifier(max_iter=1),
                ),
            ),
        ),
    ][0:2]
