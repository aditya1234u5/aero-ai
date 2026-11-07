from aero_ai.schemas import Requirements
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.geometry import build_fixed_wing_geometry

req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
design = size_fixed_wing(req)
print(build_fixed_wing_geometry(design, "outputs"))
