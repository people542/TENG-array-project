# TENG 触觉阵列各实验细节完整介绍

> 基于文件：`TENG_触觉阵列论文项目完整规划.md`  
> 项目主题：基于物理启发仿真与故障鲁棒多任务学习的 TENG 触觉阵列联合感知研究  
> 本文用途：系统说明每个实验的目的、变量、数据设置、执行流程、评价指标、预期结果、图表呈现方式和论文写法。

---

## 1. 实验总体设计

本项目的实验目标不是单纯证明某个模型在随机划分数据上准确率高，而是完整验证一个 TENG 触觉阵列仿真与学习框架是否具备以下能力：

1. 能生成符合物理直觉的阵列级 TENG 时空电压信号。
2. 能同时识别材料、估计压力、定位接触位置、估计接触半径。
3. 能在噪声、坏点、通道漂移和串扰等真实阵列问题下保持性能。
4. 能在未见过的压力、位置、噪声、接触半径和仿真参数偏移条件下进行泛化。
5. 能通过不确定性估计反映预测可靠性。

整体实验流程如下：

```text
物理启发仿真器
    ↓
生成标准训练集、验证集、随机测试集
    ↓
训练主模型和 baseline 模型
    ↓
主结果对比
    ↓
消融实验
    ↓
噪声、坏点、漂移、串扰鲁棒性实验
    ↓
跨分布泛化实验
    ↓
不确定性分析
    ↓
整理论文图表和讨论
```

实验输入统一为：

```text
8 × 8 × 200
```

其中 8×8 表示 64 个 TENG 单元，200 表示每个单元采集 200 个时间点的电压波形。

模型主要输出包括：

| 输出任务 | 类型 | 含义 |
|---|---|---|
| 材料类别 | 分类 | 判断接触材料或材料对类别 |
| 总压力 | 回归 | 估计总接触力，单位 N |
| 接触位置 | 回归 | 估计接触中心坐标 x, y |
| 接触半径 | 回归 | 估计接触区域半径或高斯展宽 |
| 不确定性 | 可靠性估计 | 判断预测是否可信 |

---

## 2. 数据集与通用实验设置

### 2.1 数据集构成

基础数据集建议包含：

| 数据集 | 数量 | 用途 |
|---|---:|---|
| Train | 10000 | 训练模型 |
| Validation | 2000 | 调参、早停、选择最佳 epoch |
| Random Test | 2000 | 同分布随机测试 |

额外测试集用于鲁棒性和泛化分析：

| 测试集 | 用途 |
|---|---|
| Test Noise | 测试不同信噪比下的性能 |
| Test Fault | 测试通道坏点比例增加时的性能 |
| Test Drift | 测试通道增益漂移影响 |
| Test Crosstalk | 测试通道串扰影响 |
| Test Unseen Force | 测试未见过压力区间 |
| Test Unseen Location | 测试未见过接触位置区域 |
| Test Unseen Radius | 测试未见过接触半径 |
| Test Parameter Shift | 测试材料参数和模型参数偏移 |

每条样本保存以下信息：

```python
sample = {
    "signal": array,          # [8, 8, 200]
    "material_id": int,       # 0-5
    "force": float,           # N
    "position": [x, y],       # mm
    "radius": float,          # mm
    "noise_snr": float,       # dB
    "fault_mask": array,      # [8, 8]
    "params": dict            # 仿真参数
}
```

### 2.2 通用仿真参数

| 参数 | 推荐设置 |
|---|---|
| 阵列大小 | 8×8 |
| 通道数量 | 64 |
| 采样点数 | 200 |
| 采样频率 | 200 Hz |
| 单条样本时长 | 1 s |
| 单元间距 | 5 mm |
| 总压力范围 | 1-20 N |
| 接触半径范围 | 3-12 mm |
| 材料类别数 | 6 |
| 噪声范围 | 10-50 dB |
| 串扰系数 | 0-15% |
| 坏点比例 | 0-40% |
| 通道增益差异 | ±20% |

### 2.3 通用评价指标

材料识别使用：

| 指标 | 含义 |
|---|---|
| Accuracy | 总体分类准确率 |
| Macro-F1 | 各类别 F1 的平均值，适合检查类别均衡性能 |
| Confusion Matrix | 查看哪些材料容易混淆 |

压力估计使用：

| 指标 | 含义 |
|---|---|
| MAE | 平均绝对误差 |
| RMSE | 均方根误差 |
| R² | 预测值与真实值拟合程度 |

位置定位使用：

```text
Position Error = sqrt((x_pred - x_true)^2 + (y_pred - y_true)^2)
```

接触半径估计使用：

| 指标 | 含义 |
|---|---|
| Radius MAE | 半径平均绝对误差 |
| Radius RMSE | 半径均方根误差 |

