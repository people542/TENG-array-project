# Step 30: 模型结构示意图

> 日期：2026-05-19  
> 对应代码：`scripts/plot_model_architecture.py`

## 1. 本步骤目标

本步骤生成论文方法部分使用的空间-时间双分支多任务网络结构示意图，补齐论文图表中“模型结构图”这一项。

## 2. 图像内容

示意图展示以下模块：

| 模块 | 说明 |
|---|---|
| Input signal | 输入张量为 `8 x 8 x 200` 的 TENG 阵列时空信号 |
| Spatial summary | 从阵列信号提取峰值、均值、能量和坐标图 |
| 2D CNN spatial branch | 空间分支输出 96 维特征 |
| Representative waveform | 选择活跃通道代表性时序波形 |
| 1D CNN temporal branch | 时间分支输出 32 维特征 |
| Concatenate | 拼接得到 128 维联合特征 |
| Shared MLP | 共享多任务表征 |
| Heads | 输出材料类别、接触力、位置和半径 |

## 3. 运行命令

```bash
python scripts/plot_model_architecture.py
```

输出文件：

```text
figures/generated/paper/model_architecture.png
```

## 4. 论文用途

该图建议放在方法章节，用于解释为什么模型同时包含空间分支和时间分支。结构消融结果可作为该图后续的实验证据：

- `no_temporal` 使材料识别准确率从 0.3667 降至 0.2500。
- `no_spatial` 使 position MAE 从 3.0527 mm 增至 13.1304 mm。

## 5. 自检要求

1. `figures/generated/paper/model_architecture.png` 存在且非空。
2. 图中必须包含空间分支、时间分支、共享层和三个输出头。
3. `python -m unittest discover -s tests` 保持通过。
