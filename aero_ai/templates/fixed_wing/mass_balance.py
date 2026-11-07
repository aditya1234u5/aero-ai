"""Mass and balance: where the centre of gravity (CG) sits along the fuselage."""
from dataclasses import dataclass
from aero_ai.schemas import Requirements, Design
from aero_ai.templates.fixed_wing.layout import compute_layout
from aero_ai.templates.fixed_wing import sizing as sz

# ---- Assumptions: where each component sits ----
WING_STRUCTURE_SHARE = 0.40      # shares of the structure mass
FUSELAGE_STRUCTURE_SHARE = 0.45
TAIL_STRUCTURE_SHARE = 0.15
PROPULSION_POSITION = 0.03       # motor in the nose (fraction of fuselage length)
AVIONICS_POSITION = 0.20
BATTERY_POSITION = 0.20
PAYLOAD_POSITION_IN_CHORD = 0.25 # payload bay at 25% of the wing chord


@dataclass
class Component:
    name: str
    mass_kg: float
    x_m: float      # distance from the nose


def component_list(design: Design, req: Requirements) -> list[Component]:
    L = compute_layout(design)
    structure = sz.STRUCTURE_FRACTION * design.total_mass_kg
    return [
        Component("propulsion", design.motor_power_w / sz.PROPULSION_W_PER_KG, PROPULSION_POSITION * L.fus_length),
        Component("avionics", sz.AVIONICS_MASS_KG, AVIONICS_POSITION * L.fus_length),
        Component("battery", design.battery_mass_kg, BATTERY_POSITION * L.fus_length),
        Component("payload", req.payload_kg, L.wing_x + PAYLOAD_POSITION_IN_CHORD * L.chord),
        Component("wing structure", WING_STRUCTURE_SHARE * structure, L.wing_x + 0.40 * L.chord),
        Component("fuselage structure", FUSELAGE_STRUCTURE_SHARE * structure, 0.50 * L.fus_length),
        Component("tail structure", TAIL_STRUCTURE_SHARE * structure, L.fus_length - 0.5 * L.h_chord),
    ]


def centre_of_gravity(components: list[Component]) -> float:
    total = sum(c.mass_kg for c in components)
    return sum(c.mass_kg * c.x_m for c in components) / total
