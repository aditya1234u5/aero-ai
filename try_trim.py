from aero_ai.schemas import Requirements
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.analysis import analyze_fixed_wing
from aero_ai.templates.fixed_wing.balance import balance_fixed_wing
from aero_ai.templates.fixed_wing.trim import trim_fixed_wing
from aero_ai.templates.fixed_wing.geometry import build_fixed_wing_geometry


def show(label, design, req):
    res = analyze_fixed_wing(design, req)
    print(f"--- {label}")
    print(f"tail incidence         : {design.tail_incidence_deg:+.2f} deg")
    print(f"pitching moment (Cm)   : {res.cruise_cm:+.3f}")
    print(f"static margin          : {res.static_margin:.0%} (AeroBuildup {res.static_margin_buildup:.0%}, vortex lattice {res.static_margin_vlm:.0%})")
    print(f"cruise angle of attack : {res.cruise_alpha_deg:.1f} deg")
    print(f"lift-to-drag / endurance: {res.lift_to_drag:.1f} / {res.endurance_min:.0f} min")
    print(f"stall speed            : {res.stall_speed_ms:.1f} m/s")
    print("issues:", [i.message for i in res.issues] or "none")


req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
balanced = balance_fixed_wing(size_fixed_wing(req), req)
show("balanced, not trimmed", balanced, req)
trimmed = trim_fixed_wing(balanced, req)
show("balanced and trimmed", trimmed, req)
print(build_fixed_wing_geometry(trimmed, "outputs_trimmed"))
