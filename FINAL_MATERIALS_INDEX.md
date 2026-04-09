# 结题 / 汇报材料统一索引

## 1. 建议优先阅读顺序

1. `PROJECT_FINAL_NOTE.md`：最终项目说明书，适合老师/评阅人先整体了解项目。
2. `README.md`：工程总览、模块入口、当前版本说明。
3. `results/summary_table.md`：四个模块的当前状态、可信口径与后续方向总表。
4. `results/all_results_index.md`：全部结果文件和图表的统一索引。
5. `results/plate_3d/summary.md`：主模块结果摘要与正式引用口径。
6. `results/plate_3d/numerical_method_note.md`：`plate_3d` 数值方法说明。
7. `results/plate_3d/error_budget.md`：`plate_3d` 误差来源说明。
8. `results/plate_3d/grid_convergence_report.md`：主量 `J_lim` 的收敛与 GCI 报告。
9. `results/plate_3d/gradient_secondary_convergence_report.md`：次级量 `center_gradient_probe` 的收敛报告。
10. `results/tip_plane/summary.md`、`results/cross_field/summary.md`、`results/pinn/summary.md`：三个扩展模块的正式说明。

## 2. 最适合结题展示的核心材料

### 2.1 主线材料（优先展示）
- `results/plate_3d/summary.md`
- `results/plate_3d/plate_phi_slice.png`
- `results/plate_3d/plate_field_slice.png`
- `results/plate_3d/plate_current_limit.png`
- `results/plate_3d/plate_grid_convergence.png`
- `results/plate_3d/plate_grid_error.png`
- `results/plate_3d/numerical_method_note.md`
- `results/plate_3d/error_budget.md`

### 2.2 扩展模块材料
- `results/tip_plane/summary.md`
- `results/tip_plane/tip_trajectory.png`
- `results/tip_plane/tip_voltage_scan.png`
- `results/cross_field/summary.md`
- `results/cross_field/cross_field_orbit.png`
- `results/cross_field/cross_field_transport_scan.png`
- `results/pinn/summary.md`
- `results/pinn/surrogate_quick_scan.png`
- `results/pinn/pinn_prediction.png`

## 3. 当前正式引用口径

### 3.1 主模块 `plate_3d`
- 主量：`J_lim`
- 次级量：`center_gradient_probe`
- 数值方法与误差说明以 `numerical_method_note.md` 和 `error_budget.md` 为准
- 网格收敛与 GCI 以 `grid_convergence_report.md` 为准

### 3.2 扩展模块
- `tip_plane`：趋势性研究结果，适合结题汇报和后续深化
- `cross_field`：汇报版交叉场研究结果，适合说明扩展研究方向
- `pinn`：主求解器辅助模块，用于快速预测与参数初猜，不替代主求解器

## 4. 工程与复现材料
- `ACTIVE_CODE_LOCK.md`：当前活跃代码版本锁定说明
- `RUN_GUIDE.md`：推荐运行顺序与操作指南
- `ENVIRONMENT_AND_REPRODUCIBILITY.md`：环境与复现说明
- `tests/README.md` 与 `tests/test_regression.py`：最小回归测试

## 5. 交付清单
- `DELIVERY_MANIFEST.md`：建议提交内容和展示顺序
- `TODAY_DONE.md`：阶段完成说明
- `ENGINEERING_CLEANUP_NOTE.md`：工程清理说明

## 6. 推荐提交包结构
- `README.md`
- `PROJECT_FINAL_NOTE.md`
- `FINAL_MATERIALS_INDEX.md`
- `ACTIVE_CODE_LOCK.md`
- `RUN_GUIDE.md`
- `ENVIRONMENT_AND_REPRODUCIBILITY.md`
- `configs/`
- `src/`
- `results/`
- `tests/`
