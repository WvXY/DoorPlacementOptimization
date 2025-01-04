from g_primitives import Vertex, Edge, Face, _GeoBase
from u_cdt import CDT


class Mesh:
    """Half-edge data structure"""

    def __init__(self):
        self.cdt = None
        self.Vertex = Vertex
        self.Edge = Edge
        self.Face = Face

        self.faces = []
        self.edges = []
        self.verts = []

        self.border_edges = []
        self.inner_fixed_edges = []

    def append(self, v=None, e=None, f=None):
        if v:
            self.verts += v
        if e:
            self.edges += e
        if f:
            self.faces += f

    def remove(self, v_list=None, e_list=None, f_list=None):
        if v_list:
            self.verts = [v for v in self.verts if v not in v_list]
        if e_list:
            self.edges = [e for e in self.edges if e not in e_list]
        if f_list:
            self.faces = [f for f in self.faces if f not in f_list]

    # alias
    @property
    def vertices(self):
        return self.verts

    @property
    def fixed_edges(self):
        return self.border_edges + self.inner_fixed_edges

    def set_default_types(self, Vertex=Vertex, Edge=Edge, Face=Face):
        self.Vertex = Vertex
        self.Edge = Edge
        self.Face = Face

    def clear(self):
        self.faces.clear()
        self.edges.clear()
        self.verts.clear()

    def reset_all_visited(self, rgeos):
        for g in rgeos:
            g.reset_visited()

    def get_block_edges(self):
        self.inner_fixed_edges = [
            e for e in self.edges if e.is_blocked and not e.is_outer
        ]
        return self.inner_fixed_edges + self.border_edges

    def create_mesh(self, vertices, edges, min_dist_to_constraint_edge=0.0):
        self.cdt = CDT(min_dist_to_constraint_edge)
        self.cdt.insert_vertices(vertices)
        self.cdt.insert_edges(edges)
        # self.cdt.erase_outer_triangles_and_holes()    # hole is also needed
        self.cdt.erase_outer_triangles()
        triangles = self.cdt.get_triangles(to_numpy=True)
        vertices = self.cdt.get_vertices(to_numpy=True)
        self.from_mesh(vertices, triangles)

    def from_mesh(self, nodes, faces):
        self.clear()

        # TODO: simplify creation process
        self.__init_nodes(nodes)
        self.__init_faces(faces)
        self.__init_half_edges(faces)

        self.__post_processing()

    def __init_nodes(self, nodes):
        for i, xy in enumerate(nodes):
            self.verts.append(self.Vertex(xy[:2]))

    def __init_faces(self, faces):
        for i, f in enumerate(faces):
            face = self.Face()
            self.faces.append(face)

    def __init_half_edges(self, faces):
        for i, (fi, fj, fk) in enumerate(faces):
            eij = self.Edge(self.verts[fi], self.verts[fj])
            ejk = self.Edge(self.verts[fj], self.verts[fk])
            eki = self.Edge(self.verts[fk], self.verts[fi])

            # face.half_edges
            eij.next, ejk.next, eki.next = ejk, eki, eij
            eij.prev, ejk.prev, eki.prev = eki, eij, ejk
            eij.face, ejk.face, eki.face = (
                self.faces[i],
                self.faces[i],
                self.faces[i],
            )

            # Set diagonal vertex
            eij.set_diagonal_vertex(self.verts[fk])
            ejk.set_diagonal_vertex(self.verts[fi])
            eki.set_diagonal_vertex(self.verts[fj])

            self.edges += [eij, ejk, eki]
            self.faces[i].set_edges([eij, ejk, eki])

            # node.edges
            self.verts[fi].add_edges([eij, eki])
            self.verts[fj].add_edges([eij, ejk])
            self.verts[fk].add_edges([ejk, eki])

    def __post_processing(self):
        self.__set_twins()
        self.__set_fixed_edges()

    def __set_twins(self):
        n = len(self.edges)
        for i in range(n):
            ei = self.edges[i]
            if ei.twin:
                continue

            for j in range(i + 1, n):
                ej = self.edges[j]
                if ej.twin:
                    continue

                if ei.ori == ej.to and ei.to == ej.ori:
                    ei.twin, ej.twin = ej, ei

    # def __set_nodes_info(self):
    #     for e in self.edges:
    #         if e.twin is None:
    #             self.verts[e.ori.vid].is_blocked = True
    #             self.verts[e.to.vid].is_blocked = True
    #             e.is_blocked = True

    def __set_fixed_edges(self):
        for fe in self.cdt.get_fixed_edges(to_numpy=True):
            v0, v1 = self.verts[fe[0]], self.verts[fe[1]]
            v0.is_blocked = True
            v1.is_blocked = True
            for e in v0.half_edges:
                if e.to == v1 or e.ori == v1:
                    e.is_blocked = True

                    if e.twin:
                        e.twin.is_blocked = True
                        self.inner_fixed_edges.append(e)
                        self.inner_fixed_edges.append(e.twin)
                    else:
                        self.border_edges.append(e)

                    break

        self.border_edges = list(set(self.border_edges))
        self.inner_fixed_edges = list(set(self.inner_fixed_edges))

    def __remove_duplicate(self):
        self.verts = set(self.verts)
        self.border_edges = set(self.border_edges)
        self.inner_fixed_edges = set(self.inner_fixed_edges)
        self.faces = set(self.faces)
        self.edges = set(self.edges)
