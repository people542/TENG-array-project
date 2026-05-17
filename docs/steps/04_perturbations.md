# Step 04: 非理想扰动模块

> 日期：2026-05-17  
> 对应代码：`simulation/perturbations.py`  
> 上游依赖：`simulation/array_generator.py`

## 1. 本步骤目标

本步骤实现 TENG 阵列仿真中的非理想扰动，用于后续噪声鲁棒性、坏点、漂移和串扰实验。

## 2. 新增接口

新增文件：

```text
simulation/perturbations.py
```

主要接口：

- `PerturbationConfig`
- `add_awgn(signal, snr_db, rng=None)`
- `apply_channel_gain(signal, gain_variation, rng=None)`
- `add_baseline_drift(signal, drift_ratio, rng=None)`
- `apply_neighbor_crosstalk(signal, crosstalk_ratio)`
- `apply_faulty_channels(signal, fault_ratio, rng=None)`
- `apply_perturbations(signal, config, rng=None)`

## 3. 扰动含义

| 扰动 | 作用 |
|---|---|
| AWGN | 模拟电路和采集噪声 |
| 通道增益 | 模拟制造差异、老化和灵敏度漂移 |
| 基线漂移 | 模拟低频环境和采集漂移 |
| 邻域串扰 | 模拟相邻单元机械/电学耦合 |
| 坏点 | 模拟失效通道 |

## 4. 当前实现顺序

`apply_perturbations()` 的固定顺序为：

```text
channel gain -> crosstalk -> baseline drift -> AWGN -> faulty channels
```

坏点最后施加，确保失效通道最终为零。

## 5. 已验证性质

基础测试覆盖：

1. 所有扰动保持输入 shape 不变。
2. AWGN、增益、串扰、漂移会改变信号。
3. 坏点数量符合 `fault_ratio`。
4. 组合扰动返回 `channel_gains` 和 `fault_mask` 元数据。

运行命令：

```bash
python -m unittest discover -s tests
```

## 6. 下一步

把扰动接入数据集生成脚本，生成训练、验证、测试和鲁棒性测试 split。
