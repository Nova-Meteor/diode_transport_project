
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from fdm_3d.grid import Grid3D


def plot_plate_phi_slice(phi: np.ndarray, grid: Grid3D, path: Path) -> None:
    mid_y = grid.mid_y_index
    fig, ax = plt.subplots(figsize=(6, 4.8))
    im = ax.imshow(
        phi[:, mid_y, :].T,
        origin='lower',
        aspect='auto',
        extent=[grid.x[0], grid.x[-1], grid.z[0], grid.z[-1]],
    )
    ax.set_xlabel('x (m)')
    ax.set_ylabel('z (m)')
    ax.set_title('Mid-plane potential distribution')
    fig.colorbar(im, ax=ax, label='Potential (V)')
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_plate_field_slice(field_mag: np.ndarray, grid: Grid3D, path: Path) -> None:
    mid_y = grid.mid_y_index
    fig, ax = plt.subplots(figsize=(6, 4.8))
    im = ax.imshow(
        field_mag[:, mid_y, :].T,
        origin='lower',
        aspect='auto',
        extent=[grid.x[0], grid.x[-1], grid.z[0], grid.z[-1]],
    )
    ax.set_xlabel('x (m)')
    ax.set_ylabel('z (m)')
    ax.set_title('Mid-plane electric field magnitude')
    fig.colorbar(im, ax=ax, label='|E| (V/m)')
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_plate_surface_field(surface_gradient_map: np.ndarray, grid: Grid3D, path: Path) -> None:
    mid_y = grid.mid_y_index
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(grid.x, surface_gradient_map[:, mid_y], label='surface dphi/dz')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('dphi/dz at cathode surface (V/m)')
    ax.set_title('Cathode surface gradient along mid-line')
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_current_scan(evaluations: list[tuple[float, float]], current_limit: float, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    js = [x for x, _ in evaluations]
    fs = [y for _, y in evaluations]
    ax.plot(js, fs, marker='o')
    ax.axhline(0.0, linestyle='--', linewidth=1.0)
    ax.axvline(current_limit, linestyle=':', linewidth=1.0)
    ax.set_xlabel('Current density J (A/m²)')
    ax.set_ylabel('Cathode surface objective f(J) (V/m)')
    ax.set_title('Current-limit search history')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_search_convergence(evaluations: list[tuple[float, float]], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(range(1, len(evaluations) + 1), [abs(y) for _, y in evaluations], marker='o')
    ax.set_xlabel('Search iteration')
    ax.set_ylabel('|f(J)| (V/m)')
    ax.set_title('Search convergence history')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_radius_sweep(radius_rows: list[dict[str, float]], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(
        [row['emitter_radius'] for row in radius_rows],
        [row['j_over_jcl'] for row in radius_rows],
        marker='o',
    )
    ax.set_xlabel('Emitter radius (m)')
    ax.set_ylabel('J_lim / J_CL')
    ax.set_title('Emitter-radius correction trend')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
