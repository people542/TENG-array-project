# Step 19: 分维度回归损失权重

> 日期：2026-05-17  
> 对应代码：`scripts/train_torch_multitask.py`

## 1. 为什么做这一步

Step 18 的高压力样本重加权能显著改善高压力 force MAE，但它同时放大了整个回归向量的损失：

```text
force, x, y, radius
```

这会让高压力样本的 position/radius 也被放大，导致默认测试和部分半径任务退化。更合理的方式是分维度加权，只提高 force 维度，而不是把所有回归任务一起放大。

## 2. 新增训练参数

```bash
--force-dim-loss-weight
--position-dim-loss-weight
--radius-dim-loss-weight
```

默认均为 1.0。

## 3. 损失函数

回归目标顺序：

```text
[force, x, y, radius]
```

分维度权重：

```text
[force_weight, position_weight, position_weight, radius_weight]
```

回归损失：

```text
per_dim_loss = (prediction - target)^2 * dim_weights
per_sample_loss = mean(per_dim_loss)
```

如果同时启用高压力样本权重，则：

```text
final_reg_loss = mean(sample_weight * per_sample_loss)
```

## 4. 建议 v4 训练命令

```bash
python scripts/train_torch_multitask.py \
  --train data/datasets/v2_augmented/train.npz \
  --val data/datasets/v2_augmented/val.npz \
  --test data/datasets/v2_augmented/test_random.npz \
  --epochs 24 \
  --batch-size 64 \
  --material-loss-weight 2.0 \
  --force-dim-loss-weight 2.0 \
  --high-force-loss-weight 1.5 \
  --model-out checkpoints/torch_multitask_v4_force_dim.pt \
  --metrics-out results/torch_multitask_v4_force_dim_metrics.json
```

## 5. 判断标准

v4 只有在同时满足以下条件时才接受：

1. `force_high_20_30n` 的 force MAE 明显优于 v2。
2. 默认随机测试的 force/position/radius 不明显差于 v2。
3. `radius_large_12_18mm` 不明显退化。
