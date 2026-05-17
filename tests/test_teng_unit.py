import unittest

import numpy as np

from simulation.material_params import DEFAULT_ARRAY_CONFIG, material_keys
from simulation.teng_unit import (
    generate_unit_waveform,
    pressure_saturation,
    sample_unit_params,
)


class TestTengUnit(unittest.TestCase):
    def test_waveform_shape_and_non_negative_values(self) -> None:
        waveform = generate_unit_waveform("ptfe_al", force_n=10.0)

        self.assertEqual(waveform.shape, (DEFAULT_ARRAY_CONFIG.sample_count,))
        self.assertTrue(np.all(np.isfinite(waveform)))
        self.assertGreaterEqual(float(waveform.min()), 0.0)
        self.assertGreater(float(waveform.max()), 0.0)

    def test_force_increases_peak_with_saturation(self) -> None:
        low = generate_unit_waveform("ptfe_al", force_n=1.0)
        mid = generate_unit_waveform("ptfe_al", force_n=10.0)
        high = generate_unit_waveform("ptfe_al", force_n=20.0)

        low_peak = float(low.max())
        mid_peak = float(mid.max())
        high_peak = float(high.max())

        self.assertGreater(mid_peak, low_peak)
        self.assertGreater(high_peak, mid_peak)
        self.assertLess(high_peak - mid_peak, mid_peak - low_peak)

    def test_materials_produce_distinct_deterministic_peaks(self) -> None:
        peaks = [
            float(generate_unit_waveform(key, force_n=10.0).max())
            for key in material_keys()
        ]

        self.assertGreater(max(peaks) - min(peaks), 0.5)

    def test_pressure_saturation_validates_inputs(self) -> None:
        with self.assertRaises(ValueError):
            pressure_saturation(-1.0, 8.0)
        with self.assertRaises(ValueError):
            pressure_saturation(1.0, 0.0)

    def test_stochastic_params_are_reproducible_with_seed(self) -> None:
        rng_a = np.random.default_rng(123)
        rng_b = np.random.default_rng(123)

        params_a = sample_unit_params("pdms_al", force_n=8.0, rng=rng_a)
        params_b = sample_unit_params("pdms_al", force_n=8.0, rng=rng_b)

        self.assertEqual(params_a.as_dict(), params_b.as_dict())


if __name__ == "__main__":
    unittest.main()
