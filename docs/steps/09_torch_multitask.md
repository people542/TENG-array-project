# Step 09: 轻量时空多任务 PyTorch 模型

> 日期：2026-05-17  
> 对应代码：`simulation/torch_multitask.py`、`scripts/train_torch_multitask.py`

## 1. 本步骤目标

本步骤实现一个轻量时空多任务神经网络，用于比传统 baseline 更充分地利用：

- 8x8 空间峰值、均值和能量图
- 最活跃通道的归一化时序波形

## 2. 模型结构

输入：

```text
(batch, 8, 8, 200)
```

空间分支：

```text
peak/mean/energy/x-coordinate/y-coordinate maps -> 2D CNN -> flattened spatial feature
```

时间分支：

```text
most active normalized waveform -> 1D CNN -> pooled feature
```

共享头：

```text
material classification head + force/x/y/radius regression head
```

回归目标使用训练集 mean/std 标准化。

## 3. 使用方式

```bash
python scripts/train_torch_multitask.py --epochs 25 --material-loss-weight 1.5
```

默认保存：

- `checkpoints/torch_multitask_best.pt`
- `results/torch_multitask_metrics.json`

## 4. 自检要求

每次训练后必须看：

1. 验证集指标是否随 epoch 改善。
2. 最终测试集是否接近验证集。
3. 训练集和测试集差距是否过大。
4. 是否至少优于 sklearn baseline；若没有优于，需要调整模型或数据规模。
