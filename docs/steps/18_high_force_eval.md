# Step 18: 高压力重加权模型评估

> 日期：2026-05-17  
> 对应代码：`scripts/compare_model_generations.py`

## 1. 本步骤目标

本步骤评估高压力重加权训练得到的 v3 模型，判断它是否应替代 v2。

## 2. 训练命令

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

## 3. 默认测试结果

v3 在 v2 默认随机测试集上：

| metric | v2 | v3 |
|---|---:|---:|
| material acc | 0.3667 | 0.3750 |
| force MAE | 2.5548 N | 3.0481 N |
| position MAE | 3.0527 mm | 3.4148 mm |
| radius MAE | 0.9711 mm | 1.0837 mm |

v3 的默认分布 force、position、radius 都比 v2 差，因此不能直接替代 v2。

## 4. 泛化结果

| split | v2 force MAE | v3 force MAE | v2 radius MAE | v3 radius MAE |
|---|---:|---:|---:|---:|
| combined_hard | 6.3855 N | 3.7642 N | 1.9107 mm | 1.7702 mm |
| force_high_20_30n | 8.1867 N | 5.6090 N | 0.9454 mm | 1.2653 mm |
| radius_large_12_18mm | 2.8457 N | 3.7103 N | 2.9339 mm | 2.8281 mm |

v3 明显改善高压力和组合困难下的 force MAE，但牺牲了普通分布和部分半径表现。

## 5. 结论

v3 是“高压力鲁棒专门模型”，不是当前默认最优模型。

当前推荐：

- 默认主模型：v2 augmented。
- 高压力/困难条件分析：报告 v3 作为 targeted robust variant。

## 6. 下一步

要得到能替代 v2 的模型，需要更细的策略：

1. 不直接加大所有高压力回归损失，而是只提高 force 维度损失权重。
2. 对 force、position、radius 使用分维度损失权重。
3. 增加 force 单调性辅助损失，减少普通分布退化。
