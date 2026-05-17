# Step 03: 8x8 阵列信号生成器

> 日期：2026-05-17  
> 对应代码：`simulation/array_generator.py`  
> 上游依赖：`simulation/material_params.py`、`simulation/teng_unit.py`

## 1. 本步骤目标

本步骤把单个 TENG 单元波形扩展到 8x8 阵列，生成后续模型需要的基本输入：

```text
signal shape = (8, 8, 200)
```

## 2. 压力分布

给定总压力、接触中心和接触半径，先用二维高斯生成每个单元的局部压力：

```text
w_i = exp(-d_i^2 / (2r^2))
F_i = F_total * w_i / sum(w_i)
```

这样可以保证所有单元压力之和等于输入总压力。

## 3. 新增接口

新增文件：

```text
simulation/array_generator.py
```

主要接口：

- `cell_coordinates(config)`
- `gaussian_pressure_map(force_n, position_x_mm, position_y_mm, radius_mm, config)`
- `generate_array_sample(material_key, force_n, position_x_mm, position_y_mm, radius_mm, ...)`
- `sample_random_array(rng, material_key, ...)`

## 4. 输出结构

`generate_array_sample()` 返回 `ArraySample`：

- `signal`：阵列时空电压信号，shape 为 `(8, 8, 200)`
- `pressure_map_n`：局部压力分布，shape 为 `(8, 8)`
- `material_key`
- `force_n`
- `position_x_mm`
- `position_y_mm`
- `radius_mm`

辅助方法：

- `peak_map()`：返回每个通道的电压峰值热力图
- `as_label_dict()`：返回数据集标签字段

## 5. 已验证性质

基础测试覆盖：

1. 阵列坐标范围为 x/y 方向 0-35 mm。
2. 高斯压力图保持总压力守恒。
3. 接触中心在角落时，压力峰值也在对应角落。
4. 生成信号 shape 为 `(8, 8, 200)`。
5. 固定随机种子时，随机样本可复现。

运行命令：

```bash
python -m unittest discover -s tests
```

## 6. 当前限制

1. 暂未加入噪声、漂移、串扰和坏点。
2. 随机波形模式中，每个通道会采样轻微不同的单元参数，用于模拟通道差异。
3. 暂未批量生成数据集文件。

## 7. 下一步

新增脚本：

```text
scripts/generate_demo_samples.py
```

目标：

1. 生成少量样本。
2. 绘制不同材料波形。
3. 绘制不同压力波形。
4. 绘制 8x8 峰值热力图。
