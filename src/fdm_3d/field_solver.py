from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fdm_3d.grid import Grid3D


@dataclass
class SurfaceMetrics:
    center_gradient: float
    center_field_z: float
    emitter_mean_gradient: float
    emitter_max_gradient: float
    edge_mean_gradient: float
    edge_enhancement: float
    surface_gradient_map: np.ndarray



def compute_electric_field(phi: np.ndarray, grid: Grid3D) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    ex = np.zeros_like(phi)
    ey = np.zeros_like(phi)
    ez = np.zeros_like(phi)

    ex[1:-1, :, :] = -(phi[2:, :, :] - phi[:-2, :, :]) / (2.0 * grid.hx)
    ey[:, 1:-1, :] = -(phi[:, 2:, :] - phi[:, :-2, :]) / (2.0 * grid.hy)
    ez[:, :, 1:-1] = -(phi[:, :, 2:] - phi[:, :, :-2]) / (2.0 * grid.hz)

    ex[0, :, :] = -(phi[1, :, :] - phi[0, :, :]) / grid.hx
    ex[-1, :, :] = -(phi[-1, :, :] - phi[-2, :, :]) / grid.hx
    ey[:, 0, :] = -(phi[:, 1, :] - phi[:, 0, :]) / grid.hy
    ey[:, -1, :] = -(phi[:, -1, :] - phi[:, -2, :]) / grid.hy
    ez[:, :, 0] = -(phi[:, :, 1] - phi[:, :, 0]) / grid.hz
    ez[:, :, -1] = -(phi[:, :, -1] - phi[:, :, -2]) / grid.hz

    emag = np.sqrt(ex * ex + ey * ey + ez * ez)
    return ex, ey, ez, emag



def _edge_mask(mask: np.ndarray) -> np.ndarray:
    neighbors = np.zeros_like(mask, dtype=int)
    neighbors[1:, :] += mask[:-1, :]
    neighbors[:-1, :] += mask[1:, :]
    neighbors[:, 1:] += mask[:, :-1]
    neighbors[:, :-1] += mask[:, 1:]
    inner = mask & (neighbors == 4)
    return mask & (~inner)



def extract_surface_metrics(phi: np.ndarray, grid: Grid3D) -> SurfaceMetrics:
    surface_gradient = (phi[:, :, 1] - phi[:, :, 0]) / grid.hz
    emitter_gradient = surface_gradient[grid.emitter_mask_2d]

    center_i, center_j, _ = grid.center_indices
    edge_mask = _edge_mask(grid.emitter_mask_2d)
    edge_values = surface_gradient[edge_mask] if np.any(edge_mask) else emitter_gradient

    center_gradient = float(surface_gradient[center_i, center_j])
    emitter_mean = float(np.mean(emitter_gradient))
    emitter_max = float(np.max(emitter_gradient))
    edge_mean = float(np.mean(edge_values))
    edge_enhancement = float(edge_mean / center_gradient) if abs(center_gradient) > 1e-16 else float("inf")

    return SurfaceMetrics(
        center_gradient=center_gradient,
        center_field_z=-center_gradient,
        emitter_mean_gradient=emitter_mean,
        emitter_max_gradient=emitter_max,
        edge_mean_gradient=edge_mean,
        edge_enhancement=edge_enhancement,
        surface_gradient_map=surface_gradient,
    )