不确定性分析使用：

| 指标 | 含义 |
|---|---|
| Error-Uncertainty Correlation | 预测误差和不确定性的相关性 |
| Calibration Curve | 置信度是否和实际误差匹配 |
| Uncertainty vs Noise/Fault | 扰动增强时不确定性是否上升 |

---

## 3. 实验 1：仿真信号合理性验证

### 3.1 实验目的

该实验用于证明仿真器生成的数据不是任意随机信号，而是符合 TENG 触觉阵列的基本物理直觉。由于当前阶段没有完整 8×8 实物阵列，仿真合理性验证是后续所有学习实验的基础。

本实验需要回答以下问题：

1. 不同材料是否产生不同幅值、衰减和波形特征？
2. 压力增大时，电压峰值是否增大并逐渐饱和？
3. 接触位置变化时，阵列峰值热力图是否随接触中心移动？
4. 接触半径增大时，激活区域是否变宽？
5. 噪声、漂移、串扰和坏点是否能产生接近真实采集问题的扰动形态？

### 3.2 实验变量

材料变量：

| 材料 | 主要变化 |
|---|---|
| PTFE/Al | 较高输出 |
| Nylon/Cu | 较高输出 |
| PDMS/Al | 柔性响应明显 |
| Kapton/Al | 响应稳定 |
| Paper/Cu | 输出较低 |
| Leather/Ag | 中等输出 |

压力变量：

```text
F_total = 1, 5, 10, 15, 20 N
```

位置变量：

```text
center, corner, edge, random interior positions
```

半径变量：

```text
r = 3, 6, 9, 12 mm
```

噪声变量：

```text
SNR = 50, 40, 30, 20, 10 dB
```

### 3.3 执行流程

1. 固定压力、位置和半径，只改变材料，生成 6 类材料的典型波形。
2. 固定材料、位置和半径，只改变压力，观察峰值和面积变化。
3. 固定材料、压力和半径，只改变接触中心，生成 8×8 峰值热力图。
4. 固定材料、压力和位置，只改变半径，观察激活区域扩散程度。
5. 固定一组基础样本，分别加入噪声、漂移、串扰和坏点，观察信号退化。

### 3.4 推荐图表

| 图编号 | 图名 | 内容 |
|---|---|---|
| Fig. 1a | 不同材料典型波形 | 6 种材料在同一压力和位置下的电压波形 |
| Fig. 1b | 不同压力波形 | 1-20 N 下峰值逐渐增大并趋于饱和 |
| Fig. 1c | 接触位置热力图 | 接触中心移动时，峰值区域同步移动 |
| Fig. 1d | 接触半径热力图 | 半径越大，响应区域越宽 |
| Fig. 1e | 扰动信号示例 | 噪声、漂移、坏点、串扰的可视化 |

### 3.5 预期结果

合理的仿真结果应表现为：

1. 不同材料的峰值、衰减速度和波形面积存在差异。
2. 压力从 1 N 增加到 20 N 时，峰值明显增加，但增幅逐渐减小。
3. 接触中心附近的阵列单元响应最大，远离中心的单元响应减弱。
4. 接触半径越大，更多相邻通道被激活。
5. 坏点会导致局部通道信号接近 0，串扰会导致邻近通道出现额外响应。

### 3.6 论文写法

论文中可以写：

```text
Before training the learning models, we first validated whether the generated signals followed expected physical trends. The simulated voltage responses showed material-dependent amplitudes and decay patterns, force-dependent nonlinear saturation, spatially localized activation around the contact center, and broader activation regions under larger contact radii.
```

中文表达可以写：

```text
在训练识别模型之前，本文首先对仿真信号的物理合理性进行验证。结果表明，生成信号能够体现材料相关的幅值与衰减差异、压力增加导致的非线性饱和、接触中心附近的局部空间响应，以及接触半径增大带来的激活区域扩展。
```

---

## 4. 实验 2：主结果对比实验

### 4.1 实验目的

主结果实验用于验证本文提出的故障鲁棒多任务模型是否优于传统机器学习方法和常见深度学习结构。

该实验需要回答：

1. 多任务模型能否同时完成材料、压力、位置和半径预测？
2. 融合空间分支和时序分支的模型是否优于单一分支模型？
3. 与 SVM、Random Forest、MLP、1D-CNN、2D-CNN、CNN-LSTM 相比，本文模型是否有整体优势？

### 4.2 对比方法

