# Step 02: TENG 单元波形仿真器

> 日期：2026-05-17  
> 对应代码：`simulation/teng_unit.py`  
> 上游依赖：`simulation/material_params.py`

## 1. 本步骤目标

本步骤实现单个 TENG 单元的 200 点电压波形生成，用于后续 8×8 阵列仿真器复用。

当前模型是 literature-guided simulation model，不是实测校准模型。

## 2. 核心公式

单元电压波形采用第一版简化模型：

```text
V(t) = A_m * S_m(F) * W(t) * exp(-t / tau_m)
```

其中：

```text
S_m(F) = 1 - exp(-F / alpha_m)
W(t) = 0.5 * (1 - cos(2*pi*f*t + phase))
```

## 3. 新增接口

新增文件：

```text
simulation/teng_unit.py
```

主要接口：

- `pressure_saturation(force_n, alpha_n)`
- `time_axis(config)`
- `contact_separation_waveform(t_s, frequency_hz, phase_cycle=0.0)`
- `deterministic_unit_params(material_key, force_n, frequency_hz=None)`
- `sample_unit_params(material_key, force_n, rng=None)`
- `generate_unit_waveform(material_key, force_n, ...)`

## 4. 默认行为

`generate_unit_waveform("ptfe_al", force_n=10.0)` 默认使用：

- 材料参数范围中点
- 频率范围中点，即 2 Hz
- 采样率 200 Hz
- 时长 1 s
- 输出 shape 为 `(200,)`

如果设置 `stochastic=True`，则会在材料参数范围内采样 `sigma`、`tau`、`alpha`、`epsilon_r`、频率、相位和幅值扰动。

## 5. 已验证性质

基础测试覆盖：

1. 输出 shape 为 `(200,)`。
2. 波形为有限非负值。
3. 压力增大时峰值增大。
4. 高压力增量小于中低压力增量，体现饱和趋势。
5. 不同材料产生不同峰值。
6. 固定随机种子时随机参数可复现。

运行命令：

```bash
python -m unittest discover -s tests
```

## 6. 当前限制

1. 电压幅值仍是归一化后的 voltage-like 值，默认 `voltage_scale=10.0`。
2. 暂未加入噪声、漂移、串扰和坏点。
3. 暂未生成阵列级空间分布。
4. 后续如完成单元实测，应使用实测波形校准 `voltage_scale`、`tau_s` 和 `alpha_n`。

## 7. 下一步

实现 `simulation/array_generator.py`：

1. 根据接触中心和半径生成 8×8 高斯压力分布。
2. 对每个单元调用 `generate_unit_waveform()`。
3. 输出 shape 为 `(8, 8, 200)` 的阵列时空信号。
