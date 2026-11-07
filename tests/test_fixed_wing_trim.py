from dataclasses import replace
from build123d import import_step
from aero_ai.templates.fixed_wing.analysis import analyze_fixed_wing
from aero_ai.templates.fixed_wing.geometry import build_fixed_wing_geometry


def test_trim_zeroes_the_pitching_moment(trimmed, req):
    res = analyze_fixed_wing(trimmed, req)
    assert abs(res.cruise_cm) < 0.01


def test_trimmed_design_is_stable_and_error_free(trimmed, req):
    res = analyze_fixed_wing(trimmed, req)
    assert res.static_margin > 0.05
    assert not [i for i in res.issues if i.severity == "error"]


def _htail_top(design, tmp_path):
    paths = build_fixed_wing_geometry(design, str(tmp_path))
    solids = list(import_step(paths[0]).solids())
    return solids[2].bounding_box().max.Z      # compound order: fuselage, wing, htail, vtail


def test_cad_tail_tilt_follows_analysis_convention(balanced, tmp_path):
    # Negative incidence = leading edge down = trailing edge up, as in the analysis
    nose_down = _htail_top(replace(balanced, tail_incidence_deg=-5.0), tmp_path / "a")
    nose_up = _htail_top(replace(balanced, tail_incidence_deg=+5.0), tmp_path / "b")
    assert nose_down > nose_up
