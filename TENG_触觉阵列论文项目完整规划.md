# TENG 触觉阵列论文项目完整规划

> 项目方向：基于物理启发仿真与故障鲁棒多任务学习的 TENG 触觉阵列联合感知研究  
> 当前阶段：无完整实物阵列，先开展仿真、算法、鲁棒性和论文框架；后期可加入少量单元实测校准。  
> 文档用途：日后继续推进项目时，把本文档发给 Codex/ChatGPT，即可快速恢复项目背景、研究路线和下一步任务。

---

## 0. 一句话总结

本项目要做的是：

**构建一个物理启发的 TENG 触觉阵列仿真平台，生成 8×8 阵列的多通道时序电压信号，并训练一个故障鲁棒多任务神经网络，同时识别材料、压力、接触位置和接触半径。**

通俗理解：TENG 阵列像一块电子皮肤。每个单元被触摸后产生电压波形；不同材料、压力、位置会导致波形幅值、形状和空间分布不同；神经网络从 64 路信号中学习判断材料、压力、位置、接触半径，以及预测是否可靠。

---

## 1. 推荐论文题目

中文主标题：

**基于物理启发仿真与故障鲁棒多任务学习的 TENG 触觉阵列联合感知研究**

如果后期加入单元实测校准，可升级为：

**基于实测校准物理仿真与故障鲁棒多任务学习的 TENG 触觉阵列联合感知研究**

英文主标题：

**Physics-Informed Simulation and Fault-Robust Multi-Task Learning for Joint Perception in TENG Tactile Arrays**

加入实测校准后的版本：

**Measurement-Calibrated Physics-Informed Simulation and Fault-Robust Multi-Task Learning for Joint Perception in TENG Tactile Arrays**

---

## 2. 论文定位

### 2.1 不建议这样写

不要把论文写成：

- 首次提出 TENG 触觉材料识别。
- 首次提出 TENG 数字孪生。
- 首次将神经网络用于 TENG 信号识别。
- 提出一种真实可部署的 TENG 触觉系统。

这些说法风险高，因为前人已经做过 TENG 材料识别、TENG 阵列、TENG + 机器学习、TENG digital twin 或相关方向。

### 2.2 建议这样定位

本文应定位为：

**面向无大规模实物数据条件下的 TENG 触觉阵列算法预研，提出一个物理启发仿真、故障鲁棒训练和多任务联合识别的完整研究框架。**

英文表述：

> This work proposes a physics-informed simulation and fault-robust multi-task learning framework for joint material, force, and contact localization perception in TENG tactile arrays.

### 2.3 核心差异化

与已有实物 TENG 识别论文相比，本项目不主打器件创新，而主打：

1. 阵列级物理启发仿真器。
2. 多任务联合识别。
3. 噪声、串扰、漂移和通道失效下的鲁棒性评估。
4. 跨分布泛化测试。
5. 后期可加入少量单元实测校准，增强可信度。

---

## 3. 研究目标

### 3.1 总目标

构建完整的仿真到学习流程：

```text
TENG 单元物理模型
        ↓
8×8 阵列接触压力分布模型
        ↓
噪声、串扰、漂移、坏点等真实扰动模型
        ↓
大规模仿真数据集
        ↓
故障鲁棒多任务神经网络
        ↓
材料识别 + 压力估计 + 位置定位 + 半径估计 + 不确定性估计
```

### 3.2 具体任务

模型输入：

```text
8 × 8 × 200
```

含义：

- 8×8：64 个 TENG 单元。
- 200：每个单元一段 200 个采样点的电压波形。

模型输出：

| 输出 | 类型 | 指标 |
|---|---|---|
| 材料类别 | 分类 | Accuracy, Macro-F1 |
| 总压力 | 回归 | MAE, RMSE |
| 接触位置 x, y | 回归 | Euclidean error |
| 接触半径 | 回归 | MAE |
| 不确定性 | 置信度/方差 | uncertainty-error correlation |

---

