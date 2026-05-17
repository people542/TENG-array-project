# Step 17: 高压力样本重加权训练

> 日期：2026-05-17  
> 对应代码：`simulation/torch_multitask.py`、`scripts/train_torch_multitask.py`

## 1. 为什么做这一步

Step 16 显示，扩展分布训练显著改善了大半径和组合困难条件，但高压力外推仍然较弱：

```text
force_high_20_30n force MAE: 9.0547 -> 8.1867 N
```

这说明模型虽然见过更多高压力样本，但训练目标仍然主要由默认压力范围和其他任务主导。由于 TENG 压力响应在高压力区饱和，信号对压力变化不敏感，高压力样本需要更高的回归损失权重。

## 2. 实现方式

`TENGDataset` 现在同时返回：

- 标准化后的回归目标 `targets`
- 原始回归目标 `raw_targets`

训练脚本新增参数：

```bash
--high-force-threshold 20.0
--high-force-loss-weight 2.5
```

当样本的原始 force 大于等于阈值时，该样本的回归 MSE 会乘以更高权重。

## 3. 损失函数

原始损失：

```text
L = w_cls * CE(material) + w_reg * MSE(regression)
```

更新后：

```text
L = w_cls * CE(material) + w_reg * mean(sample_weight * per_sample_MSE)
```

其中：

```text
sample_weight = high_force_loss_weight, if force >= high_force_threshold
sample_weight = 1.0, otherwise
```

## 4. 预期效果

预期改善：

- `force_high_20_30n` 的 force MAE
- `combined_hard` 的 force MAE

需要监控的副作用：

- 默认随机测试 force MAE 是否上升
- position/radius 是否因为回归头偏向高压力而下降
- material accuracy 是否下降

## 5. 建议训练命令

```bash
python scripts/train_torch_multitask.py \
  --train data/datasets/v2_augmented/train.npz \
  --val data/datasets/v2_augmented/val.npz \
  --test data/datasets/v2_augmented/test_random.npz \
  --epochs 24 \
  --batch-size 64 \
  --material-loss-weight 2.0 \
  --high-force-loss-weight 2.5 \
  --model-out checkpoints/torch_multitask_v3_high_force.pt \
  --metrics-out results/torch_multitask_v3_high_force_metrics.json
```

## 6. 判断标准

只有当高压力泛化改善，同时默认测试没有明显恶化时，才接受 v3。
