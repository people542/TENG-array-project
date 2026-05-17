"""Export paper-ready Markdown tables from result CSV/JSON files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("results/paper_tables.md"))
    parser.add_argument("--robustness-csv", type=Path, default=Path("results/robustness_v2_augmented.csv"))
    parser.add_argument("--robustness-title", default="Robustness Summary for v2 Augmented Checkpoint")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sections = [
        export_default_model_table(),
        export_generalization_table(),
        export_robustness_summary_table(args.robustness_csv, args.robustness_title),
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"saved={args.out}")


def export_default_model_table() -> str:
    metric_files = {
        "v1": Path("results/torch_multitask_metrics.json"),
        "v2": Path("results/torch_multitask_v2_augmented_metrics.json"),
        "v3": Path("results/torch_multitask_v3_high_force_metrics.json"),
        "v4": Path("results/torch_multitask_v4_force_dim_metrics.json"),
        "v5": Path("results/torch_multitask_v5_grid_selected_metrics.json"),
    }
    lines = [
        "## Default Random-Test Performance",
        "",
        "| model | material acc | force MAE (N) | position MAE (mm) | radius MAE (mm) |",
        "|---|---:|---:|---:|---:|",
    ]
    for model, path in metric_files.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        metrics = data["metrics"]["test_random"]
        lines.append(
            f"| {model} | {metrics['material_acc']:.4f} | {metrics['force_mae']:.4f} | "
            f"{metrics['position_mae_mm']:.4f} | {metrics['radius_mae_mm']:.4f} |"
        )
    return "\n".join(lines)


def export_generalization_table() -> str:
    rows = read_csv(Path("results/generalization_model_comparison_v1_v5.csv"))
    lines = [
        "## Generalization Performance by Model Generation",
        "",
        "| split | model | material acc | force MAE (N) | position MAE (mm) | radius MAE (mm) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['split']} | {row['model']} | {float(row['material_acc']):.4f} | "
            f"{float(row['force_mae']):.4f} | {float(row['position_mae_mm']):.4f} | "
            f"{float(row['radius_mae_mm']):.4f} |"
        )
    return "\n".join(lines)


def export_robustness_summary_table(path: Path, title: str) -> str:
    rows = read_csv(path)
    selected = [
        row
        for row in rows
        if row["split"]
        in {
            "snr_50db",
            "snr_20db",
            "snr_10db",
            "fault_0pct",
            "fault_20pct",
            "fault_40pct",
            "drift_0pct",
            "drift_20pct",
            "drift_30pct",
            "crosstalk_0pct",
            "crosstalk_10pct",
            "crosstalk_20pct",
        }
    ]
    lines = [
        f"## {title}",
        "",
        "| split | material acc | force MAE (N) | position MAE (mm) | radius MAE (mm) |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in selected:
        lines.append(
            f"| {row['split']} | {float(row['material_acc']):.4f} | {float(row['force_mae']):.4f} | "
            f"{float(row['position_mae_mm']):.4f} | {float(row['radius_mae_mm']):.4f} |"
        )
    return "\n".join(lines)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


if __name__ == "__main__":
    main()
