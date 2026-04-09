from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .sheath_estimator import estimate_sheath_metrics

E_CHARGE = 1.602176634e-19
E_MASS = 9.1093837015e-31


def _vec3(values: Any, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.shape != (3,):
        raise ValueError(f"{name} 必须是长度为 3 的数组")
    return arr


def build_initial_state(config: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, float, float, float]:
    particles = config.get("particles", {})
    num_particles = int(particles.get("num_particles", 9))
    charge = float(particles.get("charge", -E_CHARGE))
    mass = float(particles.get("mass", E_MASS))
    dt = float(particles.get("dt", 5.0e-13))

    initial_position = _vec3(particles.get("initial_position", [0.0, 0.0, 0.0]), "initial_position")
    initial_velocity = _vec3(particles.get("initial_velocity", [6.0e5, 0.0, 0.0]), "initial_velocity")
    position_spread = _vec3(particles.get("initial_position_spread", [1.0e-5, 0.0, 1.0e-6]), "initial_position_spread")
    velocity_spread = _vec3(particles.get("initial_velocity_spread", [1.2e5, 6.0e4, 1.0e5]), "initial_velocity_spread")

    rng = np.random.default_rng(int(config.get("general", {}).get("random_seed", 42)))
    positions = initial_position + rng.normal(size=(num_particles, 3)) * position_spread
    velocities = initial_velocity + rng.normal(size=(num_particles, 3)) * velocity_spread
    return positions, velocities, charge, mass, dt


def compute_space_charge_placeholder(
    positions: np.ndarray,
    charge: float,
    mass: float,
    solver_cfg: Dict[str, Any],
) -> np.ndarray:
    """Simplified pairwise repulsion placeholder with softening and scaling.

    This is intentionally lightweight and only meant to provide a qualitative
    cross-field space-charge deflection hook for the MVP project version.
    """
    if not solver_cfg.get("include_space_charge_placeholder", True):
        return np.zeros_like(positions)

    softening = float(solver_cfg.get("softening", 2.0e-6))
    scale = float(solver_cfg.get("placeholder_strength", 5.0e-4))
    n = positions.shape[0]
    accel = np.zeros_like(positions)
    coulomb_k = 8.9875517923e9

    for i in range(n):
        rij = positions[i] - positions
        r2 = np.sum(rij * rij, axis=1) + softening**2
        r2[i] = np.inf
        inv_r3 = 1.0 / (r2 * np.sqrt(r2))
        force = coulomb_k * charge * charge * np.sum(rij * inv_r3[:, None], axis=0)
        accel[i] = scale * force / mass
    return accel


def boris_push(
    positions: np.ndarray,
    velocities: np.ndarray,
    charge: float,
    mass: float,
    dt: float,
    E: np.ndarray,
    B: np.ndarray,
    extra_accel: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    qmdt2 = charge * dt / (2.0 * mass)
    E_eff = E.copy()
    if extra_accel is not None:
        E_eff = E_eff[None, :] + (mass / charge) * extra_accel
    else:
        E_eff = np.broadcast_to(E_eff, positions.shape)

    v_minus = velocities + qmdt2 * E_eff
    t = qmdt2 * B
    t2 = np.dot(t, t)
    s = 2.0 * t / (1.0 + t2)
    v_prime = v_minus + np.cross(v_minus, t)
    v_plus = v_minus + np.cross(v_prime, s)
    v_new = v_plus + qmdt2 * E_eff
    x_new = positions + v_new * dt
    return x_new, v_new


def kinetic_energy_ev(velocities: np.ndarray, mass: float) -> np.ndarray:
    return 0.5 * mass * np.sum(velocities * velocities, axis=1) / E_CHARGE


def simulate_cross_field_case(
    config: Dict[str, Any],
    B_override: np.ndarray | None = None,
) -> Dict[str, Any]:
    fields = config.get("fields", {})
    solver_cfg = config.get("solver", {})
    steps = int(config.get("particles", {}).get("steps", 2500))

    positions, velocities, charge, mass, dt = build_initial_state(config)
    E = _vec3(fields.get("E", [0.0, 0.0, -8.0e4]), "E")
    B = _vec3(fields.get("B", [0.0, 0.08, 0.0]), "B") if B_override is None else B_override.astype(float)

    n = positions.shape[0]
    traj = np.zeros((steps + 1, min(5, n), 3), dtype=float)
    energy_history = np.zeros((steps + 1, n), dtype=float)
    center_history = np.zeros((steps + 1, 3), dtype=float)
    speed_history = np.zeros(steps + 1, dtype=float)

    traj[0] = positions[: traj.shape[1]]
    energy_history[0] = kinetic_energy_ev(velocities, mass)
    center_history[0] = positions.mean(axis=0)
    speed_history[0] = np.linalg.norm(velocities, axis=1).mean()

    for step in range(1, steps + 1):
        extra_accel = compute_space_charge_placeholder(positions, charge, mass, solver_cfg)
        positions, velocities = boris_push(
            positions, velocities, charge, mass, dt, E, B, extra_accel
        )
        traj[step] = positions[: traj.shape[1]]
        energy_history[step] = kinetic_energy_ev(velocities, mass)
        center_history[step] = positions.mean(axis=0)
        speed_history[step] = np.linalg.norm(velocities, axis=1).mean()

    times = np.arange(steps + 1, dtype=float) * dt
    mean_energy = energy_history[-1].mean()
    drift_velocity = (center_history[-1] - center_history[0]) / max(times[-1], 1e-30)
    gyro_radius = estimate_sheath_metrics(E, B, charge, mass, velocities, dt)["larmor_radius_m"]

    return {
        "times": times,
        "trajectory": traj,
        "center_history": center_history,
        "energy_history": energy_history,
        "speed_history": speed_history,
        "final_positions": positions,
        "final_velocities": velocities,
        "mean_final_energy_ev": float(mean_energy),
        "drift_velocity_m_per_s": drift_velocity.tolist(),
        "larmor_radius_m": float(gyro_radius),
        "E": E.tolist(),
        "B": B.tolist(),
        "num_particles": n,
    }


def run_magnetic_scan(config: Dict[str, Any]) -> list[dict[str, float]]:
    fields = config.get("fields", {})
    B_base = _vec3(fields.get("B", [0.0, 0.08, 0.0]), "B")
    base_mag = float(np.linalg.norm(B_base))
    if base_mag == 0.0:
        direction = np.array([0.0, 1.0, 0.0])
        base_mag = 1.0
    else:
        direction = B_base / base_mag

    scan_cfg = config.get("scan", {})
    values = scan_cfg.get("magnetic_scan_values", [0.0, 0.04, 0.08, 0.12])
    results: list[dict[str, float]] = []
    for mag in values:
        B_vec = direction * float(mag)
        sim = simulate_cross_field_case(config, B_override=B_vec)
        center_end = np.array(sim["center_history"])[-1]
        results.append(
            {
                "B_magnitude_T": float(np.linalg.norm(B_vec)),
                "mean_final_energy_ev": float(sim["mean_final_energy_ev"]),
                "x_end_m": float(center_end[0]),
                "z_end_m": float(center_end[2]),
                "larmor_radius_m": float(sim["larmor_radius_m"]),
            }
        )
    return results


def save_cross_field_plots(
    output_dir: Path,
    sim: Dict[str, Any],
    scan_results: list[dict[str, float]],
) -> None:
    times_ns = np.asarray(sim["times"]) * 1e9
    traj = np.asarray(sim["trajectory"])
    centers = np.asarray(sim["center_history"])
    energies = np.asarray(sim["energy_history"])

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    for idx in range(traj.shape[1]):
        ax.plot(traj[:, idx, 0] * 1e3, traj[:, idx, 2] * 1e3, lw=1.4, label=f"e{idx+1}")
    ax.plot(centers[:, 0] * 1e3, centers[:, 2] * 1e3, "k--", lw=2.0, label="centroid")
    ax.set_xlabel("x / mm")
    ax.set_ylabel("z / mm")
    ax.set_title("Cross-field electron trajectories (x-z)")
    ax.grid(True, alpha=0.3)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "cross_field_orbit.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.plot(times_ns, energies.mean(axis=1), lw=2.0)
    ax.set_xlabel("Time / ns")
    ax.set_ylabel("Mean kinetic energy / eV")
    ax.set_title("Cross-field mean energy evolution")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "cross_field_energy.png", dpi=180)
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(7.2, 5.0))
    Bvals = [item["B_magnitude_T"] for item in scan_results]
    zend = [item["z_end_m"] * 1e3 for item in scan_results]
    xend = [item["x_end_m"] * 1e3 for item in scan_results]
    ax1.plot(Bvals, zend, marker="o", lw=2.0, label="z displacement")
    ax1.plot(Bvals, xend, marker="s", lw=2.0, label="x displacement")
    ax1.set_xlabel("Magnetic field / T")
    ax1.set_ylabel("Final mean displacement / mm")
    ax1.set_title("Trajectory deflection under different magnetic fields")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "cross_field_bscan.png", dpi=180)
    plt.close(fig)


