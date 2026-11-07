import numpy as np
import aerosandbox as asb
from build123d import Box, export_stl

af = asb.Airfoil("naca2412")
aero = af.get_aero_from_neuralfoil(alpha=5, Re=3e5, mach=0)
print({k: float(np.squeeze(aero[k])) for k in ("CL", "CD")})

export_stl(Box(10, 5, 2), "test_box.stl")
print("STL exported: test_box.stl")
