from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cross_field.eb_motion import run_cross_field_simulation
from fdm_3d.workflow import run_plate_3d_workflow
from mc_md.self_consistent_loop import run_tip_plane_simulation
from pinn.train import run_pinn_workflow


class RegressionSmokeTests(unittest.TestCase):
    maxDiff = None

    def _load_config(self, name: str) -> dict:
        with (PROJECT_ROOT / 'configs' / name).open('r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_main_list_command(self) -> None:
        env = dict(**__import__('os').environ)
        env['PYTHONPATH'] = str(SRC_DIR) + (':' + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / 'src' / 'main.py'), '--list'],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout
        self.assertIn('plate_3d', stdout)
        self.assertIn('tip_plane', stdout)
        self.assertIn('cross_field', stdout)
        self.assertIn('pinn', stdout)

    def test_plate_3d_smoke(self) -> None:
        cfg = self._load_config('plate_3d.yaml')
        cfg['grid'] = {'nx': 7, 'ny': 7, 'nz': 7}
        cfg['solver']['max_iter'] = 50
        cfg['solver']['outer_max_iter'] = 2
        cfg['solver']['tol'] = 1.0e-3
        cfg['solver']['outer_tol'] = 1.0e-2
        cfg['search'] = {
            'base_reference': 'cl',
            'scan_factors': [0.9, 1.1],
            'max_iter': 2,
            'objective_tol': 5.0e4,
            'radius_factors': [1.0],
        }
        cfg['convergence'] = {'enabled': False}
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            summary = run_plate_3d_workflow(cfg, out)
            self.assertGreater(summary['j_lim'], 0.0)
            self.assertTrue((out / 'plate_summary.json').exists())
            self.assertTrue((out / 'plate_phi_slice.png').exists())
            with (out / 'plate_summary.json').open('r', encoding='utf-8') as f:
                stored = json.load(f)
            self.assertIn('j_lim', stored)
            self.assertIn('search_status', stored)

    def test_tip_plane_smoke(self) -> None:
        cfg = self._load_config('tip_plane.yaml')
        cfg['particles']['num_electrons'] = 10
        cfg['particles']['steps'] = 50
        cfg['solver']['outer_self_consistent_loops'] = 1
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            summary = run_tip_plane_simulation(cfg, out)
            self.assertGreaterEqual(summary['transmitted_fraction'], 0.0)
            self.assertTrue((out / 'tip_summary.json').exists())
            self.assertTrue((out / 'tip_trajectory.png').exists())

    def test_cross_field_smoke(self) -> None:
        cfg = self._load_config('cross_field.yaml')
        cfg['particles']['steps'] = 200
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            summary = run_cross_field_simulation(cfg, out)
            self.assertIn('mean_final_energy_ev', summary)
            self.assertTrue((out / 'cross_field_summary.json').exists())
            self.assertTrue((out / 'cross_field_orbit.png').exists())

    def test_pinn_smoke(self) -> None:
        cfg = self._load_config('pinn.yaml')
        cfg['train']['epochs'] = 5
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            summary = run_pinn_workflow(cfg, PROJECT_ROOT, out)
            self.assertIn('rmse', summary)
            self.assertTrue((out / 'pinn_summary.json').exists())
            self.assertTrue((out / 'pinn_prediction.png').exists())
            self.assertTrue((out / 'pinn_loss.png').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
