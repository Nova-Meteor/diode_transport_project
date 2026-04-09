from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from mc_md.coulomb import electron_coulomb_field
from mc_md.emitter_geometry import TipGeometry, external_field, radial_distance

E_CHARGE = 1.602176634e-19
E_MASS = 9.1093837015e-31


@dataclass
class SimulationResult:
    positions: np.ndarray
    velocities: np.ndarray
    active_mask: np.ndarray
    reached_anode: np.ndarray
    lost_radially: np.ndarray
    trapped: np.ndarray
    trajectories: np.ndarray
    final_energy_ev: np.ndarray
    transmitted_fraction: float
    loop_diagnostics: dict[str, Any]



def kinetic_energy_ev(velocities: np.ndarray) -> np.ndarray:
    speed2 = np.sum(velocities * velocities, axis=1)
    return 0.5 * E_MASS * speed2 / E_CHARGE



def simulate_particles(
    positions: np.ndarray,
    velocities: np.ndarray,
    geometry: TipGeometry,
    effective_voltage: float,
    dt: float,
    steps: int,
    include_coulomb: bool,
    softening_length: float,
    tracked_particles: int,
    field_reduction: float,
    max_neighbors: int | None = None,
) -> SimulationResult:
    n = len(positions)
    pos = positions.copy()
    vel = velocities.copy()
    active_mask = np.ones(n, dtype=bool)
    reached_anode = np.zeros(n, dtype=bool)
    lost_radially = np.zeros(n, dtype=bool)
    tracked = min(tracked_particles, n)
    trajectories = np.zeros((steps + 1, tracked, 3), dtype=float)
    trajectories[0] = pos[:tracked]

    accel_scale = -E_CHARGE / E_MASS
    for step in range(steps):
        ext_field = external_field(pos, geometry, effective_voltage, field_reduction=field_reduction)
        if include_coulomb:
            coul_field = electron_coulomb_field(
                pos,
                active_mask=active_mask,
                softening_length=softening_length,
                max_neighbors=max_neighbors,
            )
        else:
            coul_field = np.zeros_like(pos)
        total_field = ext_field + coul_field
        total_field[~active_mask] = 0.0

        vel += accel_scale * total_field * dt
        pos += vel * dt

        radial = radial_distance(pos)
        new_reached = active_mask & (pos[:, 2] >= geometry.gap)
        new_lost = active_mask & (radial >= geometry.radial_limit)
        new_back = active_mask & (pos[:, 2] <= 0.0)

        reached_anode[new_reached] = True
        lost_radially[new_lost] = True
        active_mask[new_reached | new_lost | new_back] = False

        pos[new_reached, 2] = geometry.gap
        pos[new_back, 2] = 0.0

        trajectories[step + 1] = pos[:tracked]
        if not np.any(active_mask):
            trajectories[step + 1 :] = trajectories[step + 1]
            break

    trapped = active_mask.copy()
    final_energy = kinetic_energy_ev(vel)
    transmitted_fraction = float(np.mean(reached_anode))
    diagnostics = {
        "num_reached_anode": int(np.sum(reached_anode)),
        "num_lost_radially": int(np.sum(lost_radially)),
        "num_trapped": int(np.sum(trapped)),
        "mean_final_energy_ev": float(np.mean(final_energy)),
        "mean_transmitted_energy_ev": float(np.mean(final_energy[reached_anode])) if np.any(reached_anode) else 0.0,
        "mean_radial_exit_energy_ev": float(np.mean(final_energy[lost_radially])) if np.any(lost_radially) else 0.0,
    }
    return SimulationResult(
        positions=pos,
        velocities=vel,
        active_mask=active_mask,
        reached_anode=reached_anode,
        lost_radially=lost_radially,
        trapped=trapped,
        trajectories=trajectories,
        final_energy_ev=final_energy,
        transmitted_fraction=transmitted_fraction,
        loop_diagnostics=diagnostics,
    )
