from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import numpy as np

from fdm_3d.cl_reference import child_langmuir_current_density, emitter_area
from fdm_3d.field_solver import SurfaceMetrics, compute_electric_field, extract_surface_metrics
from fdm_3d.grid import create_uniform_grid
from fdm_3d.poisson_solver import Plate3DSolver, SolveResult


@dataclass
class EvaluationResult:
    current_density: float
    solve_result: SolveResult
    surface_metrics: SurfaceMetrics
    field_magnitude: np.ndarray
    emitter_radius: float


@dataclass
class CurrentSearchResult:
    current_limit_density: float
    evaluations: list[tuple[float, float]]
    bracketed: bool
    status: str
    best_result: EvaluationResult



def evaluate_current_density(config: Dict[str, Any], current_density: float, *, emitter_radius: float | None = None) -> EvaluationResult:
    grid, bc = create_uniform_grid(config, emitter_radius=emitter_radius)
    solver = Plate3DSolver(config, grid, bc)
    solve_result = solver.solve_self_consistent(current_density=current_density)
    _, _, _, field_magnitude = compute_electric_field(solve_result.phi, grid)
    surface_metrics = extract_surface_metrics(solve_result.phi, grid)
    return EvaluationResult(
        current_density=current_density,
        solve_result=solve_result,
        surface_metrics=surface_metrics,
        field_magnitude=field_magnitude,
        emitter_radius=grid.emitter_radius,
    )



def _surface_objective(result: EvaluationResult) -> float:
    return result.surface_metrics.center_gradient



def find_current_limit(config: Dict[str, Any], *, emitter_radius: float | None = None) -> CurrentSearchResult:
    search_cfg = config.get("search", {})
    j_cl = child_langmuir_current_density(config)
    injected = float(config["physics"].get("injected_current_density", j_cl))
    factors = search_cfg.get("scan_factors", [0.3, 0.6, 0.9, 1.2, 1.5])
    base_reference = str(search_cfg.get("base_reference", "cl")).lower()
    base_value = injected if base_reference == "injected" else j_cl
    absolute_values = [max(1.0, float(f) * base_value) for f in factors]

    evaluations: list[tuple[float, float]] = []
    full_results: list[EvaluationResult] = []
    bracket: tuple[EvaluationResult, EvaluationResult] | None = None

    for value in absolute_values:
        result = evaluate_current_density(config, value, emitter_radius=emitter_radius)
        objective = _surface_objective(result)
        evaluations.append((value, objective))
        full_results.append(result)
        if len(full_results) >= 2:
            prev = full_results[-2]
            curr = full_results[-1]
            if _surface_objective(prev) == 0.0:
                bracket = (prev, prev)
                break
            if _surface_objective(prev) * _surface_objective(curr) < 0.0:
                bracket = (prev, curr)
                break

    if bracket is None:
        best_result = min(full_results, key=lambda item: abs(_surface_objective(item)))
        return CurrentSearchResult(
            current_limit_density=best_result.current_density,
            evaluations=evaluations,
            bracketed=False,
            status="未找到严格变号区间，返回最接近阴极表面零场的样本值。",
            best_result=best_result,
        )

    left, right = bracket
    if left.current_density == right.current_density:
        return CurrentSearchResult(
            current_limit_density=left.current_density,
            evaluations=evaluations,
            bracketed=True,
            status="采样阶段已命中近似零场点。",
            best_result=left,
        )

    best_result = left if abs(_surface_objective(left)) < abs(_surface_objective(right)) else right
    max_iter = int(search_cfg.get("max_iter", 5))
    tol = float(search_cfg.get("objective_tol", 5.0e2))

    jl, fl = left.current_density, _surface_objective(left)
    jr, fr = right.current_density, _surface_objective(right)

    for _ in range(max_iter):
        if abs(fr - fl) < 1.0e-12:
            jm = 0.5 * (jl + jr)
        else:
            jm = jr - fr * (jr - jl) / (fr - fl)
            if not (min(jl, jr) < jm < max(jl, jr)):
                jm = 0.5 * (jl + jr)

        mid = evaluate_current_density(config, jm, emitter_radius=emitter_radius)
        fm = _surface_objective(mid)
        evaluations.append((jm, fm))
        if abs(fm) < abs(_surface_objective(best_result)):
            best_result = mid
        if abs(fm) < tol:
            best_result = mid
            break
        if fl * fm < 0.0:
            jr, fr = jm, fm
        else:
            jl, fl = jm, fm

    return CurrentSearchResult(
        current_limit_density=best_result.current_density,
        evaluations=evaluations,
        bracketed=True,
        status="使用扫描 + 割线/二分混合方法得到近似极限电流密度。",
        best_result=best_result,
    )



def sweep_emitter_radius(config: Dict[str, Any]) -> list[dict[str, float]]:
    geometry = config["geometry"]
    base_radius = float(geometry["emitter_radius"])
    factors = config.get("search", {}).get("radius_factors", [0.6, 0.8, 1.0, 1.2])
    j_cl = child_langmuir_current_density(config)
    data: list[dict[str, float]] = []

    for factor in factors:
        radius = base_radius * float(factor)
        current_result = find_current_limit(config, emitter_radius=radius)
        area = emitter_area(config, radius)
        j_lim = current_result.current_limit_density
        data.append(
            {
                "radius_factor": float(factor),
                "emitter_radius": radius,
                "emitter_area": area,
                "j_limit": j_lim,
                "j_over_jcl": j_lim / j_cl if j_cl > 0 else float("nan"),
                "edge_enhancement": current_result.best_result.surface_metrics.edge_enhancement,
            }
        )
    return data
