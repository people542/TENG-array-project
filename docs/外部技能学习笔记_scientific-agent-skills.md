# 外部技能学习笔记：scientific-agent-skills

> 学习日期：2026-05-17  
> 来源仓库：https://github.com/K-Dense-AI/scientific-agent-skills  
> 用途：吸收其中对本 TENG 触觉阵列项目有用的科研工作流规范，不直接复制或安装全部技能。

---

## 1. 仓库概况

`K-Dense-AI/scientific-agent-skills` 是一个面向科研代理的技能集合，覆盖文献检索、数据库查询、科研写作、数据分析、可视化、机器学习、工程仿真等方向。

该仓库对本项目最有价值的不是某个具体生物/化学技能，而是以下科研工作流习惯：

1. 文献检索要记录搜索策略、数据库、日期和筛选标准。
2. 参考文献要尽量保留 DOI、期刊、年份、用途和局限性。
3. 数据分析要生成可追溯的 Markdown 报告。
4. 图表代码要使用可维护的面向对象 Matplotlib 写法。
5. 对科研结论要区分“文献引导假设”“仿真结果”“实测结果”。

---

## 2. 对本项目最相关的技能

### 2.1 literature-review

用途：系统文献综述、研究 gap 梳理、引用验证和综述文档生成。

对本项目的启发：

1. 每次文献调研都应记录：
   - 查询日期
   - 查询关键词
   - 使用的数据库或网站
   - 纳入/排除标准
   - 最终采用文献数量
2. 文献综述不应逐篇堆砌，而应按主题综合：
   - TENG 理论建模
   - 材料电荷密度
   - TENG 阵列触觉成像
   - TENG + 机器学习
   - 鲁棒性与不确定性
3. 每篇核心文献都应记录：
   - 论文题目
   - 作者
   - 年份
   - 期刊/会议
   - DOI/URL
   - 和本项目的关系
   - 局限性

本项目采用方式：

```text
docs/TENG_仿真参数文献调研.md
```

后续继续扩展时，按上述格式补充检索策略和筛选过程。

### 2.2 paper-lookup

用途：通过多个论文数据库查找论文、DOI、开放获取版本和引用信息。

对本项目的启发：

1. 查 DOI 时优先使用 Crossref、OpenAlex、Semantic Scholar 等来源交叉验证。
2. 查具体论文时不要只记录网页标题，应记录 DOI 和出版信息。
3. 查综述和高影响论文时，可以优先关注：
   - Nature Communications
   - Nano Energy
   - ACS Nano
   - Energy & Environmental Science
   - Advanced Functional Materials
   - IEEE Sensors Journal
   - Sensors

本项目采用方式：

```text
文献记录必须包含 DOI/URL 和“用途/局限性”两项。
```

### 2.3 matplotlib

用途：科研图表绘制和 publication-quality figure 输出。

对本项目的启发：

1. 后续画图统一使用 Matplotlib 面向对象接口：

```python
fig, ax = plt.subplots()
ax.plot(x, y)
fig.savefig(path, dpi=300, bbox_inches="tight")
```

2. 图像保存要求：
   - PNG：用于快速查看和汇报。
   - PDF/SVG：用于论文图表。
   - `dpi=300`：用于论文和报告。
   - `bbox_inches="tight"`：避免多余边距。

3. TENG 仿真合理性图建议使用：
   - 波形图：line plot
   - 峰值热力图：imshow heatmap
   - 鲁棒性实验：line plot with markers
   - 主结果：bar chart 或 table
   - 误差/不确定性：scatter plot

本项目采用方式：

```text
后续所有绘图脚本放在 scripts/，输出保存到 figures/。
```

### 2.4 exploratory-data-analysis

用途：对科学数据文件做结构、质量和统计检查，并生成 Markdown 报告。

对本项目的启发：

后续生成 `.npz`、`.npy` 或 `.csv` 数据集后，不应直接进入训练，而应先生成数据检查报告。

每个数据集至少检查：

1. 样本数量。
2. `signal` shape 是否为 `[N, 8, 8, 200]`。
3. 材料类别分布是否均衡。
4. 压力、位置、半径范围是否符合设定。
5. 是否存在 NaN 或 Inf。
6. 信号峰值、均值、能量分布是否异常。
7. 随机抽样热力图和波形是否符合物理直觉。

本项目采用方式：

```text
每生成一个正式数据集，都同步生成 docs/reports/ 下的数据检查报告。
```

---

## 3. 对当前项目流程的调整

从现在开始，本项目每一步都应包含：

1. **代码或文档产出**
   - 实现对应模块或新增说明文档。
2. **本步骤说明文档**
   - 放在 `docs/steps/`。
   - 说明目标、输入、输出、验证方式、限制。
3. **验证命令**
   - 运行最小可重复检查。
4. **Git 提交**
   - 每步一个清晰 commit。
5. **必要时生成报告**
   - 文献调研、数据生成、实验结果都应有 Markdown 报告。

---

## 4. 后续项目文档规范

建议继续使用以下目录：

```text
docs/
├── steps/          # 每一步开发说明
├── reports/        # 数据检查和实验报告
├── references/     # 文献表、BibTeX、引用核查
└── figures_notes/  # 图表设计说明
```

当前已经有：

```text
docs/TENG_仿真参数文献调研.md
docs/steps/01_material_params.md
```

后续计划：

```text
docs/steps/02_teng_unit.md
docs/steps/03_array_generator.md
docs/reports/simulation_sanity_report.md
```

---

## 5. 对下一步 `teng_unit.py` 的具体要求

按照这次学习到的规范，下一步实现 `simulation/teng_unit.py` 时，应同时完成：

1. 实现代码：
   - 时间轴生成。
   - 接触-分离基础波形。
   - 压力饱和函数。
   - 单元电压波形生成。
2. 写说明文档：
   - `docs/steps/02_teng_unit.md`
3. 写最小验证：
   - 压力增大时峰值增大。
   - 同一压力下不同材料输出有差异。
   - 输出 shape 为 `(200,)`。
4. 记录限制：
   - 当前是 physics-inspired 简化模型，不是完整 V-Q-x 理论求解。

---

## 6. 本项目采用的原则

1. 不盲目安装 135 个技能，只吸收适合本项目的科研工作流。
2. 不把外部技能仓库内容直接复制进项目代码。
3. 文献、参数、数据、实验都要可追溯。
4. 每一步都要有说明文档、验证命令和 Git 提交。
5. 论文写作中始终区分仿真假设和实测结论。
