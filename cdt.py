# Constraint Delaunay Triangulation
# use CDT python binding
# https://github.com/artem-ogre/PythonCDT

import numpy as np
import PythonCDT as cdt
import matplotlib.pyplot as plt

from loader import Loader

# t = cdt.Triangulation(
#     cdt.VertexInsertionOrder.AS_PROVIDED,
#     cdt.IntersectingConstraintEdges.NOT_ALLOWED,
#     0.5,
# )

# t.insert_vertices(vv)
# ee = [cdt.Edge(0, 2)]
# t.insert_edges(ee)
# t.erase_super_triangle()

#  Test resolving fixed edge intersections
t = cdt.Triangulation(
    cdt.VertexInsertionOrder.AS_PROVIDED,
    cdt.IntersectingConstraintEdges.TRY_RESOLVE,
    0.0,
)

# ==============================================================================
# load vertices using Loader
ld = Loader(".")
# ld.load_wo_wall_case(4)
ld.load_w_walls_case(0)

print(ld.vertices)

vv = [cdt.V2d(*v) for v in ld.vertices]
if ld.indices is not None:
    ee = [cdt.Edge(e[0], e[1]) for e in ld.indices]
else:
    ee = [cdt.Edge(i, i + 1) for i in range(len(vv) - 1)]
    ee.append(cdt.Edge(len(vv) - 1, 0))

print(ee)
print(vv)

# ==============================================================================

t.insert_vertices(vv)
t.insert_edges(ee)

# t.erase_super_triangle()
t.erase_outer_triangles_and_holes()

# print(t.triangles)
# print(t.vertices)
# print(t.fixed_edges)

# ===============visualize================
plt.figure()

# plot vv
for v in vv:
    plt.plot(v.x, v.y, "ro", lw=2)

for tri in t.triangles:
    v0 = t.vertices[tri.vertices[0]]
    v1 = t.vertices[tri.vertices[1]]
    v2 = t.vertices[tri.vertices[2]]
    plt.plot([v0.x, v1.x, v2.x, v0.x], [v0.y, v1.y, v2.y, v0.y], "k-")

# for v in t.vertices:
#     plt.plot(v.x, v.y, "ro")

# for e in t.fixed_edges:
#     v1 = t.vertices[e.v1]
#     v2 = t.vertices[e.v2]
#     plt.plot([v1.x, v2.x], [v1.y, v2.y], lw=6, c="k")

for e in ld.indices:
    v1 = ld.vertices[e[0]]
    v2 = ld.vertices[e[1]]
    plt.plot([v1[0], v2[0]], [v1[1], v2[1]], lw=4, c="k")

plt.axis("equal")
plt.show()
