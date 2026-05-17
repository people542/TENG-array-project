# Step 23: 模型代际对比图

> 日期：2026-05-17  
> 对应代码：`scripts/plot_model_comparison.py`

## 1. 本步骤目标

本步骤把 v1-v5 的泛化结果画成图，便于论文实验部分展示不同训练策略的收益和代价。

## 2. 输入

默认读取：

```text
results/generalization_model_comparison_v1_v5.csv
```

该表由 `scripts/compare_model_generations.py` 生成，包含：

- split
- model
- material_acc
- force_mae
- position_mae_mm
- radius_mae_mm

## 3. 使用方式

```bash
python scripts/plot_model_comparison.py
```

默认输出：

```text
figures/generated/model_comparison/
```

每个泛化 split 生成一张图。

## 4. 图中包含

每张图包含 4 个子图：

- material accuracy
- force MAE
- position MAE
- radius MAE

横轴为模型代际：

```text
v1, v2, v3, v4, v5
```

## 5. 当前结论

图表应支持以下结论：

1. v2 扩展训练显著改善大半径和组合困难条件。
2. v3 高压力重加权显著改善高压力 force，但普通分布有副作用。
3. v4 是相对均衡的折中。
4. v5 虽来自短周期网格搜索，但完整训练后没有替代 v4。

## 6. 自检

生成后检查所有 PNG 文件非空：

```bash
python -c "from pathlib import Path; files=list(Path('figures/generated/model_comparison').glob('*.png')); assert files and all(p.stat().st_size > 0 for p in files)"
```
