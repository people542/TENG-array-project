# Step 15: 扩展分布训练集

> 日期：2026-05-17  
> 对应代码：`scripts/generate_augmented_dataset.py`

## 1. 为什么做这一步

前一轮泛化实验显示，当前模型在普通随机测试上可用，但在两类分布外条件下明显失败：

1. 高压力外推：`force_high_20_30n` 的 force MAE 约 9 N。
2. 大半径外推：`radius_large_12_18mm` 的 radius MAE 约 4.5 mm。

这说明仅用默认训练分布 `force=1-20 N`、`radius=3-12 mm` 很难让模型学习到分布外响应。正确处理方式不是只调模型，而是把已知任务需求纳入训练分布，形成扩展分布训练集。

## 2. 训练集组成

`scripts/generate_augmented_dataset.py` 默认生成：

- `train.npz`：1200 条
- `val.npz`：240 条
- `test_random.npz`：240 条

训练集由 6 部分混合：

| 部分 | 目的 |
|---|---|
| 默认分布 | 保持普通测试性能 |
| 高压力 `18-30 N` | 覆盖高压力外推 |
| 小半径 `1-4 mm` | 覆盖尖锐接触 |
| 大半径 `10-18 mm` | 覆盖大面积接触 |
| 边缘位置 | 改善边界定位 |
| 组合困难样本 | 让模型见到多因素叠加扰动 |

验证集和随机测试集仍使用默认分布，用来检查扩展训练是否破坏普通分布性能。

## 3. 扰动设置

默认训练扰动：

- SNR 40 dB
- 通道增益 ±10%
- 串扰 5%
- 坏点 3%
- 基线漂移 2%

组合困难训练样本额外使用：

- SNR 25 dB
- 坏点 15%
- 基线漂移 8%

## 4. 使用方式

```bash
python scripts/generate_augmented_dataset.py --train 1200 --val 240 --test 240
```

默认输出：

```text
data/datasets/v2_augmented/
```

## 5. 自检要求

生成后必须运行：

```bash
python scripts/check_dataset.py \
  data/datasets/v2_augmented/train.npz \
  data/datasets/v2_augmented/val.npz \
  data/datasets/v2_augmented/test_random.npz
```

检查重点：

1. shape 是否为 `(N, 8, 8, 200)`。
2. 压力图总和是否等于总压力。
3. 训练集 force 范围应扩展到约 30 N。
4. 训练集 radius 范围应覆盖约 1-18 mm。
5. 材料类别是否均衡。

## 6. 后续判断标准

训练新模型后，必须同时比较：

1. 默认随机测试是否明显下降。
2. `force_high_20_30n` 是否显著改善。
3. `radius_large_12_18mm` 是否显著改善。
4. `combined_hard` 是否改善。

如果只改善外推但严重损害随机测试，不能作为最终方法。
