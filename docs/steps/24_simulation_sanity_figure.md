# Step 24: 仿真合理性总图

> 日期：2026-05-17  
> 对应代码：`scripts/plot_simulation_sanity_figure.py`

## 1. 本步骤目标

本步骤生成一张论文级仿真合理性总图，用于证明当前信号生成器不是任意随机数据，而是满足基本物理直觉。

## 2. 图的组成

输出图包含 4 个部分：

| 子图 | 内容 | 验证点 |
|---|---|---|
| a | 不同材料的单元波形 | 材料参数导致幅值和衰减差异 |
| b | 不同压力的单元波形 | 压力增大时峰值上升并趋于饱和 |
| c | 不同接触位置的 8x8 峰值热力图 | 空间峰值跟随接触中心移动 |
| d | 不同接触半径的 8x8 峰值热力图 | 半径增大时激活区域扩展 |

## 3. 固定参数

材料波形：

- force = 10 N
- frequency = 默认中点 2 Hz
- 材料 = 当前 6 类材料

压力波形：

- material = PTFE/Al
- force = 1, 5, 10, 15, 20 N

位置热力图：

- material = PTFE/Al
- force = 12 N
- radius = 6 mm
- position = top-left, center, bottom-right

半径热力图：

- material = PTFE/Al
- force = 12 N
- position = center
- radius = 3, 7, 12 mm

## 4. 使用方式

```bash
python scripts/plot_simulation_sanity_figure.py
```

默认输出：

```text
figures/generated/paper/simulation_sanity.png
```

## 5. 自检

生成后必须检查：

1. 文件存在且非空。
2. 材料波形不是完全重合。
3. 压力波形峰值随压力上升。
4. 位置热力图峰值移动方向正确。
5. 半径热力图激活区域随半径增大而扩展。

## 6. 论文用途

该图适合放在实验第一节或方法验证部分，作为后续多任务学习、鲁棒性和泛化实验的仿真基础说明。
