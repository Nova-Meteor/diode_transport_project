
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fdm_3d.cl_reference import child_langmuir_current_density
from fdm_3d.current_search import find_current_limit, sweep_emitter_radius
from fdm_3d.grid import create_uniform_grid
from utils.plot import (
    plot_current_scan,
    plot_plate_field_slice,
    plot_plate_phi_slice,
    plot_plate_surface_field,
    plot_radius_sweep,
    plot_search_convergence,
)


def run_plate_3d_workflow(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    search_result = find_current_limit(config)
    best = search_result.best_result
    solve_result = best.solve_result
    metrics = best.surface_metrics
    grid, _ = create_uniform_grid(config, emitter_radius=best.emitter_radius)
    j_cl = child_langmuir_current_density(config)

    summary = {
        'module': 'plate_3d',
        'j_cl': j_cl,
        'j_lim': search_result.current_limit_density,
        'j_over_jcl': search_result.current_limit_density / j_cl if j_cl > 0 else float('nan'),
        'center_gradient': metrics.center_gradient,
        'center_field_z': metrics.center_field_z,
        'emitter_mean_gradient': metrics.emitter_mean_gradient,
        'emitter_max_gradient': metrics.emitter_max_gradient,
        'edge_mean_gradient': metrics.edge_mean_gradient,
        'edge_enhancement': metrics.edge_enhancement,
        'solver_iterations': int(solve_result.iterations),
        'outer_iterations': int(solve_result.outer_iterations),
        'converged': bool(solve_result.converged),
        'max_delta': float(solve_result.max_delta),
        'search_status': search_result.status,
        'search_bracketed': bool(search_result.bracketed),
        'search_evaluations': [
            {'current_density': float(j), 'objective': float(f)} for j, f in search_result.evaluations
        ],
    }

    radius_rows = sweep_emitter_radius(config)
    with (output_dir / 'plate_summary.json').open('w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with (output_dir / 'plate_search_history.json').open('w', encoding='utf-8') as f:
        json.dump(summary['search_evaluations'], f, ensure_ascii=False, indent=2)
    with (output_dir / 'radius_sweep.json').open('w', encoding='utf-8') as f:
        json.dump(radius_rows, f, ensure_ascii=False, indent=2)

    plot_plate_phi_slice(solve_result.phi, grid, output_dir / 'plate_phi_slice.png')
    plot_plate_field_slice(best.field_magnitude, grid, output_dir / 'plate_field_slice.png')
    plot_plate_surface_field(metrics.surface_gradient_map, grid, output_dir / 'plate_surface_field.png')
    plot_current_scan(search_result.evaluations, search_result.current_limit_density, output_dir / 'plate_current_limit.png')
    plot_search_convergence(search_result.evaluations, output_dir / 'plate_search_convergence.png')
    plot_radius_sweep(radius_rows, output_dir / 'plate_radius_sweep.png')

    summary_md = f"""# plate_3d 结果摘要

## 1. 当前模型定位

- 当前版本为三维平板二极管有限差分主模块的第一版工程实现。
- 数值方法采用非线性泊松方程 + SOR 迭代 + 电流扫描 / 割线 / 二分混合搜索。
- 当前结果适合作为项目日内闭环与参数趋势展示，不作为最终论文级高精度结论。

## 2. 核心结果

- 1D Child-Langmuir 基准电流密度: {summary['j_cl']:.6e} A/m²
- 当前近似极限电流密度: {summary['j_lim']:.6e} A/m²
- 相对 CL 修正 J_lim / J_CL: {summary['j_over_jcl']:.6f}
- 阴极中心表面势梯度 dphi/dz: {summary['center_gradient']:.6e} V/m
- 阴极中心法向电场 Ez: {summary['center_field_z']:.6e} V/m
- 发射区平均表面势梯度: {summary['emitter_mean_gradient']:.6e} V/m
- 发射区边缘增强系数: {summary['edge_enhancement']:.6f}
- 内层迭代步数: {summary['solver_iterations']}
- 外层自洽迭代步数: {summary['outer_iterations']}
- 是否收敛: {summary['converged']}
- 搜索说明: {summary['search_status']}

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
"""
    (output_dir / 'summary.md').write_text(summary_md, encoding='utf-8')

    return summary
