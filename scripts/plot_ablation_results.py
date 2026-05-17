"""Plot structural ablation results."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


METRICS = [
    ("material_acc", "Material accuracy"),
    ("force_mae", "Force MAE (N)"),
    ("position_mae_mm", "Position MAE (mm)"),
    ("radius_mae_mm", "Radius MAE (mm)"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path("results/ablation_structural_v1.csv"))
    parser.add_argument("--split", default="test_random")
    parser.add_argument("--out", type=Path, default=Path("figures/generated/ablation/structural_ablation.png"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = [row for row in read_rows(args.csv) if row["split"] == args.split]
    if not rows:
        raise ValueError(f"No rows found for split {args.split!r}.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plot_rows(rows, args.out)
    print(f"saved={args.out}")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def plot_rows(rows: list[dict[str, str]], output_path: Path) -> None:
    variants = [row["variant"] for row in rows]
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), constrained_layout=True)
    for ax, (metric, title) in zip(axes.ravel(), METRICS):
        values = [float(row[metric]) for row in rows]
        ax.bar(variants, values, color="#59A14F")
        ax.set_title(title)
        ax.set_xlabel("Variant")
        ax.set_ylabel(title)
        ax.grid(True, axis="y", alpha=0.25)
        if metric == "material_acc":
            ax.set_ylim(0.0, 1.0)
        else:
            ax.set_ylim(bottom=0.0)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
