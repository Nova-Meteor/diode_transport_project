# plate_3d 结果摘要

## 1. 当前模型定位

- 当前版本为三维平板二极管有限差分主模块的第一版工程实现。
- 数值方法采用非线性泊松方程 + SOR 迭代 + 电流扫描 / 割线 / 二分混合搜索。
- 当前结果适合作为项目日内闭环与参数趋势展示，不作为最终论文级高精度结论。

## 2. 核心结果

- 1D Child-Langmuir 基准电流密度: 2.333902e+05 A/m²
- 当前近似极限电流密度: 2.892055e+05 A/m²
- 相对 CL 修正 J_lim / J_CL: 1.239150
- 阴极中心表面势梯度 dphi/dz: 5.033489e+02 V/m
- 阴极中心法向电场 Ez: -5.033489e+02 V/m
- 发射区平均表面势梯度: 2.030853e+05 V/m
- 发射区边缘增强系数: 762.540122
- 内层迭代步数: 101
- 外层自洽迭代步数: 5
- 是否收敛: False
- 搜索说明: 使用扫描 + 割线/二分混合方法得到近似极限电流密度。

## 3. 输出图表

- `plate_phi_slice.png`：中截面电势分布图
- `plate_field_slice.png`：中截面电场强度分布图
- `plate_surface_field.png`：阴极表面势梯度横向分布图
- `plate_current_limit.png`：极限电流搜索曲线
- `plate_search_convergence.png`：搜索迭代收敛曲线
- `plate_radius_sweep.png`：发射半径修正趋势图

## 4. 结构化文件

- `plate_summary.json`：主结果摘要
- `plate_search_history.json`：搜索历史
- `radius_sweep.json`：发射半径扫描结果
