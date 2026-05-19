# Step 31: 论文 LaTeX 表格导出

> 日期：2026-05-19  
> 对应代码：`scripts/export_latex_tables.py`

## 1. 本步骤目标

本步骤把已经完成的论文实验结果导出为 LaTeX `table` 环境，方便后续写论文时直接引用，而不只依赖 Markdown 表格。

## 2. 输入文件

脚本读取以下结果文件：

| 输入 | 用途 |
|---|---|
| `results/torch_multitask_metrics.json` | v1 默认随机测试 |
| `results/torch_multitask_v2_augmented_metrics.json` | v2 默认随机测试 |
| `results/torch_multitask_v3_high_force_metrics.json` | v3 默认随机测试 |
| `results/torch_multitask_v4_force_dim_metrics.json` | v4 默认随机测试 |
| `results/torch_multitask_v5_grid_selected_metrics.json` | v5 默认随机测试 |
| `results/generalization_model_comparison_v1_v5.csv` | 跨分布泛化 |
| `results/robustness_v2_augmented.csv` | v2 主模型鲁棒性 |
| `results/ablation_structural_v1.csv` | 结构消融 |

## 3. 运行命令

```bash
python scripts/export_latex_tables.py
```

输出文件：

```text
results/paper_tables.tex
```

## 4. 导出表格

当前导出四张表：

1. 默认随机测试性能表：`tab:default-random-test`
2. 代表性泛化结果表：`tab:generalization-summary`
3. v2 鲁棒性结果表：`tab:v2-robustness`
4. 结构消融结果表：`tab:structural-ablation`

## 5. 自检要求

1. `results/paper_tables.tex` 存在且非空。
2. 文件中包含四个 `\label{...}`。
3. `python -m unittest discover -s tests` 保持通过。
