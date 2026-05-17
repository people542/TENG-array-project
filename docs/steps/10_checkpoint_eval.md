# Step 10: Checkpoint 复用评估脚本

> 日期：2026-05-17  
> 对应代码：`scripts/evaluate_torch_checkpoint.py`

## 1. 本步骤目标

本步骤新增独立评估脚本，用同一个已保存 PyTorch checkpoint 评估任意 `.npz` split。

## 2. 使用方式

```bash
python scripts/evaluate_torch_checkpoint.py \
  data/datasets/v1/train.npz \
  data/datasets/v1/val.npz \
  data/datasets/v1/test_random.npz
```

默认读取：

```text
checkpoints/torch_multitask_best.pt
```

## 3. 用途

后续鲁棒性实验和跨分布泛化实验不应重新训练模型，而应：

1. 固定训练得到的 checkpoint。
2. 生成不同扰动或分布偏移 split。
3. 用本脚本统一评估。
