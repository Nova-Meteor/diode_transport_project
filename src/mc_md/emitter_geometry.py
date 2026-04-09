from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

E_CHARGE = 1.602176634e-19


@dataclass
class TipGeometry:
    tip_radius: float
    tip_height: float
    gap: float
    anode_voltage: float
    emission_radius: float
    radial_limit: float
    field_enhancement: float



def make_tip_geometry(config: dict) -> TipGeometry:
    geometry = config.get("geometry", {})
    tip_radius = float(geometry.get("tip_radius", 50e-9))
    tip_height = float(geometry.get("tip_height", 1e-6))
    gap = float(geometry.get("gap", 5e-6))
    anode_voltage = float(geometry.get("anode_voltage", 500.0))
    emission_radius = float(geometry.get("emission_radius", max(2.5 * tip_radius, 1.5e-7)))
    radial_limit = float(geometry.get("radial_limit", max(8.0 * emission_radius, 1.5e-6)))
    field_enhancement = float(geometry.get("field_enhancement", 4.0))
    return TipGeometry(
        tip_radius=tip_radius,
        tip_height=tip_height,
        gap=gap,
        anode_voltage=anode_voltage,
        emission_radius=emission_radius,
        radial_limit=radial_limit,
        field_enhancement=field_enhancement,
    )



def sample_emission_sites(num_electrons: int, geometry: TipGeometry, rng: np.random.Generator) -> np.ndarray:
    """Sample electrons from a small circular patch near the tip apex."""
    radii = geometry.emission_radius * np.sqrt(rng.random(num_electrons))
    angles = 2.0 * np.pi * rng.random(num_electrons)
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    # Start slightly above cathode to avoid singular self-field and zero-step sticking.
    z = np.full(num_electrons, max(0.02 * geometry.tip_radius, 1e-10))
    return np.column_stack([x, y, z])



def initial_velocities(
    num_electrons: int,
    init_energy_ev: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Create a small thermal-like spread, biased towards +z emission."""
    energy_joule = max(init_energy_ev, 1e-4) * E_CHARGE
    speed = np.sqrt(2.0 * energy_joule / 9.1093837015e-31)
    theta = np.arccos(np.sqrt(rng.random(num_electrons)))
    phi = 2.0 * np.pi * rng.random(num_electrons)
    vx = speed * np.sin(theta) * np.cos(phi)
    vy = speed * np.sin(theta) * np.sin(phi)
    vz = np.abs(speed * np.cos(theta))
    return np.column_stack([vx, vy, vz])



def external_field(
    positions: np.ndarray,
    geometry: TipGeometry,
    effective_voltage: float,
    field_reduction: float = 0.0,
) -> np.ndarray:
    """Simplified tip-to-plane field: enhanced near axis and apex, mainly along +z."""
    x = positions[:, 0]
    y = positions[:, 1]
    z = positions[:, 2]
    r2 = x * x + y * y
    background_ez = max(effective_voltage, 0.0) / max(geometry.gap, 1e-12)
    radial_profile = np.exp(-r2 / max(geometry.emission_radius**2, 1e-18))
    axial_profile = np.exp(-z / max(0.25 * geometry.gap, 1e-12))
    enhanced = geometry.field_enhancement * background_ez * radial_profile * axial_profile
    ez_mag = np.maximum(background_ez + enhanced - field_reduction, 0.0)

    # For a positively biased anode at +z, electrostatic field points mainly toward -z.
    ez = -ez_mag

    # weak electrostatic focusing toward the axis
    ex = (0.08 * background_ez / max(geometry.radial_limit, 1e-12)) * x
    ey = (0.08 * background_ez / max(geometry.radial_limit, 1e-12)) * y
    return np.column_stack([ex, ey, ez])



def estimate_emission_current_density(geometry: TipGeometry, effective_voltage: float) -> float:
    """Engineering surrogate for a minimal demonstrator; keeps values in a readable range."""
    local_field = geometry.field_enhancement * max(effective_voltage, 0.0) / max(geometry.gap, 1e-12)
    field_gv_per_m = local_field / 1e9
    return float(5.0e6 * field_gv_per_m**2 * np.exp(-1.2 / max(field_gv_per_m, 1e-6)))



def radial_distance(positions: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(positions[:, :2] ** 2, axis=1))
