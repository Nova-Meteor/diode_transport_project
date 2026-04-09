# 基于深度学习的二极管电子输运特性研究

## 1. 项目简介

本项目围绕**空间电荷限制电流**与**电子输运特性**展开，目标是构建一个兼顾数值模拟、粒子输运与 AI 辅助建模的研究型工程框架。当前工程包含四个主要模块：

- **fdm_3d**：三维平板二极管有限差分主模块，用于求解非线性泊松方程、电势分布、电场分布、空间电荷限制电流极限值，以及网格收敛与误差评估。
- **mc_md / tip_plane**：针尖-平板结构的蒙特卡洛/分子动力学模块，用于研究离散空间电荷作用下的电子轨迹、能量演化与发射趋势。
- **cross_field**：交叉电磁场电子输运模块，用于分析电子在电场与磁场共同作用下的轨道偏转、漂移行为与磁场扫描趋势。
- **pinn**：AI 辅助模块，当前定位为**主求解器的辅助工具**，包括 surrogate 代理模型和 1D Poisson PINN demo，用于参数初猜、趋势预测与物理约束建模演示。

当前版本已经从最初的“最小演示版”推进到**稳定可交付的研究工程版**：

- `plate_3d` 已形成主线结果、数值方法说明、误差来源说明和收敛分析材料；
- `tip_plane` 已具备可运行的趋势性粒子输运研究框架；
- `cross_field` 已由演示版整理成适合汇报的扩展模块；
- `pinn` 已重新定位为服务主线的辅助模块，而非独立主结果模块。

---

## 2. 当前完成内容

### 已完成

- [x] 项目目录结构初始化与统一整理
- [x] 依赖文件 `requirements.txt`
- [x] 统一参数配置文件 `configs/*.yaml`
- [x] 统一运行入口 `src/main.py`
- [x] `plate_3d`：主求解流程、极限电流搜索、参数扫描、收敛分析、误差说明
- [x] `tip_plane`：针尖-平板 MC/MD 工程强化版结果与电压扫描图
- [x] `cross_field`：交叉场输运汇报版结果与磁场扫描图
- [x] `pinn`：surrogate 代理模型、1D Poisson PINN demo 与 quick scan
- [x] 工程清理、活跃代码锁定、环境与复现说明
- [x] 最基本的回归测试 `tests/test_regression.py`
- [x] 最终项目说明书与结题/汇报材料索引

### 当前定位

- **主线模块**：`plate_3d`
- **扩展模块**：`tip_plane`、`cross_field`
- **辅助模块**：`pinn`

### 当前边界

本工程已具备“**可运行、可展示、可复现、可继续研究**”的基础，但仍属于**研究工程版 / 论文前期版本**，尚未完全达到所有模块的最终论文级高精度终稿状态。特别是：

- `plate_3d` 已形成较完整主线结果，但更高层级网格验证仍可继续精化；
- `tip_plane` 当前使用的是工程近似场与趋势性自洽，不是最终严格解析场模型；
- `cross_field` 当前更适合作为扩展研究模块，而非论文主结果；
- `pinn` 当前主要服务于主求解器辅助预测，不替代主物理求解流程。

---

## 3. 推荐阅读顺序

如果你第一次阅读本项目，建议按以下顺序查看：

1. `PROJECT_FINAL_NOTE.md`：最终项目说明书
2. `FINAL_MATERIALS_INDEX.md`：结题/汇报材料统一索引
3. `results/summary_table.md`：各模块完成状态总表
4. `results/plate_3d/summary.md`：主线模块摘要
5. `results/plate_3d/numerical_method_note.md`：数值方法说明
6. `results/plate_3d/error_budget.md`：误差来源说明
7. 各扩展模块摘要：
   - `results/tip_plane/summary.md`
   - `results/cross_field/summary.md`
   - `results/pinn/summary.md`

---

## 4. 运行方法

### 查看模块列表

```bash
python src/main.py --list
```

### 推荐的主模块运行方式

#### 4.1 三维平板主算例

```bash
python src/main.py --module plate_3d --config configs/plate_3d.yaml
```

#### 4.2 三维平板收敛分析

```bash
python src/main.py --module plate_3d --config configs/plate_3d_convergence.yaml
```

#### 4.3 针尖-平板模块

