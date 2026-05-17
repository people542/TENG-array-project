# TENG 触觉阵列仿真参数文献调研

> 调研日期：2026-05-17  
> 用途：为 `simulation/material_params.py`、TENG 单元模型、阵列压力分布、噪声/漂移/串扰模型提供第一版 literature-guided 参数范围。  
> 注意：不同论文的器件结构、面积、频率、湿度、负载、电极和表面微结构差异很大，因此本文不把任何单个数值当作绝对常数，而是整理成适合仿真预研的参数区间。

---

## 1. 对仿真最有用的结论

第一版仿真建议把材料参数拆成 3 个层次：

1. `tribo_charge_density`：材料相关有效电荷密度，用于控制电压幅值。
2. `decay_tau`：电荷/波形衰减时间常数，用于控制波形动态差异。
3. `force_alpha`：压力饱和参数，用于控制压力增加时的非线性饱和。

推荐在代码中保存以下参数：

```python
{
    "name": "PTFE/Al",
    "sigma_range_uc_m2": (70.0, 140.0),
    "tau_range_s": (0.8, 1.8),
    "alpha_range_n": (6.0, 10.0),
    "epsilon_r_range": (2.0, 2.2),
}
```

其中 `sigma_range_uc_m2` 是用于仿真的有效电荷密度范围，不等同于某个具体实验器件的直接测量值。它主要参考定量 triboelectric series 和 TENG figure-of-merit 文献，并结合普通器件输出量级进行保守设定。

---

## 2. 材料电荷密度依据

### 2.1 定量 triboelectric series

Zou 等人在 Nature Communications 2019 中系统测量了多种材料的 triboelectric charge density，提出用 TECD 定量排列 triboelectric series。该工作对仿真最有价值，因为它给出了同一测试平台下不同材料的相对强弱。

可用于本项目的近似参考值如下：

| 材料 | 文献中 TECD 量级 | 对仿真的意义 |
|---|---:|---|
| PTFE | 约 -113 μC/m² | 强负性材料，适合作为高输出材料 |
| PDMS | 约 -102 μC/m² | 强负性柔性材料 |
| Kapton / Polyimide | 约 -93 μC/m² | 负性且稳定 |
| PVDF | 约 -87 μC/m² | 负性材料，可作为扩展材料 |
| Leather | 约 -54 μC/m² | 中等强度材料 |
| PMMA | 约 -49 μC/m² | 中等强度材料 |
| Nylon 6 | 约 -18 μC/m² | 在该标准体系中偏弱 |
| Copy paper / Cellulose | 约 -18 μC/m² | 较弱、低成本材料 |

注意事项：

- TECD 的正负号依赖参考体系和测试方式。仿真材料识别任务第一版只需要控制幅值和动态差异，可以先使用绝对值或归一化后的有效值。
- 真实 TENG 的输出不仅由材料决定，还受接触面积、微结构、湿度、频率、压力、电极、电路负载和表面污染影响。
- Nylon 在常见 triboelectric series 中经常被视为偏正性材料，但 Zou 等的标准化测量值与常识性序列表达并不完全等价。仿真中应把 Nylon/Cu 设为中高输出但参数波动较大的材料对，而不是只按单一表格排序。

### 2.2 TENG figure-of-merit 文献

Zi 等人在 Nature Communications 2015 中讨论了 TENG 标准化性能评价方法，并指出 surface charge density 是决定 TENG 输出能力的核心量之一。该类文献支持在仿真中使用 `sigma` 控制输出幅值，并通过参数扰动模拟器件差异。

该文献更适合作为“为什么用电荷密度作为核心参数”的理论依据，而不是直接给出某个触觉阵列的材料参数表。

---

## 3. 第一版材料参数推荐

下表是建议写入 `simulation/material_params.py` 的初始范围。

