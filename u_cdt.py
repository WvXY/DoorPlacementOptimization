# Constraint Delaunay Triangulation
# use CDT python binding
# https://github.com/artem-ogre/PythonCDT

import numpy as np

import PythonCDT as cdt


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
            ee = [cdt.Edge(ie[0], ie[1]) for ie in indices]
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

    def erase_outer_triangles(self):
        self.t.erase_outer_triangles()

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
    from u_data_loader import Loader
    from u_visualization import Visualizer

    # Load data
    ld = Loader(".")
    # ld.load_closed_rooms_case(case_id)
    ld.load_final_case(0)
    ld.optimize()

    print(ld.vertices)

    e_raw = ld.edges
    v_raw = ld.vertices

    i_cdt = CDT()
    i_cdt.insert_vertices(ld.vertices)
    i_cdt.insert_edges(ld.edges)
    i_cdt.erase_outer_triangles()

    v = i_cdt.get_vertices(to_numpy=True)
    e = i_cdt.get_fixed_edges(to_numpy=True)
    t = i_cdt.get_triangles(to_numpy=True)

    for ee in e_raw:
        plt.plot(v_raw[ee, 0], v_raw[ee, 1], "b-", lw=2)

    for tri in t:
        plt.fill(v[tri, 0], v[tri, 1], edgecolor="black", fill=False)

    # for ee in e:
    #     plt.plot(v[ee, 0], v[ee, 1], "r-", lw=8)

    plt.show()
