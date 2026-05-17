# Step 07: 最小 NumPy Baseline

> 日期：2026-05-17  
> 对应代码：`simulation/baseline_features.py`、`scripts/run_baseline.py`

## 1. 本步骤目标

本步骤实现不依赖深度学习框架的最小 baseline，用于确认数据集可以被加载、特征可以被提取、评估链路可以跑通。

## 2. 特征

从 `signal` 中提取：

- 每通道峰值图，64 维
- 每通道均值图，64 维
- 每通道能量图，64 维
- 全局统计，6 维

总特征维度：

```text
198
```

## 3. 模型

当前 baseline 包含：

- 材料分类：标准化特征后的最近质心分类器
- 压力估计：标准化特征后的 ridge 线性回归
- 配置选择：在验证集上选择 `summary/full` 特征和 ridge 正则强度

这是 sanity-check baseline，不是最终论文主模型。

## 4. 使用方式

```bash
python scripts/run_baseline.py
```

默认读取：

- `data/datasets/v1/train.npz`
- `data/datasets/v1/val.npz`
- `data/datasets/v1/test_random.npz`

## 5. 下一步

后续可以继续实现：

1. 位置和半径的 ridge regression baseline。
2. 1D-CNN、2D-CNN、时空融合多任务模型。
3. 鲁棒性和跨分布测试 split。
