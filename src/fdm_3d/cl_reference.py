from __future__ import annotations

import math
from typing import Any, Dict



def child_langmuir_current_density(config: Dict[str, Any]) -> float:
    geometry = config["geometry"]
    physics = config["physics"]
    voltage = float(physics["anode_voltage"])
    gap = float(geometry["d"])
    epsilon0 = float(physics.get("epsilon0", 8.854e-12))
    electron_charge = abs(float(physics.get("electron_charge", 1.602176634e-19)))
    electron_mass = float(physics.get("electron_mass", 9.1093837015e-31))
    return (4.0 / 9.0) * epsilon0 * math.sqrt(2.0 * electron_charge / electron_mass) * voltage ** 1.5 / (gap * gap)



def emitter_area(config: Dict[str, Any], emitter_radius: float | None = None) -> float:
    radius = float(emitter_radius if emitter_radius is not None else config["geometry"]["emitter_radius"])
    return math.pi * radius * radius
