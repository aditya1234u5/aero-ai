"""Trim: tilt the horizontal tail until the pitching moment at cruise is zero."""
from dataclasses import replace
from scipy.optimize import brentq
from aero_ai.schemas import Requirements, Design
from aero_ai.templates.fixed_wing.analysis import analyze_fixed_wing

MAX_TAIL_INCIDENCE_DEG = 8.0


def trim_fixed_wing(design: Design, req: Requirements) -> Design:
    """Return a copy of the design with the tail incidence that makes Cm = 0 at cruise."""

    def cruise_cm(incidence: float) -> float:
        return analyze_fixed_wing(replace(design, tail_incidence_deg=incidence), req).cruise_cm

    low, high = -MAX_TAIL_INCIDENCE_DEG, MAX_TAIL_INCIDENCE_DEG
    if cruise_cm(low) * cruise_cm(high) > 0:
        raise RuntimeError("Tail incidence within +/-8 degrees cannot trim this design")
    return replace(design, tail_incidence_deg=brentq(cruise_cm, low, high, xtol=0.01))
