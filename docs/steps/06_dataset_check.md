# Step 06: 数据集检查脚本

> 日期：2026-05-17  
> 对应代码：`scripts/check_dataset.py`

## 1. 本步骤目标

本步骤新增数据集检查脚本，用于在训练前快速确认 `.npz` split 的结构和标签范围。

## 2. 使用方式

```bash
python scripts/check_dataset.py data/datasets/v1/train.npz data/datasets/v1/val.npz data/datasets/v1/test_random.npz
```

## 3. 检查内容

脚本会打印：

- `signal` shape 和 dtype
- `pressure_map` shape
- `material_index` shape
- 压力范围
- x/y 位置范围
- 半径范围
- 信号数值范围
- 压力守恒误差
- 材料类别计数

同时会强制检查：

1. `signal` shape 必须是 `(N, 8, 8, 200)`。
2. `pressure_map.sum(axis=(1,2))` 必须等于 `force`。
3. `signal` 必须全是有限值。

## 4. 下一步

可以开始实现最小 baseline：

1. 从 `.npz` 加载数据。
2. 提取简单手工特征，例如每通道峰值、均值、能量。
3. 先做材料分类和压力回归的传统 baseline。