| 方法 | 输入特征 | 作用 |
|---|---|---|
| SVM | 手工统计特征 | 传统分类基线 |
| Random Forest | 手工统计特征 | 非线性传统模型 |
| MLP | 手工统计特征或展平信号 | 简单神经网络基线 |
| 1D-CNN | 多通道时序信号 | 只建模时间特征 |
| 2D-CNN | 峰值图或统计特征图 | 只建模空间特征 |
| CNN-LSTM | 时序信号 | 建模局部时序和长期依赖 |
| Ours | 8×8×200 信号 | 空间-时序融合多任务模型 |

传统方法使用的手工特征建议包括：

```text
peak, mean, std, energy, time_to_peak, area_under_curve
```

对于 64 个通道，总特征数为：

```text
64 × 6 = 384
```

也可以加入空间统计特征：

```text
最大响应通道位置
加权中心坐标
峰值热力图二阶矩
有效激活通道数
```

### 4.3 数据设置

使用标准随机划分数据：

```text
train: 10000
val: 2000
test_random: 2000
```

训练集、验证集和测试集来自相同参数分布，但样本不重复。

### 4.4 训练设置

深度模型建议统一训练配置：

| 参数 | 设置 |
|---|---|
| Optimizer | AdamW |
| Learning Rate | 1e-3 |
| Batch Size | 32 或 64 |
| Epochs | 80-120 |
| Early Stopping | 15 epochs |
| Weight Decay | 1e-4 |
| Dropout | 0.2-0.4 |
| Gradient Clipping | 5.0 |

为了保证公平比较，所有深度模型使用相同训练集、验证集、测试集和早停策略。

### 4.5 评价指标

主表格建议包含：

| Model | Acc | Macro-F1 | Force MAE | Force RMSE | Position Error | Radius MAE |
|---|---:|---:|---:|---:|---:|---:|
| SVM | | | | | | |
| Random Forest | | | | | | |
| MLP | | | | | | |
| 1D-CNN | | | | | | |
| 2D-CNN | | | | | | |
| CNN-LSTM | | | | | | |
| Ours | | | | | | |

### 4.6 预期结果

预期现象如下：

1. SVM 和 Random Forest 在材料分类上可能有一定效果，但对压力、位置和半径联合估计能力有限。
2. MLP 能学习非线性关系，但难以充分利用空间结构和时序结构。
3. 1D-CNN 对材料和压力可能较好，但位置定位能力不足。
4. 2D-CNN 对位置和半径可能较好，但材料波形动态识别能力不足。
5. CNN-LSTM 比 1D-CNN 更强，但缺少显式空间分支时，定位和半径估计仍可能不如本文模型。
6. 本文模型由于融合空间和时序特征，应在综合指标上表现最好。

### 4.7 论文写法

主结果部分应强调综合性能，而不是只强调一个最高准确率。推荐写法：

```text
Compared with conventional machine learning models and single-branch neural networks, the proposed model achieved better balanced performance across classification and regression tasks. This indicates that spatial contact distribution and temporal waveform dynamics provide complementary information for joint tactile perception.
```

---

## 5. 实验 3：消融实验

### 5.1 实验目的

消融实验用于证明模型中每个模块确实有贡献，而不是简单堆叠结构。该实验是论文说服力的重要来源。

主要验证：

1. 空间分支是否有助于位置和半径估计？
2. 时序分支是否有助于材料和压力识别？
3. Attention 是否提升关键时间段和关键通道的特征提取？
4. 多任务学习是否优于单任务独立训练？
5. 鲁棒训练是否提升扰动条件下性能？
6. 不确定性模块是否能反映预测可靠性？

### 5.2 消融版本

| Variant | 改动 |
|---|---|
| Full Model | 完整模型 |
| w/o spatial branch | 去掉空间分支，只使用时序分支 |
| w/o temporal branch | 去掉时序分支，只使用空间统计图 |
| w/o attention | 去掉注意力层，直接池化时序特征 |
| w/o multi-task | 每个任务单独训练模型 |
| w/o robust training | 训练时不加入噪声、坏点、漂移和串扰增强 |
| w/o uncertainty | 去掉 MC Dropout 或不确定性估计 |

### 5.3 数据设置

基础消融使用 random test。  
鲁棒训练相关消融还需要在 noise test 和 fault test 上对比。

### 5.4 评价表格

推荐主消融表：

| Variant | Acc | Macro-F1 | Force MAE | Position Error | Radius MAE |
|---|---:|---:|---:|---:|---:|
| Full Model | | | | | |
| w/o spatial branch | | | | | |
| w/o temporal branch | | | | | |
| w/o attention | | | | | |
| w/o multi-task | | | | | |
| w/o robust training | | | | | |

鲁棒训练消融表：

| Variant | Noise Acc | Noise Force MAE | Fault Acc | Fault Position Error |
|---|---:|---:|---:|---:|
| Full Model | | | | |
| w/o robust training | | | | |

### 5.5 预期结果

预期表现：

