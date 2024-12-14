# Constraint Delaunay Triangulation
# use CDT python binding
# https://github.com/artem-ogre/PythonCDT

import PythonCDT as cdt

import numpy as np


class CDT:
    def __init__(self, min_dist_to_constraint_edge=0.0):
        self.t = cdt.Triangulation(
            cdt.VertexInsertionOrder.AS_PROVIDED,
            cdt.IntersectingConstraintEdges.TRY_RESOLVE,
            min_dist_to_constraint_edge,
        )

    # input data
    def insert_vertices(self, vertices: list | np.ndarray):
        self.t.insert_vertices([cdt.V2d(*v) for v in vertices])

    def insert_edges(self, indices: list | np.ndarray = None):
        if indices is not None:
            ee = [cdt.Edge(e[0], e[1]) for e in indices]
        else:
            n = len(self.t.vertices)
            ee = [cdt.Edge(i, i + 1) for i in range(n - 1)]
            ee.append(cdt.Edge(n - 1, 0))
        self.t.insert_edges(ee)

    # settings
    def erase_super_triangle(self):
        self.t.erase_super_triangle()

    def erase_outer_triangles_and_holes(self):
        self.t.erase_outer_triangles_and_holes()

    # get data
    def get_triangles(self, to_numpy=False):
        if to_numpy:
            return np.array(
                [
                    [tri.vertices[0], tri.vertices[1], tri.vertices[2]]
                    for tri in self.t.triangles
                ]
            )
        return self.t.triangles

    def get_vertices(self, to_numpy=False):
        if to_numpy:
            return np.array([[v.x, v.y] for v in self.t.vertices])
        return self.t.vertices

    def get_fixed_edges(self, to_numpy=False):
        if to_numpy:
            return np.array([[e.v1, e.v2] for e in self.t.fixed_edges])
        return self.t.fixed_edges

    def get_edges(self, to_numpy=False):
        if to_numpy:
            return np.array([[e.v1, e.v2] for e in self.t.edges])
        return self.t.edges


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from loader import Loader

    ld = Loader(".")
    ld.load_w_walls_case(3)
    ld.remove_duplicates()
    vertices = np.delete(ld.vertices, 1, 1)
    edges = ld.edges
    print(vertices)

    t = CDT()
    t.insert_vertices(vertices)
    t.insert_edges(edges)
    t.erase_outer_triangles_and_holes()

    plt.figure()

    # plot vv
    vv = t.get_vertices()
    for v in vv:
        plt.plot(v.x, v.y, "ro", lw=2)

    for tri in t.get_triangles():
        v0 = vv[tri.vertices[0]]
        v1 = vv[tri.vertices[1]]
        v2 = vv[tri.vertices[2]]
        plt.plot([v0.x, v1.x, v2.x, v0.x], [v0.y, v1.y, v2.y, v0.y], "k-")

    for e in edges:
        v1 = vertices[e[0]]
        v2 = vertices[e[1]]
        plt.plot([v1[0], v2[0]], [v1[1], v2[1]], lw=4, c="k")

    plt.axis("equal")
    plt.show()
