# Step 11: 鲁棒性测试 Split 生成

> 日期：2026-05-17  
> 对应代码：`scripts/generate_robustness_splits.py`

## 1. 本步骤目标

本步骤生成固定 checkpoint 评估用的鲁棒性测试 split，覆盖噪声、坏点、串扰和漂移。

## 2. 使用方式

```bash
python scripts/generate_robustness_splits.py --count 120
```

默认输出到：

```text
data/robustness/v1/
```

## 3. 当前 split

噪声：

- `snr_50db`
- `snr_40db`
- `snr_30db`
- `snr_20db`
- `snr_10db`

坏点：

- `fault_0pct`
- `fault_10pct`
- `fault_20pct`
- `fault_30pct`
- `fault_40pct`

串扰：

- `crosstalk_0pct`
- `crosstalk_5pct`
- `crosstalk_10pct`
- `crosstalk_20pct`

漂移：

- `drift_0pct`
- `drift_5pct`
- `drift_10pct`
- `drift_20pct`
- `drift_30pct`

## 4. 评估方式

生成后用固定 checkpoint 评估：

```bash
python scripts/evaluate_torch_checkpoint.py data/robustness/v1/snr_20db.npz
```

正式记录结果时应批量评估全部 split，并观察指标随扰动强度是否单调恶化或总体恶化。

注意：同一扰动类型下所有强度使用同一随机种子生成基础接触样本，只改变扰动强度，避免把样本差异误当成鲁棒性差异。
