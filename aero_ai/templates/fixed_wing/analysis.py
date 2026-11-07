"""Fixed-wing aerodynamic analysis with AeroSandbox (low fidelity, seconds to run)."""
import numpy as np
import aerosandbox as asb
from aero_ai.schemas import Requirements, Design, Issue, Results
from aero_ai.templates.fixed_wing.layout import compute_layout, WING_AIRFOIL, TAIL_AIRFOIL
from aero_ai.templates.fixed_wing import sizing as sz
from aero_ai.templates.fixed_wing.mass_balance import component_list, centre_of_gravity


def _build_airplane(design: Design, cg_x: float) -> asb.Airplane:
    L = compute_layout(design)
    wing_af = asb.Airfoil(WING_AIRFOIL)
    tail_af = asb.Airfoil(TAIL_AIRFOIL)

    wing = asb.Wing(name="Wing", symmetric=True, xsecs=[
        asb.WingXSec(xyz_le=[L.wing_x, 0, 0], chord=L.chord, airfoil=wing_af),
        asb.WingXSec(xyz_le=[L.wing_x, L.span / 2, 0], chord=L.chord, airfoil=wing_af),
    ])
    htail = asb.Wing(name="HTail", symmetric=True, xsecs=[
        asb.WingXSec(xyz_le=[L.h_x, 0, 0], chord=L.h_chord, airfoil=tail_af, twist=design.tail_incidence_deg),
        asb.WingXSec(xyz_le=[L.h_x, L.h_span / 2, 0], chord=L.h_chord, airfoil=tail_af, twist=design.tail_incidence_deg),
    ])
    vtail = asb.Wing(name="VTail", symmetric=False, xsecs=[
        asb.WingXSec(xyz_le=[L.v_x, 0, 0], chord=L.v_chord, airfoil=tail_af),
        asb.WingXSec(xyz_le=[L.v_x, 0, L.v_height], chord=L.v_chord, airfoil=tail_af),
    ])
    fuselage = asb.Fuselage(name="Fuselage", xsecs=[
        asb.FuselageXSec(xyz_c=[f * L.fus_length, 0, 0], radius=L.fus_diameter / 2)
        for f in (0.0, 0.5, 1.0)
    ])
    # Moment reference point = the real centre of gravity from the mass and balance
    return asb.Airplane(
        name="uav", wings=[wing, htail, vtail], fuselages=[fuselage],
        xyz_ref=[cg_x, 0, 0],
        s_ref=L.area, c_ref=L.chord, b_ref=L.span,
    )


def _run(airplane: asb.Airplane, velocity: float, alpha_deg: float) -> dict:
    op = asb.OperatingPoint(
        velocity=velocity, alpha=alpha_deg, atmosphere=asb.Atmosphere(altitude=0)
    )
    result = asb.AeroBuildup(airplane=airplane, op_point=op).run()
    return {k: float(np.squeeze(result[k])) for k in ("CL", "CD", "Cm")}


def _margins(airplane: asb.Airplane, velocity: float, alpha_deg: float, chord: float) -> dict:
    """Static margin (fraction of chord) from AeroBuildup and from a vortex lattice."""
    margins = {}
    for name, method in (("buildup", asb.AeroBuildup), ("vlm", asb.VortexLatticeMethod)):
        points = []
        for a in (alpha_deg - 1.0, alpha_deg + 1.0):
            op = asb.OperatingPoint(velocity=velocity, alpha=a, atmosphere=asb.Atmosphere(altitude=0))
            r = method(airplane=airplane, op_point=op).run()
            points.append((float(np.squeeze(r["CL"])), float(np.squeeze(r["Cm"]))))
        cl_alpha = (points[1][0] - points[0][0]) / 2.0
        cm_alpha = (points[1][1] - points[0][1]) / 2.0
        margins[name] = -cm_alpha / cl_alpha
    return margins


def static_margin_at(design: Design, req: Requirements, alpha_deg: float = 3.0) -> float:
    """Quick conservative static margin, used by the balance solver."""
    cg_x = centre_of_gravity(component_list(design, req))
    airplane = _build_airplane(design, cg_x)
    return min(_margins(airplane, req.cruise_speed_ms, alpha_deg, design.chord_m).values())


