"""Plot robustness curves from the robustness CSV result table."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


METRICS = [
    ("material_acc", "Material accuracy", "higher"),
    ("force_mae", "Force MAE (N)", "lower"),
    ("position_mae_mm", "Position MAE (mm)", "lower"),
    ("radius_mae_mm", "Radius MAE (mm)", "lower"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path("results/robustness_v1.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("figures/generated/robustness"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_rows(args.csv)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for group, group_rows in sorted(rows.items()):
        output_path = args.out_dir / f"{group}_robustness.png"
        plot_group(group, group_rows, output_path)
        print(f"saved={output_path}")


def load_rows(path: Path) -> dict[str, list[dict[str, float | str]]]:
    grouped: dict[str, list[dict[str, float | str]]] = defaultdict(list)
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            parsed = {
                "split": row["split"],
                "group": row["group"],
                "level": float(row["level"]),
            }
            for metric, _, _ in METRICS:
                parsed[metric] = float(row[metric])
            grouped[str(parsed["group"])].append(parsed)
    for group_rows in grouped.values():
        group_rows.sort(key=lambda item: float(item["level"]))
    return grouped


def plot_group(group: str, rows: list[dict[str, float | str]], output_path: Path) -> None:
    x = [float(row["level"]) for row in rows]
    x_label = "SNR (dB)" if group == "snr" else "Perturbation level"
    if group == "snr":
        rows = list(reversed(rows))
        x = [float(row["level"]) for row in rows]

    fig, axes = plt.subplots(2, 2, figsize=(9, 6), constrained_layout=True)
    for ax, (metric, title, direction) in zip(axes.ravel(), METRICS):
        y = [float(row[metric]) for row in rows]
        ax.plot(x, y, marker="o", linewidth=2)
        ax.set_title(f"{group}: {title}")
        ax.set_xlabel(x_label)
        ax.set_ylabel(title)
        ax.grid(True, alpha=0.25)
        if group == "snr":
            ax.invert_xaxis()
        if direction == "higher":
            ax.set_ylim(bottom=0.0, top=max(1.0, max(y) * 1.1))
        else:
            ax.set_ylim(bottom=0.0)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
