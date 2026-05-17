import unittest

import torch

from simulation.dataset_generator import generate_dataset_split
from simulation.torch_multitask import TENGDataset, TENGMultiTaskNet, TargetScaler


class TestTorchMultitask(unittest.TestCase):
    def test_model_forward_shapes(self) -> None:
        signal = torch.rand(4, 8, 8, 200)

        for variant in ("full", "no_temporal", "no_spatial"):
            model = TENGMultiTaskNet(material_classes=6, variant=variant)
            material_logits, regression = model(signal)

            self.assertEqual(material_logits.shape, (4, 6))
            self.assertEqual(regression.shape, (4, 4))

    def test_model_rejects_unknown_variant(self) -> None:
        with self.assertRaises(ValueError):
            TENGMultiTaskNet(material_classes=6, variant="bad")

    def test_dataset_outputs(self) -> None:
        split = generate_dataset_split(6, rng=123, stochastic_waveform=False)
        dataset = TENGDataset(split, TargetScaler.from_split(split))
        signal, material, targets, raw_targets = dataset[0]

        self.assertEqual(signal.shape, (8, 8, 200))
        self.assertEqual(material.ndim, 0)
        self.assertEqual(targets.shape, (4,))
        self.assertEqual(raw_targets.shape, (4,))


if __name__ == "__main__":
    unittest.main()
