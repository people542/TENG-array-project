import unittest

from simulation.dataset_generator import generate_dataset_split
from simulation.sklearn_baseline import evaluate_sklearn_baseline, fit_select_sklearn_baseline


class TestSklearnBaseline(unittest.TestCase):
    def test_fit_select_and_evaluate_sklearn_baseline(self) -> None:
        train = generate_dataset_split(24, rng=123, stochastic_waveform=False)
        val = generate_dataset_split(12, rng=456, stochastic_waveform=False)

        model, val_metrics = fit_select_sklearn_baseline(
            train,
            val,
            feature_modes=("summary",),
            random_state=123,
        )
        metrics = evaluate_sklearn_baseline(model, val)

        self.assertIn(model.classifier_name, {"extra_trees", "random_forest", "hist_gradient_boosting"})
        self.assertIn(model.regressor_name, {"extra_trees", "random_forest"})
        self.assertGreaterEqual(val_metrics.material_accuracy, 0.0)
        self.assertGreaterEqual(metrics.force_mae, 0.0)
        self.assertGreaterEqual(metrics.position_mae_mm, 0.0)
        self.assertGreaterEqual(metrics.radius_mae_mm, 0.0)


if __name__ == "__main__":
    unittest.main()