1. 去掉空间分支后，位置误差和半径误差明显上升。
2. 去掉时序分支后，材料识别准确率和压力估计性能下降。
3. 去掉 attention 后，整体性能小幅下降，尤其在噪声样本上更明显。
4. 去掉多任务学习后，部分任务可能接近完整模型，但综合性能下降。
5. 去掉鲁棒训练后，在干净测试集上变化可能不大，但在噪声、坏点、漂移和串扰测试集上明显变差。

### 5.6 论文写法

可以写：

```text
The ablation study confirms the complementary roles of the spatial and temporal branches. Removing the spatial branch mainly degraded localization and radius estimation, while removing the temporal branch caused larger drops in material recognition and force estimation. These results support the design motivation of using spatial-temporal feature fusion for TENG tactile array perception.
```

---

## 6. 实验 4：噪声鲁棒性实验

### 6.1 实验目的

真实 TENG 信号容易受到采集电路、电磁环境、接触不稳定和机械振动影响。噪声鲁棒性实验用于验证模型在不同信噪比下是否仍能进行可靠识别。

本实验需要回答：

1. 信噪比降低时，各任务性能如何下降？
2. 本文模型是否比 baseline 更抗噪？
3. 不确定性是否会随着噪声增强而增加？

### 6.2 测试条件

设置不同 SNR：

```text
50 dB, 40 dB, 30 dB, 20 dB, 10 dB
```

其中：

| SNR | 含义 |
|---|---|
| 50 dB | 接近干净信号 |
| 40 dB | 轻微噪声 |
| 30 dB | 中等噪声 |
| 20 dB | 明显噪声 |
| 10 dB | 严重噪声 |

### 6.3 执行流程

1. 使用同一组基础测试样本。
2. 分别加入不同强度的高斯白噪声。
3. 保持材料、压力、位置和半径标签不变。
4. 对每个 SNR 测试所有模型。
5. 记录分类准确率、压力误差、位置误差、半径误差和不确定性。

### 6.4 推荐图表

| 图名 | 横轴 | 纵轴 |
|---|---|---|
| Acc vs SNR | SNR | Accuracy |
| Force MAE vs SNR | SNR | Force MAE |
| Position Error vs SNR | SNR | Position Error |
| Uncertainty vs SNR | SNR | Mean Uncertainty |

### 6.5 预期结果

随着 SNR 从 50 dB 降至 10 dB：

1. 材料识别准确率逐渐下降。
2. 压力 MAE 和位置误差逐渐上升。
3. 未做鲁棒训练的模型下降更明显。
4. 本文模型由于训练时加入噪声增强，性能下降更平缓。
5. 不确定性应随噪声增强而升高。

### 6.6 论文写法

可以写：

```text
As the SNR decreased, all models showed performance degradation. However, the proposed fault-robust model maintained a slower degradation trend, indicating better tolerance to measurement noise. Meanwhile, the estimated uncertainty increased under low-SNR conditions, suggesting that the model could partially reflect reduced prediction reliability.
```

---

## 7. 实验 5：坏点鲁棒性实验

### 7.1 实验目的

阵列传感器在实际使用中可能出现局部单元损坏、电极连接失效、采集通道故障或长期使用导致的响应消失。坏点鲁棒性实验用于评估模型在部分通道失效时的可靠性。

### 7.2 坏点设置

测试坏点比例：

```text
0%, 5%, 10%, 20%, 30%, 40%
```

坏点处理方式：

```text
V_i(t) = 0
```

或者更接近真实情况：

```text
V_i(t) = low_amplitude_noise
```

坏点类型可以分为：

| 类型 | 含义 |
|---|---|
| Random Fault | 随机通道失效 |
| Block Fault | 连续区域失效 |
| Edge Fault | 边缘通道失效 |
| High-response Fault | 恰好接触中心附近通道失效 |

第一版建议先做 Random Fault；后续可加入 Block Fault 作为更严格测试。

### 7.3 执行流程

1. 从 random test 复制一组测试样本。
2. 对每条样本随机选择一定比例通道作为坏点。
3. 将坏点通道波形置零或替换为低幅值噪声。
4. 分别测试不同坏点比例下的模型性能。
5. 比较有无 channel dropout 训练增强的模型。

### 7.4 推荐图表

| 图名 | 横轴 | 纵轴 |
|---|---|---|
| Acc vs Fault Ratio | 坏点比例 | Accuracy |
| Force MAE vs Fault Ratio | 坏点比例 | Force MAE |
| Position Error vs Fault Ratio | 坏点比例 | Position Error |
| Uncertainty vs Fault Ratio | 坏点比例 | Mean Uncertainty |

还可以展示一组坏点热力图：

```text
原始峰值热力图
坏点 mask
坏点后的峰值热力图
预测位置误差
```

