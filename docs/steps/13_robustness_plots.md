# Step 13: 鲁棒性曲线图

> 日期：2026-05-17  
> 对应代码：`scripts/plot_robustness_results.py`

## 1. 本步骤目标

本步骤把 `results/robustness_v1.csv` 转成论文实验图，用于观察噪声、坏点、串扰和漂移强度变化下的多任务性能趋势。

## 2. 使用方式

```bash
python scripts/plot_robustness_results.py
```

默认输出：

```text
figures/generated/robustness/
```

## 3. 输出图

- `snr_robustness.png`
- `fault_robustness.png`
- `crosstalk_robustness.png`
- `drift_robustness.png`

每张图包含：

- material accuracy
- force MAE
- position MAE
- radius MAE

## 4. 自检

生成后应检查文件非空，并观察：

1. SNR 降低时，误差总体上升。
2. 漂移增强时，位置和半径误差明显上升。
3. 坏点比例增加时，空间相关任务变差。
4. 串扰曲线如果变化较弱，需要在论文中如实说明当前串扰模型/强度下影响有限。
