"""Fixed-wing geometry: design numbers -> 3D model (STEP + STL)."""
import os
import numpy as np
import aerosandbox as asb
from build123d import (
    BuildLine, BuildSketch, Compound, Cylinder, Plane, Polyline,
    Pos, Rot, export_step, export_stl, extrude, make_face,
)
from aero_ai.schemas import Design
from aero_ai.templates.fixed_wing.layout import compute_layout, WING_AIRFOIL, TAIL_AIRFOIL


def _airfoil_points(name: str, chord: float):
    """Airfoil outline as (x, z) points scaled to the chord, with no repeated end point."""
    coords = asb.Airfoil(name).repanel(n_points_per_side=40).coordinates * chord
    pts = [tuple(map(float, p)) for p in coords]
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    return pts


def _extruded_airfoil(name: str, chord: float, length: float):
    """An airfoil section extruded symmetrically along the Y axis (total length given)."""
    with BuildSketch(Plane.XZ) as sketch:
        with BuildLine():
            Polyline(*_airfoil_points(name, chord), close=True)
        make_face()
    return extrude(sketch.sketch, amount=length / 2, both=True)


def build_fixed_wing_geometry(design: Design, out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    L = compute_layout(design)

    # Fuselage: a cylinder along the X axis, nose at x = 0
    fuselage = Pos(L.fus_length / 2, 0, 0) * (
        Rot(0, 90, 0) * Cylinder(L.fus_diameter / 2, L.fus_length)
    )
    wing = Pos(L.wing_x, 0, 0) * _extruded_airfoil(WING_AIRFOIL, L.chord, L.span)
    htail = Pos(L.h_x, 0, 0) * (
        Rot(0, design.tail_incidence_deg, 0) * _extruded_airfoil(TAIL_AIRFOIL, L.h_chord, L.h_span)
    )

    # Vertical tail: same section extruded along Y, then stood up on its edge (about X)
    vtail_flat = _extruded_airfoil(TAIL_AIRFOIL, L.v_chord, L.v_height)
    vtail = Pos(L.v_x, 0, L.v_height / 2) * (Rot(90, 0, 0) * vtail_flat)

    model = Compound([fuselage, wing, htail, vtail], label="fixed_wing")

    step_path = os.path.join(out_dir, "fixed_wing.step")
    stl_path = os.path.join(out_dir, "fixed_wing.stl")
    export_step(model, step_path)
    export_stl(model, stl_path)
    return [step_path, stl_path]

