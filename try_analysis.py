from aero_ai.schemas import Requirements
from aero_ai.templates.fixed_wing import sizing as sz
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.analysis import analyze_fixed_wing

req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
design = size_fixed_wing(req)
res = analyze_fixed_wing(design, req)

assumed_cd = sz.CD0 + sz.CL_CRUISE**2 / (3.14159265 * sz.OSWALD_E * sz.ASPECT_RATIO)
print(f"cruise angle of attack : {res.cruise_alpha_deg:.1f} deg")
print(f"cruise CL              : {res.cruise_cl:.2f} (sizing assumed {sz.CL_CRUISE})")
print(f"lift-to-drag           : {res.lift_to_drag:.1f} (sizing assumed {sz.CL_CRUISE / assumed_cd:.1f})")
print(f"stall speed            : {res.stall_speed_ms:.1f} m/s (cruise {req.cruise_speed_ms} m/s)")
print(f"max CL                 : {res.cl_max:.2f}")
print(f"endurance              : {res.endurance_min:.0f} min (required {req.endurance_min:.0f})")
print(f"static margin          : {res.static_margin:.0%}")
print(f"pitching moment (Cm)   : {res.cruise_cm:+.2f}")
print("issues:")
for i in res.issues:
    print(f"  [{i.severity}] {i.message}")
