# 结果总表

| 模块 | 当前状态 | 正式定位 | 当前最可信输出 | 主要结果文件 | 后续方向 |
|---|---|---|---|---|---|
| `plate_3d` | 主线模块，已形成阶段性研究版 | 论文主方向与结题主结果来源 | 主量 `J_lim`；次级量 `center_gradient_probe` | `results/plate_3d/summary.md`、`numerical_method_note.md`、`error_budget.md`、`grid_convergence_report.md` | 继续优化最细网格 warm-start 与次级量收敛 |
| `tip_plane` | 已完成工程强化版 | 趋势性粒子输运研究模块 | 轨迹、能谱展宽、FN 电流估计与电压扫描趋势 | `results/tip_plane/summary.md`、`tip_trajectory.png`、`tip_voltage_scan.png` | 更真实针尖场与更严格强自洽 |
| `cross_field` | 已完成汇报版 | 交叉场扩展研究模块 | `E×B` 漂移、轨道包络、Larmor 半径与磁场扫描 | `results/cross_field/summary.md`、`cross_field_orbit.png`、`cross_field_transport_scan.png` | 加入真实空间电荷-电磁场耦合 |
| `pinn` | 已完成辅助模块版 | 主求解器辅助与 AI 演示模块 | surrogate 快速预测、1D PINN demo | `results/pinn/summary.md`、`surrogate_quick_scan.png`、`pinn_prediction.png` | 与主 PDE 更紧密耦合 |

## plate_3d 当前正式引用口径

- 主量：`J_lim`
- 次级量：`center_gradient_probe`
- 数值方法以 `results/plate_3d/numerical_method_note.md` 为准
- 误差来源说明以 `results/plate_3d/error_budget.md` 为准
- 网格收敛与 GCI 以 `results/plate_3d/grid_convergence_report.md` 为准

## 使用建议

- 结题/汇报优先展示 `plate_3d`
- `tip_plane`、`cross_field` 用于体现扩展研究方向
- `pinn` 用于说明 AI 辅助主求解器的可行性，不应替代主求解器结果
