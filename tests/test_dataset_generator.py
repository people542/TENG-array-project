import tempfile
import unittest
from pathlib import Path

import numpy as np

from simulation.dataset_generator import (
    generate_dataset_split,
    load_dataset_split,
    save_dataset_split,
)
from simulation.perturbations import PerturbationConfig


class TestDatasetGenerator(unittest.TestCase):
    def test_generate_dataset_split_shapes(self) -> None:
        split = generate_dataset_split(12, rng=123, stochastic_waveform=False)

        self.assertEqual(split.signal.shape, (12, 8, 8, 200))
        self.assertEqual(split.pressure_map.shape, (12, 8, 8))
        self.assertEqual(split.material_key.shape, (12,))
        self.assertEqual(split.material_index.shape, (12,))
        self.assertEqual(split.force.shape, (12,))
        self.assertEqual(split.position.shape, (12, 2))
        self.assertEqual(split.radius.shape, (12,))
        self.assertTrue(np.allclose(split.pressure_map.sum(axis=(1, 2)), split.force))

    def test_generate_dataset_split_is_reproducible(self) -> None:
        split_a = generate_dataset_split(8, rng=123)
        split_b = generate_dataset_split(8, rng=123)

        self.assertTrue(np.allclose(split_a.signal, split_b.signal))
        self.assertTrue(np.array_equal(split_a.material_key, split_b.material_key))
        self.assertTrue(np.allclose(split_a.position, split_b.position))

    def test_perturbed_dataset_generation(self) -> None:
        clean = generate_dataset_split(4, rng=123, stochastic_waveform=False)
        disturbed = generate_dataset_split(
            4,
            rng=123,
            stochastic_waveform=False,
            perturbation=PerturbationConfig(snr_db=30.0, gain_variation=0.1),
        )

        self.assertEqual(disturbed.signal.shape, clean.signal.shape)
        self.assertFalse(np.allclose(disturbed.signal, clean.signal))

    def test_save_and_load_dataset_split(self) -> None:
        split = generate_dataset_split(3, rng=123)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "split.npz"
            save_dataset_split(split, path)
            loaded = load_dataset_split(path)

        self.assertTrue(np.allclose(split.signal, loaded.signal))
        self.assertTrue(np.array_equal(split.material_key, loaded.material_key))
        self.assertTrue(np.allclose(split.force, loaded.force))


if __name__ == "__main__":
    unittest.main()
