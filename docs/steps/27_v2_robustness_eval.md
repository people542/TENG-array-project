# Step 27: v2 主模型鲁棒性评估

> 日期：2026-05-17  
> 对应代码：`scripts/run_robustness_eval.py`、`scripts/plot_robustness_results.py`、`scripts/export_paper_tables.py`

## 1. 为什么做这一步

之前的鲁棒性结果 `results/robustness_v1.csv` 使用的是 v1 checkpoint：

```text
checkpoints/torch_multitask_best.pt
```

但当前推荐默认主模型已经变成 v2 augmented：

```text
checkpoints/torch_multitask_v2_augmented.pt
```

论文主线应保持一致，因此需要用 v2 checkpoint 重新评估同一组鲁棒性 split。

## 2. 评估命令

```bash
python scripts/run_robustness_eval.py \
  --checkpoint checkpoints/torch_multitask_v2_augmented.pt \
  --out results/robustness_v2_augmented.csv
```

## 3. 绘图命令

```bash
python scripts/plot_robustness_results.py \
  --csv results/robustness_v2_augmented.csv \
  --out-dir figures/generated/robustness_v2
```

## 4. 表格更新

```bash
python scripts/export_paper_tables.py \
  --robustness-csv results/robustness_v2_augmented.csv \
  --robustness-title "Robustness Summary for v2 Augmented Checkpoint"
```

输出仍为：

```text
results/paper_tables.md
```

## 5. 判断标准

v2 鲁棒性应重点观察：

1. SNR 降低时是否出现误差上升。
2. 漂移增强时 position/radius 是否退化。
3. 坏点比例增加时空间任务是否退化。
4. v2 与 v1 相比是否保持或改善鲁棒性。

## 6. 注意事项

鲁棒性 split 是配对式生成的：同一扰动类型下基础样本一致，只改变扰动强度。因此趋势比非配对 split 更可信。

## 7. 对比 v1 和 v2

新增对比脚本：

```bash
python scripts/compare_robustness_results.py
```

默认输出：

```text
results/robustness_v1_vs_v2.csv
```
