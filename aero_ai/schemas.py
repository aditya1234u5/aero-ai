from dataclasses import dataclass, field


@dataclass
class Requirements:
    aircraft_type: str          # "fixed_wing" or "quadcopter"
    payload_kg: float           # mass the aircraft must carry
    endurance_min: float        # how long it must fly
    cruise_speed_ms: float      # target cruise speed in m/s


@dataclass
class Design:
    aircraft_type: str
    total_mass_kg: float
    wing_area_m2: float = 0.0
    wingspan_m: float = 0.0
    chord_m: float = 0.0
    battery_mass_kg: float = 0.0
    motor_power_w: float = 0.0
    wing_position: float = 0.30   # wing leading edge, as a fraction of fuselage length
    h_tail_volume: float = 0.50   # horizontal tail volume coefficient (sets tail size)
    tail_incidence_deg: float = 0.0  # horizontal tail angle, positive = leading edge up


@dataclass
class Issue:
    severity: str               # "error" or "warning"
    message: str


@dataclass
class Results:
    stall_speed_ms: float = 0.0
    lift_to_drag: float = 0.0
    cruise_alpha_deg: float = 0.0
    cruise_cl: float = 0.0
    cruise_cd: float = 0.0
    cl_max: float = 0.0
    cruise_cm: float = 0.0
    static_margin: float = 0.0
    endurance_min: float = 0.0
    cg_x_m: float = 0.0
    neutral_point_x_m: float = 0.0
    static_margin_buildup: float = 0.0
    static_margin_vlm: float = 0.0
    issues: list = field(default_factory=list)

