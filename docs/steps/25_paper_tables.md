# Step 25: 论文实验表格导出

> 日期：2026-05-17  
> 对应代码：`scripts/export_paper_tables.py`

## 1. 本步骤目标

本步骤把已生成的 JSON/CSV 实验结果导出为 Markdown 表格，便于直接复制到论文草稿或继续转成 LaTeX 表格。

## 2. 输入文件

默认读取：

- `results/torch_multitask_metrics.json`
- `results/torch_multitask_v2_augmented_metrics.json`
- `results/torch_multitask_v3_high_force_metrics.json`
- `results/torch_multitask_v4_force_dim_metrics.json`
- `results/torch_multitask_v5_grid_selected_metrics.json`
- `results/generalization_model_comparison_v1_v5.csv`
- `results/robustness_v1.csv`

## 3. 输出文件

```text
results/paper_tables.md
```

## 4. 表格内容

导出的 Markdown 包含三组表：

1. 默认随机测试性能表。
2. v1-v5 跨分布泛化性能表。
3. v1 checkpoint 鲁棒性摘要表。

## 5. 使用方式

```bash
python scripts/export_paper_tables.py
```

## 6. 自检

生成后必须检查：

1. `results/paper_tables.md` 存在且非空。
2. 表格包含 v1-v5。
3. 表格包含关键泛化 split：`combined_hard`、`force_high_20_30n`、`radius_large_12_18mm`。
4. 数值与对应 CSV/JSON 一致。

## 7. 当前限制

鲁棒性摘要目前只使用 v1 checkpoint 的鲁棒性结果。如果后续决定以 v2 或 v4 作为主模型，应重新生成对应 checkpoint 的鲁棒性结果，并更新该表。