### 7.5 预期结果

预期坏点比例越高，模型性能越差。但鲁棒训练模型应表现为：

1. 0-10% 坏点时性能下降较小。
2. 20-30% 坏点时仍保持可用。
3. 40% 坏点时性能明显下降，但不确定性显著升高。
4. 如果坏点集中在接触中心附近，位置误差会明显上升。

### 7.6 论文写法

可以写：

```text
The fault robustness experiment simulates channel failures in tactile arrays. The proposed model maintained stable performance under moderate random channel failures, while the model without robust training degraded rapidly. This suggests that channel dropout augmentation improves the model's ability to infer tactile information from incomplete spatial observations.
```

---

## 8. 实验 6：通道漂移鲁棒性实验

### 8.1 实验目的

TENG 阵列中不同单元可能因制造差异、材料老化、环境湿度、表面污染或电路增益变化而产生响应强度漂移。通道漂移实验用于模拟这种长期使用中的非理想问题。

### 8.2 漂移模型

对每个通道加入随机增益：

```text
V_i'(t) = g_i · V_i(t)
```

其中：

```text
g_i ~ Uniform(1 - d, 1 + d)
```

漂移强度：

```text
d = 0%, 5%, 10%, 20%, 30%
```

### 8.3 执行流程

1. 固定测试样本。
2. 为每个通道随机生成增益系数。
3. 对整条波形乘以通道增益。
4. 测试不同漂移强度下的模型性能。
5. 比较是否使用增益漂移增强训练。

### 8.4 评价指标和图表

| 图名 | 横轴 | 纵轴 |
|---|---|---|
| Acc vs Gain Drift | 漂移强度 | Accuracy |
| Force MAE vs Gain Drift | 漂移强度 | Force MAE |
| Position Error vs Gain Drift | 漂移强度 | Position Error |

### 8.5 预期结果

漂移会影响模型对幅值的判断，因此压力估计最容易受到影响。位置估计也可能受到影响，因为某些通道被放大或缩小后，空间峰值中心会偏移。材料识别可能受到中等影响，因为材料类别不仅依赖幅值，也依赖波形衰减和动态特征。

### 8.6 论文写法

可以写：

```text
Gain drift mainly affected force estimation because force-related information is strongly amplitude-dependent. The proposed model showed improved tolerance to moderate gain variations after drift augmentation, indicating its potential for long-term array operation where channel sensitivities may change over time.
```

---

## 9. 实验 7：串扰鲁棒性实验

### 9.1 实验目的

在多通道阵列采集中，相邻通道可能由于电气耦合、结构耦合或信号采集线路影响产生串扰。串扰会使未直接受力的通道出现虚假响应，影响位置和半径判断。

### 9.2 串扰模型

推荐使用邻域均值串扰：

```text
V_i'(t) = V_i(t) + γ · mean(V_neighbors(t))
```

串扰强度：

```text
γ = 0%, 5%, 10%, 15%, 20%
```

其中 `V_neighbors(t)` 表示上、下、左、右或 8 邻域通道的信号。

### 9.3 执行流程

1. 生成无串扰基础测试样本。
2. 按不同 γ 添加邻域串扰。
3. 测试所有模型在不同串扰强度下的性能。
4. 重点观察位置误差和半径误差。

### 9.4 推荐图表

| 图名 | 横轴 | 纵轴 |
|---|---|---|
| Position Error vs Crosstalk | 串扰强度 | Position Error |
| Radius MAE vs Crosstalk | 串扰强度 | Radius MAE |
| Acc vs Crosstalk | 串扰强度 | Accuracy |

还可以展示：

```text
无串扰峰值热力图
5% 串扰峰值热力图
15% 串扰峰值热力图
20% 串扰峰值热力图
```

### 9.5 预期结果

串扰会导致响应区域扩散，因此：

1. 接触半径估计容易偏大。
2. 位置估计在轻微串扰下影响较小，但强串扰下误差增大。
3. 材料识别受影响相对较小，除非串扰明显改变整体波形。
4. 鲁棒训练模型应比未增强模型更稳定。

### 9.6 论文写法

可以写：

```text
Crosstalk primarily influenced spatial perception tasks by broadening the apparent activation region. The proposed model retained lower localization and radius estimation errors under moderate crosstalk, showing that crosstalk augmentation helped the model distinguish true contact patterns from coupled neighboring responses.
```

---

## 10. 实验 8：跨分布泛化实验

### 10.1 实验目的

跨分布泛化是本项目最重要的实验之一。随机测试只能说明模型在同分布样本上有效，但不能说明模型真正理解了触觉信号规律。跨分布测试用于检验模型在训练时未见过的条件下是否仍能工作。

该实验回应一个关键质疑：

