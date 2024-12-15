from g_primitives import Vertex, Edge, Face, _GeoBase
from u_cdt import CDT


class Mesh(_GeoBase):
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

    # alias
    @property
    def vertices(self):
        return self.verts

    @property
    def fixed_edges(self):
        return self.border_edges + self.inner_fixed_edges

    def set_default_types(self, Node=Vertex, Edge=Edge, Face=Face):
        self.Vertex = Node
        self.Edge = Edge
        self.Face = Face

    def clear(self):
        self.faces.clear()
        self.edges.clear()
        self.verts.clear()

    def get_block_edges(self):
        self.inner_fixed_edges = [
            e for e in self.edges if e.is_blocked and not e.outside
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
            face.verts = [
                self.verts[f[0]],
                self.verts[f[1]],
                self.verts[f[2]],
            ]
            self.faces.append(face)

            for j in f:
                self.verts[j].faces.append(face)

    def __init_half_edges(self, faces):
        for i, (fi, fj, fk) in enumerate(faces):
            # prev i - k - j - i
            self.verts[fi].prev.append(self.verts[fk])
            self.verts[fj].prev.append(self.verts[fi])
            self.verts[fk].prev.append(self.verts[fj])
            # next i - j - k - i
            self.verts[fi].next.append(self.verts[fj])
            self.verts[fj].next.append(self.verts[fk])
            self.verts[fk].next.append(self.verts[fi])

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
            self.faces[i].half_edges = [eij, ejk, eki]

            # node.edges
            self.verts[fi].edges += [eij, eki]
            self.verts[fj].edges += [eij, ejk]
            self.verts[fk].edges += [ejk, eki]

    def __post_processing(self):
        self.__set_twins()
        self.__set_nodes_info()
        self.__set_faces_info()
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

    def __set_nodes_info(self):
        for e in self.edges:
            if e.twin is None:
                self.verts[e.ori.vid].border = True
                self.verts[e.to.vid].border = True
                e.is_blocked = True

    def __set_faces_info(self):
        for f in self.faces:
            f.set_adj_faces()

    def __set_fixed_edges(self):
        for fe in self.cdt.get_fixed_edges(to_numpy=True):
            v0, v1 = self.verts[fe[0]], self.verts[fe[1]]
            for e in v0.edges:
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
