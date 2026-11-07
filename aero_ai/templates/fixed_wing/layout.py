"""Single source of truth for fixed-wing layout (used by geometry AND analysis)."""
from dataclasses import dataclass
from aero_ai.schemas import Design

# ---- Assumptions: standard first-pass sizing rules ----
WING_AIRFOIL = "naca2412"     # cambered airfoil for lift
TAIL_AIRFOIL = "naca0009"     # symmetric airfoil for tail surfaces
FUSELAGE_LENGTH_PER_SPAN = 0.75  # fuselage length as a fraction of wingspan
FUSELAGE_DIAMETER_PER_CHORD = 0.6
MIN_FUSELAGE_DIAMETER_M = 0.08
V_TAIL_VOLUME_COEFF = 0.04    # vertical tail volume coefficient (typical 0.02-0.05)
H_TAIL_ASPECT_RATIO = 4.0
V_TAIL_ASPECT_RATIO = 1.5


@dataclass
class Layout:
    span: float
    chord: float
    area: float
    fus_length: float
    fus_diameter: float
    wing_x: float       # wing leading edge position along the fuselage
    h_span: float
    h_chord: float
    h_x: float          # horizontal tail leading edge position
    v_height: float
    v_chord: float
    v_x: float          # vertical tail leading edge position


def compute_layout(design: Design) -> Layout:
    span, chord, area = design.wingspan_m, design.chord_m, design.wing_area_m2

    fus_length = FUSELAGE_LENGTH_PER_SPAN * span
    fus_diameter = max(MIN_FUSELAGE_DIAMETER_M, FUSELAGE_DIAMETER_PER_CHORD * chord)
    wing_x = design.wing_position * fus_length

    # Tail sizing from tail volume coefficients: area = V x reference length x wing area / tail arm
    tail_arm = 0.5 * fus_length
    s_h = design.h_tail_volume * chord * area / tail_arm
    s_v = V_TAIL_VOLUME_COEFF * span * area / tail_arm
    h_span = (H_TAIL_ASPECT_RATIO * s_h) ** 0.5
    h_chord = s_h / h_span
    v_height = (V_TAIL_ASPECT_RATIO * s_v) ** 0.5
    v_chord = s_v / v_height

    return Layout(
        span=span, chord=chord, area=area,
        fus_length=fus_length, fus_diameter=fus_diameter, wing_x=wing_x,
        h_span=h_span, h_chord=h_chord, h_x=fus_length - h_chord,
        v_height=v_height, v_chord=v_chord, v_x=fus_length - v_chord,
    )