| 材料对 | `sigma_range_uc_m2` | `tau_range_s` | `alpha_range_n` | `epsilon_r_range` | 仿真定位 |
|---|---:|---:|---:|---:|---|
| PTFE/Al | 70-140 | 0.8-1.8 | 6-10 | 2.0-2.2 | 高输出、强负性材料 |
| PDMS/Al | 60-130 | 0.5-1.4 | 7-12 | 2.5-3.2 | 柔性材料，压力响应更平滑 |
| Kapton/Al | 50-120 | 0.8-2.0 | 8-13 | 3.1-3.6 | 稳定薄膜材料 |
| Nylon/Cu | 35-100 | 0.6-1.5 | 5-9 | 3.0-4.0 | 中高输出，保留较大波动 |
| Paper/Cu | 20-60 | 0.3-1.0 | 4-8 | 2.0-3.5 | 低成本、低输出、湿度敏感 |
| Leather/Ag | 25-70 | 0.4-1.2 | 6-11 | 2.5-4.0 | 触觉场景材料，中等输出 |

这些范围的设计原则：

1. PTFE、PDMS、Kapton 的 `sigma` 上限较高，因为文献中的 TECD 量级较大。
2. Paper 和 Leather 设为中低输出，符合定量序列表中的较低 TECD 量级。
3. Nylon/Cu 保留较宽范围，因为 Nylon 在不同 triboelectric series 和器件结构中的相对位置差异较大。
4. `tau_range_s` 暂时作为波形衰减形状参数，不声称是材料固有常数。
5. `alpha_range_n` 是触觉阵列任务中的压力饱和参数，主要用于模拟接触面积随压力增加逐渐饱和的趋势。

---

## 4. 介电常数参数依据

介电常数用于简化表达 TENG 中介质层对电势分布的影响。第一版仿真不需要精确建模多层电介质，只需要将其作为材料差异和幅值缩放的一部分。

常见范围：

| 材料 | 相对介电常数范围 | 说明 |
|---|---:|---|
| PTFE | 约 2.0-2.2 | 低介电常数氟聚合物 |
| PDMS | 约 2.5-3.2 | 常见柔性介电层 |
| Kapton / Polyimide | 约 3.1-3.6 | 常见聚酰亚胺薄膜 |
| Nylon | 约 3.0-4.0 | 受湿度影响较明显 |
| Paper / Cellulose | 约 2.0-3.5 | 受湿度、密度和纤维结构影响 |
| Leather | 约 2.5-4.0 | 天然材料，离散性较大 |

仿真建议：

```text
epsilon_factor = 1 / epsilon_r
```

或者第一版更简单地把 `epsilon_r` 并入材料幅值系数中，不单独暴露。

---

## 5. 压力响应和饱和参数

TENG 触觉/压力传感论文普遍显示，输出电压、电荷或电流会随压力增加而增加，但在较高压力下趋于饱和。这通常来自真实接触面积增加逐渐变慢、材料形变饱和、电荷转移上限和器件结构限制。

第一版推荐压力饱和函数：

```text
S(F_i) = 1 - exp(-F_i / alpha_m)
```

其中：

| 参数 | 推荐范围 | 含义 |
|---|---:|---|
| `F_i` | 由阵列高斯压力分布得到 | 第 i 个单元局部压力 |
| `alpha_m` | 4-13 N | 材料相关压力饱和速度 |

解释：

- `alpha_m` 越小，小压力时响应增长越快，也更早饱和。
- `alpha_m` 越大，压力响应更缓慢，高压力下仍有增长。
- Paper/Cu 可以设为较小 `alpha`，表示低压力下接触面积变化明显但较快饱和。
- Kapton/Al 和 PDMS/Al 可以设为较大 `alpha`，表示响应更平滑。

---

## 6. 时间波形和衰减参数

TENG 接触-分离模式理论通常用位移 `x(t)`、电荷 `Q`、电压 `V` 和电容变化描述输出。Niu 等关于接触模式 TENG 的理论工作说明，输出受表面电荷密度、间距、介电厚度、面积和外电路共同影响。

为了服务触觉识别任务，第一版不直接求解完整 V-Q-x 方程，而使用简化波形：

```text
V_i(t) = A_i · waveform(t) · exp(-t / tau_m)
```

其中：

```text
waveform(t) = 0.5 · (1 - cos(2π f t))
```