```text
模型是否只是记住了仿真器生成的数据分布？
```

### 10.2 泛化场景

| 场景 | 训练分布 | 测试分布 | 目的 |
|---|---|---|---|
| Random Split | 全范围随机 | 全范围随机 | 基础性能 |
| Unseen Force | 1-15 N | 15-20 N | 高压力外推 |
| Unseen Location | 中心区域 | 边缘区域 | 空间外推 |
| Unseen Noise | 30-50 dB | 10-20 dB | 噪声外推 |
| Unseen Radius | 3-8 mm | 8-12 mm | 接触尺度外推 |
| Parameter Shift | 标准参数 | σ、τ、α 偏移 ±20% | 仿真参数偏移 |

### 10.3 各场景说明

#### 10.3.1 未见过压力区间

训练：

```text
F_total = 1-15 N
```

测试：

```text
F_total = 15-20 N
```

目的：检查模型是否能外推到更高压力。  
难点：TENG 压力响应存在饱和，超过训练区间后模型可能低估压力。

#### 10.3.2 未见过位置区域

训练：

```text
接触中心位于阵列中间区域
```

测试：

```text
接触中心位于边缘或角落区域
```

目的：检查模型是否能处理边缘效应。  
难点：边缘区域响应不完整，高斯分布被阵列边界截断，位置估计更困难。

#### 10.3.3 未见过噪声水平

训练：

```text
SNR = 30-50 dB
```

测试：

```text
SNR = 10-20 dB
```

目的：检查模型面对更强噪声时的鲁棒性。

#### 10.3.4 未见过接触半径

训练：

```text
r = 3-8 mm
```

测试：

```text
r = 8-12 mm
```

目的：检查模型能否推广到更大接触面积。

#### 10.3.5 参数偏移

训练使用标准材料参数范围。  
测试时对关键参数加入偏移：

```text
σ_m shift: ±20%
τ_m shift: ±20%
α_m shift: ±20%
```

目的：检查模型是否对仿真参数设定过度敏感。

### 10.4 推荐表格

| Test Scenario | Acc | Macro-F1 | Force MAE | Position Error | Radius MAE |
|---|---:|---:|---:|---:|---:|
| Random Split | | | | | |
| Unseen Force | | | | | |
| Unseen Location | | | | | |
| Unseen Noise | | | | | |
| Unseen Radius | | | | | |
| Parameter Shift | | | | | |

### 10.5 预期结果

跨分布测试通常会比随机测试更差，这是正常且合理的。论文中不应回避这一点，而应说明哪些场景下降明显、哪些场景仍保持可用。

预期：

1. Unseen Force 中压力 MAE 增加明显。
2. Unseen Location 中位置误差增加明显，尤其边缘和角落。
3. Unseen Noise 中所有指标下降，不确定性上升。
4. Unseen Radius 中半径 MAE 增加，位置可能也受影响。
5. Parameter Shift 中材料识别和压力估计都可能下降。

### 10.6 论文写法

可以写：

```text
Although performance decreased under distribution shifts, the proposed model retained reasonable prediction ability in several unseen scenarios. The largest degradation occurred in edge-location and high-noise tests, indicating that boundary effects and severe measurement noise remain challenging for simulation-trained tactile models.
```

中文讨论可以写：

```text
跨分布实验结果表明，模型在随机测试集上的高性能并不完全等同于真实泛化能力。边缘接触、强噪声和参数偏移会显著增加预测难度。因此，本文将跨分布测试作为框架有效性的重要验证，而不是只报告同分布随机划分结果。
```

---

## 11. 实验 9：不确定性分析实验

### 11.1 实验目的

在真实触觉系统中，模型不仅要给出预测结果，还应能判断预测是否可靠。不确定性分析用于验证模型在困难样本、强噪声样本、坏点样本和跨分布样本上是否给出更高不确定性。

### 11.2 方法设置

第一版推荐使用 Monte Carlo Dropout：

1. 训练时正常使用 dropout。
2. 测试时保持 dropout 开启。
3. 对同一样本重复前向传播 20 次。
4. 多次预测的均值作为最终预测。
5. 多次预测的方差作为不确定性。

公式表达：

```text
ŷ = mean(ŷ_1, ŷ_2, ..., ŷ_T)
u = var(ŷ_1, ŷ_2, ..., ŷ_T)
```

其中 `T = 20`。

### 11.3 分析内容

#### 11.3.1 误差与不确定性相关性

计算每条样本的预测误差和不确定性，分析二者是否正相关：

```text
高不确定性样本是否更容易预测错误？
```

可以使用 Pearson 或 Spearman 相关系数。

#### 11.3.2 噪声与不确定性关系

测试不同 SNR 下的平均不确定性：

```text
SNR 越低，不确定性是否越高？
```

