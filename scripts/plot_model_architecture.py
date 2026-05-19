"""Create a paper-ready architecture diagram for the TENG multi-task model."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("figures/generated/paper/model_architecture.png"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plot_architecture(args.out)
    print(f"saved={args.out}")


def plot_architecture(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 7), constrained_layout=True)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7)
    ax.axis("off")

    colors = {
        "input": "#DCEBFA",
        "spatial": "#D9EAD3",
        "temporal": "#FCE5CD",
        "shared": "#EADCF8",
        "head": "#F4CCCC",
        "note": "#F7F7F7",
    }

    draw_box(ax, 0.4, 2.75, 1.8, 1.0, "Input signal\n8 x 8 x 200", colors["input"])
    draw_box(ax, 2.8, 4.25, 2.0, 0.85, "Spatial summary\npeak / mean / energy\n+ coordinate maps", colors["spatial"])
    draw_box(ax, 5.35, 4.25, 1.8, 0.85, "2D CNN\nspatial branch\n96 features", colors["spatial"])
    draw_box(ax, 2.8, 1.65, 2.0, 0.85, "Representative\nactive-channel\nwaveform", colors["temporal"])
    draw_box(ax, 5.35, 1.65, 1.8, 0.85, "1D CNN\ntemporal branch\n32 features", colors["temporal"])
    draw_box(ax, 7.8, 2.95, 1.65, 0.9, "Concatenate\n128 features", colors["shared"])
    draw_box(ax, 10.05, 2.95, 1.65, 0.9, "Shared MLP\n128 hidden", colors["shared"])
    draw_box(ax, 12.0, 4.45, 0.8, 0.85, "Material\nclass", colors["head"])
    draw_box(ax, 12.0, 2.95, 0.8, 0.85, "Force\nN", colors["head"])
    draw_box(ax, 12.0, 1.45, 0.8, 0.85, "Position\nx, y\nRadius", colors["head"])

    draw_arrow(ax, (2.2, 3.25), (2.8, 4.68))
    draw_arrow(ax, (4.8, 4.68), (5.35, 4.68))
    draw_arrow(ax, (2.2, 3.25), (2.8, 2.08))
    draw_arrow(ax, (4.8, 2.08), (5.35, 2.08))
    draw_arrow(ax, (7.15, 4.68), (7.8, 3.4))
    draw_arrow(ax, (7.15, 2.08), (7.8, 3.4))
    draw_arrow(ax, (9.45, 3.4), (10.05, 3.4))
    draw_arrow(ax, (11.7, 3.4), (12.0, 4.88))
    draw_arrow(ax, (11.7, 3.4), (12.0, 3.38))
    draw_arrow(ax, (11.7, 3.4), (12.0, 1.88))

    draw_box(
        ax,
        0.55,
        0.35,
        11.9,
        0.55,
        "Training objective: material cross-entropy + scaled regression MSE. "
        "Ablations remove the temporal or spatial branch to verify branch contributions.",
        colors["note"],
        fontsize=9,
        radius=0.04,
    )
    ax.text(
        6.5,
        6.35,
        "Spatial-temporal multi-task network for TENG tactile-array perception",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
    )

    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def draw_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    facecolor: str,
    fontsize: int = 10,
    radius: float = 0.08,
) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.03,rounding_size={radius}",
        linewidth=1.2,
        edgecolor="#333333",
        facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize)


def draw_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float]) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=1.2,
        color="#333333",
        shrinkA=3,
        shrinkB=3,
    )
    ax.add_patch(arrow)


if __name__ == "__main__":
    main()
