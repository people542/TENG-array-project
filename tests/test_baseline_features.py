import unittest

import numpy as np

from simulation.baseline_features import (
    evaluate_baseline,
    extract_handcrafted_features,
    fit_baseline,
    predict_force,
    predict_material,
    select_baseline,
)
from simulation.dataset_generator import generate_dataset_split


class TestBaselineFeatures(unittest.TestCase):
    def test_extract_handcrafted_features_shape(self) -> None:
        split = generate_dataset_split(6, rng=123, stochastic_waveform=False)
        features = extract_handcrafted_features(split.signal)

        self.assertEqual(features.shape, (6, 222))
        self.assertTrue(np.all(np.isfinite(features)))

    def test_fit_and_predict_baseline(self) -> None:
        train = generate_dataset_split(18, rng=123, stochastic_waveform=False)
        test = generate_dataset_split(6, rng=456, stochastic_waveform=False)
        model = fit_baseline(train)

        material_pred = predict_material(model, test.signal)
        force_pred = predict_force(model, test.signal)

        self.assertEqual(material_pred.shape, (6,))
        self.assertEqual(force_pred.shape, (6,))
        self.assertTrue(np.all(np.isfinite(force_pred)))

    def test_evaluate_baseline_returns_metrics(self) -> None:
        train = generate_dataset_split(18, rng=123, stochastic_waveform=False)
        test = generate_dataset_split(6, rng=456, stochastic_waveform=False)
        result = evaluate_baseline(fit_baseline(train), test)

        self.assertGreaterEqual(result.material_accuracy, 0.0)
        self.assertLessEqual(result.material_accuracy, 1.0)
        self.assertGreaterEqual(result.force_mae, 0.0)
        self.assertGreaterEqual(result.force_rmse, 0.0)

    def test_select_baseline_returns_model_and_validation_result(self) -> None:
        train = generate_dataset_split(18, rng=123, stochastic_waveform=False)
        val = generate_dataset_split(6, rng=456, stochastic_waveform=False)
        model, result = select_baseline(
            train,
            val,
            ridge_lambdas=(0.1, 1.0),
            feature_modes=("summary", "full"),
        )

        self.assertIn(model.feature_mode, {"summary", "full"})
        self.assertIn(model.ridge_lambda, {0.1, 1.0})
        self.assertGreaterEqual(result.material_accuracy, 0.0)


if __name__ == "__main__":
    unittest.main()
