# Engineering Cleanup Note

This cleanup pass standardized the project without breaking the active runtime paths.

## What was cleaned

- Archived experimental `plate_3d` probe scripts under `tools/experimental_plate3d/`.
- Archived exploratory progress artifacts under `results/plate_3d/archive/experimental/`.
- Created canonical result mirrors under:
  - `results/plate_3d/final_release/`
  - `results/plate_3d/convergence/`

## Compatibility policy

Active workflows still write to the original result paths under `results/plate_3d/`.
The `final_release/` and `convergence/` folders are curated mirrors for reporting and delivery.

## Canonical usage

- Main executable: `src/main.py`
- Active plate solver workflow: `src/fdm_3d/workflow.py`
- Plate main result set: `results/plate_3d/final_release/`
- Plate convergence set: `results/plate_3d/convergence/`
