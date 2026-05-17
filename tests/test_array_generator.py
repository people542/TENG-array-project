import unittest

import numpy as np

from simulation.array_generator import (
    cell_coordinates,
    gaussian_pressure_map,
    generate_array_sample,
    sample_random_array,
)
from simulation.material_params import DEFAULT_ARRAY_CONFIG


class TestArrayGenerator(unittest.TestCase):
    def test_cell_coordinates_shape_and_extent(self) -> None:
        coords = cell_coordinates()

        self.assertEqual(coords.shape, (8, 8, 2))
        self.assertTrue(np.allclose(coords[0, 0], [0.0, 0.0]))
        self.assertTrue(np.allclose(coords[-1, -1], [35.0, 35.0]))

    def test_pressure_map_conserves_total_force(self) -> None:
        pressure = gaussian_pressure_map(
            force_n=12.0,
            position_x_mm=15.0,
            position_y_mm=20.0,
            radius_mm=6.0,
        )

        self.assertEqual(pressure.shape, DEFAULT_ARRAY_CONFIG.array_shape)
        self.assertAlmostEqual(float(pressure.sum()), 12.0, places=10)
        self.assertGreater(float(pressure.max()), 0.0)

    def test_pressure_map_peak_tracks_contact_center(self) -> None:
        pressure = gaussian_pressure_map(
            force_n=10.0,
            position_x_mm=0.0,
            position_y_mm=0.0,
            radius_mm=4.0,
        )

        self.assertEqual(np.unravel_index(np.argmax(pressure), pressure.shape), (0, 0))

    def test_array_sample_shape_and_peak_map(self) -> None:
        sample = generate_array_sample(
            "ptfe_al",
            force_n=10.0,
            position_x_mm=20.0,
            position_y_mm=15.0,
            radius_mm=6.0,
        )

        self.assertEqual(sample.signal.shape, (8, 8, 200))
        self.assertEqual(sample.pressure_map_n.shape, (8, 8))
        self.assertEqual(sample.peak_map().shape, (8, 8))
        self.assertAlmostEqual(float(sample.pressure_map_n.sum()), 10.0, places=10)
        self.assertTrue(np.all(np.isfinite(sample.signal)))

    def test_random_array_is_reproducible_with_seed(self) -> None:
        sample_a = sample_random_array(123, material_key="pdms_al")
        sample_b = sample_random_array(123, material_key="pdms_al")

        self.assertTrue(np.allclose(sample_a.signal, sample_b.signal))
        self.assertEqual(sample_a.as_label_dict(), sample_b.as_label_dict())


if __name__ == "__main__":
    unittest.main()
