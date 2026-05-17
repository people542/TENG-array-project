"""Generate demo TENG array samples and validation figures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.array_generator import generate_array_sample, sample_random_array
from simulation.material_params import DEFAULT_ARRAY_CONFIG, material_keys, material_labels
from simulation.teng_unit import generate_unit_waveform, time_axis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100, help="Number of demo samples.")
    parser.add_argument("--seed", type=int, default=20260517, help="Random seed.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/demo_samples"))
    parser.add_argument("--figure-dir", type=Path, default=Path("figures/generated"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    args.figure_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    samples = generate_demo_samples(args.count, rng)
    save_samples(samples, args.data_dir / "demo_samples.npz")
    plot_material_waveforms(args.figure_dir / "demo_material_waveforms.png")
    plot_force_waveforms(args.figure_dir / "demo_force_waveforms.png")
    plot_peak_heatmaps(args.figure_dir / "demo_peak_heatmaps.png")

    print(f"generated_samples={len(samples)}")
    print(f"data={args.data_dir / 'demo_samples.npz'}")
    print(f"figures={args.figure_dir}")


def generate_demo_samples(count: int, rng: np.random.Generator) -> list:
    """Generate a small balanced-ish set of random material samples."""
    keys = material_keys()
    samples = []
    for index in range(count):
        material_key = keys[index % len(keys)]
        samples.append(sample_random_array(rng, material_key=material_key))
    return samples


def save_samples(samples: list, output_path: Path) -> None:
    """Save demo samples and labels as a compact NPZ artifact."""
    signals = np.stack([sample.signal for sample in samples], axis=0)
    pressure_maps = np.stack([sample.pressure_map_n for sample in samples], axis=0)
    material = np.array([sample.material_key for sample in samples])
    force = np.array([sample.force_n for sample in samples], dtype=float)
    position = np.array(
        [[sample.position_x_mm, sample.position_y_mm] for sample in samples],
        dtype=float,
    )
    radius = np.array([sample.radius_mm for sample in samples], dtype=float)

    np.savez_compressed(
        output_path,
        signal=signals,
        pressure_map=pressure_maps,
        material=material,
        force=force,
        position=position,
        radius=radius,
    )


def plot_material_waveforms(output_path: Path) -> None:
    """Plot deterministic waveforms for all configured materials."""
    t_s = time_axis()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for key, label in zip(material_keys(), material_labels()):
        waveform = generate_unit_waveform(key, force_n=10.0)
        ax.plot(t_s, waveform, label=label, linewidth=1.8)

    ax.set_title("Material-dependent TENG unit waveforms")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage-like response")
    ax.grid(True, alpha=0.25)
    ax.legend(ncols=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_force_waveforms(output_path: Path) -> None:
    """Plot the force saturation trend for one material."""
    t_s = time_axis()
    forces = [1.0, 5.0, 10.0, 15.0, 20.0]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for force in forces:
        waveform = generate_unit_waveform("ptfe_al", force_n=force)
        ax.plot(t_s, waveform, label=f"{force:g} N", linewidth=1.8)

    ax.set_title("Force-dependent TENG unit waveforms")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage-like response")
    ax.grid(True, alpha=0.25)
    ax.legend(title="Force")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_peak_heatmaps(output_path: Path) -> None:
    """Plot peak-voltage heatmaps for different contact positions."""
    cases = [
        (8.0, 8.0, "near top-left"),
        (17.5, 17.5, "center"),
        (28.0, 28.0, "near bottom-right"),
    ]

    fig, axes = plt.subplots(1, len(cases), figsize=(9, 3.2), constrained_layout=True)
    vmax = None
    heatmaps = []
    for x_mm, y_mm, _ in cases:
        sample = generate_array_sample(
            "ptfe_al",
            force_n=12.0,
            position_x_mm=x_mm,
            position_y_mm=y_mm,
            radius_mm=6.0,
        )
        heatmaps.append(sample.peak_map())
        vmax = max(float(sample.peak_map().max()), vmax or 0.0)

    for ax, heatmap, (_, _, title) in zip(axes, heatmaps, cases):
        image = ax.imshow(heatmap, origin="upper", cmap="viridis", vmin=0.0, vmax=vmax)
        ax.set_title(title)
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
        ax.set_xticks(range(DEFAULT_ARRAY_CONFIG.array_shape[1]))
        ax.set_yticks(range(DEFAULT_ARRAY_CONFIG.array_shape[0]))

    fig.colorbar(image, ax=axes, shrink=0.8, label="Peak response")
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
