# Step 26: 实验产物索引

> 日期：2026-05-17  
> 对应文档：`docs/experiment_artifacts_index.md`

## 1. 本步骤目标

本步骤建立实验产物索引，明确每个数据集、checkpoint、CSV、图像和表格文件的用途，避免后续论文写作时混淆 v1-v5 模型和不同 split。

## 2. 新增文档

```text
docs/experiment_artifacts_index.md
```

## 3. 索引内容

索引包含：

1. 仿真合理性图。
2. 数据集目录。
3. 模型 checkpoint。
4. 结果 CSV/Markdown 表格。
5. 鲁棒性和模型对比图。
6. 当前推荐论文叙事。
7. 已知不足。

## 4. 当前推荐

默认主模型：

```text
checkpoints/torch_multitask_v2_augmented.pt
```

高压力专门模型：

```text
checkpoints/torch_multitask_v3_high_force.pt
```

均衡鲁棒模型：

```text
checkpoints/torch_multitask_v4_force_dim.pt
```

## 5. 下一步

建议接下来做：

1. 用 v2 checkpoint 重新生成鲁棒性结果。
2. 更新 `results/paper_tables.md` 中的鲁棒性摘要。
3. 开始写论文方法部分草稿。
