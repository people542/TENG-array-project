# Step 20: 分维度 Force 权重模型评估

> 日期：2026-05-17  
> 对应代码：`scripts/train_torch_multitask.py`、`scripts/compare_model_generations.py`

## 1. 本步骤目标

本步骤评估 v4 模型：只提高 force 维度损失权重，并降低高压力样本整体权重，尝试在高压力外推和普通分布性能之间取得更平衡的结果。

## 2. 训练命令

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

## 3. 默认测试结果

v4 在 v2 默认随机测试集上：

| metric | v2 | v3 | v4 |
|---|---:|---:|---:|
| material acc | 0.3667 | 0.3750 | 0.3792 |
| force MAE | 2.5548 N | 3.0481 N | 2.7677 N |
| position MAE | 3.0527 mm | 3.4148 mm | 2.7148 mm |
| radius MAE | 0.9711 mm | 1.0837 mm | 1.0439 mm |

v4 相比 v3 明显减少了普通分布副作用；相比 v2，force 和 radius 略差，但 material 和 position 更好。

## 4. 泛化结果

| split | v2 force MAE | v3 force MAE | v4 force MAE |
|---|---:|---:|---:|
| combined_hard | 6.3855 N | 3.7642 N | 5.6876 N |
| force_high_20_30n | 8.1867 N | 5.6090 N | 6.7299 N |
| radius_large_12_18mm | 2.8457 N | 3.7103 N | 2.7201 N |

v4 的高压力改善不如 v3，但明显优于 v2，同时大半径 force 不退化。

## 5. 当前推荐

- 默认主模型：v2 augmented，原因是普通分布 force/radius 最稳。
- 均衡鲁棒模型：v4 force-dim，原因是高压力比 v2 强，普通分布副作用比 v3 小。
- 高压力专门模型：v3 high-force，原因是高压力 force MAE 最低，但默认测试退化明显。

## 6. 下一步

如果要继续优化，应做更系统的验证集选择：

1. 在 `force_dim_loss_weight = [1.5, 2.0, 3.0]` 和 `high_force_loss_weight = [1.0, 1.25, 1.5, 2.0]` 上网格搜索。
2. 用默认验证集 + 高压力验证集的联合 score 选模型。
3. 把模型选择过程写成脚本，而不是手动比较。
