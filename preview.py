import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

m = trimesh.load("outputs/fixed_wing.stl")
print("watertight:", m.is_watertight, "| triangles:", len(m.faces))
fig = plt.figure(figsize=(14, 5))
for i, (el, az, title) in enumerate([(25, -60, "3D view"), (90, -90, "Top view"), (0, -90, "Side view")]):
    ax = fig.add_subplot(1, 3, i + 1, projection="3d")
    ax.add_collection3d(Poly3DCollection(m.triangles, facecolor="#8fb3d9", edgecolor="#2b4a6b", linewidth=0.1))
    b = m.bounds
    c = (b[0] + b[1]) / 2
    r = (b[1] - b[0]).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.view_init(el, az)
    ax.set_title(title)
    ax.set_axis_off()
plt.tight_layout()
plt.savefig("preview.png", dpi=110)
print("saved preview.png")
