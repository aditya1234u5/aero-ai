from build123d import import_step
from aero_ai.templates.fixed_wing.analysis import analyze_fixed_wing
from aero_ai.templates.fixed_wing.geometry import build_fixed_wing_geometry
from aero_ai.templates.fixed_wing.layout import compute_layout
from aero_ai.templates.fixed_wing.mass_balance import component_list


def test_component_masses_add_up_to_total(sized, req):
    total = sum(c.mass_kg for c in component_list(sized, req))
    assert abs(total - sized.total_mass_kg) < 1e-6


def test_balance_hits_cg_and_margin_targets(balanced, req):
    res = analyze_fixed_wing(balanced, req)
    L = compute_layout(balanced)
    assert abs((res.cg_x_m - L.wing_x) / L.chord - 0.30) < 0.01
    assert abs(res.static_margin - 0.10) < 0.03


def test_balancing_shrinks_an_oversized_tail(sized, balanced, req):
    before = analyze_fixed_wing(sized, req)
    after = analyze_fixed_wing(balanced, req)
    assert before.static_margin > 0.35
    assert after.static_margin < 0.20
    assert balanced.h_tail_volume < sized.h_tail_volume


def test_balanced_design_still_builds_valid_geometry(balanced, tmp_path):
    paths = build_fixed_wing_geometry(balanced, str(tmp_path))
    assert import_step(paths[0]).is_valid
