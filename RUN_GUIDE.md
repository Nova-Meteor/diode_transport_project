# 运行指南（RUN_GUIDE）

本文档给出本项目的推荐运行顺序、各配置文件用途、常见命令与结果查看路径。建议先阅读 `README.md`，再按本文档执行。

---

## 1. 推荐运行顺序

若希望尽快确认工程可运行，建议按以下顺序执行：

1. 查看可用模块
2. 运行 `cross_field` 或 `tip_plane` 轻量模块，确认入口与图表输出正常
3. 运行 `plate_3d` 主算例
4. 运行 `pinn` 辅助模块
5. 如需数值验证，再运行 `plate_3d_convergence.yaml`
6. 最后运行回归测试，确认当前版本没有被改坏

推荐顺序如下：

```bash
python src/main.py --list
python src/main.py --module cross_field --config configs/cross_field.yaml
python src/main.py --module tip_plane --config configs/tip_plane.yaml
python src/main.py --module plate_3d --config configs/plate_3d.yaml
python src/main.py --module pinn --config configs/pinn.yaml
python src/main.py --module plate_3d --config configs/plate_3d_convergence.yaml
PYTHONPATH=src python -m unittest discover -s tests -v
```

---

## 2. 配置文件用途说明

### 2.1 `configs/plate_3d.yaml`

用于三维平板二极管主算例。适合：
- 主结果复现
- 参数扫描
- 结果图生成
- 结题/汇报中的主线结果展示

输出目录主要为：
- `results/plate_3d/`
- `results/plate_3d/final_release/`

### 2.2 `configs/plate_3d_convergence.yaml`

用于三维平板二极管网格收敛与误差分析。适合：
- Richardson / GCI 报告复现
- 高网格验证
- 数值方法章节的支撑材料生成

输出目录主要为：
- `results/plate_3d/convergence/`
- `results/plate_3d/` 下的收敛分析图与报告

### 2.3 `configs/tip_plane.yaml`

用于针尖-平板 MC/MD 工程强化版。适合：
- 轨迹图生成
- 能量分布与能谱展宽展示
- 电压扫描结果复现

输出目录主要为：
- `results/tip_plane/`

### 2.4 `configs/cross_field.yaml`

用于交叉场汇报版结果。适合：
- E×B 漂移演示
- 轨道包络与磁场扫描
- 漂移速度 / Larmor 半径关系图输出

输出目录主要为：
- `results/cross_field/`

### 2.5 `configs/pinn.yaml`

用于 AI/PINN 辅助模块。适合：
- surrogate 代理模型训练
- 1D Poisson PINN demo 复现
- 快速参数扫描辅助结果生成

输出目录主要为：
- `results/pinn/`

---

## 3. 常用运行命令

### 3.1 查看可用模块

```bash
python src/main.py --list
```

### 3.2 运行主模块 `plate_3d`

```bash
python src/main.py --module plate_3d --config configs/plate_3d.yaml
```

### 3.3 运行网格收敛分析

```bash
python src/main.py --module plate_3d --config configs/plate_3d_convergence.yaml
```

### 3.4 运行针尖模块

```bash
python src/main.py --module tip_plane --config configs/tip_plane.yaml
```

### 3.5 运行交叉场模块

```bash
python src/main.py --module cross_field --config configs/cross_field.yaml
```

### 3.6 运行 AI/PINN 辅助模块

```bash
python src/main.py --module pinn --config configs/pinn.yaml
```

---

## 4. 结果查看建议

### 4.1 `plate_3d`
优先查看：
- `results/plate_3d/summary.md`
- `results/plate_3d/numerical_method_note.md`
- `results/plate_3d/error_budget.md`
- `results/plate_3d/grid_convergence_report.md`

图表优先查看：
- `plate_phi_slice.png`
- `plate_field_slice.png`
- `plate_surface_field.png`
- `plate_current_limit.png`
- `plate_grid_convergence.png`
- `plate_grid_error.png`

### 4.2 `tip_plane`
优先查看：
- `results/tip_plane/summary.md`
- `tip_trajectory.png`
- `tip_energy_hist.png`
- `tip_coulomb_compare.png`

### 4.3 `cross_field`
优先查看：
- `results/cross_field/summary.md`
- `cross_field_orbit.png`
- `cross_field_bscan.png`
- `cross_field_transport_scan.png`

### 4.4 `pinn`
优先查看：
- `results/pinn/summary.md`
- `surrogate_training_loss.png`
- `pinn_prediction.png`
- `pinn_solution.png`
- `surrogate_quick_scan.png`

---

## 5. 回归测试

项目内置最基本的 smoke/regression 测试，用于确认四个模块入口仍然可用。

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

说明：
- 测试采用轻量配置，目标是尽快发现入口失效或结果文件路径失效
- 测试通过不代表物理精度已经达到论文终稿要求，只代表工程入口和基本输出正常

---

## 6. 建议的复现口径

如果只是为了展示项目结果，建议复现以下三部分：

1. `plate_3d` 主算例
2. `tip_plane` 或 `cross_field` 任一扩展模块
3. `pinn` quick scan 辅助结果

如果是为了写方法或数值验证部分，建议再补：

4. `plate_3d_convergence.yaml`
5. `grid_convergence_report.md`
6. `error_budget.md`

---

## 7. 常见注意事项

- 建议始终在项目根目录执行命令
- 若直接运行 `python src/main.py` 不带参数，程序只会提示模块与配置用法，不会默认执行任何模块
- 若在 Windows PowerShell 中运行，请先激活虚拟环境，再执行相同命令
- 若修改了 `src/` 下的活跃求解器或工作流，建议立即运行一次 `tests/test_regression.py` 进行回归检查

