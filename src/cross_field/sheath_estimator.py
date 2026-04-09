from __future__ import annotations

from typing import Any, Dict

import numpy as np


def estimate_sheath_metrics(
    E: np.ndarray,
    B: np.ndarray,
    charge: float,
    mass: float,
    velocities: np.ndarray,
    dt: float,
) -> Dict[str, float]:
    """Return rough single-particle scale indicators for the MVP cross-field module.

    These are engineering estimates for visualization and comparison only.
    """
    E_mag = float(np.linalg.norm(E))
    B_mag = float(np.linalg.norm(B))
    v_mean = np.mean(np.linalg.norm(velocities, axis=1)) if velocities.size else 0.0
    v_perp = v_mean

    if B_mag > 0.0:
        omega_c = abs(charge) * B_mag / mass
        larmor_radius = v_perp / max(omega_c, 1e-30)
        exb = np.linalg.norm(np.cross(E, B)) / max(B_mag * B_mag, 1e-30)
        sheath_thickness = max(larmor_radius, exb * dt * 50.0)
    else:
        omega_c = 0.0
        larmor_radius = 0.0
        exb = 0.0
        accel = abs(charge) * E_mag / mass
        sheath_thickness = 0.5 * accel * (50.0 * dt) ** 2

    return {
        "cyclotron_frequency_rad_per_s": float(omega_c),
        "larmor_radius_m": float(larmor_radius),
        "exb_drift_m_per_s": float(exb),
        "sheath_thickness_m": float(sheath_thickness),
    }
