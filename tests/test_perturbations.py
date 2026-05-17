import unittest

import numpy as np

from simulation.array_generator import generate_array_sample
from simulation.perturbations import (
    PerturbationConfig,
    add_awgn,
    add_baseline_drift,
    apply_channel_gain,
    apply_faulty_channels,
    apply_neighbor_crosstalk,
    apply_perturbations,
)


class TestPerturbations(unittest.TestCase):
    def setUp(self) -> None:
        self.signal = generate_array_sample("ptfe_al", 10.0, 17.5, 17.5, 6.0).signal

    def test_awgn_preserves_shape(self) -> None:
        noisy = add_awgn(self.signal, snr_db=30.0, rng=123)

        self.assertEqual(noisy.shape, self.signal.shape)
        self.assertFalse(np.allclose(noisy, self.signal))

    def test_channel_gain_returns_gains(self) -> None:
        shifted, gains = apply_channel_gain(self.signal, gain_variation=0.2, rng=123)

        self.assertEqual(shifted.shape, self.signal.shape)
        self.assertEqual(gains.shape, self.signal.shape[:2])
        self.assertGreaterEqual(float(gains.min()), 0.8)
        self.assertLessEqual(float(gains.max()), 1.2)

    def test_crosstalk_preserves_shape_and_changes_signal(self) -> None:
        mixed = apply_neighbor_crosstalk(self.signal, crosstalk_ratio=0.1)

        self.assertEqual(mixed.shape, self.signal.shape)
        self.assertFalse(np.allclose(mixed, self.signal))

    def test_faulty_channels_zeroes_expected_count(self) -> None:
        faulty, mask = apply_faulty_channels(self.signal, fault_ratio=0.25, rng=123)

        self.assertEqual(faulty.shape, self.signal.shape)
        self.assertEqual(mask.shape, self.signal.shape[:2])
        self.assertEqual(int(mask.sum()), 16)
        self.assertTrue(np.all(faulty[mask] == 0.0))

    def test_baseline_drift_preserves_shape(self) -> None:
        drifted = add_baseline_drift(self.signal, drift_ratio=0.03, rng=123)

        self.assertEqual(drifted.shape, self.signal.shape)
        self.assertFalse(np.allclose(drifted, self.signal))

    def test_apply_perturbations_returns_metadata(self) -> None:
        config = PerturbationConfig(
            snr_db=35.0,
            gain_variation=0.1,
            crosstalk_ratio=0.05,
            fault_ratio=0.1,
            baseline_drift_ratio=0.02,
        )
        disturbed, metadata = apply_perturbations(self.signal, config, rng=123)

        self.assertEqual(disturbed.shape, self.signal.shape)
        self.assertIn("channel_gains", metadata)
        self.assertIn("fault_mask", metadata)
        self.assertTrue(np.all(disturbed[metadata["fault_mask"]] == 0.0))


if __name__ == "__main__":
    unittest.main()