## 4. 预期创新点

### 创新点 1：物理启发 TENG 阵列仿真框架

构建一个阵列级信号生成器，模拟：材料差异、压力非线性饱和、接触位置和接触半径、接触-分离动态波形、电荷衰减、通道灵敏度差异、基线漂移、电路噪声、相邻单元串扰和通道失效。

注意：不要说“首次提出 TENG 数字孪生”，可以说“面向 TENG 触觉阵列联合感知任务的物理启发仿真框架”。

### 创新点 2：多任务联合感知

一个网络同时完成：

```text
材料识别 + 压力估计 + 接触位置定位 + 接触半径估计
```

多任务学习的理论依据：材料、压力和位置都影响同一组时空电压信号；底层空间-时序特征可共享；多任务训练可以提高特征利用效率，并可能减少单任务过拟合。

### 创新点 3：故障鲁棒训练

训练和测试时考虑真实阵列问题：随机坏点、通道增益漂移、基线漂移、高斯噪声、1/f 噪声、相邻通道串扰、信号幅值扰动。

重点不是只在理想数据上报高准确率，而是证明模型在坏点和噪声下仍然可用。

### 创新点 4：跨分布泛化评估

设计比随机划分更严格的测试：未见过压力区间、未见过位置区域、未见过噪声水平、未见过接触半径、仿真参数偏移。

这个部分用于回应审稿人可能的质疑：模型是不是只学会了作者设定的仿真规则。

### 创新点 5：不确定性估计

让模型不只输出预测值，还输出可靠性：

```text
压力 = 8.3 N ± 0.5 N
位置 = (12.0 mm, 15.2 mm), uncertainty = 0.12
```

推荐第一版使用 Monte Carlo Dropout：训练时保留 dropout；测试时重复 forward 20 次；多次预测的均值作为结果；多次预测的方差作为不确定性。

---

## 5. 文献调研计划

### 5.1 需要调研的文献类别

至少整理 25-40 篇文献，分成以下类别：

| 类别 | 关注内容 |
|---|---|
| TENG 触觉传感器 | 材料识别、压力识别、纹理识别 |
| TENG 阵列 | 位置检测、压力分布、电子皮肤 |
| TENG + 机器学习 | SVM、CNN、LSTM、深度学习识别 |
| TENG 仿真/建模 | 电荷密度、输出电压、电荷衰减、接触分离模型 |
| 传感器数字孪生 | 仿真到学习、simulation-to-real |
| 鲁棒触觉识别 | 噪声、坏点、漂移、跨域泛化 |
| 不确定性估计 | MC Dropout、ensemble、calibration |

### 5.2 文献综述中要找出的 gap

建议写成：

1. 大多数 TENG 触觉识别工作依赖真实器件数据，而大规模阵列制备和采集成本较高。
2. 现有工作多关注单一任务，例如材料识别或压力识别，较少系统研究材料、压力和位置的联合感知。
3. 对通道失效、串扰、漂移、噪声和参数偏移等阵列实际问题的系统鲁棒性评估不足。
4. 缺少用于 TENG 触觉阵列算法预研的物理启发仿真和 benchmark 框架。

### 5.3 文献记录模板

```text
题目：
年份：
期刊/会议：
是否有实物：
TENG 类型：
是否阵列：
任务：材料/压力/位置/纹理/物体识别
算法：SVM/CNN/LSTM/Transformer/其他
数据规模：
主要结果：
局限性：
和本项目的关系：
```

---

## 6. 仿真模型设计

### 6.1 单元输出模型

推荐仿真公式：

```text
V_i(t) =
K_i · σ_m · S_m(F_i) · d(t, v) / ε_eff
· exp(-t / τ_m)
+ B_i(t)
+ η_i(t)
+ γ∑V_j(t)
```

其中：

