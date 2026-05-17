# Step 16: 扩展训练模型评估

> 日期：2026-05-17  
> 对应代码：`scripts/compare_generalization_results.py`

## 1. 本步骤目标

本步骤训练并评估使用扩展训练分布的 v2 模型，判断它是否解决 v1 在高压力和大半径泛化上的弱点。

## 2. 训练命令

```bash
python scripts/train_torch_multitask.py \
  --train data/datasets/v2_augmented/train.npz \
  --val data/datasets/v2_augmented/val.npz \
  --test data/datasets/v2_augmented/test_random.npz \
  --epochs 24 \
  --batch-size 64 \
  --material-loss-weight 2.0 \
  --model-out checkpoints/torch_multitask_v2_augmented.pt \
  --metrics-out results/torch_multitask_v2_augmented_metrics.json
```

## 3. 默认分布结果

v2 在自己的默认测试集上：

| metric | value |
|---|---:|
| material acc | 0.3667 |
| force MAE | 2.5548 N |
| position MAE | 3.0527 mm |
| radius MAE | 0.9711 mm |

对比 v1，普通随机测试没有明显损坏，force/radius 还略有改善，但材料准确率略低。

## 4. 泛化结果

评估命令：

```bash
python scripts/run_generalization_eval.py \
  --checkpoint checkpoints/torch_multitask_v2_augmented.pt \
  --out results/generalization_v2_augmented.csv
```

| split | material acc | force MAE | position MAE | radius MAE |
|---|---:|---:|---:|---:|
| combined_hard | 0.5250 | 6.3855 N | 6.8397 mm | 1.9107 mm |
| force_high_20_30n | 0.3250 | 8.1867 N | 3.2428 mm | 0.9454 mm |
| position_edges | 0.3167 | 3.1547 N | 3.2509 mm | 1.0478 mm |
| radius_large_12_18mm | 0.4083 | 2.8457 N | 4.6635 mm | 2.9339 mm |
| radius_small_1_3mm | 0.3917 | 3.6457 N | 4.6922 mm | 2.6189 mm |

## 5. 与 v1 的关键对比

v2 相比 v1：

- `combined_hard` 明显改善：
  - material acc: 0.1750 -> 0.5250
  - force MAE: 9.4394 -> 6.3855 N
  - position MAE: 9.6872 -> 6.8397 mm
  - radius MAE: 3.4223 -> 1.9107 mm
- `radius_large_12_18mm` 明显改善：
  - radius MAE: 4.4924 -> 2.9339 mm
  - position MAE: 6.0882 -> 4.6635 mm
- `force_high_20_30n` 只小幅改善：
  - force MAE: 9.0547 -> 8.1867 N

## 6. 自检结论

扩展分布训练是正确方向，但还没有彻底解决高压力外推。原因可能是压力响应函数本身在高压力区趋于饱和，波形幅值对压力变化不敏感，模型很难仅靠信号反推出 20-30 N 的绝对压力。

## 7. 下一步

下一步应针对高压力任务做专门改进：

1. 对 force regression 使用更高损失权重或高压力样本重加权。
2. 增加压力单调性约束或辅助峰值/能量回归。
3. 把 force 目标改为归一化到更宽范围后训练，避免训练集中高压力占比仍不足。
4. 单独评估 force head，避免材料分类和半径任务抢占容量。
