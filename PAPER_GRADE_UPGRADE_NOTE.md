# 论文级精化版本说明（本轮）

本轮升级目标不是“宣称已经达到最终论文定稿级别”，而是把原先的最小演示工程进一步推进为更接近论文前期研究代码的版本，重点体现在以下方面：

## 1. plate_3d 主模块

- 新增注入初始能量 `injected_energy_ev`，避免纯零初速近似过于理想化。
- 在自洽循环中加入电荷密度欠松弛 `charge_relaxation`，使外层收敛更稳，更接近 Gummel 型迭代思想。
- 区分“搜索网格”和“最终主解网格”：参数扫描与极限电流搜索默认在较粗网格上完成，最终主解在配置指定网格上重求，兼顾效率与精度。
- 新增 `plate_solver_convergence.png`，显式输出内层 SOR 残差和外层自洽变化量。
- 新增 `voltage_sweep.json` 与 `plate_voltage_sweep.png`，增强物理趋势分析能力。
- 新增 `plate_solution_arrays.npz`，保存 `phi / rho / |E|` 主解数组，便于后续论文作图和二次分析。

## 2. tip_plane 模块

- 将原来的占位发射电流估计替换为 Fowler–Nordheim / Murphy–Good 风格估计。
- 新增材料参数：功函数 `work_function_ev`、有效发射面积 `effective_emission_area`。
- 使用更合理的轴对称近似场替代原始过于简单的外加场表达式。
- 新增顶端局域场计算 `apex_local_field_v_per_m`。
- 新增 FN 发射电流、电流密度输出。
- 新增电压扫描结果 `tip_voltage_scan.json` 和图 `tip_voltage_scan.png`。

## 3. pinn 模块

- 代理模型训练集不再只依赖半径扫描，也会自动吸收 `plate_3d` 电压扫描结果作为锚点。
- 修复 `radius_sweep.json` 既可能是列表也可能是字典的兼容问题。
- 新增真实的 1D Poisson PINN 训练，不再只是残差占位图。
- 输出 `pinn_solution.png` 与 `pinn_training_history.json`。

## 4. 统一入口

- `main.py` 已恢复为四模块真实分发入口，而非占位输出。
- 当前命令行入口均可运行：
  - `plate_3d`
  - `tip_plane`
  - `cross_field`
  - `pinn`

## 5. 当前阶段定位

当前代码已经从“最小演示版”推进为“论文前期研究级工程版”。

仍然尚未完成的高精度论文级工作包括但不限于：

- `plate_3d` 更高分辨率网格与系统误差分析；
- `tip_plane` 严格旋转椭球/针尖解析场、自洽发射边界与更大粒子数并行化；
- `cross_field` 真实空间电荷边界与截止频率模型；
- `pinn` 面向主物理问题的高维 PDE 约束训练。

因此，本轮版本应理解为：**更接近论文级，但仍属于可继续深化的研究代码版本。**
