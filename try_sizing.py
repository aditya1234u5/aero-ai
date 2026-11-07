from aero_ai.schemas import Requirements
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing

req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
design = size_fixed_wing(req)
for name, value in vars(design).items():
    print(name, value if isinstance(value, str) else round(value, 3))