```bash
python src/main.py --module tip_plane --config configs/tip_plane.yaml
```

#### 4.4 交叉场模块

```bash
python src/main.py --module cross_field --config configs/cross_field.yaml
```

#### 4.5 AI / PINN 模块

```bash
python src/main.py --module pinn --config configs/pinn.yaml
```

---

## 5. 回归测试

项目已包含最基本的 smoke / regression 测试，覆盖：

- `main.py --list`
- `plate_3d` 轻量主算例
- `tip_plane` 轻量运行
- `cross_field` 轻量运行
- `pinn` 轻量训练

运行方式：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

测试说明见：

- `tests/README.md`

---

## 6. 各模块说明

### 6.1 `plate_3d` 模块

这是当前工程的**核心主线模块**，主要完成：

- 三维平板有限差分网格构建
- 非线性泊松方程数值求解
- 电势与电场分布计算
- 阴极表面梯度提取
- 空间电荷限制电流极限值 `J_lim` 搜索
- 参数扫描、收敛分析与误差评估

建议优先查看：

- `results/plate_3d/summary.md`
- `results/plate_3d/numerical_method_note.md`
- `results/plate_3d/error_budget.md`
- `results/plate_3d/grid_convergence_report.md`

### 6.2 `tip_plane` 模块

该模块研究针尖-平板结构中离散空间电荷对电子输运的影响，当前已完成：

- 电子发射采样
- 粒子推进
- 库仑作用对比
- 电压扫描结果图
- 发射电流与能量演化趋势表达

当前模块适合用于：

- 趋势性分析
- 汇报展示
- 后续更严格针尖模型的代码基础

### 6.3 `cross_field` 模块

该模块用于演示和分析交叉电场、磁场共同作用下的电子输运行为，当前已完成：

- Boris 积分推进
- 轨道图与能量图
- 磁场扫描趋势
- 轨道包络与漂移速度指标

当前模块定位为：

- 扩展研究模块
- 交叉场方向的汇报材料基础

### 6.4 `pinn` 模块

当前 `pinn` 模块的定位已经明确调整为：

- **surrogate 代理模型**：为 `plate_3d` 提供快速参数趋势预测与 `J_lim` 初猜
- **1D Poisson PINN demo**：展示物理约束网络训练的可行性

注意：

- 当前 `pinn` 不是主求解器替代品；
- 当前训练数据主要来自 `plate_3d` 的已有扫描结果及物理缩放；
- 当前 AI 模块的价值在于“辅助主线”，而不是单独作为最终高精度主结果。

---

## 7. 主要结果入口

### 主线结果

- `results/plate_3d/summary.md`
- `results/plate_3d/final_release/`
- `results/plate_3d/convergence/`

### 扩展模块结果

- `results/tip_plane/summary.md`
- `results/cross_field/summary.md`
- `results/pinn/summary.md`

### 项目级索引

- `results/summary_table.md`
- `results/all_results_index.md`
- `FINAL_MATERIALS_INDEX.md`
- `PROJECT_FINAL_NOTE.md`

---

## 8. 环境与复现

建议优先参考：

- `RUN_GUIDE.md`
- `ENVIRONMENT_AND_REPRODUCIBILITY.md`

推荐环境：

- Python 3.10+
- `numpy`
- `scipy`
- `matplotlib`
- `pyyaml`
- `torch`

安装依赖：

```bash
pip install -r requirements.txt
```

---

## 9. 当前正式版本口径

当前建议将本工程理解为：

> 一个以 `plate_3d` 为主线、兼顾 `tip_plane`、`cross_field` 与 `pinn` 扩展模块的研究工程版平台。它已经具备稳定运行、图表输出、结果说明、测试和复现文档等基础条件，适合用于结题展示、阶段性科研总结以及后续论文工作底盘。

如果用于结题或汇报，建议优先围绕以下三点展开：

1. `plate_3d` 主线成果与数值分析
2. `tip_plane` / `cross_field` 扩展研究结果
3. `pinn` 作为辅助模块服务主线的定位

---

## 10. 当前版本说明

当前版本为：

- **最终稳定版 / Final Release 系列**

如果后续继续开发，建议在此版本基础上继续，而不要回退到更早的中间压缩包或旧版入口文件。