| 符号 | 含义 | 建议范围 |
|---|---|---|
| `V_i(t)` | 第 i 个 TENG 单元电压 | 输出信号 |
| `K_i` | 通道灵敏度差异 | 0.8-1.2 |
| `σ_m` | 材料有效电荷密度 | 20-65 μC/m² |
| `S_m(F_i)` | 压力饱和函数 | 0-1 |
| `F_i` | 第 i 个单元受到的局部压力 | 由高斯分布决定 |
| `d(t,v)` | 接触-分离距离 | 0-5 mm |
| `ε_eff` | 等效介电常数 | 文献范围或归一化常数 |
| `τ_m` | 电荷衰减时间常数 | 0.2-2.0 s |
| `B_i(t)` | 基线漂移 | 低频缓慢变化 |
| `η_i(t)` | 噪声 | 10-50 dB |
| `γ∑V_j(t)` | 邻近通道串扰 | 0-15% |

### 6.2 压力饱和函数

推荐：

```text
S_m(F_i) = 1 - exp(-F_i / α_m)
```

含义：小压力时接触面积快速增加；大压力时接触趋于饱和；`α_m` 是材料相关饱和参数。

### 6.3 接触-分离距离函数

基础版本：

```text
d(t) = d_max · 0.5 · (1 - cos(2πft))
```

增强版本可加入速度、相位和接触保持阶段：

```text
d(t) = contact_separation_waveform(t, frequency, speed, dwell_time)
```

第一版先用正弦式距离变化，后期再加入非对称加载/卸载。

### 6.4 阵列压力分布

8×8 阵列坐标：

```text
x_i, y_i ∈ array grid
spacing = 5 mm
```

局部压力：

```text
w_i = exp(-distance_i^2 / (2r^2))
F_i = F_total · w_i / sum(w_i)
```

其中：

| 参数 | 含义 |
|---|---|
| `F_total` | 总接触压力 |
| `cx, cy` | 接触中心 |
| `r` | 接触半径/高斯展宽 |
| `x_i, y_i` | 第 i 个单元坐标 |

### 6.5 噪声和故障模型

至少包含：

1. 高斯白噪声：`η_white(t) ~ N(0, σ_noise)`。
2. 低频基线漂移：`B_i(t) = small_amplitude · low_frequency_wave`。
3. 通道增益漂移：`K_i = 1 + random_uniform(-drift, drift)`。
4. 坏点：`V_i(t) = fault_mask_i · V_i(t)`。
5. 串扰：`V_i_final(t) = V_i(t) + γ · mean(V_neighbors(t))`。

---

## 7. 仿真参数建议

### 7.1 基本参数

| 参数 | 建议值 |
|---|---|
| 阵列规模 | 8×8 |
| 通道数 | 64 |
| 采样点 | 200 |
| 采样频率 | 200 Hz |
| 单条信号时长 | 1 s |
| 接触频率 | 1-3 Hz |
| 最大分离距离 | 5 mm |
| 单元间距 | 5 mm |
| 总压力范围 | 1-20 N |
| 接触半径 | 3-12 mm |
| 噪声水平 | 10-50 dB |
| 串扰系数 | 0-15% |
| 通道增益差异 | ±20% |
| 坏点比例 | 0-40% |

### 7.2 材料参数初始表

第一版可以设置 6 类材料：

| 材料对 | `σ_m` 范围 μC/m² | `τ_m` 范围 s | `α_m` 范围 N | 备注 |
|---|---:|---:|---:|---|
| PTFE/Al | 40-60 | 0.8-1.8 | 6-10 | 输出高 |
| Nylon/Cu | 45-65 | 0.6-1.5 | 5-9 | 输出高 |
| PDMS/Al | 35-55 | 0.5-1.4 | 7-12 | 柔性 |
| Kapton/Al | 30-50 | 0.8-2.0 | 8-13 | 稳定 |
| Paper/Cu | 20-40 | 0.3-1.0 | 4-8 | 低成本 |
| Leather/Ag | 25-45 | 0.4-1.2 | 6-11 | 触觉场景 |