def write_summary(output_dir: Path, config: Dict[str, Any], sim: Dict[str, Any], scan_results: list[dict[str, float]]) -> Dict[str, Any]:
    E = np.asarray(sim["E"])
    B = np.asarray(sim["B"])
    center_end = np.asarray(sim["center_history"])[-1]
    sheath_metrics = estimate_sheath_metrics(
        E,
        B,
        float(config.get("particles", {}).get("charge", -E_CHARGE)),
        float(config.get("particles", {}).get("mass", E_MASS)),
        np.asarray(sim["final_velocities"]),
        float(config.get("particles", {}).get("dt", 5.0e-13)),
    )

    summary = {
        "num_particles": int(sim["num_particles"]),
        "mean_final_energy_ev": float(sim["mean_final_energy_ev"]),
        "center_end_m": center_end.tolist(),
        "drift_velocity_m_per_s": sim["drift_velocity_m_per_s"],
        "larmor_radius_m": float(sim["larmor_radius_m"]),
        "sheath_metrics": sheath_metrics,
        "magnetic_scan": scan_results,
    }

    with (output_dir / "cross_field_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    lines = [
        "# 交叉场最小版结果汇总",
        "",
        "## 1. 模块说明",
        "",
        "本模块为交叉电磁场电子输运的最小演示版，采用 Boris 积分器推进电子轨道，",
        "并保留一个简化的空间电荷占位力接口，用于展示 E-B 场作用下的轨道偏转与磁场扫描趋势。",
        "",
        "## 2. 当前参数",
        "",
        f"- 电场 E = {sim['E']} V/m",
        f"- 磁场 B = {sim['B']} T",
        f"- 粒子数 = {sim['num_particles']}",
        f"- 时间步长 dt = {config.get('particles', {}).get('dt')} s",
        f"- 步数 steps = {config.get('particles', {}).get('steps')}",
        f"- 积分器 = {config.get('solver', {}).get('integrator', 'boris')}",
        f"- 空间电荷占位开关 = {config.get('solver', {}).get('include_space_charge_placeholder', True)}",
        "",
        "## 3. 核心结果",
        "",
        f"- 平均最终能量 = {summary['mean_final_energy_ev']:.6f} eV",
        f"- 末端质心位置 = {summary['center_end_m']}",
        f"- 平均漂移速度 = {summary['drift_velocity_m_per_s']}",
        f"- Larmor 半径 = {summary['larmor_radius_m']:.6e} m",
        f"- 近似鞘层厚度 = {summary['sheath_metrics']['sheath_thickness_m']:.6e} m",
        f"- E×B 漂移速度 = {summary['sheath_metrics']['exb_drift_m_per_s']:.6e} m/s",
        "",
        "## 4. 图表文件",
        "",
        "- `cross_field_orbit.png`：电子轨道 x-z 投影图",
        "- `cross_field_energy.png`：平均动能随时间演化图",
        "- `cross_field_bscan.png`：不同磁场强度下的末端位移对比图",
        "",
        "## 5. 说明",
        "",
        "当前结果用于演示交叉场电子轨迹和磁场偏转趋势，不作为最终论文级鞘层模型。",
        "后续可在此基础上继续接入更严格的空间电荷力、自洽边界条件和截止频率估计。",
    ]
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def run_cross_field_simulation(config: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    sim = simulate_cross_field_case(config)
    scan_results = run_magnetic_scan(config)
    save_cross_field_plots(output_dir, sim, scan_results)
    summary = write_summary(output_dir, config, sim, scan_results)
    return summary
