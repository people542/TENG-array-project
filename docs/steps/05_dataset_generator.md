# Step 05: 数据集生成器

> 日期：2026-05-17  
> 对应代码：`simulation/dataset_generator.py`、`scripts/generate_dataset.py`

## 1. 本步骤目标

本步骤把材料参数、单元波形、阵列压力分布和扰动模块串联起来，生成可直接用于多任务学习的数据集 split。

## 2. 输出字段

每个 `.npz` split 包含：

| 字段 | shape | 含义 |
|---|---:|---|
| `signal` | `(N, 8, 8, 200)` | 阵列时空电压信号 |
| `pressure_map` | `(N, 8, 8)` | 局部压力分布 |
| `material_key` | `(N,)` | 材料字符串标签 |
| `material_index` | `(N,)` | 材料分类编号 |
| `force` | `(N,)` | 总压力，单位 N |
| `position` | `(N, 2)` | 接触中心 x/y，单位 mm |
| `radius` | `(N,)` | 接触半径，单位 mm |

## 3. 新增接口

新增文件：

```text
simulation/dataset_generator.py
```

主要接口：

- `DatasetSplit`
- `generate_dataset_split(count, rng=None, perturbation=None, stochastic_waveform=True)`
- `save_dataset_split(split, output_path)`
- `load_dataset_split(input_path)`

## 4. 生成脚本

新增脚本：

```bash
python scripts/generate_dataset.py
```

默认生成：

- `data/datasets/v1/train.npz`，600 条
- `data/datasets/v1/val.npz`，120 条
- `data/datasets/v1/test_random.npz`，120 条

默认开启轻度扰动：

- SNR 40 dB
- 通道增益 ±10%
- 串扰 5%
- 坏点 3%
- 基线漂移 2%

后续正式训练可以把样本量扩大到规划文档中的规模。

## 5. 已验证性质

基础测试覆盖：

1. 所有输出字段 shape 正确。
2. 每个样本的 `pressure_map` 总和等于 `force`。
3. 固定随机种子可复现。
4. 扰动数据集与干净数据集不同。
5. NPZ 保存和读取一致。

运行命令：

```bash
python -m unittest discover -s tests
```

## 6. 下一步

实现最小 baseline 或数据检查脚本：

1. 加载 `.npz` split。
2. 打印标签范围和材料分布。
3. 随机抽样绘图，确认数据集没有异常。