说明：纯仿真阶段把这些参数称为 literature-guided assumptions；后期若有实测，用实测波形拟合这些参数。

---

## 8. 数据集设计

### 8.1 数据规模

推荐：

```text
train: 10000 samples
val: 2000 samples
test_random: 2000 samples
```

额外生成鲁棒性和泛化测试集：

```text
test_noise
test_fault
test_drift
test_crosstalk
test_unseen_force
test_unseen_location
test_unseen_radius
test_param_shift
```

### 8.2 单条数据结构

建议保存为字典：

```python
sample = {
    "signal": array,          # shape: [8, 8, 200]
    "material_id": int,       # 0-5
    "force": float,           # N
    "position": [x, y],       # mm
    "radius": float,          # mm
    "noise_snr": float,       # dB
    "fault_mask": array,      # shape: [8, 8]
    "params": dict            # simulation parameters
}
```

### 8.3 项目文件结构

```text
teng-array-project/
├── simulation/
│   ├── teng_unit.py
│   ├── array_generator.py
│   ├── noise_models.py
│   ├── material_params.py
│   └── dataset_builder.py
├── models/
│   ├── multitask_net.py
│   ├── baselines.py
│   └── losses.py
├── experiments/
│   ├── train_main.py
│   ├── run_baselines.py
│   ├── run_ablation.py
│   ├── run_robustness.py
│   └── run_generalization.py
├── data/
├── figures/
├── checkpoints/
├── results/
├── paper/
└── README.md
```

---

## 9. 模型设计

### 9.1 输入

```text
Input shape: B × 8 × 8 × 200
```

### 9.2 空间分支

目的：学习阵列中哪个区域响应强，从而判断位置和接触半径。

可选输入：每个通道的峰值图 `8 × 8 × 1`，或每个通道的统计特征图 `8 × 8 × feature_dim`。

统计特征包括：peak、mean、std、energy、time_to_peak、signal area。

空间分支：

```text
Conv2D → BatchNorm → ReLU → Conv2D → Pooling → Flatten → spatial embedding
```

### 9.3 时序分支

目的：学习波形的动态特征，用于材料、压力和信号质量识别。

结构：

```text
Channel projection
→ 1D CNN
→ BiLSTM
→ Attention
→ temporal embedding
```

### 9.4 融合层

```text
fusion = concat(spatial_embedding, temporal_embedding)
shared = MLP(fusion)
```

### 9.5 输出头

| Head | 输出 | 损失 |
|---|---|---|
| material head | 6 类 logits | CrossEntropy |
| force head | 1 个值 | MSE/MAE |
| position head | x, y | MSE |
| radius head | 1 个值 | MSE |
| uncertainty | 方差或 MC Dropout | NLL 或预测方差 |

### 9.6 总损失

基础版：

```text
L = L_material + λ1 L_force + λ2 L_position + λ3 L_radius
```

建议初始权重：

```text
λ1 = 1.0
λ2 = 0.5
λ3 = 0.5
```

注意：压力、位置、半径最好归一化到 0-1，否则不同任务的损失量级会不平衡。

---

## 10. Baseline 设计

### 10.1 必须比较的方法

| 方法 | 目的 |
|---|---|
| SVM | 传统机器学习基线 |
| Random Forest | 非线性传统方法 |
| MLP | 简单神经网络 |
| 1D-CNN | 只看时序 |
| 2D-CNN | 只看空间 |
| CNN-LSTM | 无 attention |
| Ours | 完整模型 |

### 10.2 传统方法输入特征

对 64 个通道提取：peak、mean、std、energy、time_to_peak、area_under_curve。

总特征数：

```text
64 channels × 6 features = 384 features
```

也可以加空间特征：最大响应通道位置、加权中心坐标、峰值热力图的二阶矩、有效激活通道数。

---

## 11. 训练设置

### 11.1 深度模型训练参数

