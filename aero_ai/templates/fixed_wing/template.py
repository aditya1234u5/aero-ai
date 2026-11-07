from aero_ai.schemas import Requirements, Design, Issue, Results
from aero_ai.templates.base import AircraftTemplate
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.validator import validate_fixed_wing
from aero_ai.templates.fixed_wing.balance import balance_fixed_wing
from aero_ai.templates.fixed_wing.trim import trim_fixed_wing
from aero_ai.templates.fixed_wing.geometry import build_fixed_wing_geometry
from aero_ai.templates.fixed_wing.analysis import analyze_fixed_wing


class FixedWingTemplate(AircraftTemplate):
    name = "fixed_wing"

    def size(self, req: Requirements) -> Design:
        return size_fixed_wing(req)

    def validate(self, design: Design) -> list[Issue]:
        return validate_fixed_wing(design)

    def refine(self, design: Design, req: Requirements) -> Design:
        return trim_fixed_wing(balance_fixed_wing(design, req), req)

    def build_geometry(self, design: Design, out_dir: str) -> list[str]:
        return build_fixed_wing_geometry(design, out_dir)

    def analyze(self, design: Design, req: Requirements) -> Results:
        return analyze_fixed_wing(design, req)
