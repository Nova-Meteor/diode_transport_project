from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from mc_md.emitter_geometry import (
    estimate_emission_current_density,
    initial_velocities,
    make_tip_geometry,
    sample_emission_sites,
)
from mc_md.particle_pusher import SimulationResult, simulate_particles

E_CHARGE = 1.602176634e-19



def _plot_trajectories(result: SimulationResult, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    traj = result.trajectories
    for idx in range(traj.shape[1]):
        r_nm = np.sqrt(traj[:, idx, 0] ** 2 + traj[:, idx, 1] ** 2) * 1e9
        z_um = traj[:, idx, 2] * 1e6
        ax.plot(z_um, r_nm, linewidth=1.1, alpha=0.85)
    ax.set_xlabel("z (µm)")
    ax.set_ylabel("radial distance (nm)")
    ax.set_title("Tip-plane electron trajectories")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "tip_trajectory.png", dpi=180)
    plt.close(fig)



def _plot_energy_histograms(with_coulomb: SimulationResult, without_coulomb: SimulationResult, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(without_coulomb.final_energy_ev, bins=24, alpha=0.55, label="without Coulomb")
    ax.hist(with_coulomb.final_energy_ev, bins=24, alpha=0.55, label="with Coulomb")
    ax.set_xlabel("Final kinetic energy (eV)")
    ax.set_ylabel("Counts")
    ax.set_title("Electron energy spectrum")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "tip_energy_hist.png", dpi=180)
    plt.close(fig)



def _plot_coulomb_comparison(with_coulomb: dict[str, Any], without_coulomb: dict[str, Any], output_dir: Path) -> None:
    labels = ["transmitted fraction", "mean final energy (norm.)", "mean transmitted energy (norm.)"]
    base = np.array([
        without_coulomb["transmitted_fraction"],
        without_coulomb["mean_final_energy_ev"],
        without_coulomb["mean_transmitted_energy_ev"],
    ], dtype=float)
    base = np.where(base == 0.0, 1.0, base)
    vals_without = np.array([
        without_coulomb["transmitted_fraction"],
        without_coulomb["mean_final_energy_ev"],
        without_coulomb["mean_transmitted_energy_ev"],
    ]) / base
    vals_with = np.array([
        with_coulomb["transmitted_fraction"],
        with_coulomb["mean_final_energy_ev"],
        with_coulomb["mean_transmitted_energy_ev"],
    ]) / base

    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.bar(x - width / 2, vals_without, width, label="without Coulomb")
    ax.bar(x + width / 2, vals_with, width, label="with Coulomb")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=10)
    ax.set_ylabel("Normalized value")
    ax.set_title("Discrete Coulomb effect comparison")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "tip_coulomb_compare.png", dpi=180)
    plt.close(fig)



