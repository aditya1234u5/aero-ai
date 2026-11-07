from abc import ABC, abstractmethod
from aero_ai.schemas import Requirements, Design, Issue, Results


class AircraftTemplate(ABC):
    """Every aircraft type must implement these five steps."""

    name: str   # the aircraft_type string that selects this template

    @abstractmethod
    def size(self, req: Requirements) -> Design:
        """Turn requirements into design numbers."""

    @abstractmethod
    def validate(self, design: Design) -> list[Issue]:
        """Reject physically impossible designs."""

    @abstractmethod
    def refine(self, design: Design, req: Requirements) -> Design:
        """Tune the layout (balance, trim) so the design flies well."""

    @abstractmethod
    def build_geometry(self, design: Design, out_dir: str) -> list[str]:
        """Create 3D files and return their paths."""

    @abstractmethod
    def analyze(self, design: Design, req: Requirements) -> Results:
        """Run the simulations."""
