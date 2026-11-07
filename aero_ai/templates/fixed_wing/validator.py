"""Reality checks for fixed-wing designs."""
from aero_ai.schemas import Design, Issue

G = 9.81


def validate_fixed_wing(design: Design) -> list[Issue]:
    issues: list[Issue] = []

    if design.total_mass_kg <= 0 or design.wing_area_m2 <= 0:
        return [Issue("error", "Mass and wing area must be positive")]

    # Wing loading in N/m^2
    wing_loading = design.total_mass_kg * G / design.wing_area_m2
    if wing_loading < 15 or wing_loading > 300:
        issues.append(Issue("error", f"Wing loading {wing_loading:.0f} N/m2 is unrealistic (15-300)"))
    elif wing_loading < 30 or wing_loading > 200:
        issues.append(Issue("warning", f"Wing loading {wing_loading:.0f} N/m2 is unusual (30-200)"))

    # Battery mass fraction
    battery_fraction = design.battery_mass_kg / design.total_mass_kg
    if battery_fraction > 0.5:
        issues.append(Issue("error", f"Battery is {battery_fraction:.0%} of total mass (max 50%)"))
    elif battery_fraction > 0.35:
        issues.append(Issue("warning", f"Battery is {battery_fraction:.0%} of total mass (above 35%)"))

    # Power loading in W/kg
    power_loading = design.motor_power_w / design.total_mass_kg
    if power_loading < 50:
        issues.append(Issue("error", f"Power loading {power_loading:.0f} W/kg is too low to fly safely (min 50)"))
    elif power_loading < 100:
        issues.append(Issue("warning", f"Power loading {power_loading:.0f} W/kg is low for good climb (aim for 100+)"))

    # Wingspan
    if design.wingspan_m > 3.0:
        issues.append(Issue("warning", f"Wingspan {design.wingspan_m:.1f} m is hard to build and transport"))

    return issues
