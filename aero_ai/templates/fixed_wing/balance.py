"""Balance: place the wing so the CG is sensible, then size the tail for the target margin."""
from dataclasses import replace
from scipy.optimize import brentq
from aero_ai.schemas import Requirements, Design
from aero_ai.templates.fixed_wing.analysis import static_margin_at
from aero_ai.templates.fixed_wing.layout import compute_layout
from aero_ai.templates.fixed_wing.mass_balance import component_list, centre_of_gravity

WING_POSITION_RANGE = (0.05, 0.60)   # wing leading edge, fraction of fuselage length
TAIL_VOLUME_RANGE = (0.05, 0.80)     # horizontal tail volume coefficient


def _cg_in_chords(design: Design, req: Requirements) -> float:
    L = compute_layout(design)
    return (centre_of_gravity(component_list(design, req)) - L.wing_x) / L.chord


def balance_fixed_wing(
    design: Design, req: Requirements,
    target_cg_chord: float = 0.30, target_margin: float = 0.10,
) -> Design:
    """Step A: move the wing so the CG sits at target_cg_chord of the wing chord.
    Step B: resize the horizontal tail so the static margin equals target_margin.
    The two steps affect each other slightly, so we repeat them a few times."""
    for _ in range(4):
        # Step A: wing position (mass balance only, no aerodynamics needed)
        def cg_gap(position: float) -> float:
            return _cg_in_chords(replace(design, wing_position=position), req) - target_cg_chord

        if cg_gap(WING_POSITION_RANGE[0]) * cg_gap(WING_POSITION_RANGE[1]) > 0:
            raise RuntimeError("No wing position puts the CG at the target point on the chord")
        design = replace(design, wing_position=brentq(cg_gap, *WING_POSITION_RANGE, xtol=1e-4))

        # Step B: tail size (needs the aerodynamic analysis)
        def margin_gap(volume: float) -> float:
            return static_margin_at(replace(design, h_tail_volume=volume), req) - target_margin

        if margin_gap(TAIL_VOLUME_RANGE[0]) * margin_gap(TAIL_VOLUME_RANGE[1]) > 0:
            raise RuntimeError("No tail size reaches the target static margin")
        design = replace(design, h_tail_volume=brentq(margin_gap, *TAIL_VOLUME_RANGE, xtol=1e-3))
    return design
