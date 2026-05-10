"""
Conway's Game of Life using imgui_bundle for UI and SlangPy for GPU updates.

This is a proof-of-concept starter architecture. SlangPy APIs are still evolving,
so the SlangPy device/module/buffer calls may need small adjustments depending
on the installed version.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

import numpy as np


GRID_WIDTH = 128
GRID_HEIGHT = 128
SLANG_FILE = Path(__file__).with_name("life.slang")


@dataclass
class LifeSettings:
    running: bool = True
    generation: int = 0
    updates_per_second: float = 10.0
    random_fill_percent: float = 0.25


class LifeState:
    """Holds CPU-side state and delegates GPU updates to SlangPy when available."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.settings = LifeSettings()
        self.current = np.zeros((height, width), dtype=np.uint32)
        self.next_grid = np.zeros((height, width), dtype=np.uint32)

        self._last_update = time.monotonic()

        self.randomize()

        self.slang_available = False
        self.slang_module = None
        self.slang_function = None
        self.spy = None

        self._try_init_slang()

    def _try_init_slang(self) -> None:
        """Initializes SlangPy resources if available."""
        try:
            import slangpy as spy  # type: ignore

            self.spy = spy
            self.slang_available = True
        except Exception as exc:  # pragma: no cover - env-dependent
            print(f"SlangPy unavailable; falling back to CPU update: {exc}")
            self.slang_available = False

    def randomize(self) -> None:
        """Randomizes the grid using the configured fill percentage."""
        fill = self.settings.random_fill_percent
        random_values = np.random.random((self.height, self.width))
        self.current = (random_values < fill).astype(np.uint32)
        self.next_grid.fill(0)
        self.settings.generation = 0

    def clear(self) -> None:
        """Clears the grid."""
        self.current.fill(0)
        self.next_grid.fill(0)
        self.settings.generation = 0

    def step(self) -> None:
        """Advances the simulation by one generation."""
        if self.slang_available:
            self._step_gpu_placeholder()
        else:
            self._step_cpu()

        self.settings.generation += 1

    def _step_gpu_placeholder(self) -> None:
        """Placeholder for SlangPy-backed GPU update until concrete API binding."""
        self._step_cpu()

    def _step_cpu(self) -> None:
        """CPU fallback implementation of Conway's Game of Life."""
        current = self.current

        neighbors = (
            np.roll(np.roll(current, -1, axis=0), -1, axis=1)
            + np.roll(current, -1, axis=0)
            + np.roll(np.roll(current, -1, axis=0), 1, axis=1)
            + np.roll(current, -1, axis=1)
            + np.roll(current, 1, axis=1)
            + np.roll(np.roll(current, 1, axis=0), -1, axis=1)
            + np.roll(current, 1, axis=0)
            + np.roll(np.roll(current, 1, axis=0), 1, axis=1)
        )

        survives = (current == 1) & ((neighbors == 2) | (neighbors == 3))
        born = (current == 0) & (neighbors == 3)

        self.next_grid = (survives | born).astype(np.uint32)
        self.current, self.next_grid = self.next_grid, self.current

    def update_if_needed(self) -> None:
        """Advances the simulation based on the configured speed."""
        if not self.settings.running:
            return

        now = time.monotonic()
        delay = 1.0 / max(self.settings.updates_per_second, 1.0)

        if now - self._last_update >= delay:
            self.step()
            self._last_update = now

    def to_rgba_image(self) -> np.ndarray:
        """Converts the Life grid to an RGBA image array."""
        image = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        image[:, :, 3] = 255

        live = self.current == 1
        image[live, 0] = 255
        image[live, 1] = 255
        image[live, 2] = 255

        return image


life = LifeState(GRID_WIDTH, GRID_HEIGHT)


def draw_ui() -> None:
    """Draws the ImGui interface."""
    from imgui_bundle import imgui

    life.update_if_needed()

    imgui.begin("Conway's Game of Life - SlangPy + ImGui Bundle")

    imgui.text(f"Generation: {life.settings.generation}")
    imgui.text(f"Grid: {life.width} x {life.height}")

    if life.slang_available:
        imgui.text("Backend: SlangPy available (CPU placeholder)")
    else:
        imgui.text("Backend: CPU fallback")

    _, life.settings.running = imgui.checkbox("Running", life.settings.running)

    _, life.settings.updates_per_second = imgui.slider_float(
        "Updates / second",
        life.settings.updates_per_second,
        1.0,
        60.0,
    )

    _, life.settings.random_fill_percent = imgui.slider_float(
        "Random fill",
        life.settings.random_fill_percent,
        0.01,
        0.90,
    )

    if imgui.button("Step"):
        life.step()

    imgui.same_line()

    if imgui.button("Randomize"):
        life.randomize()

    imgui.same_line()

    if imgui.button("Clear"):
        life.clear()

    imgui.separator()
    imgui.text("Display note:")
    imgui.text("The starter code keeps the simulation usable with CPU fallback.")
    imgui.text("Next step: upload the RGBA grid as a texture for real display.")

    imgui.end()


def main() -> None:
    """Runs the application."""
    from imgui_bundle import immapp

    immapp.run(
        draw_ui,
        window_title="Conway Life - SlangPy + ImGui Bundle",
        window_size=(900, 700),
    )


if __name__ == "__main__":
    main()
