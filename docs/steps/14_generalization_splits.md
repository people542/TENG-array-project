# Step 14: 跨分布泛化 Split

> 日期：2026-05-17  
> 对应代码：`scripts/generate_generalization_splits.py`、`scripts/run_generalization_eval.py`

## 1. 本步骤目标

本步骤生成并评估训练分布外的测试 split，用固定 checkpoint 检查跨压力、跨半径、边缘位置和组合困难条件下的泛化能力。

## 2. Split

- `force_high_20_30n`：高于训练默认范围的压力。
- `radius_small_1_3mm`：小于训练默认范围的接触半径。
- `radius_large_12_18mm`：大于训练默认范围的接触半径。
- `position_edges`：接触中心集中在阵列边缘 5 mm 内。
- `combined_hard`：高压力、大半径、边缘位置、20 dB 噪声、20% 坏点、10% 漂移。

## 3. 使用方式

```bash
python scripts/generate_generalization_splits.py --count 120
python scripts/run_generalization_eval.py
```

默认输出：

- 数据：`data/generalization/v1/`
- 结果：`results/generalization_v1.csv`

## 4. 自检

泛化结果不要求优于随机测试，但必须如实记录退化。特别是 `combined_hard` 应明显差于 `test_random`，否则说明 split 不够困难。