#### 11.3.3 坏点与不确定性关系

测试不同坏点比例下的平均不确定性：

```text
坏点越多，不确定性是否越高？
```

#### 11.3.4 高不确定性案例分析

选取不确定性最高的若干样本，展示：

1. 输入峰值热力图。
2. 波形示例。
3. 真实标签。
4. 预测结果。
5. 预测误差。
6. 不确定性数值。

### 11.4 推荐图表

| 图名 | 内容 |
|---|---|
| Error vs Uncertainty Scatter | 每个点是一条测试样本 |
| Mean Uncertainty vs SNR | 噪声越强，不确定性越高 |
| Mean Uncertainty vs Fault Ratio | 坏点越多，不确定性越高 |
| High-Uncertainty Case Study | 高不确定性样本可视化 |

### 11.5 预期结果

合理结果应为：

1. 误差和不确定性存在正相关。
2. 低 SNR 样本平均不确定性更高。
3. 高坏点比例样本平均不确定性更高。
4. 边缘位置、强噪声、接触中心附近坏点样本更容易出现高不确定性。

### 11.6 论文写法

可以写：

```text
The uncertainty analysis showed a positive correlation between predictive uncertainty and estimation error. Samples with severe noise, high fault ratios, or boundary contacts tended to produce larger uncertainty values, indicating that MC Dropout can provide a useful reliability indicator for simulation-trained TENG tactile perception models.
```

---

## 12. 补充实验：参数敏感性分析

### 12.1 实验目的

参数敏感性分析用于评估仿真器关键参数对模型性能和信号形态的影响。该实验可以增强仿真研究的可信度，回应“参数是否人为设定导致结果”的质疑。

### 12.2 分析参数

| 参数 | 含义 | 偏移范围 |
|---|---|---|
| σ_m | 材料有效电荷密度 | ±10%, ±20%, ±30% |
| τ_m | 电荷衰减时间常数 | ±10%, ±20%, ±30% |
| α_m | 压力饱和参数 | ±10%, ±20%, ±30% |
| ε_eff | 等效介电常数 | ±10%, ±20% |
| K_i | 通道灵敏度 | ±10%, ±20%, ±30% |

### 12.3 执行方式

1. 固定训练集参数。
2. 测试时分别改变一个参数，其余参数保持不变。
3. 观察各任务性能变化。
4. 分析哪些参数对模型影响最大。

### 12.4 预期结论

通常：

1. σ_m 对材料识别和压力估计影响较大。
2. τ_m 对材料识别影响较大，因为它影响波形衰减。
3. α_m 对压力估计影响较大，因为它决定压力饱和曲线。
4. K_i 对位置和压力均有影响。

---

## 13. 补充实验：小规模实测校准验证

### 13.1 实验目的

如果后期能制作单个 TENG 单元，可以加入小规模实测校准实验。该实验不要求制作完整 8×8 阵列，目标是用少量实测波形校准仿真参数，提高仿真可信度。

### 13.2 实测设置

| 项目 | 建议 |
|---|---|
| TENG 单元数 | 1 个 |
| 材料数量 | 至少 3 种 |
| 压力等级 | 1, 5, 10, 15, 20 N |
| 每组重复次数 | 20-50 次 |
| 采集设备 | 示波器、数据采集卡或 Arduino 模块 |

### 13.3 校准参数

可拟合参数包括：

```text
σ_m
τ_m
α_m
noise level
baseline drift
response time
```

### 13.4 推荐图表

| 图名 | 内容 |
|---|---|
| Measured vs Simulated Waveform | 实测波形与校准后仿真波形对比 |
| Force-Peak Curve | 不同压力下实测和仿真峰值对比 |
| Parameter Table | 校准前后参数 |

### 13.5 论文表述

可以写：

```text
The simulator was calibrated using low-cost single-cell TENG measurements and then expanded to array-level signal generation.
```

如果没有实测，则应诚实写：

```text
The current study is mainly based on literature-guided physics-informed simulation. Future work will include single-cell measurements for parameter calibration and array-level experimental validation.
```

---

## 14. 实验章节推荐写作结构

论文实验章节可按以下结构组织：

```text
5. Experiments
  5.1 Dataset and Simulation Settings
  5.2 Evaluation Metrics
  5.3 Baselines and Implementation Details
  5.4 Simulation Validity Analysis
  5.5 Main Results
  5.6 Ablation Study
  5.7 Robustness Analysis
  5.8 Generalization Analysis
  5.9 Uncertainty Analysis
```

其中：

1. `5.4 Simulation Validity Analysis` 对应实验 1。
2. `5.5 Main Results` 对应实验 2。
3. `5.6 Ablation Study` 对应实验 3。
4. `5.7 Robustness Analysis` 合并实验 4-7。
5. `5.8 Generalization Analysis` 对应实验 8。
6. `5.9 Uncertainty Analysis` 对应实验 9。

