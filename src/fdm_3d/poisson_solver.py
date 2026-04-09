from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import numpy as np

from fdm_3d.grid import BoundaryCondition, Grid3D


@dataclass
class SolveResult:
    phi: np.ndarray
    rho: np.ndarray
    iterations: int
    outer_iterations: int
    converged: bool
    max_delta: float
    history: list[float]


class Plate3DSolver:
    def __init__(self, config: Dict[str, Any], grid: Grid3D, bc: BoundaryCondition):
        self.config = config
        self.grid = grid
        self.bc = bc
        self.physics = config["physics"]
        self.solver_cfg = config["solver"]
        self.electron_charge = abs(float(self.physics.get("electron_charge", 1.602176634e-19)))
        self.electron_mass = float(self.physics.get("electron_mass", 9.1093837015e-31))
        self.epsilon0 = float(self.physics.get("epsilon0", 8.854e-12))
        self.phi_floor = float(self.physics.get("phi_floor", 0.5))

        self.hx2 = grid.hx * grid.hx
        self.hy2 = grid.hy * grid.hy
        self.hz2 = grid.hz * grid.hz
        self.inv_hx2 = 1.0 / self.hx2
        self.inv_hy2 = 1.0 / self.hy2
        self.inv_hz2 = 1.0 / self.hz2
        self.denom = 2.0 * (self.inv_hx2 + self.inv_hy2 + self.inv_hz2)

        nx, ny, nz = grid.shape
        ii, jj, kk = np.indices((nx - 2, ny - 2, nz - 2))
        red_mask = ((ii + jj + kk) % 2) == 0
        self.red_mask = red_mask
        self.black_mask = ~red_mask

    def initialize_potential(self) -> np.ndarray:
        phi = np.zeros(self.grid.shape, dtype=float)
        z_norm = (self.grid.z - self.grid.z[0]) / (self.grid.z[-1] - self.grid.z[0])
        for k, weight in enumerate(z_norm):
            phi[:, :, k] = self.bc.cathode_potential + weight * (self.bc.anode_potential - self.bc.cathode_potential)
        phi[:, :, 0] = self.bc.cathode_potential
        phi[:, :, -1] = self.bc.anode_potential
        self._apply_side_boundaries(phi)
        return phi

    def _apply_side_boundaries(self, phi: np.ndarray) -> None:
        if self.bc.side_boundary.lower() == "neumann":
            phi[0, :, :] = phi[1, :, :]
            phi[-1, :, :] = phi[-2, :, :]
            phi[:, 0, :] = phi[:, 1, :]
            phi[:, -1, :] = phi[:, -2, :]
        else:
            phi[0, :, :] = self.bc.cathode_potential
            phi[-1, :, :] = self.bc.cathode_potential
            phi[:, 0, :] = self.bc.cathode_potential
            phi[:, -1, :] = self.bc.cathode_potential
        phi[:, :, 0] = self.bc.cathode_potential
        phi[:, :, -1] = self.bc.anode_potential

    def compute_space_charge_density(self, phi: np.ndarray, current_density: float) -> np.ndarray:
        rho = np.zeros_like(phi)
        phi_eff = np.maximum(phi, self.phi_floor)
        velocity = np.sqrt(np.maximum(2.0 * self.electron_charge * phi_eff / self.electron_mass, 1.0))
        rho[self.grid.beam_mask_3d] = -current_density / velocity[self.grid.beam_mask_3d]
        rho[:, :, 0] = 0.0
        rho[:, :, -1] = 0.0
        return rho

    def _candidate_interior(self, phi: np.ndarray, rho: np.ndarray) -> np.ndarray:
        return (
            (phi[2:, 1:-1, 1:-1] + phi[:-2, 1:-1, 1:-1]) * self.inv_hx2
            + (phi[1:-1, 2:, 1:-1] + phi[1:-1, :-2, 1:-1]) * self.inv_hy2
            + (phi[1:-1, 1:-1, 2:] + phi[1:-1, 1:-1, :-2]) * self.inv_hz2
            + rho[1:-1, 1:-1, 1:-1] / self.epsilon0
        ) / self.denom

    def solve_fixed_rho(self, phi: np.ndarray, rho: np.ndarray) -> tuple[np.ndarray, int, bool, float, list[float]]:
        omega = float(self.solver_cfg.get("omega", 1.6))
        tol = float(self.solver_cfg.get("tol", 1.0e-6))
        max_iter = int(self.solver_cfg.get("max_iter", 600))
        history: list[float] = []

        converged = False
        max_delta = np.inf
        for iteration in range(1, max_iter + 1):
            max_delta = 0.0
            interior = phi[1:-1, 1:-1, 1:-1]
            for mask in (self.red_mask, self.black_mask):
                candidate = self._candidate_interior(phi, rho)
                delta = omega * (candidate - interior)
                if mask.any():
                    current_delta = float(np.max(np.abs(delta[mask])))
                    if current_delta > max_delta:
                        max_delta = current_delta
                    interior[mask] += delta[mask]
                self._apply_side_boundaries(phi)

            history.append(max_delta)
            if max_delta < tol:
                converged = True
                break

        self._apply_side_boundaries(phi)
        return phi, iteration, converged, max_delta, history

    def solve_self_consistent(self, current_density: float) -> SolveResult:
        outer_max_iter = int(self.solver_cfg.get("outer_max_iter", 5))
        outer_tol = float(self.solver_cfg.get("outer_tol", 5.0e-5))
        phi = self.initialize_potential()
        rho = np.zeros_like(phi)
        history: list[float] = []
        converged = False
        final_iterations = 0
        max_delta = np.inf

        for outer in range(1, outer_max_iter + 1):
            old_phi = phi.copy()
            rho = self.compute_space_charge_density(phi, current_density)
            phi, final_iterations, inner_converged, max_delta, inner_history = self.solve_fixed_rho(phi, rho)
            history.extend(inner_history)
            outer_change = float(np.max(np.abs(phi - old_phi)))
            if outer_change < outer_tol and inner_converged:
                converged = True
                return SolveResult(
                    phi=phi,
                    rho=rho,
                    iterations=final_iterations,
                    outer_iterations=outer,
                    converged=True,
                    max_delta=max_delta,
                    history=history,
                )

        return SolveResult(
            phi=phi,
            rho=rho,
            iterations=final_iterations,
            outer_iterations=outer_max_iter,
            converged=converged,
            max_delta=max_delta,
            history=history,
        )
