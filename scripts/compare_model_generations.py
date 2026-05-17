"""Compare v1, v2, and v3 generalization result CSV files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


METRICS = ["material_acc", "force_mae", "position_mae_mm", "radius_mae_mm"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v1", type=Path, default=Path("results/generalization_v1.csv"))
    parser.add_argument("--v2", type=Path, default=Path("results/generalization_v2_augmented.csv"))
    parser.add_argument("--v3", type=Path, default=Path("results/generalization_v3_high_force.csv"))
    parser.add_argument("--v4", type=Path, default=Path("results/generalization_v4_force_dim.csv"))
    parser.add_argument("--v5", type=Path, default=Path("results/generalization_v5_grid_selected.csv"))
    parser.add_argument("--out", type=Path, default=Path("results/generalization_model_comparison.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tables = {
        "v1": load_csv(args.v1),
        "v2": load_csv(args.v2),
        "v3": load_csv(args.v3),
        "v4": load_csv(args.v4),
        "v5": load_csv(args.v5),
    }
    splits = sorted(set.intersection(*(set(table) for table in tables.values())))
    rows = []
    for split in splits:
        for model_name, table in tables.items():
            row = {"split": split, "model": model_name, **table[split]}
            rows.append(row)
        print(format_split(split, tables))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["split", "model", *METRICS])
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


def format_split(split: str, tables: dict[str, dict[str, dict[str, float]]]) -> str:
    force_values = " ".join(
        f"{model}:force={tables[model][split]['force_mae']:.3f},radius={tables[model][split]['radius_mae_mm']:.3f}"
        for model in ("v1", "v2", "v3", "v4", "v5")
    )
    return f"{split}: {force_values}"


if __name__ == "__main__":
    main()