| 参数 | 值 |
|---|---|
| optimizer | AdamW |
| learning rate | 1e-3 |
| batch size | 32 或 64 |
| epochs | 80-120 |
| scheduler | ReduceLROnPlateau 或 CosineAnnealing |
| early stopping | 15 epochs |
| weight decay | 1e-4 |
| gradient clipping | 5.0 |
| dropout | 0.2-0.4 |

如果没有 GPU：先用 2000-5000 个样本测试代码；最终训练可用 Colab T4 GPU。

### 11.2 数据增强

训练时随机加入：噪声增强、幅值缩放、时间平移、通道 dropout、通道增益漂移、基线漂移、串扰扰动。

---

## 12. 实验设计

### 实验 1：仿真信号合理性

目的：证明仿真数据符合物理直觉。

展示：不同材料典型波形、不同压力波形变化、不同位置 8×8 峰值热力图、不同接触半径空间分布、不同噪声信号。

预期现象：材料参数越高，电压响应越强；压力越大，峰值越大并逐渐饱和；接触中心附近通道响应最大；接触半径越大，激活区域越宽；噪声越强，波形越不稳定。

### 实验 2：主结果

| Model | Acc | Macro-F1 | Force MAE | Force RMSE | Position Error | Radius MAE |
|---|---:|---:|---:|---:|---:|---:|
| SVM | | | | | | |
| Random Forest | | | | | | |
| MLP | | | | | | |
| 1D-CNN | | | | | | |
| 2D-CNN | | | | | | |
| CNN-LSTM | | | | | | |
| Ours | | | | | | |

### 实验 3：消融实验

| Variant | Acc | Force MAE | Position Error | Radius MAE |
|---|---:|---:|---:|---:|
| Full model | | | | |
| w/o spatial branch | | | | |
| w/o temporal branch | | | | |
| w/o attention | | | | |
| w/o multi-task | | | | |
| w/o robust training | | | | |
| w/o uncertainty | | | | |

预期：去掉空间分支，位置误差明显上升；去掉时序分支，材料和压力性能下降；去掉鲁棒训练，噪声和坏点测试性能下降；去掉多任务学习，整体略降或某些任务下降。

### 实验 4：噪声鲁棒性

测试：

```text
SNR = 50, 40, 30, 20, 10 dB
```

记录：Acc vs SNR、Force MAE vs SNR、Position error vs SNR、Uncertainty vs SNR。

### 实验 5：坏点鲁棒性

测试：

```text
Fault ratio = 0%, 5%, 10%, 20%, 30%, 40%
```

记录：材料识别准确率下降曲线、压力误差上升曲线、位置误差上升曲线、不确定性上升曲线。

### 实验 6：通道漂移鲁棒性

测试：

```text
Gain drift = ±0%, ±5%, ±10%, ±20%, ±30%
```

目的：模拟传感器老化和制造差异。

### 实验 7：串扰鲁棒性

测试：

```text
Crosstalk = 0%, 5%, 10%, 15%, 20%
```

目的：模拟多通道采集中的电气耦合。

### 实验 8：跨分布泛化

| 场景 | 训练 | 测试 |
|---|---|---|
| Random split | 随机分布 | 同分布随机测试 |
| Unseen force | 1-15 N | 15-20 N |
| Unseen location | 中心区域 | 边缘区域 |
| Unseen noise | 30-50 dB | 10-20 dB |
| Unseen radius | 3-8 mm | 8-12 mm |
| Parameter shift | 标准参数 | σ、τ、α 扰动 ±20% |

这是论文中非常重要的实验。

### 实验 9：不确定性分析

分析：预测误差与不确定性的相关性、噪声强度与不确定性的关系、坏点比例与不确定性的关系、高不确定性样本的典型案例可视化。

---

## 13. 结果图表清单

至少准备以下图：

1. Overall framework figure。
2. TENG 单元物理模型图。
3. 8×8 阵列接触压力分布图。
4. 材料典型波形对比。
5. 压力变化波形对比。
6. 接触位置热力图。
7. 网络结构图。
8. 材料识别混淆矩阵。
9. 压力预测散点图。
10. 位置预测误差热图。
11. 噪声鲁棒性曲线。
12. 坏点鲁棒性曲线。
13. 串扰/漂移鲁棒性曲线。
14. 不确定性与误差关系图。

