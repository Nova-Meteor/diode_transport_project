#!/usr/bin/env bash
set -e
python src/main.py --module plate_3d --config configs/plate_3d.yaml
python src/main.py --module tip_plane --config configs/tip_plane.yaml
python src/main.py --module cross_field --config configs/cross_field.yaml
python src/main.py --module pinn --config configs/pinn.yaml
