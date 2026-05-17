# Step 01：材料参数模块

> 日期：2026-05-17  
> 对应代码：`simulation/material_params.py`  
> 上游依据：`docs/TENG_仿真参数文献调研.md`

---

## 1. 本步骤目标

本步骤把文献调研中整理的 TENG 材料参数范围固化成代码模块，作为后续单元波形仿真、阵列仿真和数据集生成的统一参数入口。

本步骤不生成波形，也不训练模型，只解决一个问题：

```text
后续仿真器从哪里读取材料参数和默认阵列设置？
```

---

## 2. 新增内容

新增文件：

```text
simulation/material_params.py
```

该文件包含：

1. `MaterialConfig`：单个材料对的参数范围。
2. `ArrayConfig`：默认阵列几何和采样配置。
3. `MATERIAL_CONFIGS`：6 类材料对参数表。
4. `DEFAULT_ARRAY_CONFIG`：8×8 阵列默认配置。
5. 辅助函数：
   - `material_keys()`
   - `material_labels()`
   - `material_index_map()`
   - `get_material_config()`
   - `validate_material_configs()`

---

## 3. 材料类别

当前固定 6 类材料对：

| 类别索引 | key | label |
|---:|---|---|
| 0 | `ptfe_al` | PTFE/Al |
| 1 | `pdms_al` | PDMS/Al |
| 2 | `kapton_al` | Kapton/Al |
| 3 | `nylon_cu` | Nylon/Cu |
| 4 | `paper_cu` | Paper/Cu |
| 5 | `leather_ag` | Leather/Ag |

类别顺序由 `MATERIAL_CONFIGS` 的插入顺序决定，后续生成数据集时应使用 `material_index_map()`，避免手写类别编号。

---

## 4. 参数含义

每个材料对包含以下参数：

| 参数 | 单位 | 作用 |
|---|---|---|
| `sigma_range_uc_m2` | μC/m² | 有效 triboelectric charge density，用于控制幅值 |
| `tau_range_s` | s | 波形衰减时间常数，用于控制动态形状 |
| `alpha_range_n` | N | 压力饱和参数，用于控制压力响应曲线 |
| `epsilon_r_range` | 无量纲 | 相对介电常数范围，用于幅值缩放或后续物理模型 |

这些值是 literature-guided simulation parameters，不是实测校准值。

---

## 5. 默认阵列配置

`DEFAULT_ARRAY_CONFIG` 当前设置为：

| 参数 | 值 |
|---|---|
| 阵列形状 | 8×8 |
| 通道数 | 64 |
| 单元间距 | 5 mm |
| 采样率 | 200 Hz |
| 单条样本时长 | 1 s |
| 每通道采样点 | 200 |
| 压力范围 | 1-20 N |
| 接触半径 | 3-12 mm |
| 接触频率 | 1-3 Hz |
| 训练噪声范围 | 30-50 dB |
| 通道增益差异 | ±20% |
| 训练串扰范围 | 0-15% |
| 训练坏点比例 | 0-15% |

---

## 6. 校验方式

本步骤使用以下命令校验：

```bash
python -c "from simulation.material_params import validate_material_configs; validate_material_configs(); print('ok')"
```

同时检查：

```bash
python -c "from simulation.material_params import DEFAULT_ARRAY_CONFIG; print(DEFAULT_ARRAY_CONFIG.channel_count, DEFAULT_ARRAY_CONFIG.sample_count)"
```

期望输出：

```text
ok
64 200
```

---

## 7. 后续使用方式

下一步 `simulation/teng_unit.py` 应从本模块读取材料参数：

```python
from simulation.material_params import get_material_config

config = get_material_config("ptfe_al")
params = config.midpoint()
```

然后用：

```text
sigma_uc_m2
tau_s
alpha_n
epsilon_r
```

生成单个 TENG 单元的 200 点电压波形。

---

## 8. 当前限制

1. 参数尚未经过实测校准。
2. `tau_range_s` 是仿真波形形状参数，不应写成严格材料固有常数。
3. `alpha_range_n` 是压力响应简化参数，不是从具体压力-电压曲线拟合得到。
4. 后期若完成单元 TENG 实测，应更新本模块并记录校准方法。
