import unittest
from unittest.mock import patch

import numpy as np

from conway_slangpy_imgui.app import LifeState

MONOTONIC_PATCH_PATH = "conway_slangpy_imgui.app.time.monotonic"


class LifeStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.life = LifeState(5, 5)
        self.life.slang_available = False

    def test_clear_sets_all_cells_dead_and_resets_generation(self) -> None:
        self.life.current.fill(1)
        self.life.settings.generation = 9

        self.life.clear()

        self.assertEqual(self.life.settings.generation, 0)
        self.assertTrue(np.all(self.life.current == 0))

    def test_step_advances_blinker(self) -> None:
        self.life.clear()
        self.life.current[2, 1:4] = 1

        self.life.step()

        expected = np.zeros((5, 5), dtype=np.uint32)
        expected[1:4, 2] = 1
        np.testing.assert_array_equal(self.life.current, expected)
        self.assertEqual(self.life.settings.generation, 1)

    def test_to_rgba_image_alpha_full_and_live_cells_white(self) -> None:
        self.life.clear()
        self.life.current[1, 1] = 1

        image = self.life.to_rgba_image()

        self.assertEqual(image.shape, (5, 5, 4))
        self.assertTrue(np.all(image[:, :, 3] == 255))
        np.testing.assert_array_equal(image[1, 1], np.array([255, 255, 255, 255], dtype=np.uint8))
        np.testing.assert_array_equal(image[0, 0], np.array([0, 0, 0, 255], dtype=np.uint8))

    def test_update_if_needed_respects_running_and_timing(self) -> None:
        test_updates_per_second = 100.0

        with patch(MONOTONIC_PATCH_PATH, return_value=10.0):
            life = LifeState(5, 5)
        life.slang_available = False
        life.clear()
        life.current[2, 1:4] = 1
        life.settings.updates_per_second = test_updates_per_second

        life.settings.running = False
        with patch(MONOTONIC_PATCH_PATH, return_value=11.0):
            life.update_if_needed()
        self.assertEqual(life.settings.generation, 0)

        life.settings.running = True
        with patch(MONOTONIC_PATCH_PATH, return_value=10.005):
            life.update_if_needed()
        self.assertEqual(life.settings.generation, 0)

        with patch(MONOTONIC_PATCH_PATH, return_value=10.02):
            life.update_if_needed()
        self.assertEqual(life.settings.generation, 1)


if __name__ == "__main__":
    unittest.main()
