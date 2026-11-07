import sys
from aero_ai.schemas import Requirements
from aero_ai.pipeline import run_pipeline

payload, endurance, speed = (float(x) for x in sys.argv[1:4]) if len(sys.argv) >= 4 else (1.0, 45.0, 15.0)
req = Requirements("fixed_wing", payload_kg=payload, endurance_min=endurance, cruise_speed_ms=speed)
result = run_pipeline(req, out_dir="outputs_pipeline")

print(f"request: {payload} kg payload, {endurance:.0f} min, {speed} m/s")
print("success:", result.ok)
if result.design:
    d = result.design
    print(f"mass {d.total_mass_kg:.2f} kg | span {d.wingspan_m:.2f} m | wing area {d.wing_area_m2:.3f} m2 | battery {d.battery_mass_kg:.2f} kg")
if result.results:
    r = result.results
    print(f"L/D {r.lift_to_drag:.1f} | stall {r.stall_speed_ms:.1f} m/s | endurance {r.endurance_min:.0f} min | static margin {r.static_margin:.0%}")
for f in result.files:
    print("file:", f)
for i in result.issues:
    print(f"[{i.severity}] {i.message}")
