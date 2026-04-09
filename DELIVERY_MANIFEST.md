# DELIVERY_MANIFEST

## 建议提交内容
- `PROJECT_FINAL_NOTE.md`
- `FINAL_MATERIALS_INDEX.md`
- `README.md`
- `ACTIVE_CODE_LOCK.md`
- `RUN_GUIDE.md`
- `ENVIRONMENT_AND_REPRODUCIBILITY.md`
- `requirements.txt`
- `configs/`
- `src/`
- `results/`
- `tests/`
- `DELIVERY_MANIFEST.md`

## 建议最先展示的材料
1. `PROJECT_FINAL_NOTE.md`
2. `FINAL_MATERIALS_INDEX.md`
3. `results/plate_3d/summary.md`
4. `results/plate_3d/plate_phi_slice.png`
5. `results/plate_3d/plate_field_slice.png`
6. `results/plate_3d/plate_current_limit.png`
7. `results/plate_3d/plate_grid_convergence.png`
8. `results/tip_plane/summary.md`
9. `results/cross_field/summary.md`
10. `results/pinn/summary.md`

## 推荐阅读顺序
1. `PROJECT_FINAL_NOTE.md`
2. `FINAL_MATERIALS_INDEX.md`
3. `README.md`
4. `results/summary_table.md`
5. `results/all_results_index.md`
6. `results/plate_3d/summary.md`
7. `results/plate_3d/numerical_method_note.md`
8. `results/plate_3d/error_budget.md`
9. `results/plate_3d/grid_convergence_report.md`

## 常用运行命令
### 单模块
```bash
python src/main.py --module plate_3d --config configs/plate_3d.yaml
python src/main.py --module tip_plane --config configs/tip_plane.yaml
python src/main.py --module cross_field --config configs/cross_field.yaml
python src/main.py --module pinn --config configs/pinn.yaml
```

### 回归测试
```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## 交付说明
当前工程已经包含：
- 主线模块 `plate_3d` 的正式结果与数值说明
- 三个扩展模块的正式汇报说明
- 运行与复现说明
- 最小回归测试

若用于结题或阶段汇报，建议优先围绕 `plate_3d` 展开，把其余三个模块作为扩展研究方向说明。