建议范围：

| 参数 | 推荐范围 | 说明 |
|---|---:|---|
| `sample_rate_hz` | 200 | 每条样本 1 s，200 点 |
| `duration_s` | 1.0 | 单次接触-分离周期或短序列 |
| `frequency_hz` | 1-3 | 触觉按压/释放频率 |
| `tau_m` | 0.3-2.0 s | 材料/表面状态相关衰减形状参数 |
| `phase_jitter` | 0-0.05 cycle | 模拟接触同步误差 |
| `amplitude_jitter` | ±5%-15% | 模拟重复接触差异 |

`tau_m` 的论文依据更适合作为“表面电荷会随时间、湿度和环境条件衰减”的现象依据。不同实验中的衰减常数差异很大，因此第一版把它作为波形形状参数，而不是严格材料物性。

---

## 7. 阵列空间参数

8×8 阵列压力分布建议使用二维高斯：

```text
w_i = exp(-d_i^2 / (2r^2))
F_i = F_total · w_i / sum(w_i)
```

推荐参数：

| 参数 | 推荐范围 | 说明 |
|---|---:|---|
| `array_shape` | 8×8 | 64 通道 |
| `spacing_mm` | 5 | 单元中心间距 |
| `force_total_n` | 1-20 | 总接触压力 |
| `contact_radius_mm` | 3-12 | 接触半径/高斯展宽 |
| `position_x_mm` | 0-35 | 8 个点间距 5 mm 时的坐标范围 |
| `position_y_mm` | 0-35 | 同上 |

解释：

- `r = 3 mm` 时响应集中在少数单元。
- `r = 12 mm` 时响应扩散到更大区域。
- 边缘位置会产生截断的高斯分布，应保留作为泛化测试。

---

## 8. 噪声、漂移、串扰和坏点参数

真实 TENG 阵列的非理想因素包括电子噪声、机械接触随机性、环境湿度、表面电荷衰减、通道增益差异、阵列串扰和坏点。第一版建议参数如下：

| 扰动 | 推荐范围 | 实现方式 |
|---|---:|---|
| 高斯白噪声 | SNR 10-50 dB | 按信号功率换算噪声标准差 |
| 基线漂移 | 峰值幅值的 0-5% | 低频正弦或随机游走 |
| 通道增益差异 | ±20% | 每通道乘以固定 `K_i` |
| 通道增益漂移 | ±0%-30% | 测试集额外扰动 |
| 串扰 | 0%-20% | 邻域均值耦合 |
| 坏点比例 | 0%-40% | 通道置零或低幅值噪声 |
| 时间平移 | ±5-10 samples | 模拟接触不同步 |

建议训练时的增强范围略小，测试时的压力更大：

| 类型 | 训练增强 | 鲁棒性测试 |
|---|---:|---:|
| SNR | 30-50 dB | 10, 20, 30, 40, 50 dB |
| 坏点 | 0%-15% | 0%-40% |
| 漂移 | ±0%-10% | ±0%-30% |
| 串扰 | 0%-10% | 0%-20% |

---

## 9. 推荐写入代码的默认配置

```python
DEFAULT_ARRAY_CONFIG = {
    "array_shape": (8, 8),
    "spacing_mm": 5.0,
    "sample_rate_hz": 200,
    "duration_s": 1.0,
    "force_range_n": (1.0, 20.0),
    "radius_range_mm": (3.0, 12.0),
    "contact_frequency_range_hz": (1.0, 3.0),
    "snr_range_db": (30.0, 50.0),
    "gain_variation": 0.20,
    "crosstalk_range": (0.0, 0.15),
    "fault_ratio_range": (0.0, 0.15),
}
```

