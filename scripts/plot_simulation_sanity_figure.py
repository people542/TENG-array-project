"""Create a combined simulation sanity-check figure for the paper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.array_generator import generate_array_sample
from simulation.material_params import material_keys, material_labels
from simulation.teng_unit import generate_unit_waveform, time_axis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("figures/generated/paper/simulation_sanity.png"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(12, 9), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)

    plot_material_waveforms(fig.add_subplot(grid[0, 0]))
    plot_force_waveforms(fig.add_subplot(grid[0, 1]))
    plot_position_heatmaps(fig, grid[1, 0])
    plot_radius_heatmaps(fig, grid[1, 1])

    fig.suptitle("Physics-guided TENG tactile-array simulation sanity checks", fontsize=14)
    fig.savefig(args.out, dpi=220)
    plt.close(fig)
    print(f"saved={args.out}")


def plot_material_waveforms(ax: plt.Axes) -> None:
    t_s = time_axis()
    for key, label in zip(material_keys(), material_labels()):
        waveform = generate_unit_waveform(key, force_n=10.0)
        ax.plot(t_s, waveform, label=label, linewidth=1.6)
    ax.set_title("a. Material-dependent unit waveforms")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage-like response")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7, ncols=2)


def plot_force_waveforms(ax: plt.Axes) -> None:
    t_s = time_axis()
    for force in (1.0, 5.0, 10.0, 15.0, 20.0):
        waveform = generate_unit_waveform("ptfe_al", force_n=force)
        ax.plot(t_s, waveform, label=f"{force:g} N", linewidth=1.6)
    ax.set_title("b. Force-dependent saturation")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage-like response")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)


def plot_position_heatmaps(fig: plt.Figure, spec) -> None:
    subgrid = spec.subgridspec(1, 3)
    cases = [(7.5, 7.5, "top-left"), (17.5, 17.5, "center"), (27.5, 27.5, "bottom-right")]
    heatmaps = []
    for x_mm, y_mm, _ in cases:
        sample = generate_array_sample("ptfe_al", 12.0, x_mm, y_mm, 6.0)
        heatmaps.append(sample.peak_map())
    vmax = max(float(heatmap.max()) for heatmap in heatmaps)
    image = None
    for index, (heatmap, (_, _, title)) in enumerate(zip(heatmaps, cases)):
        ax = fig.add_subplot(subgrid[0, index])
        image = ax.imshow(heatmap, cmap="viridis", vmin=0.0, vmax=vmax)
        ax.set_title(f"c{index + 1}. {title}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    assert image is not None
    fig.colorbar(image, ax=[fig.axes[-3], fig.axes[-2], fig.axes[-1]], shrink=0.75, label="Peak")


def plot_radius_heatmaps(fig: plt.Figure, spec) -> None:
    subgrid = spec.subgridspec(1, 3)
    cases = [(3.0, "3 mm"), (7.0, "7 mm"), (12.0, "12 mm")]
    heatmaps = []
    for radius_mm, _ in cases:
        sample = generate_array_sample("ptfe_al", 12.0, 17.5, 17.5, radius_mm)
        heatmaps.append(sample.peak_map())
    vmax = max(float(heatmap.max()) for heatmap in heatmaps)
    image = None
    for index, (heatmap, (_, title)) in enumerate(zip(heatmaps, cases)):
        ax = fig.add_subplot(subgrid[0, index])
        image = ax.imshow(heatmap, cmap="magma", vmin=0.0, vmax=vmax)
        ax.set_title(f"d{index + 1}. radius {title}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    assert image is not None
    fig.colorbar(image, ax=[fig.axes[-3], fig.axes[-2], fig.axes[-1]], shrink=0.75, label="Peak")


if __name__ == "__main__":
    main()
