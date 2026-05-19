# Step 29: 仿真实验完成度审计

> 日期：2026-05-19  
> 对应文档：`docs/experiment_artifacts_index.md`、`results/paper_tables.md`

## 1. 本步骤目标

本步骤不新增模型，而是对当前仿真实验体系做完成度审计，明确哪些实验已经完成、哪些结果应进入论文主线、哪些内容只作为补充或历史记录。这样后续写论文时不会混淆 v1-v5、鲁棒性版本和结构消融版本。

## 2. 审计范围

审计覆盖以下实验族：

| 实验族 | 状态 | 主产物 |
|---|---|---|
| 仿真合理性可视化 | 完成 | `figures/generated/paper/simulation_sanity.png` |
| 基础数据集与随机测试 | 完成 | `data/datasets/v1/`、`data/datasets/v2_augmented/` |
| baseline 与主模型训练 | 完成 | `results/torch_multitask_metrics.json`、`results/torch_multitask_v2_augmented_metrics.json` |
| 增强分布训练 | 完成 | `checkpoints/torch_multitask_v2_augmented.pt` |
| 高压力专项模型 | 完成 | `checkpoints/torch_multitask_v3_high_force.pt` |
| 均衡鲁棒模型 | 完成 | `checkpoints/torch_multitask_v4_force_dim.pt` |
| 网格搜索记录 | 完成，作为 smoke search | `results/force_weight_grid_smoke.csv` |
| 跨分布泛化 | 完成 | `results/generalization_model_comparison_v1_v5.csv` |
| v2 主模型鲁棒性 | 完成 | `results/robustness_v2_augmented.csv` |
| v1/v2 鲁棒性对比 | 完成 | `results/robustness_v1_vs_v2.csv` |
| 结构消融 | 完成 | `results/ablation_structural_v1.csv` |
| 论文表格导出 | 完成 | `results/paper_tables.md` |

## 3. 论文主线采用版本

建议论文主线采用如下版本：

| 角色 | 采用版本 | 理由 |
|---|---|---|
| 历史 baseline | v1 | 证明初始数据分布和基础模型能力 |
| 默认主模型 | v2 augmented | 默认测试中 force/radius 更稳，泛化表现比 v1 明显提升 |
| 高压力专项模型 | v3 high-force | 高压力和 combined hard 场景 force MAE 最好 |
| 均衡鲁棒模型 | v4 force-dim | 高压力优于 v2，默认分布副作用小于 v3 |
| 搜索记录 | v5 grid-selected | 仅证明短周期搜索流程，不作为最终推荐 |
| 架构证明 | structural ablation | 支撑空间-时间双分支结构必要性 |

## 4. 关键结论

1. v2 augmented 应作为默认主模型：它在默认测试中 force MAE 为 2.5548 N、position MAE 为 3.0527 mm、radius MAE 为 0.9711 mm，综合优于 v1。
2. v3 high-force 是高压力专项模型：在 `force_high_20_30n` split 上 force MAE 为 5.6090 N，优于 v2 的 8.1867 N。
3. v4 force-dim 是均衡候选：在高压力场景优于 v2，同时默认测试退化小于 v3。
4. 结构消融支持双分支设计：`no_temporal` 使材料准确率从 0.3667 降至 0.2500；`no_spatial` 使位置误差从 3.0527 mm 增至 13.1304 mm。
5. 鲁棒性主要短板是低 SNR 和强 drift 下的 radius 估计：v2 在 `snr_10db` 的 radius MAE 为 4.5305 mm，在 `drift_30pct` 为 4.1706 mm。

## 5. 完成度判断

当前仿真实验已经足够支撑完整论文初稿。后续若继续做实验，应属于增强实验或补充实验，而不是主线实验缺失。

建议把后续工作切换为：

1. 论文方法章节草稿。
2. 论文实验章节草稿。
3. 模型结构示意图和结果图排版。
4. 针对低 SNR/强 drift radius 误差的专项增强，作为可选补充。

## 6. 自检记录

本步骤同步更新：

- `docs/experiment_artifacts_index.md`
- `docs/steps/29_simulation_experiment_completion_audit.md`

需要再次执行的自动检查：

```bash
python -m unittest discover -s tests
python scripts/export_paper_tables.py
```