```python
MATERIAL_CONFIGS = {
    "ptfe_al": {
        "label": "PTFE/Al",
        "sigma_range_uc_m2": (70.0, 140.0),
        "tau_range_s": (0.8, 1.8),
        "alpha_range_n": (6.0, 10.0),
        "epsilon_r_range": (2.0, 2.2),
    },
    "pdms_al": {
        "label": "PDMS/Al",
        "sigma_range_uc_m2": (60.0, 130.0),
        "tau_range_s": (0.5, 1.4),
        "alpha_range_n": (7.0, 12.0),
        "epsilon_r_range": (2.5, 3.2),
    },
    "kapton_al": {
        "label": "Kapton/Al",
        "sigma_range_uc_m2": (50.0, 120.0),
        "tau_range_s": (0.8, 2.0),
        "alpha_range_n": (8.0, 13.0),
        "epsilon_r_range": (3.1, 3.6),
    },
    "nylon_cu": {
        "label": "Nylon/Cu",
        "sigma_range_uc_m2": (35.0, 100.0),
        "tau_range_s": (0.6, 1.5),
        "alpha_range_n": (5.0, 9.0),
        "epsilon_r_range": (3.0, 4.0),
    },
    "paper_cu": {
        "label": "Paper/Cu",
        "sigma_range_uc_m2": (20.0, 60.0),
        "tau_range_s": (0.3, 1.0),
        "alpha_range_n": (4.0, 8.0),
        "epsilon_r_range": (2.0, 3.5),
    },
    "leather_ag": {
        "label": "Leather/Ag",
        "sigma_range_uc_m2": (25.0, 70.0),
        "tau_range_s": (0.4, 1.2),
        "alpha_range_n": (6.0, 11.0),
        "epsilon_r_range": (2.5, 4.0),
    },
}
```

---

## 10. 参考论文记录

### R1. Quantifying the triboelectric series

- Title: Quantifying the triboelectric series
- Authors: Zou et al.
- Journal: Nature Communications
- Year: 2019
- DOI / URL: https://doi.org/10.1038/s41467-019-09461-x
- 用途：提供多种材料的定量 TECD，支撑 `sigma_range_uc_m2` 的相对排序。
- 记录重点：PTFE、PDMS、Kapton/Polyimide、Leather、Nylon、Paper/Cellulose 等材料的电荷密度量级。
- 局限：TECD 是在标准化接触对象和测试条件下得到的，不等同于任意 TENG 器件的实际输出。

### R2. Standards and figure-of-merits for quantifying the performance of triboelectric nanogenerators

- Title: Standards and figure-of-merits for quantifying the performance of triboelectric nanogenerators
- Authors: Zi et al.
- Journal: Nature Communications
- Year: 2015
- DOI / URL: https://doi.org/10.1038/ncomms9376
- 用途：说明 surface charge density 是 TENG 输出能力的核心量之一，支持用 `sigma` 作为仿真核心参数。
- 局限：重点是标准化评价指标，不是触觉阵列数据集。

### R3. Theoretical study of contact-mode triboelectric nanogenerators as an effective power source

- Title: Theoretical study of contact-mode triboelectric nanogenerators as an effective power source
- Authors: Niu et al.
- Journal: Energy & Environmental Science
- Year: 2013
- DOI / URL: https://doi.org/10.1039/C3EE42571A
- 用途：支撑接触-分离模式中电压、电荷、间距、电容和表面电荷密度之间的理论关系。
- 局限：完整理论模型比本项目第一版仿真复杂，第一版只抽取核心物理趋势。

### R4. Theoretical systems of triboelectric nanogenerators

- Title: Theoretical systems of triboelectric nanogenerators
- Authors: Niu and Wang
- Journal: Nano Energy
- Year: 2015
- DOI / URL: https://doi.org/10.1016/j.nanoen.2014.11.034
- 用途：作为 TENG 工作模式和基本理论建模综述来源。
- 局限：不直接给触觉阵列材料参数。

### R5. Effect of humidity and pressure on the triboelectric nanogenerator

- Title: Effect of humidity and pressure on the triboelectric nanogenerator
- Authors: Nguyen and Yang
- Journal: Nano Energy
- Year: 2013
- DOI / URL: https://doi.org/10.1016/j.nanoen.2013.07.012
- 用途：支持把压力和湿度作为影响 TENG 输出的重要因素；用于设置压力响应、湿度/漂移扰动和天然材料更强随机性。
- 局限：该论文不是触觉阵列任务，不能直接给 8×8 阵列参数。

