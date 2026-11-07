from aero_ai.schemas import Requirements
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.analysis import analyze_fixed_wing
from aero_ai.templates.fixed_wing.balance import balance_fixed_wing
from aero_ai.templates.fixed_wing.layout import compute_layout
from aero_ai.templates.fixed_wing.geometry import build_fixed_wing_geometry


def show(label, design, req):
    res = analyze_fixed_wing(design, req)
    L = compute_layout(design)
    print(f"--- {label}")
    print(f"wing position          : {design.wing_position:.0%} of fuselage ({L.wing_x:.3f} m from nose)")
    print(f"CG                     : {res.cg_x_m:.3f} m = {(res.cg_x_m - L.wing_x) / L.chord:.0%} of wing chord")
    print(f"neutral point          : {res.neutral_point_x_m:.3f} m = {(res.neutral_point_x_m - L.wing_x) / L.chord:.0%} of wing chord")
    print(f"tail size              : volume coefficient {design.h_tail_volume:.2f}")
    print(f"static margin          : {res.static_margin:.0%} (AeroBuildup {res.static_margin_buildup:.0%}, vortex lattice {res.static_margin_vlm:.0%})")
    print(f"pitching moment (Cm)   : {res.cruise_cm:+.3f}")
    print(f"lift-to-drag / endurance: {res.lift_to_drag:.1f} / {res.endurance_min:.0f} min")
    for i in res.issues:
        print(f"  [{i.severity}] {i.message}")


req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
design = size_fixed_wing(req)
show("before balancing", design, req)
balanced = balance_fixed_wing(design, req)
show("after balancing", balanced, req)
print(build_fixed_wing_geometry(balanced, "outputs_balanced"))
