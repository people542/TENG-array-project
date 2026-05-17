"""Compare robustness CSV files for two model checkpoints."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


METRICS = ["material_acc", "force_mae", "position_mae_mm", "radius_mae_mm"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path("results/robustness_v1.csv"))
    parser.add_argument("--new", type=Path, default=Path("results/robustness_v2_augmented.csv"))
    parser.add_argument("--out", type=Path, default=Path("results/robustness_v1_vs_v2.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = load_csv(args.base)
    new = load_csv(args.new)
    rows = []
    for split in sorted(set(base) & set(new)):
        row = {"split": split}
        for metric in METRICS:
            base_value = base[split][metric]
            new_value = new[split][metric]
            row[f"{metric}_base"] = base_value
            row[f"{metric}_new"] = new_value
            row[f"{metric}_delta"] = new_value - base_value
        rows.append(row)
        print(
            f"{split}: "
            f"acc {row['material_acc_base']:.4f}->{row['material_acc_new']:.4f} "
            f"force {row['force_mae_base']:.4f}->{row['force_mae_new']:.4f} "
            f"pos {row['position_mae_mm_base']:.4f}->{row['position_mae_mm_new']:.4f} "
            f"radius {row['radius_mae_mm_base']:.4f}->{row['radius_mae_mm_new']:.4f}"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["split"]
        for metric in METRICS:
            fieldnames.extend([f"{metric}_base", f"{metric}_new", f"{metric}_delta"])
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved={args.out}")


def load_csv(path: Path) -> dict[str, dict[str, float]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return {
            row["split"]: {metric: float(row[metric]) for metric in METRICS}
            for row in reader
        }


if __name__ == "__main__":
    main()