### R6. Triboelectric active sensor array for pressure detection and tactile imaging

- Title: Triboelectric active sensor array for self-powered static and dynamic pressure detection and tactile imaging
- Authors: Yang et al.
- Journal: ACS Nano
- Year: 2013
- DOI / URL: https://doi.org/10.1021/nn4044057
- 用途：支撑 TENG 阵列可用于压力分布和触觉成像，支持本项目使用 8×8 阵列热力图。
- 局限：具体阵列结构与本项目仿真设定不同。

### R7. Achieving ultrahigh triboelectric charge density for efficient energy harvesting

- Title: Achieving ultrahigh triboelectric charge density for efficient energy harvesting
- Authors: Liu et al.
- Journal: Nature Communications
- Year: 2017
- DOI / URL: https://doi.org/10.1038/s41467-017-00131-4
- 用途：说明普通仿真中几十 μC/m² 量级是合理起点，同时高性能器件可通过电荷注入等方法达到更高电荷密度。
- 局限：该工作面向高电荷密度能量采集，不应直接作为普通触觉阵列的默认参数。

### R8. Visualization and standardized quantification of surface charge density for triboelectric materials

- Title: Visualization and standardized quantification of surface charge density for triboelectric materials
- Journal: Nature Communications
- Year: 2024
- DOI / URL: https://doi.org/10.1038/s41467-024-49660-9
- 用途：支持表面电荷密度可视化、标准化测量和电荷衰减分析；可作为后续 `tau_range_s` 和长期漂移模型的依据。
- 局限：更偏材料表征，不是 TENG 触觉阵列数据集。

### R9. Nanostructured versus flat compact electrode for triboelectric nanogenerators at high humidity

- Title: Nanostructured versus flat compact electrode for triboelectric nanogenerators at high humidity
- Journal: Scientific Reports
- Year: 2021
- DOI / URL: https://doi.org/10.1038/s41598-021-95621-3
- 用途：支持湿度和表面结构会显著影响 TENG 输出；用于设置噪声、漂移和材料参数扰动。
- 局限：器件结构与触觉阵列不同。

### R10. A flexible triboelectric tactile sensor for simultaneous material and texture recognition

- Title: A flexible triboelectric tactile sensor for simultaneous material and texture recognition
- Journal: Nano Energy
- Year: 2022
- DOI / URL: https://doi.org/10.1016/j.nanoen.2021.106798
- 用途：支持 TENG 信号可用于材料和纹理识别，并可结合深度学习进行高精度分类。
- 局限：该工作是实物触觉传感器，不提供可直接迁移到 8×8 阵列的统一仿真参数。

### R11. Fingerprint-inspired electronic skin based on triboelectric nanogenerator for fine texture recognition

- Title: Fingerprint-inspired electronic skin based on triboelectric nanogenerator for fine texture recognition
- Journal: Nano Energy
- Year: 2021
- DOI / URL: https://doi.org/10.1016/j.nanoen.2021.106001
- 用途：支持 TENG 波形动态特征与纹理/材料类触觉识别相关，说明后续模型应保留时序分支。
- 局限：目标是精细纹理识别，不是材料、压力、位置和半径联合预测。

---

## 11. 后续需要继续精查的内容

后续如果要把论文写得更扎实，建议继续补充：

1. 每种目标材料的具体 dielectric constant 文献来源。
2. 每种材料在 TENG 器件中的实测输出电压、电流、转移电荷范围。
3. 压力-电压曲线的真实拟合参数，用于校准 `alpha_range_n`。
4. 湿度对 Paper、Leather、Nylon 的影响数据。
5. TENG 阵列串扰和坏点的真实实验报道。

---

## 12. 对当前项目的使用方式

第一版代码实现时，应直接采用第 9 节的配置。论文写作时，应把这些参数称为：

```text
literature-guided simulation parameters
```

不要写成：

```text
experimentally measured parameters
```

除非后期确实完成了单元 TENG 实测校准。
