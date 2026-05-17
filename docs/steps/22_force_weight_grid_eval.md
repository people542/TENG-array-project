# Step 22: Force 权重网格搜索结果评估

> 日期：2026-05-17  
> 对应代码：`scripts/run_force_weight_grid.py`、`scripts/compare_model_generations.py`

## 1. 本步骤目标

本步骤执行小规模 force 权重网格搜索，并验证短周期选择出的候选模型在完整训练后是否真的优于 v2/v3/v4。

## 2. Smoke 网格搜索

运行命令：

```bash
python scripts/run_force_weight_grid.py \
  --epochs 8 \
  --force-dim-weights 1.0,2.0 \
  --high-force-sample-weights 1.0,1.5 \
  --out results/force_weight_grid_smoke.csv \
  --checkpoint-dir checkpoints/grid_force_weights_smoke
```

结果：

| tag | default force MAE | high-force MAE | score |
|---|---:|---:|---:|
| fdw1_hsw1 | 2.7392 | 7.1655 | 2.6008 |
| fdw1_hsw1p5 | 3.1337 | 5.4956 | 2.3775 |
| fdw2_hsw1 | 2.6715 | 6.5499 | 2.4752 |
| fdw2_hsw1p5 | 2.8732 | 6.1599 | 2.4168 |

短周期选择：

```text
force_dim_loss_weight = 1.0
high_force_loss_weight = 1.5
```

## 3. v5 完整训练

训练命令：

```bash
python scripts/train_torch_multitask.py \
  --train data/datasets/v2_augmented/train.npz \
  --val data/datasets/v2_augmented/val.npz \
  --test data/datasets/v2_augmented/test_random.npz \
  --epochs 24 \
  --batch-size 64 \
  --material-loss-weight 2.0 \
  --force-dim-loss-weight 1.0 \
  --high-force-loss-weight 1.5 \
  --model-out checkpoints/torch_multitask_v5_grid_selected.pt \
  --metrics-out results/torch_multitask_v5_grid_selected_metrics.json
```

默认测试：

| metric | value |
|---|---:|
| material acc | 0.3792 |
| force MAE | 2.8926 N |
| position MAE | 3.1885 mm |
| radius MAE | 1.1331 mm |

泛化测试：

| split | material acc | force MAE | position MAE | radius MAE |
|---|---:|---:|---:|---:|
| combined_hard | 0.5333 | 4.7705 N | 6.1893 mm | 1.6176 mm |
| force_high_20_30n | 0.3750 | 6.4846 N | 3.1186 mm | 0.9498 mm |
| radius_large_12_18mm | 0.4000 | 3.5111 N | 4.5933 mm | 2.5845 mm |

## 4. 结论

v5 高压力比 v4 略好，但默认测试和大半径 force 不如 v4，整体没有替代价值。

重要经验：

短周期网格搜索可以筛候选，但不能直接当最终选择。短周期最优组合在完整训练后可能不再最优。

## 5. 当前推荐保持不变

- 默认主模型：v2 augmented。
- 高压力专门模型：v3 high-force。
- 均衡鲁棒模型：v4 force-dim。
- v5 仅作为网格搜索候选记录，不作为推荐模型。

## 6. 下一步

下一步更适合做实验结果可视化和论文表格，而不是继续盲目调权重：

1. 画 v1-v5 模型对比图。
2. 画泛化 split 的任务误差柱状图。
3. 整理可直接放论文的实验表。
