# 全部结果统一索引

## 1. 项目级说明文件
- `../PROJECT_FINAL_NOTE.md`：最终项目说明书
- `../FINAL_MATERIALS_INDEX.md`：结题/汇报材料统一索引
- `../README.md`：工程总览与运行入口
- `../ACTIVE_CODE_LOCK.md`：活跃代码版本锁定说明
- `../RUN_GUIDE.md`：运行指南
- `../ENVIRONMENT_AND_REPRODUCIBILITY.md`：环境与复现说明
- `../DELIVERY_MANIFEST.md`：交付建议与提交清单

## 2. 项目级结果总览
- `summary_table.md`：四个模块的状态、口径、输出与后续方向总表
- `self_check_report.md`：前期自查与补漏洞报告

## 3. plate_3d（主线模块）
### 3.1 正式说明
- `plate_3d/summary.md`：主结果摘要与正式引用口径
- `plate_3d/numerical_method_note.md`：数值方法说明
- `plate_3d/error_budget.md`：误差来源说明
- `plate_3d/grid_convergence_report.md`：主量 `J_lim` 的网格收敛与 GCI 报告
- `plate_3d/gradient_secondary_convergence_report.md`：次级量 `center_gradient_probe` 的收敛报告

### 3.2 主结果数据与图表
- `plate_3d/plate_summary.json`
- `plate_3d/plate_phi_slice.png`
- `plate_3d/plate_field_slice.png`
- `plate_3d/plate_surface_field.png`
- `plate_3d/plate_current_limit.png`
- `plate_3d/plate_search_convergence.png`
- `plate_3d/plate_radius_sweep.png`
- `plate_3d/plate_grid_convergence.png`
- `plate_3d/plate_grid_error.png`
- `plate_3d/plate_center_gradient_probe_convergence.png`
- `plate_3d/plate_center_gradient_probe_error.png`
- `plate_3d/plate_centerline_convergence.png`

### 3.3 过程性与补充材料
- `plate_3d/plate_search_history.json`
- `plate_3d/radius_sweep.json`
- `plate_3d/grid_convergence.json`
- `plate_3d/gradient_secondary_convergence.json`
- `plate_3d/search_refinement_report.md`
- `plate_3d/higher_grid_validation_progress.md`

## 4. tip_plane
- `tip_plane/summary.md`：模块正式说明
- `tip_plane/tip_summary.json`：主结果 JSON
- `tip_plane/tip_trajectory.png`：电子轨迹图
- `tip_plane/tip_energy_hist.png`：能量分布图
- `tip_plane/tip_coulomb_compare.png`：有/无库仑作用对比图
- `tip_plane/tip_voltage_scan.png`：电压扫描图
- `tip_plane/tip_voltage_scan.json`：电压扫描数据

## 5. cross_field
- `cross_field/summary.md`：模块正式说明
- `cross_field/cross_field_summary.json`：主结果 JSON
- `cross_field/cross_field_orbit.png`：交叉场轨道图
- `cross_field/cross_field_energy.png`：能量图
- `cross_field/cross_field_bscan.png`：磁场扫描图
- `cross_field/cross_field_transport_scan.png`：输运量扫描图

## 6. pinn / AI
- `pinn/summary.md`：模块正式说明与定位
- `pinn/pinn_summary.json`：主结果 JSON
- `pinn/surrogate_dataset.csv`：训练数据集
- `pinn/dataset_metadata.json`：数据集说明
- `pinn/surrogate_model.pt`：训练好的代理模型
- `pinn/surrogate_training_loss.png`：代理模型训练损失图
- `pinn/pinn_prediction.png`：代理模型预测效果图
- `pinn/pinn_solution.png`：1D Poisson PINN 解图
- `pinn/pinn_residual_demo.png`：PINN 残差演示图
- `pinn/surrogate_quick_scan.csv`：快速扫描数据
- `pinn/surrogate_quick_scan.png`：快速扫描图
- `pinn/pinn_training_history.json`：训练历史
