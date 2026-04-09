from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class SurrogateDataset:
    x: np.ndarray
    y: np.ndarray
    feature_names: list[str]
    target_name: str
    metadata: dict[str, Any]


def _child_langmuir_j(voltage: np.ndarray, gap: np.ndarray, *, epsilon0: float, electron_charge: float, electron_mass: float) -> np.ndarray:
    return (4.0 / 9.0) * epsilon0 * np.sqrt(2.0 * electron_charge / electron_mass) * np.power(voltage, 1.5) / np.square(gap)


def _interp_radius_correction(radius_values: np.ndarray, sweep_radius: np.ndarray, sweep_correction: np.ndarray) -> np.ndarray:
    order = np.argsort(sweep_radius)
    radius_sorted = sweep_radius[order]
    corr_sorted = sweep_correction[order]
    return np.interp(radius_values, radius_sorted, corr_sorted, left=corr_sorted[0], right=corr_sorted[-1])


def load_plate3d_reference(project_root: Path) -> dict[str, Any]:
    import yaml

    plate_config_path = project_root / 'configs' / 'plate_3d.yaml'
    radius_sweep_path = project_root / 'results' / 'plate_3d' / 'radius_sweep.json'
    plate_summary_path = project_root / 'results' / 'plate_3d' / 'plate_summary.json'

    with plate_config_path.open('r', encoding='utf-8') as f:
        plate_config = yaml.safe_load(f)
    with radius_sweep_path.open('r', encoding='utf-8') as f:
        radius_sweep = json.load(f)
    with plate_summary_path.open('r', encoding='utf-8') as f:
        plate_summary = json.load(f)

    return {
        'config': plate_config,
        'radius_sweep': radius_sweep,
        'plate_summary': plate_summary,
    }


def build_surrogate_dataset(config: dict[str, Any], project_root: Path) -> SurrogateDataset:
    general_cfg = config.get('general', {})
    data_cfg = config.get('data', {})
    rng = np.random.default_rng(int(general_cfg.get('random_seed', 42)))

    reference = load_plate3d_reference(project_root)
    plate_cfg = reference['config']
    radius_sweep = reference['radius_sweep']['items']
    plate_summary = reference['plate_summary']

    geometry = plate_cfg['geometry']
    physics = plate_cfg['physics']
    base_gap = float(geometry['d'])
    base_voltage = float(physics['anode_voltage'])
    base_radius = float(geometry['emitter_radius'])

    epsilon0 = float(physics.get('epsilon0', 8.854e-12))
    electron_charge = abs(float(physics.get('electron_charge', 1.602176634e-19)))
    electron_mass = float(physics.get('electron_mass', 9.1093837015e-31))

    sweep_radius = np.array([float(item['emitter_radius']) for item in radius_sweep], dtype=float)
    sweep_correction = np.array([float(item['j_over_jcl']) for item in radius_sweep], dtype=float)

    num_samples = int(data_cfg.get('num_samples', 64))
    voltage_range = data_cfg.get('voltage_range', [0.7, 1.3])
    gap_range = data_cfg.get('gap_range', [0.8, 1.2])
    radius_range = data_cfg.get('radius_range', [0.7, 1.3])
    noise_level = float(data_cfg.get('noise_level', 0.01))

    voltages = base_voltage * rng.uniform(float(voltage_range[0]), float(voltage_range[1]), size=num_samples)
    gaps = base_gap * rng.uniform(float(gap_range[0]), float(gap_range[1]), size=num_samples)
    radii = base_radius * rng.uniform(float(radius_range[0]), float(radius_range[1]), size=num_samples)

    j_cl = _child_langmuir_j(voltages, gaps, epsilon0=epsilon0, electron_charge=electron_charge, electron_mass=electron_mass)
    radius_corr = _interp_radius_correction(radii, sweep_radius, sweep_correction)
    j_lim = j_cl * radius_corr
    if noise_level > 0:
        j_lim = j_lim * (1.0 + rng.normal(0.0, noise_level, size=num_samples))

    x = np.stack([gaps, voltages, radii], axis=1)
    y = j_lim.reshape(-1, 1)

    anchor_x = np.array([[base_gap, base_voltage, float(item['emitter_radius'])] for item in radius_sweep], dtype=float)
    anchor_y = np.array([[float(item['j_limit'])] for item in radius_sweep], dtype=float)

    x = np.concatenate([x, anchor_x], axis=0)
    y = np.concatenate([y, anchor_y], axis=0)

    metadata = {
        'dataset_kind': 'physics_guided_surrogate',
        'num_generated_samples': num_samples,
        'num_anchor_samples': int(anchor_x.shape[0]),
        'noise_level': noise_level,
        'radius_correction_range': [float(np.min(sweep_correction)), float(np.max(sweep_correction))],
        'feature_ranges': {
            'gap': [float(np.min(x[:, 0])), float(np.max(x[:, 0]))],
            'voltage': [float(np.min(x[:, 1])), float(np.max(x[:, 1]))],
            'emitter_radius': [float(np.min(x[:, 2])), float(np.max(x[:, 2]))],
        },
        'base_reference': {
            'gap': base_gap,
            'voltage': base_voltage,
            'emitter_radius': base_radius,
            'j_over_jcl': float(plate_summary['j_over_jcl']),
        },
        'note': '训练集由 plate_3d 已有半径扫描结果和 Child-Langmuir 物理缩放共同构建，不等同于全量高精度数值求解。',
    }

    return SurrogateDataset(
        x=x,
        y=y,
        feature_names=['gap', 'voltage', 'emitter_radius'],
        target_name='current_limit_density',
        metadata=metadata,
    )
