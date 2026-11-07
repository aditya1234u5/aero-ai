from aero_ai.schemas import Requirements
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.analysis import analyze_fixed_wing


def _run():
    req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
    design = size_fixed_wing(req)
    return req, design, analyze_fixed_wing(design, req)


def test_cruise_lift_matches_sizing_assumption():
    _, _, res = _run()
    assert abs(res.cruise_cl - 0.6) < 0.01


def test_aircraft_can_stall_below_cruise_speed():
    req, _, res = _run()
    assert 0 < res.stall_speed_ms < req.cruise_speed_ms


def test_sizing_and_analysis_agree():
    req, _, res = _run()
    assert 8 < res.lift_to_drag < 18
    assert abs(res.endurance_min - req.endurance_min) < 0.2 * req.endurance_min


def test_design_is_statically_stable():
    _, _, res = _run()
    assert res.static_margin > 0
