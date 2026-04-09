from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import numpy as np


@dataclass
class Grid3D:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    hx: float
    hy: float
    hz: float
    emitter_mask_2d: np.ndarray
    beam_mask_3d: np.ndarray
    emitter_radius: float

    @property
    def nx(self) -> int:
        return self.x.size

    @property
    def ny(self) -> int:
        return self.y.size

    @property
    def nz(self) -> int:
        return self.z.size

    @property
    def shape(self) -> tuple[int, int, int]:
        return (self.nx, self.ny, self.nz)

    @property
    def center_indices(self) -> tuple[int, int, int]:
        return (self.nx // 2, self.ny // 2, self.nz // 2)

    @property
    def mid_y_index(self) -> int:
        return self.ny // 2


@dataclass
class BoundaryCondition:
    cathode_potential: float
    anode_potential: float
    side_boundary: str = "neumann"


@dataclass
class PlotSlices:
    phi_slice_path: Path
    field_slice_path: Path
    surface_field_path: Path
    current_scan_path: Path | None = None



def _build_emitter_mask(x: np.ndarray, y: np.ndarray, emitter_radius: float) -> np.ndarray:
    xx, yy = np.meshgrid(x, y, indexing="ij")
    return (xx**2 + yy**2) <= emitter_radius**2



def create_uniform_grid(config: Dict[str, Any], *, emitter_radius: float | None = None) -> tuple[Grid3D, BoundaryCondition]:
    geometry = config["geometry"]
    grid_cfg = config["grid"]
    boundary_cfg = config["boundary"]

    lx = float(geometry["lx"])
    ly = float(geometry["ly"])
    d = float(geometry["d"])
    radius = float(emitter_radius if emitter_radius is not None else geometry["emitter_radius"])

    nx = int(grid_cfg["nx"])
    ny = int(grid_cfg["ny"])
    nz = int(grid_cfg["nz"])

    x = np.linspace(-0.5 * lx, 0.5 * lx, nx)
    y = np.linspace(-0.5 * ly, 0.5 * ly, ny)
    z = np.linspace(float(geometry.get("cathode_z", 0.0)), float(geometry.get("anode_z", d)), nz)

    hx = float(x[1] - x[0]) if nx > 1 else 1.0
    hy = float(y[1] - y[0]) if ny > 1 else 1.0
    hz = float(z[1] - z[0]) if nz > 1 else 1.0

    emitter_mask_2d = _build_emitter_mask(x, y, radius)
    beam_mask_3d = np.repeat(emitter_mask_2d[:, :, None], nz, axis=2)
    beam_mask_3d[:, :, 0] = False
    beam_mask_3d[:, :, -1] = False

    grid = Grid3D(
        x=x,
        y=y,
        z=z,
        hx=hx,
        hy=hy,
        hz=hz,
        emitter_mask_2d=emitter_mask_2d,
        beam_mask_3d=beam_mask_3d,
        emitter_radius=radius,
    )
    bc = BoundaryCondition(
        cathode_potential=float(boundary_cfg["cathode_potential"]),
        anode_potential=float(boundary_cfg["anode_potential"]),
        side_boundary=str(boundary_cfg.get("side_boundary", "neumann")),
    )
    return grid, bc