---

## 14. 论文写作结构

### Abstract

包含：背景、方法、任务、实验、结论。结论要说该仿真框架可用于无大规模实物条件下的算法预研，不要说已经完成真实部署。

### 1. Introduction

建议逻辑：

1. TENG 触觉传感器在电子皮肤、机器人、可穿戴等领域有价值。
2. 阵列化 TENG 可以提供空间触觉信息。
3. 但大规模阵列制备、标定和采集成本高。
4. 现有工作多依赖实测数据，且多关注单任务。
5. 实际阵列存在噪声、串扰、通道漂移和坏点。
6. 本文提出物理启发仿真与鲁棒多任务学习框架。

贡献：

```text
1. Physics-informed TENG tactile array simulator.
2. Fault-robust multi-task learning architecture.
3. Systematic robustness and generalization benchmark.
4. Uncertainty-aware prediction under noisy and faulty conditions.
```

### 2. Related Work

分三节：

```text
2.1 TENG-based tactile sensing
2.2 Machine learning for tactile perception
2.3 Simulation, robustness, and uncertainty in sensor learning
```

### 3. Physics-Informed Simulation

写：单元模型、阵列空间模型、材料参数、噪声/串扰/漂移/坏点、数据生成流程。

### 4. Fault-Robust Multi-Task Learning

写：输入表示、空间分支、时序分支、attention、多任务输出、损失函数、鲁棒训练、不确定性估计。

### 5. Experiments

写：Dataset、Baselines、Metrics、Main results、Ablation、Robustness、Generalization、Uncertainty analysis。

### 6. Discussion

必须诚实写：当前主要基于仿真；没有完整 8×8 实物阵列验证；后续计划用少量单元实测校准参数；该框架适合作为 TENG 阵列算法设计和预验证平台。

### 7. Conclusion

总结即可，不要过度宣称真实部署性能。

---

## 15. 后期实物校准方案

如果后期能做最小实物，不需要做 8×8 阵列，只需做单元级 TENG。

| 项目 | 建议 |
|---|---|
| 单元数 | 1 个 |
| 材料 | 至少 3 种 |
| 压力等级 | 1, 5, 10, 15, 20 N |
| 每组重复 | 20-50 次 |
| 采集设备 | 示波器/数据采集卡/Arduino 模块 |
| 目标 | 拟合仿真参数，不是训练大模型 |

可校准参数：

```text
σ_m
τ_m
α_m
noise level
baseline drift
response time
```

实测加入论文后的表述：

> The simulator was calibrated using low-cost single-cell TENG measurements and then expanded to array-level signal generation.

这会明显增强论文可信度。

---

## 16. 时间规划

### 10 周纯仿真版本

| 周数 | 任务 | 产出 |
|---|---|---|
| 第 1 周 | 文献调研、确定研究定位 | 文献表、论文 gap |
| 第 2 周 | 编写单元仿真和阵列仿真 | `teng_unit.py`, `array_generator.py` |
| 第 3 周 | 生成数据集和可视化 | 数据集、波形图、热力图 |
| 第 4 周 | 实现主模型并跑通训练 | 初版模型结果 |
| 第 5 周 | 实现 baseline | SVM, RF, MLP, 1D-CNN, 2D-CNN |
| 第 6 周 | 消融实验 | ablation 表格 |
| 第 7 周 | 噪声、坏点、漂移、串扰鲁棒性 | 鲁棒性曲线 |
| 第 8 周 | 跨分布泛化实验 | generalization 表格 |
| 第 9 周 | 不确定性分析和图表整理 | uncertainty 图 |
| 第 10 周 | 写论文初稿 | manuscript 初稿 |

### 加实物后的额外 2-4 周

