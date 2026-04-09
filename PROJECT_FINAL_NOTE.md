# 最终项目说明书

## 一、项目基本信息

**项目名称：** 基于深度学习的二极管电子输运特性研究  
**项目形态：** 多模块数值模拟与辅助智能建模工程  
**当前版本定位：** 可运行、可展示、可复现、可继续扩展的研究版本

本项目围绕空间电荷限制电子输运问题展开，面向真空电子器件中平板结构、针尖发射结构、交叉场结构及人工智能辅助建模等场景，构建了统一的代码工程与结果输出体系。项目不是单一脚本，而是一套由几何建模、数值离散、自洽迭代、参数扫描、结果可视化、辅助代理模型和回归测试共同组成的研究型工程。

当前版本的总体目标不是一次性完成全部高精度科研结论，而是完成一套**主线明确、模块完整、结果可追踪、后续可继续深化**的项目底盘。其中，`plate_3d` 模块作为主论文方向重点推进，`tip_plane`、`cross_field` 与 `PINN/AI` 模块作为扩展方向同步形成了可运行的研究版成果。

---

## 二、项目目标与研究内容

本项目的核心问题是分析空间电荷作用下电子从阴极向阳极输运时的电流限制、电势重分布、能谱展宽、轨道偏转及辅助智能建模问题。围绕这一目标，当前工程实现了以下四个研究模块：

1. **三维平板二极管有限差分模块（plate_3d）**  
   研究有限发射面积、三维空间电荷限制电流问题，建立泊松方程数值模型，并通过外层自洽与极限电流搜索获得 `J_lim`、边缘增强和中心线电势分布等结果。

2. **针尖—平板 MC/MD 模块（tip_plane）**  
   建立针尖发射的粒子推进与离散库仑作用模型，给出电子轨迹、能谱展宽以及电压扫描下的趋势性结果，并以 Fowler–Nordheim / Murphy–Good 风格模型估计发射电流。

3. **交叉场模块（cross_field）**  
   建立均匀电磁场中的电子轨道积分模型，给出 `E×B` 漂移、轨道包络、Larmor 半径和磁场扫描结果，形成可汇报的交叉场最小研究版。

4. **PINN / AI 辅助模块（pinn）**  
   建立面向 `plate_3d` 主模块的代理模型和 1D Poisson PINN 演示模型，用于快速预测 `J_lim` 趋势、辅助参数扫描和展示物理约束训练路线的可行性。

---

## 三、项目工程结构说明

当前项目采取统一工程目录管理，主要目录如下：

- `src/`：核心代码目录，包含四个模块的实现与统一入口。
- `configs/`：配置文件目录，区分主算例、收敛分析与各模块参数设置。
- `results/`：结果输出目录，包含主结果、收敛分析、图表、摘要和索引。
- `tests/`：基础回归测试目录。
- `tools/`：实验性辅助脚本与归档工具目录。
- `README.md`：项目总览说明。
- `RUN_GUIDE.md`：运行指南。
- `ENVIRONMENT_AND_REPRODUCIBILITY.md`：环境与复现说明。

项目统一入口为：

```bash
python src/main.py --module <module_name> --config <config_path>
```

支持的模块包括：

- `plate_3d`
- `tip_plane`
- `cross_field`
- `pinn`

项目同时提供基础回归测试：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

---

## 四、当前已完成的主要成果

### 4.1 `plate_3d` 主模块成果

`plate_3d` 是当前全项目最成熟、最接近论文主结果的模块。当前版本已经完成：

- 三维平板二极管几何与有限发射面积建模
- 七点差分离散下的泊松方程数值求解
- 红黑 SOR 内层迭代
- 外层空间电荷自洽迭代
- 极限电流 `J_lim` 搜索
- 电势、电场与表面梯度提取
- 电压扫描与发射半径扫描
- Richardson / GCI 网格收敛分析
- 次级量 `center_gradient_probe` 收敛分析
- 数值方法说明与误差来源说明

当前 `plate_3d` 已形成以下正式说明文件：

- `results/plate_3d/summary.md`
- `results/plate_3d/numerical_method_note.md`
- `results/plate_3d/error_budget.md`
- `results/plate_3d/grid_convergence_report.md`
- `results/plate_3d/gradient_secondary_convergence_report.md`

当前该模块最可信的结论口径是：

- 主量以 `J_lim` 为核心；
- 次级量以 `center_gradient_probe` 为主要收敛验证对象；
- 高网格 warm-start 继续验证已完成到可形成阶段性正式报告的程度。

### 4.2 `tip_plane` 模块成果

当前 `tip_plane` 已经从最小演示版提升为研究表达较完整的工程版，完成内容包括：

- 针尖几何参数化与发射点采样
- 粒子推进与离散库仑相互作用开关
- 工程型外层自洽反馈
- 轨迹图、能量分布图与库仑作用对比图
- 电压扫描结果整理
- 基于 Fowler–Nordheim / Murphy–Good 风格模型的发射电流估计
- 模块假设、适用范围与局限性说明

### 4.3 `cross_field` 模块成果

当前 `cross_field` 已经从演示版整理为可汇报版，完成内容包括：

- 均匀电场与磁场下的电子轨道积分
- 多粒子轨道包络展示
- `E×B` 漂移估计
- Larmor 半径估计
- 磁场扫描图与输运量扫描图
- 汇报版理论背景与模块定位说明

### 4.4 `PINN/AI` 模块成果

当前 `PINN/AI` 模块已明确定位为主求解器辅助模块，而不是独立主结果模块。当前已完成：