def _write_summary_markdown(summary: dict[str, Any], output_dir: Path) -> None:
    loops = summary["self_consistent_history"]
    lines = [
        "# tip_plane 模块结果说明",
        "",
        "## 1. 模块说明",
        "当前结果为针尖-平板 MC/MD 最小版：采用简化外加场、有限电子数、离散库仑开关和 2-3 次外层自洽更新，目标是生成可展示的电子轨迹、能谱展宽与离散空间电荷影响对比。",
        "",
        "## 2. 关键参数",
        f"- 电子数: {summary['num_electrons']}",
        f"- 时间步长: {summary['dt']:.3e} s",
        f"- 时间步数: {summary['steps']}",
        f"- 外层自洽轮数: {summary['outer_loops']}",
        f"- 针尖半径: {summary['tip_radius_m']:.3e} m",
        f"- 间隙: {summary['gap_m']:.3e} m",
        f"- 标称阳极电压: {summary['anode_voltage_v']:.3f} V",
        f"- 是否考虑离散库仑: {summary['include_coulomb']}",
        "",
        "## 3. 最终结果",
        f"- 最终有效电压: {summary['final_effective_voltage_v']:.6f} V",
        f"- 透射比例: {summary['transmitted_fraction']:.6f}",
        f"- 平均最终能量: {summary['mean_final_energy_ev']:.6f} eV",
        f"- 平均透射能量: {summary['mean_transmitted_energy_ev']:.6f} eV",
        f"- 近似发射电流密度: {summary['emission_current_density_a_per_m2']:.6e} A/m²",
        f"- 能谱展宽: {summary['energy_spread_std_ev']:.6f} eV",
        "",
        "## 4. 离散库仑作用对比",
        f"- 无库仑透射比例: {summary['without_coulomb']['transmitted_fraction']:.6f}",
        f"- 有库仑透射比例: {summary['with_coulomb']['transmitted_fraction']:.6f}",
        f"- 无库仑平均最终能量: {summary['without_coulomb']['mean_final_energy_ev']:.6f} eV",
        f"- 有库仑平均最终能量: {summary['with_coulomb']['mean_final_energy_ev']:.6f} eV",
        "",
        "## 5. 自洽搜索历史",
        "| loop | effective_voltage (V) | transmitted_fraction | mean_final_energy (eV) | field_reduction (V/m) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for item in loops:
        lines.append(
            f"| {item['loop']} | {item['effective_voltage_v']:.6f} | {item['transmitted_fraction']:.6f} | {item['mean_final_energy_ev']:.6f} | {item['field_reduction_v_per_m']:.6e} |"
        )
    lines += [
        "",
        "## 6. 输出图表",
        "- `tip_trajectory.png`：电子轨迹图",
        "- `tip_energy_hist.png`：有/无库仑作用下的最终能量分布对比",
        "- `tip_coulomb_compare.png`：离散库仑作用对透射和能量的归一化对比",
        "",
        "## 7. 说明",
        "当前模型属于最小版工程实现，外加场和自洽反馈采用简化近似，适合作为项目当天的可运行展示框架，而不是最终论文级物理模型。",
        "",
    ]
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")



def run_tip_plane_simulation(config: dict, output_dir: Path) -> dict[str, Any]:
    general = config.get("general", {})
    geometry = make_tip_geometry(config)
    particles_cfg = config.get("particles", {})
    solver = config.get("solver", {})

    seed = int(general.get("random_seed", 42))
    rng = np.random.default_rng(seed)

    num_electrons = int(particles_cfg.get("num_electrons", 100))
    init_energy_ev = float(particles_cfg.get("init_energy_ev", 0.2))
    dt = float(particles_cfg.get("dt", 1e-14))
    steps = int(particles_cfg.get("steps", 1000))
    include_coulomb = bool(particles_cfg.get("include_coulomb", True))
    softening_length = float(particles_cfg.get("softening_length", max(0.2 * geometry.tip_radius, 1e-9)))
    tracked_particles = int(solver.get("tracked_particles", min(16, num_electrons)))
    outer_loops = int(solver.get("outer_self_consistent_loops", 3))
    self_consistency_gain = float(solver.get("self_consistency_gain", 0.25))
    max_neighbors = solver.get("max_neighbors")
    max_neighbors = None if max_neighbors in (None, "none", "None") else int(max_neighbors)

    emission_sites = sample_emission_sites(num_electrons, geometry, rng)
    initial_v = initial_velocities(num_electrons, init_energy_ev, rng)

    effective_voltage = geometry.anode_voltage
    field_reduction = 0.0
    self_history: list[dict[str, Any]] = []
    result_with_coulomb: SimulationResult | None = None

    for loop in range(1, outer_loops + 1):
        result_with_coulomb = simulate_particles(
            positions=emission_sites,
            velocities=initial_v,
            geometry=geometry,
            effective_voltage=effective_voltage,
            dt=dt,
            steps=steps,
            include_coulomb=include_coulomb,
            softening_length=softening_length,
            tracked_particles=tracked_particles,
            field_reduction=field_reduction,
            max_neighbors=max_neighbors,
        )
        transmit = result_with_coulomb.transmitted_fraction
        crowding_factor = min(
            0.35,
            self_consistency_gain
            * geometry.field_enhancement
            * (num_electrons / 100.0)
            * (softening_length / max(geometry.emission_radius, 1e-12))
            * (0.55 + 0.45 * (1.0 - transmit)),
        )
        effective_voltage = max(geometry.anode_voltage * (1.0 - crowding_factor), 0.30 * geometry.anode_voltage)
        field_reduction = (geometry.anode_voltage - effective_voltage) / max(geometry.gap, 1e-12)
        self_history.append(
            {
                "loop": loop,
                "effective_voltage_v": float(effective_voltage),
                "transmitted_fraction": float(transmit),
                "mean_final_energy_ev": float(result_with_coulomb.loop_diagnostics["mean_final_energy_ev"]),
                "field_reduction_v_per_m": float(field_reduction),
            }
        )

    assert result_with_coulomb is not None
    result_without_coulomb = simulate_particles(
        positions=emission_sites,
        velocities=initial_v,
        geometry=geometry,
        effective_voltage=geometry.anode_voltage,
        dt=dt,
        steps=steps,
        include_coulomb=False,
        softening_length=softening_length,
        tracked_particles=tracked_particles,
        field_reduction=0.0,
        max_neighbors=max_neighbors,
    )

    emission_current_density = estimate_emission_current_density(geometry, effective_voltage)
    with_diag = {
        "transmitted_fraction": result_with_coulomb.transmitted_fraction,
        **result_with_coulomb.loop_diagnostics,
    }
    without_diag = {
        "transmitted_fraction": result_without_coulomb.transmitted_fraction,
        **result_without_coulomb.loop_diagnostics,
    }
    summary = {
        "module": "tip_plane",
        "num_electrons": num_electrons,
        "dt": dt,
        "steps": steps,
        "outer_loops": outer_loops,
        "tip_radius_m": geometry.tip_radius,
        "tip_height_m": geometry.tip_height,
        "gap_m": geometry.gap,
        "anode_voltage_v": geometry.anode_voltage,
        "final_effective_voltage_v": effective_voltage,
        "include_coulomb": include_coulomb,
        "transmitted_fraction": result_with_coulomb.transmitted_fraction,
        "mean_final_energy_ev": result_with_coulomb.loop_diagnostics["mean_final_energy_ev"],
        "mean_transmitted_energy_ev": result_with_coulomb.loop_diagnostics["mean_transmitted_energy_ev"],
        "energy_spread_std_ev": float(np.std(result_with_coulomb.final_energy_ev)),
        "emission_current_density_a_per_m2": emission_current_density,
        "with_coulomb": with_diag,
        "without_coulomb": without_diag,
        "self_consistent_history": self_history,
    }

    _plot_trajectories(result_with_coulomb, output_dir)
    _plot_energy_histograms(result_with_coulomb, result_without_coulomb, output_dir)
    _plot_coulomb_comparison(with_diag, without_diag, output_dir)
    (output_dir / "tip_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_summary_markdown(summary, output_dir)
    return summary
