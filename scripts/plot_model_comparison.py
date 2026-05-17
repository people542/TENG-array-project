"""Plot model-generation comparison from a long-form CSV table."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
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
    parser.add_argument("--csv", type=Path, default=Path("results/generalization_model_comparison_v1_v5.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("figures/generated/model_comparison"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_rows(args.csv)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for split, split_rows in rows.items():
        output_path = args.out_dir / f"{split}.png"
        plot_split(split, split_rows, output_path)
        print(f"saved={output_path}")


def load_rows(path: Path) -> dict[str, list[dict[str, float | str]]]:
    grouped: dict[str, list[dict[str, float | str]]] = defaultdict(list)
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            parsed = {"split": row["split"], "model": row["model"]}
            for metric, _ in METRICS:
                parsed[metric] = float(row[metric])
            grouped[row["split"]].append(parsed)
    model_order = {"v1": 1, "v2": 2, "v3": 3, "v4": 4, "v5": 5}
    for split_rows in grouped.values():
        split_rows.sort(key=lambda item: model_order[str(item["model"])])
    return dict(sorted(grouped.items()))


def plot_split(split: str, rows: list[dict[str, float | str]], output_path: Path) -> None:
    models = [str(row["model"]) for row in rows]
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), constrained_layout=True)
    for ax, (metric, title) in zip(axes.ravel(), METRICS):
        values = [float(row[metric]) for row in rows]
        ax.bar(models, values, color="#4C78A8")
        ax.set_title(f"{split}: {title}")
        ax.set_xlabel("Model generation")
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
