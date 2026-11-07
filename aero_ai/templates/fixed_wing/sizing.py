"""Fixed-wing sizing: requirements -> first-pass design numbers."""
import math
from aero_ai.schemas import Requirements, Design

# ---- Assumptions: first-pass textbook values, to be validated later ----
RHO = 1.225               # air density at sea level, kg/m^3
G = 9.81                  # gravity, m/s^2
ASPECT_RATIO = 8.0        # span^2 / wing area; typical small UAV: 6-10
CL_CRUISE = 0.6           # lift coefficient at cruise
CD0 = 0.03                # zero-lift drag (fuselage, tail, skin friction)
OSWALD_E = 0.8            # wing efficiency factor
ETA_PROPULSION = 0.55     # propeller efficiency x motor/ESC efficiency
AVIONICS_POWER_W = 5.0    # flight controller, radio, servos
AVIONICS_MASS_KG = 0.15
BATTERY_WH_PER_KG = 150.0 # LiPo pack-level specific energy
BATTERY_USABLE = 0.8      # do not drain the battery completely
STRUCTURE_FRACTION = 0.25 # airframe mass as a fraction of total mass
PEAK_POWER_FACTOR = 3.0   # peak power vs cruise power (for climbing)
MIN_POWER_LOADING_W_PER_KG = 120.0  # climb requirement: peak W per kg of total mass
PROPULSION_W_PER_KG = 800.0  # motor + ESC + propeller power density


def size_fixed_wing(req: Requirements, max_iter: int = 100, tol: float = 1e-6) -> Design:
    v = req.cruise_speed_ms
    mass = req.payload_kg * 2.0  # initial guess, refined by iteration

    for _ in range(max_iter):
        weight = mass * G

        # Step 1: lift = weight  ->  wing area
        wing_area = 2 * weight / (RHO * v**2 * CL_CRUISE)

        # Step 2: wing shape
        span = math.sqrt(ASPECT_RATIO * wing_area)
        chord = wing_area / span

        # Step 3: drag -> power
        cd = CD0 + CL_CRUISE**2 / (math.pi * OSWALD_E * ASPECT_RATIO)
        lift_to_drag = CL_CRUISE / cd
        drag = weight / lift_to_drag
        p_electric = drag * v / ETA_PROPULSION
        p_total = p_electric + AVIONICS_POWER_W

        # Step 4: battery and propulsion masses
        energy_wh = p_total * req.endurance_min / 60.0
        battery_mass = energy_wh / (BATTERY_WH_PER_KG * BATTERY_USABLE)
        peak_power = max(PEAK_POWER_FACTOR * p_electric, MIN_POWER_LOADING_W_PER_KG * mass)
        propulsion_mass = peak_power / PROPULSION_W_PER_KG

        # Step 5: new total mass (structure is a fraction of the total)
        fixed = req.payload_kg + battery_mass + propulsion_mass + AVIONICS_MASS_KG
        new_mass = fixed / (1.0 - STRUCTURE_FRACTION)

        if abs(new_mass - mass) < tol:
            return Design(
                aircraft_type="fixed_wing",
                total_mass_kg=new_mass,
                wing_area_m2=wing_area,
                wingspan_m=span,
                chord_m=chord,
                battery_mass_kg=battery_mass,
                motor_power_w=peak_power,
            )
        mass = new_mass

    raise RuntimeError("Sizing did not converge: requirements may be unrealistic")