| 周数 | 任务 |
|---|---|
| 额外第 1 周 | 制作单元 TENG，搭建采集流程 |
| 额外第 2 周 | 采集不同材料和压力波形 |
| 额外第 3 周 | 拟合参数，更新仿真器 |
| 额外第 4 周 | 补实测-仿真对比图，修改论文 |

---

## 17. 最低完成标准

如果时间有限，最低必须完成：

```text
1. 物理启发仿真器
2. 8×8×200 数据集
3. 多任务模型
4. baseline 对比
5. 消融实验
6. 噪声鲁棒性
7. 坏点鲁棒性
8. 跨压力/跨位置泛化
9. 主要图表
10. 论文初稿
```

这些完成后，作为本科生论文项目已经比较完整。

---

## 18. 投稿目标判断

| 目标 | 可行性 | 备注 |
|---|---:|---|
| 本科毕业论文 | 很稳 | 工作量足够 |
| 校级/省级创新项目论文 | 很稳 | 系统完整 |
| 中文普通期刊/会议 | 有机会 | 注意写作规范 |
| Sensors / Applied Sciences | 有机会 | 需要实验完整和英文规范 |
| IEEE Access | 有机会但有难度 | 需要对比充分 |
| IEEE Sensors Journal | 可以尝试但不稳 | 无完整实物是短板 |
| Nano Energy / Advanced Functional Materials | 不建议 | 器件创新和实测不足 |

---

## 19. 风险与应对

### 风险 1：审稿人认为仿真数据不可信

应对：明确称为 physics-informed simulation；参数来自文献范围；加参数敏感性分析；加跨分布测试；后期尽量加单元实测校准。

### 风险 2：模型只是学会了仿真公式

应对：加噪声、串扰、漂移、坏点；加未见过压力/位置/噪声测试；加参数偏移测试；加传统 baseline 和消融实验。

### 风险 3：创新性不足

应对：不主打“材料识别”；主打“故障鲁棒多任务联合感知”；主打“阵列级仿真 benchmark”；加不确定性估计。

### 风险 4：实验量太大

应对：先完成最低版：

```text
仿真器 + 主模型 + baseline + 消融 + 噪声/坏点 + 泛化
```

再追加：

```text
不确定性 + 实测校准 + 更多参数敏感性
```

---

## 20. 日后继续工作时给 Codex 的说明

以后如果要继续这个项目，可以直接告诉 Codex：

```text
请阅读 D:\URTP\TENG_触觉阵列论文项目完整规划.md。
如果该路径不可访问，请阅读 D:\temp\TENG_触觉阵列论文项目完整规划.md。
我们要继续做这个 TENG 触觉阵列论文项目。
当前要完成第 X 阶段：……
请按照文档里的研究路线继续推进。
```

每次推进后，在下面的日志里记录：

```text
日期：
完成内容：
新增文件：
实验结果：
遇到问题：
下一步：
```

---

## 21. 项目进度日志

### 2026-05-16

完成内容：

- 明确项目方向：TENG 触觉阵列仿真 + 多任务学习 + 故障鲁棒性。
- 明确当前阶段可以在无实物条件下完全开展仿真和算法实验。
- 制定完整论文级规划。

下一步建议：

1. 建立项目代码目录。
2. 实现 TENG 单元仿真器。
3. 实现 8×8 阵列压力分布和信号生成。
4. 先生成 100 条样本并画波形和热力图，确认仿真逻辑正确。

---

## 22. 下一步最小执行清单

建议马上做：

```text
Step 1: 创建项目目录 teng-array-project
Step 2: 写 simulation/material_params.py
Step 3: 写 simulation/teng_unit.py
Step 4: 写 simulation/array_generator.py
Step 5: 生成 100 条样本
Step 6: 画 3 类图：
        - 不同材料波形
        - 不同压力波形
        - 不同位置 8×8 热力图
Step 7: 检查物理趋势是否合理
```

如果这些图符合直觉，再进入大规模数据集和模型训练。
