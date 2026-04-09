from __future__ import annotations

import numpy as np

EPS0 = 8.8541878128e-12
E_CHARGE = 1.602176634e-19
COULOMB_PREFAC = E_CHARGE / (4.0 * np.pi * EPS0)



def electron_coulomb_field(
    positions: np.ndarray,
    active_mask: np.ndarray,
    softening_length: float,
    max_neighbors: int | None = None,
) -> np.ndarray:
    """Electric field caused by other electrons. O(N^2), acceptable for small N."""
    n = len(positions)
    field = np.zeros_like(positions)
    active_indices = np.where(active_mask)[0]
    if active_indices.size <= 1:
        return field

    active_positions = positions[active_indices]
    for local_i, idx_i in enumerate(active_indices):
        delta = positions[idx_i] - active_positions
        dist2 = np.sum(delta * delta, axis=1) + softening_length**2
        valid = dist2 > softening_length**2 * 1.0000001
        if not np.any(valid):
            continue
        delta = delta[valid]
        dist2 = dist2[valid]
        if max_neighbors is not None and len(dist2) > max_neighbors:
            nearest = np.argpartition(dist2, max_neighbors)[:max_neighbors]
            delta = delta[nearest]
            dist2 = dist2[nearest]
        inv_dist3 = 1.0 / np.power(dist2, 1.5)
        field[idx_i] = -COULOMB_PREFAC * np.sum(delta * inv_dist3[:, None], axis=0)
    return field
