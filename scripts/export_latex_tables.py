"""Export paper-ready LaTeX tables from result CSV/JSON files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("results/paper_tables.tex"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sections = [
        default_model_table(),
        generalization_summary_table(),
        robustness_table(),
        ablation_table(),
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"saved={args.out}")


def default_model_table() -> str:
    metric_files = {
        "v1": Path("results/torch_multitask_metrics.json"),
        "v2": Path("results/torch_multitask_v2_augmented_metrics.json"),
        "v3": Path("results/torch_multitask_v3_high_force_metrics.json"),
        "v4": Path("results/torch_multitask_v4_force_dim_metrics.json"),
        "v5": Path("results/torch_multitask_v5_grid_selected_metrics.json"),
    }
    rows = []
    for model, path in metric_files.items():
        metrics = json.loads(path.read_text(encoding="utf-8"))["metrics"]["test_random"]
        rows.append(
            [
                model,
                f"{metrics['material_acc']:.4f}",
                f"{metrics['force_mae']:.4f}",
                f"{metrics['position_mae_mm']:.4f}",
                f"{metrics['radius_mae_mm']:.4f}",
            ]
        )
    return latex_table(
        caption="Default random-test performance.",
        label="tab:default-random-test",
        columns=["Model", "Material Acc.", "Force MAE (N)", "Position MAE (mm)", "Radius MAE (mm)"],
        rows=rows,
        alignment="lrrrr",
    )


def generalization_summary_table() -> str:
    rows = []
    for row in read_csv(Path("results/generalization_model_comparison_v1_v5.csv")):
        if row["split"] not in {"combined_hard", "force_high_20_30n", "radius_large_12_18mm"}:
            continue
        rows.append(
            [
                row["split"],
                row["model"],
                f"{float(row['material_acc']):.4f}",
                f"{float(row['force_mae']):.4f}",
                f"{float(row['position_mae_mm']):.4f}",
                f"{float(row['radius_mae_mm']):.4f}",
            ]
        )
    return latex_table(
        caption="Representative cross-distribution generalization results.",
        label="tab:generalization-summary",
        columns=["Split", "Model", "Material Acc.", "Force MAE (N)", "Position MAE (mm)", "Radius MAE (mm)"],
        rows=rows,
        alignment="llrrrr",
    )


def robustness_table() -> str:
    selected = {
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
    rows = []
    for row in read_csv(Path("results/robustness_v2_augmented.csv")):
        if row["split"] not in selected:
            continue
        rows.append(
            [
                row["split"],
                f"{float(row['material_acc']):.4f}",
                f"{float(row['force_mae']):.4f}",
                f"{float(row['position_mae_mm']):.4f}",
                f"{float(row['radius_mae_mm']):.4f}",
            ]
        )
    return latex_table(
        caption="Robustness of the v2 augmented checkpoint.",
        label="tab:v2-robustness",
        columns=["Split", "Material Acc.", "Force MAE (N)", "Position MAE (mm)", "Radius MAE (mm)"],
        rows=rows,
        alignment="lrrrr",
    )


def ablation_table() -> str:
    rows = []
    for row in read_csv(Path("results/ablation_structural_v1.csv")):
        if row["split"] != "test_random":
            continue
        rows.append(
            [
                row["variant"],
                f"{float(row['material_acc']):.4f}",
                f"{float(row['force_mae']):.4f}",
                f"{float(row['position_mae_mm']):.4f}",
                f"{float(row['radius_mae_mm']):.4f}",
            ]
        )
    return latex_table(
        caption="Structural ablation on the v2 augmented data.",
        label="tab:structural-ablation",
        columns=["Variant", "Material Acc.", "Force MAE (N)", "Position MAE (mm)", "Radius MAE (mm)"],
        rows=rows,
        alignment="lrrrr",
    )


def latex_table(
    caption: str,
    label: str,
    columns: list[str],
    rows: list[list[str]],
    alignment: str,
) -> str:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        f"\\caption{{{escape_latex(caption)}}}",
        f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{{alignment}}}",
        "\\hline",
        " & ".join(escape_latex(column) for column in columns) + " \\\\",
        "\\hline",
    ]
    for row in rows:
        lines.append(" & ".join(escape_latex(value) for value in row) + " \\\\")
    lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines)


def escape_latex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in str(value))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


if __name__ == "__main__":
    main()
