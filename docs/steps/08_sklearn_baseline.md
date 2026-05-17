# Step 08: 验证集选择的 Sklearn Baseline

> 日期：2026-05-17  
> 对应代码：`simulation/sklearn_baseline.py`、`scripts/run_sklearn_baseline.py`

## 1. 本步骤目标

本步骤实现比 NumPy baseline 更强的传统机器学习 baseline，并在验证集上选择配置。

## 2. 任务

同时评估四个任务：

- 材料分类 accuracy
- 压力估计 MAE / RMSE
- 位置估计欧氏误差 MAE / RMSE，单位 mm
- 半径估计 MAE / RMSE，单位 mm

## 3. 候选模型

分类器候选：

- ExtraTreesClassifier
- RandomForestClassifier
- HistGradientBoostingClassifier

回归器候选：

- ExtraTreesRegressor
- RandomForestRegressor

特征候选：

- `summary`：6 维全局统计
- `full`：198 维通道峰值、均值、能量和全局统计

## 4. 使用方式

```bash
python scripts/run_sklearn_baseline.py
```

运行前应先生成并检查数据：

```bash
python scripts/generate_dataset.py
python scripts/check_dataset.py data/datasets/v1/train.npz data/datasets/v1/val.npz data/datasets/v1/test_random.npz
```

## 5. 自检标准

每次运行后需要看：

1. 验证集和测试集是否接近，避免只在验证集上偶然好。
2. 训练集和测试集差距是否过大，若过大说明过拟合。
3. 材料分类是否明显高于随机水平，6 类随机约 16.7%。
4. 压力、位置、半径误差是否低于标签范围的粗略随机猜测。

如果不满足，应扩大数据量、调整扰动强度或使用时空深度模型。
