from g_primitives import Vertex, Edge, Face
from u_cdt import CDT


class Mesh:
    """Half-edge data structure"""

    def __init__(self):
        self.cdt = None
        self.Vertex = Vertex
        self.Edge = Edge
        self.Face = Face

        self.faces = None
        self.edges = None
        self.verts = None
        self.fixed_edges = None

        self.border_edges = []
        self.inner_fixed_edges = []

    def append(self, v=None, e=None, f=None):
        if v:
            self.verts.update(v)
        if e:
            self.edges.update(e)
        if f:
            self.faces.update(f)

    def remove(self, v_list=None, e_list=None, f_list=None):
        if v_list:
            self.verts.difference_update(v_list)
        if e_list:
            self.edges.difference_update(e_list)
        if f_list:
            self.faces.difference_update(f_list)

    # alias
    @property
    def vertices(self):
        return self.verts

    def set_default_types(self, Vertex, Edge, Face):
        self.Vertex = Vertex
        self.Edge = Edge
        self.Face = Face

    def clear(self):
        self.faces.clear()
        self.edges.clear()
        self.verts.clear()

    def reset_all_visit_status(self, rgeos):
        for g in rgeos:
            g.reset_visit_status()

    def get_block_edges(self):
        self.inner_fixed_edges = [
            e for e in self.edges if e.is_blocked and not e.is_outer
        ]
        return self.inner_fixed_edges + list(self.border_edges)

    def create_mesh(self, vertices, edges, min_dist_to_constraint_edge=0.0):
        self.cdt = CDT(min_dist_to_constraint_edge)
        self.cdt.insert_vertices(vertices)
        self.cdt.insert_edges(edges)
        self.cdt.erase_outer_triangles()
        # self.cdt.erase_outer_triangles_and_holes()  # hole is also needed

        self.fixed_edges = self.cdt.get_fixed_edges(to_numpy=True)
        triangles = self.cdt.get_triangles(to_numpy=True)
        vertices = self.cdt.get_vertices(to_numpy=True)

        self.from_mesh(vertices, triangles)
        del self.cdt

    def from_mesh(self, nodes, faces):
        # self.clear()

        self.verts, self.edges, self.faces = [], [], []
        self.__init_nodes(nodes)
        self.__init_faces(faces)
        self.__init_half_edges(faces)
        self.__post_processing()

        self.__all_to_set()

    def __init_nodes(self, nodes):
        for i, xy in enumerate(nodes):
            vertex = self.Vertex(xy[:2])
            vertex.is_fixed = True
            self.verts.append(vertex)

    def __init_faces(self, faces: list):
        self.faces = [self.Face() for _ in range(len(faces))]

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

    def __set_fixed_edges(self):
        for fe in self.fixed_edges:
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

    def __all_to_set(self):
        self.verts = set(self.verts)
        self.edges = set(self.edges)
        self.faces = set(self.faces)
        self.border_edges = set(self.border_edges)
        self.inner_fixed_edges = set(self.inner_fixed_edges)
