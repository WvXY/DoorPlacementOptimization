# Constraint Delaunay Triangulation
# use CDT python binding
# https://github.com/artem-ogre/PythonCDT

import numpy as np
import PythonCDT as cdt
import matplotlib.pyplot as plt

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

vv = [cdt.V2d(-1, 0), cdt.V2d(0, 0.5), cdt.V2d(1, 0), cdt.V2d(0, -0.5)]
vv2 = [cdt.V2d(0, 0), cdt.V2d(0.1, 0), cdt.V2d(0.1, 0.1)]

ee = [
    # cdt.Edge(0, 2),
    # cdt.Edge(1, 3),
    cdt.Edge(0, 1),
    cdt.Edge(1, 2),
    cdt.Edge(2, 3),
    cdt.Edge(3, 0),
]
ee2 = [cdt.Edge(5, 4), cdt.Edge(6, 5)]

t.insert_vertices(vv)
t.insert_vertices(vv2)
t.insert_edges(ee)
t.insert_edges(ee2)
t.erase_super_triangle()
# t.erase_outer_triangles_and_holes()

print(t.triangles)
print(t.vertices)
print(t.fixed_edges)

# visualize
plt.figure()

# plot vv
for v in vv:
    plt.plot(v.x, v.y, "ro", lw=2)

for tri in t.triangles:
    v0 = t.vertices[tri.vertices[0]]
    v1 = t.vertices[tri.vertices[1]]
    v2 = t.vertices[tri.vertices[2]]
    plt.plot([v0.x, v1.x, v2.x, v0.x], [v0.y, v1.y, v2.y, v0.y], "k-")

for v in t.vertices:
    plt.plot(v.x, v.y, "ro")

plt.show()