---

## 15. 所有实验的执行优先级

如果时间充足，建议完成全部实验。  
如果时间有限，优先级如下：

| 优先级 | 实验 | 是否必须 |
|---|---|---|
| P0 | 仿真信号合理性 | 必须 |
| P0 | 主结果对比 | 必须 |
| P0 | 消融实验 | 必须 |
| P0 | 噪声鲁棒性 | 必须 |
| P0 | 坏点鲁棒性 | 必须 |
| P1 | 跨压力泛化 | 强烈建议 |
| P1 | 跨位置泛化 | 强烈建议 |
| P1 | 通道漂移鲁棒性 | 建议 |
| P1 | 串扰鲁棒性 | 建议 |
| P2 | 不确定性分析 | 加分项 |
| P2 | 参数敏感性 | 加分项 |
| P2 | 单元实测校准 | 有条件再做 |

最低可交付实验组合：

```text
仿真合理性
主结果对比
消融实验
噪声鲁棒性
坏点鲁棒性
跨压力泛化
跨位置泛化
```

这个组合已经能支撑一篇较完整的本科论文或创新项目论文。

---

## 16. 实验结果整理建议

最终结果建议整理为以下图表：

| 编号 | 图表 | 对应实验 |
|---|---|---|
| Fig. 1 | 总体框架图 | 方法概览 |
| Fig. 2 | 仿真模型和阵列压力分布 | 仿真方法 |
| Fig. 3 | 仿真信号合理性图 | 实验 1 |
| Table 1 | 材料参数表 | 仿真设置 |
| Table 2 | 主结果对比表 | 实验 2 |
| Table 3 | 消融实验表 | 实验 3 |
| Fig. 4 | 混淆矩阵 | 实验 2 |
| Fig. 5 | 压力预测散点图 | 实验 2 |
| Fig. 6 | 位置预测误差热图 | 实验 2 |
| Fig. 7 | 噪声鲁棒性曲线 | 实验 4 |
| Fig. 8 | 坏点鲁棒性曲线 | 实验 5 |
| Fig. 9 | 漂移和串扰鲁棒性曲线 | 实验 6-7 |
| Table 4 | 跨分布泛化表 | 实验 8 |
| Fig. 10 | 不确定性与误差关系 | 实验 9 |

---

## 17. 讨论部分应强调的内容

实验完成后，讨论部分建议重点写：

1. 仿真信号能反映材料、压力、位置和接触半径变化的基本物理趋势。
2. 空间分支和时序分支对不同任务具有互补作用。
3. 鲁棒训练能显著改善噪声和坏点条件下的性能。
4. 跨分布测试比随机测试更严格，也更接近真实应用中的未知条件。
5. 不确定性估计可以为模型预测提供可靠性参考。
6. 当前研究仍主要基于仿真，缺少完整实物阵列验证。
7. 后续应使用单元实测校准参数，并进一步扩展到真实阵列实验。

需要避免的过度表述：

```text
本文实现了真实可部署的 TENG 触觉系统。
本文首次提出 TENG 数字孪生。
本文证明模型可以直接用于所有真实 TENG 阵列。
```

推荐谨慎表述：

```text
本文提出了一个面向 TENG 触觉阵列算法预研的物理启发仿真与故障鲁棒多任务学习框架。
```

---

## 18. 下一步执行建议

建议按照以下顺序推进代码和实验：

1. 实现材料参数表和 TENG 单元波形生成。
2. 实现 8×8 阵列压力分布和空间热力图。
3. 生成少量样本，完成实验 1 的可视化。
4. 生成标准 train、val、test_random 数据集。
5. 实现手工特征提取和传统 baseline。
6. 实现主模型并完成主结果实验。
7. 做消融实验。
8. 做噪声和坏点鲁棒性实验。
9. 做跨压力和跨位置泛化实验。
10. 有时间再补漂移、串扰、不确定性和参数敏感性分析。

---

## 19. 简短总结

本项目的实验体系应围绕“仿真是否合理、模型是否有效、模块是否必要、系统是否鲁棒、跨分布是否可泛化、预测是否可靠”六个问题展开。

对应关系如下：

| 核心问题 | 对应实验 |
|---|---|
| 仿真是否合理 | 实验 1 |
| 模型是否有效 | 实验 2 |
| 模块是否必要 | 实验 3 |
| 系统是否鲁棒 | 实验 4-7 |
| 跨分布是否可泛化 | 实验 8 |
| 预测是否可靠 | 实验 9 |

只要这些实验按顺序完成，论文的实验章节就会形成比较完整的逻辑闭环。