def analyze_fixed_wing(design: Design, req: Requirements) -> Results:
    cg_x = centre_of_gravity(component_list(design, req))
    airplane = _build_airplane(design, cg_x)
    v = req.cruise_speed_ms
    weight = design.total_mass_kg * sz.G
    q = 0.5 * sz.RHO * v**2

    # Step 1: sweep angle of attack and record the aircraft's polar
    alphas = np.arange(-2.0, 21.0, 1.0)
    runs = [_run(airplane, v, a) for a in alphas]
    cl = np.array([r["CL"] for r in runs])
    cd = np.array([r["CD"] for r in runs])
    i_max = int(np.argmax(cl))
    cl_max = float(cl[i_max])

    results = Results(cl_max=cl_max, cg_x_m=cg_x)
    results.stall_speed_ms = float(np.sqrt(2 * weight / (sz.RHO * design.wing_area_m2 * cl_max)))

    # Step 2: lift must equal weight at cruise -> required CL -> angle of attack
    cl_required = weight / (q * design.wing_area_m2)
    if cl_required >= cl_max:
        results.issues.append(Issue("error", f"Cannot hold level flight at {v} m/s: needs CL {cl_required:.2f} but max is {cl_max:.2f}"))
        return results
    alpha_cruise = float(np.interp(cl_required, cl[: i_max + 1], alphas[: i_max + 1]))

    # Step 3: drag, lift-to-drag, and the moment at that cruise point
    cruise = _run(airplane, v, alpha_cruise)
    results.cruise_alpha_deg = alpha_cruise
    results.cruise_cl = cruise["CL"]
    results.cruise_cd = cruise["CD"]
    results.cruise_cm = cruise["Cm"]
    results.lift_to_drag = cruise["CL"] / cruise["CD"]

    # Step 4: static margin from two independent methods; design to the more conservative one
    margins = _margins(airplane, v, alpha_cruise, design.chord_m)
    results.static_margin_buildup = margins["buildup"]
    results.static_margin_vlm = margins["vlm"]
    results.static_margin = min(margins.values())   # fraction of the reference chord
    results.neutral_point_x_m = cg_x + results.static_margin * design.chord_m

    # Step 5: achieved endurance, using the same propulsion assumptions as the sizing
    drag_n = cruise["CD"] * q * design.wing_area_m2
    p_total = drag_n * v / sz.ETA_PROPULSION + sz.AVIONICS_POWER_W
    energy_wh = design.battery_mass_kg * sz.BATTERY_WH_PER_KG * sz.BATTERY_USABLE
    results.endurance_min = energy_wh / p_total * 60.0

    # Step 6: turn the numbers into pass/fail messages
    if results.stall_speed_ms > 0.8 * v:
        results.issues.append(Issue("warning", f"Stall speed {results.stall_speed_ms:.1f} m/s is close to cruise speed {v} m/s"))
    if results.endurance_min < 0.9 * req.endurance_min:
        results.issues.append(Issue("error", f"Endurance {results.endurance_min:.0f} min is below the required {req.endurance_min:.0f} min"))
    elif results.endurance_min < req.endurance_min:
        results.issues.append(Issue("warning", f"Endurance {results.endurance_min:.0f} min is slightly below the required {req.endurance_min:.0f} min"))
    if results.static_margin < 0:
        results.issues.append(Issue("error", "Aircraft is statically unstable (negative static margin)"))
    elif results.static_margin < 0.05:
        results.issues.append(Issue("warning", f"Static margin {results.static_margin:.0%} is very small (aim for 5-15%)"))
    elif results.static_margin > 0.35:
        results.issues.append(Issue("warning", f"Static margin {results.static_margin:.0%} is very large: tail may be oversized or CG could sit further back"))
    if abs(results.cruise_cm) > 0.05:
        results.issues.append(Issue("warning", f"Not trimmed at cruise (Cm {results.cruise_cm:+.2f}): needs tail incidence, elevator, or the tail angle changed"))
    return results



