# 活跃代码版本锁定说明

本文件用于锁定当前项目的**活跃代码版本**，避免后续维护时混淆“正式运行路径”和“实验/探针脚本”。

## 1. 正式统一入口

当前唯一正式入口为：

- `src/main.py`

推荐运行方式：

```bash
python src/main.py --module plate_3d --config configs/plate_3d.yaml
python src/main.py --module plate_3d --config configs/plate_3d_convergence.yaml
python src/main.py --module tip_plane --config configs/tip_plane.yaml
python src/main.py --module cross_field --config configs/cross_field.yaml
python src/main.py --module pinn --config configs/pinn.yaml
```

## 2. plate_3d 活跃文件

以下文件组成当前 `plate_3d` 的正式活跃代码路径：

- `src/fdm_3d/grid.py`
- `src/fdm_3d/cl_reference.py`
- `src/fdm_3d/field_solver.py`
- `src/fdm_3d/poisson_solver.py`
- `src/fdm_3d/current_search.py`
- `src/fdm_3d/workflow.py`
- `src/utils/plot.py`

plate_3d 的正式配置文件：

- `configs/plate_3d.yaml`：日常主算例
- `configs/plate_3d_convergence.yaml`：收敛分析/高网格验证

## 3. 其他模块活跃文件

- `tip_plane`：`src/mc_md/self_consistent_loop.py` 及其依赖
- `cross_field`：`src/cross_field/eb_motion.py` 与 `src/cross_field/sheath_estimator.py`
- `pinn`：`src/pinn/dataset.py`、`src/pinn/model.py`、`src/pinn/train.py`

## 4. 实验脚本归档

先前用于 37/55 层 warm-start 探针和临时验证的脚本，已归档至：

- `tools/experimental_plate3d/`

这些脚本**不属于正式运行路径**，仅用于研究调试和历史复现。

## 5. 锁定原则

后续若要继续维护，请遵循以下原则：

1. 新功能优先并入 `src/` 正式路径，不再把根目录探针脚本当正式代码。
2. `results/plate_3d/summary.md`、`numerical_method_note.md`、`error_budget.md` 作为当前方法和口径说明的权威文本。
3. 若后续再次切换求解器/搜索器实现，应同步更新本文件与 `README.md`。

## 6. 当前建议引用口径

对外说明时，建议使用下列三份文件作为 `plate_3d` 的正式说明入口：

- `results/plate_3d/summary.md`
- `results/plate_3d/numerical_method_note.md`
- `results/plate_3d/error_budget.md`
