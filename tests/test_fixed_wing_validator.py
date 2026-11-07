from aero_ai.schemas import Requirements, Design
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.validator import validate_fixed_wing


def test_sized_design_has_no_errors():
    req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
    issues = validate_fixed_wing(size_fixed_wing(req))
    assert not [i for i in issues if i.severity == "error"]


def test_tiny_wing_is_rejected():
    design = Design("fixed_wing", total_mass_kg=2.0, wing_area_m2=0.01,
                    wingspan_m=0.3, battery_mass_kg=0.3, motor_power_w=300)
    issues = validate_fixed_wing(design)
    assert any(i.severity == "error" and "Wing loading" in i.message for i in issues)


def test_battery_heavy_design_is_rejected():
    design = Design("fixed_wing", total_mass_kg=2.0, wing_area_m2=0.3,
                    wingspan_m=1.5, battery_mass_kg=1.2, motor_power_w=300)
    issues = validate_fixed_wing(design)
    assert any(i.severity == "error" and "Battery" in i.message for i in issues)


def test_sized_design_has_good_climb_power():
    req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
    design = size_fixed_wing(req)
    assert design.motor_power_w / design.total_mass_kg >= 100
