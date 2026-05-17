# Step 28: 结构消融实验

> 日期：2026-05-17  
> 对应代码：`simulation/torch_multitask.py`、`scripts/run_ablation_experiments.py`、`scripts/plot_ablation_results.py`

## 1. 本步骤目标

本步骤完成主模型结构消融，验证空间分支和时间分支是否对多任务感知有贡献。

## 2. 消融设置

模型变体：

| variant | 说明 |
|---|---|
| `full` | 使用空间分支和时间分支 |
| `no_temporal` | 去掉时间分支，只使用空间峰值/均值/能量/坐标图 |
| `no_spatial` | 去掉空间分支，只使用最活跃通道的归一化时序波形 |

## 3. 训练数据和设置

默认使用当前推荐的 v2 augmented 数据集：

```text
data/datasets/v2_augmented/train.npz
data/datasets/v2_augmented/val.npz
data/datasets/v2_augmented/test_random.npz
```

默认训练参数：

```text
epochs = 18
batch_size = 64
material_loss_weight = 2.0
```

## 4. 运行命令

```bash
python scripts/run_ablation_experiments.py --epochs 18
```

输出：

```text
results/ablation_structural_v1.csv
checkpoints/ablation_structural/
```

绘图：

```bash
python scripts/plot_ablation_results.py
```

输出：

```text
figures/generated/ablation/structural_ablation.png
```

## 5. 自检要求

1. 三个 variant 都应成功生成 checkpoint 和 metrics。
2. `results/ablation_structural_v1.csv` 应包含 train/val/test_random 三个 split。
3. 图像文件应存在且非空。
4. 预期现象：
   - `no_spatial` 的位置和半径估计应明显变差。
   - `no_temporal` 的材料识别可能下降。
   - `full` 应在综合指标上最好或接近最好。

## 6. 论文用途

该实验用于支撑空间-时间双分支设计，而不是只报告最终模型结果。
## 7. 实际结果

本轮已完成 `full`、`no_temporal`、`no_spatial` 三个结构变体训练，并在 `test_random` 上得到如下结果：

| variant | material acc | force MAE (N) | position MAE (mm) | radius MAE (mm) |
|---|---:|---:|---:|---:|
| full | 0.3667 | 2.5548 | 3.0527 | 0.9711 |
| no_temporal | 0.2500 | 2.7937 | 3.6466 | 1.0699 |
| no_spatial | 0.3167 | 4.8840 | 13.1304 | 2.4070 |

结论：

1. `full` 在综合指标上最优，尤其是 force、position、radius 三个连续量估计均为本组最好。
2. `no_temporal` 的材料分类准确率从 0.3667 降至 0.2500，说明时间波形分支对材料识别有明确贡献。
3. `no_spatial` 的位置误差从 3.0527 mm 增至 13.1304 mm，半径误差从 0.9711 mm 增至 2.4070 mm，说明空间分支是定位和接触半径估计的关键结构。

## 8. 自检记录

- 单元测试：`python -m unittest discover -s tests`，28 个测试通过。
- 实验产物：
  - `results/ablation_structural_v1.csv`
  - `figures/generated/ablation/structural_ablation.png`
  - `checkpoints/ablation_structural/full.pt`
  - `checkpoints/ablation_structural/no_temporal.pt`
  - `checkpoints/ablation_structural/no_spatial.pt`
- 论文表格：`results/paper_tables.md` 已纳入结构消融表。
