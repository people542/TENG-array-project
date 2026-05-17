# Step 21: Force 权重网格搜索

> 日期：2026-05-17  
> 对应代码：`scripts/run_force_weight_grid.py`

## 1. 为什么做这一步

前面 v2/v3/v4 是人工选择权重后训练：

- v2：扩展分布训练，普通分布最稳。
- v3：高压力样本整体重加权，高压力 force 最好，但普通分布退化。
- v4：force 维度重加权，副作用较小，但高压力改善不如 v3。

继续人工试权重不够严谨。更正确的方法是用固定候选集合做网格搜索，并用统一 score 选择模型。

## 2. 搜索参数

默认搜索：

```text
force_dim_loss_weight = [1.0, 1.5, 2.0]
high_force_loss_weight = [1.0, 1.5, 2.0]
```

每个组合训练一个短周期模型，默认 `epochs=12`，用于快速模型选择。

## 3. 选择数据

训练集：

```text
data/datasets/v2_augmented/train.npz
```

默认验证集：

```text
data/datasets/v2_augmented/val.npz
```

高压力验证集：

```text
data/generalization/v1/force_high_20_30n.npz
```

## 4. 选择分数

脚本使用 lower-is-better score：

```text
score =
  (1 - default_material_acc)
  + default_force_mae / 6
  + default_position_mae / 12
  + default_radius_mae / 3
  + high_force_mae / 10
```

含义：

- 保留默认分布性能。
- 显式惩罚高压力 force MAE。
- 不让高压力优化完全压倒材料、位置和半径任务。

## 5. 使用方式

快速搜索：

```bash
python scripts/run_force_weight_grid.py \
  --epochs 12 \
  --force-dim-weights 1.0,1.5,2.0 \
  --high-force-sample-weights 1.0,1.5,2.0
```

输出：

```text
results/force_weight_grid.csv
checkpoints/grid_force_weights/
```

## 6. 自检要求

搜索后必须检查：

1. 最优组合是否只是高压力指标好但默认验证集崩掉。
2. 最优 checkpoint 是否能在完整泛化集上复评。
3. 如果短周期搜索选出的组合不稳定，应延长 epoch 或固定更多随机种子。

## 7. 局限

这是单 seed、短周期搜索，适合快速筛选，不是最终论文级超参数搜索。正式实验应使用更大数据和重复种子。
