from g_primitives import Node, Edge, Face, _GeoBase
from u_cdt import CDT


class Mesh(_GeoBase):
    """Half-edge data structure"""

    def __init__(self):
        self.cdt = None
        self.Node = Node
        self.Edge = Edge
        self.Face = Face

        self.faces = []
        self.edges = []
        self.nodes = []

        self.border_edges = []
        self.inner_fixed_edges = []

    # alias
    @property
    def vertices(self):
        return self.nodes

    @property
    def fixed_edges(self):
        return self.border_edges + self.inner_fixed_edges

    def set_default_types(self, Node=Node, Edge=Edge, Face=Face):
        self.Node = Node
        self.Edge = Edge
        self.Face = Face

    def clear(self):
        self.faces.clear()
        self.edges.clear()
        self.nodes.clear()

    # def get_node_by_vid(self, vid):
    #     for n in self.nodes:
    #         if n.vid == vid:
    #             return n
    #     return None

    def create(self, vertices, edges, min_dist_to_constraint_edge=0.0):
        self.cdt = CDT(min_dist_to_constraint_edge)
        self.cdt.insert_vertices(vertices)
        self.cdt.insert_edges(edges)
        self.cdt.erase_outer_triangles_and_holes()
        triangles = self.cdt.get_triangles(to_numpy=True)
        vertices = self.cdt.get_vertices(to_numpy=True)
        self.from_mesh(vertices, triangles)

    def from_mesh(self, nodes, faces):
        self.clear()

        self.__init_nodes(nodes)
        self.__init_faces(faces)
        self.__init_half_edges(faces)

        self.__post_processing()

    def __init_nodes(self, nodes):
        for i, xy in enumerate(nodes):
            self.nodes.append(self.Node(xy[:2], i))

    def __init_faces(self, faces):
        for i, f in enumerate(faces):
            face = self.Face()
            face.nodes = [
                self.nodes[f[0]],
                self.nodes[f[1]],
                self.nodes[f[2]],
            ]
            self.faces.append(face)

            for j in f:
                self.nodes[j].faces.append(face)

    def __init_half_edges(self, faces):
        for i, (fi, fj, fk) in enumerate(faces):
            # prev i - k - j - i
            self.nodes[fi].prev.append(self.nodes[fk])
            self.nodes[fj].prev.append(self.nodes[fi])
            self.nodes[fk].prev.append(self.nodes[fj])
            # next i - j - k - i
            self.nodes[fi].next.append(self.nodes[fj])
            self.nodes[fj].next.append(self.nodes[fk])
            self.nodes[fk].next.append(self.nodes[fi])

            eij = self.Edge(self.nodes[fi], self.nodes[fj])
            ejk = self.Edge(self.nodes[fj], self.nodes[fk])
            eki = self.Edge(self.nodes[fk], self.nodes[fi])

            # face.half_edges
            eij.next, ejk.next, eki.next = ejk, eki, eij
            eij.prev, ejk.prev, eki.prev = eki, eij, ejk
            eij.face, ejk.face, eki.face = (
                self.faces[i],
                self.faces[i],
                self.faces[i],
            )

            self.edges += [eij, ejk, eki]
            self.faces[i].half_edges = [eij, ejk, eki]

            # node.edges
            self.nodes[fi].edges += [eij, eki]
            self.nodes[fj].edges += [eij, ejk]
            self.nodes[fk].edges += [ejk, eki]

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

                if ei.origin == ej.to and ei.to == ej.origin:
                    ei.twin, ej.twin = ej, ei

    def __set_nodes_info(self):
        for e in self.edges:
            if e.twin is None:
                self.nodes[e.origin.idx].border = True
                self.nodes[e.to.idx].border = True
                e.is_blocked = True

    def __set_faces_info(self):
        for f in self.faces:
            f.set_adj_faces()
            f.set_center()

    def __set_fixed_edges(self):
        for fe in self.cdt.get_fixed_edges(to_numpy=True):
            v0, v1 = self.nodes[fe[0]], self.nodes[fe[1]]
            for e in v0.edges:
                if e.to == v1 or e.origin == v1:
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
        self.nodes = set(self.nodes)
        self.border_edges = set(self.border_edges)
        self.inner_fixed_edges = set(self.inner_fixed_edges)
        self.faces = set(self.faces)
        self.edges = set(self.edges)