- 基于 `plate_3d` 数据的 surrogate 代理模型训练
- 1D Poisson PINN 演示训练
- 代理模型快速预测 `J_lim` 趋势的 quick scan
- 模块用途、边界与局限说明

其当前作用是：

- 为 `plate_3d` 提供参数扫描初猜；
- 展示引入物理约束训练的可行路线；
- 作为后续智能加速主求解器的基础。

---

## 五、关键图表索引

当前项目最建议优先查看的图表如下。

### 5.1 `plate_3d`

- `plate_phi_slice.png`：中截面电势分布图
- `plate_field_slice.png`：中截面电场分布图
- `plate_surface_field.png`：阴极表面场分布图
- `plate_current_limit.png`：极限电流搜索结果图
- `plate_search_convergence.png`：搜索过程收敛图
- `plate_radius_sweep.png`：发射半径扫描图
- `plate_voltage_sweep.png`：阳极电压扫描图
- `plate_grid_convergence.png`：`J_lim` 网格收敛图
- `plate_grid_error.png`：GCI / 误差图
- `plate_center_gradient_probe_convergence.png`：次级量收敛图

### 5.2 `tip_plane`

- `tip_trajectory.png`：电子轨迹图
- `tip_energy_hist.png`：能量分布图
- `tip_coulomb_compare.png`：有/无库仑作用对比图
- `tip_voltage_scan.png`：电压扫描图

### 5.3 `cross_field`

- `cross_field_orbit.png`：交叉场轨道图
- `cross_field_energy.png`：能量图
- `cross_field_bscan.png`：磁场扫描图
- `cross_field_transport_scan.png`：输运量扫描图

### 5.4 `PINN/AI`

- `surrogate_training_loss.png`：代理模型训练损失图
- `pinn_prediction.png`：代理模型预测效果图
- `pinn_solution.png`：PINN 解图
- `pinn_residual_demo.png`：PINN 残差演示图
- `surrogate_quick_scan.png`：代理模型快速扫描图

---

## 六、当前最可信结论

就当前项目整体成熟度而言，最可信的结论主要集中在 `plate_3d` 主模块。其核心原因在于：

- 数值方法、误差说明和收敛分析已经最完整；
- 已建立网格收敛与次级量收敛报告；
- 主量 `J_lim` 已具备较完整的定量分析口径；
- 主结果可以被较明确地区分为“正式引用结果”和“实验/测试结果”。

对整个项目而言，目前最稳妥的总体表述是：

1. 项目已经建立起一套统一的多模块电子输运研究工程；
2. `plate_3d` 已经具备作为论文主方向继续深化的基础；
3. `tip_plane`、`cross_field` 和 `PINN/AI` 已经形成了可运行、可展示、可扩展的研究版模块；
4. 项目已经完成从“最小演示版”向“阶段性研究版”的过渡。

---

## 七、当前局限性说明

尽管当前工程已经达到较完整的研究版状态，但仍存在以下局限：

### 7.1 `plate_3d`

- 最高层高网格验证仍然计算代价较高；
- 某些次级量（特别是表面梯度相关量）仍比主量更敏感；
- 最细层 warm-start 收敛仍有继续优化空间；
- 表面导数与边缘增强定义仍可继续精炼。

### 7.2 `tip_plane`

- 当前针尖局域场仍为工程近似，不是严格解析场或有限元场；
- 发射与空间电荷反馈尚未形成严格强自洽闭环；
- 当前结果更适合做趋势性研究，而非最终高精度定量结论。

### 7.3 `cross_field`

- 仍未纳入真正的空间电荷—电磁场强耦合；
- 鞘层厚度、截止频率等仍停留在估计或接口层；
- 更适合作为扩展研究方向，而非当前主结果来源。

### 7.4 `PINN/AI`

- 目前 surrogate 与 1D PINN 仍以辅助与演示为主；
- 尚未直接替代主 PDE 的高维求解；
- 更多体现为研究储备与方法探索。

---

## 八、后续工作建议

若项目继续推进，建议优先级如下：

1. 继续深挖 `plate_3d`，作为论文主结果模块进一步做高网格验证与误差分解；
2. 完善 `tip_plane` 的局域场模型与更严格的发射自洽；
3. 在 `cross_field` 中引入更真实的空间电荷耦合与稳定性指标；
4. 将 `PINN/AI` 从辅助模型进一步推进为与主 PDE 更紧密耦合的智能加速工具；
5. 持续完善工程测试、版本锁定和结果归档规范。

---

## 九、当前推荐阅读顺序

为了便于老师、评阅人或后续维护者快速理解项目，建议按以下顺序阅读：

1. `README.md`
2. `RUN_GUIDE.md`
3. `results/summary_table.md`
4. `results/all_results_index.md`
5. `results/plate_3d/summary.md`
6. `results/plate_3d/numerical_method_note.md`
7. `results/plate_3d/error_budget.md`
8. `results/plate_3d/grid_convergence_report.md`
9. 其他模块的 `summary.md`

---

## 十、结论

综合来看，本项目已经完成了从项目构想到工程化实现、从最小演示到阶段性研究版的构建过程。当前版本已经具备如下特点：

- **可运行**：统一入口、统一配置、统一结果输出；
- **可展示**：主结果图、扫描图、对比图和汇报型材料齐全；
- **可复现**：环境说明、运行指南、回归测试和版本锁定文件齐全；
- **可扩展**：主线明确，扩展模块已具备继续深化的代码基础。

因此，当前工程适合作为：

- 结题材料支撑工程；
- 阶段性科研成果展示平台；
- 后续论文工作的代码底盘；
- 新成员继续接手的开发基础。
