import os
from build123d import import_step
from aero_ai.schemas import Requirements
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.geometry import build_fixed_wing_geometry


def _build(tmp_path):
    req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
    design = size_fixed_wing(req)
    paths = build_fixed_wing_geometry(design, str(tmp_path))
    return design, paths


def test_files_are_created(tmp_path):
    _, paths = _build(tmp_path)
    assert all(os.path.getsize(p) > 0 for p in paths)


def test_geometry_matches_design(tmp_path):
    design, paths = _build(tmp_path)
    model = import_step(paths[0])
    box = model.bounding_box()
    assert model.is_valid
    assert abs((box.max.Y - box.min.Y) - design.wingspan_m) < 1e-3
