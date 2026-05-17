# Step 12: 鲁棒性评估结果表

> 日期：2026-05-17  
> 对应代码：`scripts/run_robustness_eval.py`

## 1. 本步骤目标

本步骤把所有鲁棒性 split 的 checkpoint 评估结果保存为 CSV，便于后续画曲线和写论文实验表。

## 2. 使用方式

```bash
python scripts/run_robustness_eval.py
```

默认读取：

- checkpoint：`checkpoints/torch_multitask_best.pt`
- split 目录：`data/robustness/v1`

默认输出：

```text
results/robustness_v1.csv
```

## 3. 输出字段

- `split`
- `group`
- `level`
- `material_acc`
- `force_mae`
- `position_mae_mm`
- `radius_mae_mm`

## 4. 当前观察

配对式 split 评估后，SNR 降低、漂移增强、坏点增加时位置和半径误差总体变差。串扰在当前强度和模型下影响较小，后续如需更明显趋势，可扩大串扰强度或改变串扰模型。
