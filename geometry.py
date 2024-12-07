import numpy as np
import pygmsh

class _GeoBase:
    __guid = 0

    def __init__(self):
        self.guid = _GeoBase.__guid
        _GeoBase.__guid += 1


class Node(_GeoBase):
    __vid = 0

    def __init__(self, pos, idx=None):
        super().__init__()

        self.idx = idx
        self.pos = pos
        self.next = []
        self.prev = []

        self.edges = []
        self.faces = []
        self.border = False

        self.vid = Node.__vid
        Node.__vid += 1

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def z(self):
        return self.pos[2]

    @property
    def xy(self):
        return self.pos[:2]

    @property
    def neighbors(self):
        return set(self.next + self.prev)

    # @property
    # def vid(self):
    #     return self.__vid

    def __eq__(self, other: "Node"):
        return self.vid == other.vid

    def __sub__(self, other):
        return self.xy - other.xy

    def __ne__(self, other):
        return not self.__eq__(other)

    # def move(self, dx, dy) -> None:
    #     if self.border:
    #         return
    #     xy_old = self.xy.copy()
    #     self.xy += [dx, dy]
    #     for f in self.faces:
    #         if f.flipped:
    #             self.xy = xy_old
    #             return

    def remove_duplicate(self):
        self.next = set(self.next)
        self.prev = set(self.prev)
        self.edges = set(self.edges)
        self.faces = set(self.faces)

    @xy.setter
    def xy(self, value):
        self._xy = value


class Edge(_GeoBase):
    def __init__(self, origin, to):
        super().__init__()

        # half edge with direction origin -> to
        self.origin = origin
        self.to = to
        self.face = None
        self.twin = None
        self.next = None
        self.prev = None

        self.is_wall = False

    @property
    def outside(self):
        return not self.twin

    @property
    def gid(self):
        return self.face.gid

    def dir(self):
        return (self.to.xy - self.origin.xy) / self.length()

    def orth(self):
        return np.array([dir[1], -dir[0]])

    def length(self):
        return np.linalg.norm(self.to.xy - self.origin.xy)

    def intersect(self, other):
        pass

    @staticmethod
    def get_all_blocked(edges: list):
        return [e for e in edges if e.is_wall]


class Face(_GeoBase):
    def __init__(self):
        super().__init__()

        self.nodes = []
        self.gid = 0
        self.half_edges = []
        self.adj_faces = []
        self.center = None

    @property
    def area(self):
        area = 0
        for i in range(3):
            j = (i + 1) % 3
            area += (
                    self.nodes[i].x * self.nodes[j].y - self.nodes[j].x * self.nodes[i].y
            )
        return area / 2

    @property
    def flipped(self):
        return self.area < 0

    @property
    def neighbors(self):
        return self.adj_faces

    @property
    def xy(self):
        return self.center

    @property
    def x(self):
        return self.center[0]

    @property
    def y(self):
        return self.center[1]

    def set_adj_faces(self):
        self.adj_faces = []
        for e in self.half_edges:
            if e.twin:
                self.adj_faces.append(e.twin.face)
        return self.adj_faces

    def remove_duplicate(self):
        self.nodes = set(self.nodes)
        self.half_edges = set(self.half_edges)

    def set_center(self):
        if not self.nodes:
            return
        else:
            xys = [n.xy for n in self.nodes]
            self.center = np.average(xys, axis=0)

    def get_portal(self, other: "Face"):    # TODO: make sure nodes are clockwise
        for e in self.half_edges:
            if e.twin and e.twin.face == other:
                return e.origin, e.to
        return None


class Mesh:
    def __init__(self):
        self.faces = []
        self.edges = []
        self.nodes = []

        self.blocked_edges = None

    @property  # alias
    def vertices(self):
        return self.nodes

    def create(self, polygon, mesh_size=0.1):
        with pygmsh.geo.Geometry() as geom:
            geom.add_polygon(
                polygon,
                mesh_size=mesh_size,
            )
            mesh = geom.generate_mesh()
            # return mesh.points, mesh.cells_dict["triangle"]
        self.from_mesh(mesh.points, mesh.cells_dict["triangle"])

    def from_mesh(self, nodes, faces):
        self.clear()

        # nodes
        for i, xy in enumerate(nodes):
            self.nodes.append(Node(xy[:2], i))

        # faces
        for i, f in enumerate(faces):
            face = Face()
            face.nodes = [
                self.nodes[f[0]],
                self.nodes[f[1]],
                self.nodes[f[2]],
            ]
            self.faces.append(face)

            for j in f:
                self.nodes[j].faces.append(face)

        for i, (fi, fj, fk) in enumerate(faces):
            # prev i - k - j - i
            self.nodes[fi].prev.append(self.nodes[fk])
            self.nodes[fj].prev.append(self.nodes[fi])
            self.nodes[fk].prev.append(self.nodes[fj])
            # next i - j - k - i
            self.nodes[fi].next.append(self.nodes[fj])
            self.nodes[fj].next.append(self.nodes[fk])
            self.nodes[fk].next.append(self.nodes[fi])

            eij = Edge(self.nodes[fi], self.nodes[fj])
            ejk = Edge(self.nodes[fj], self.nodes[fk])
            eki = Edge(self.nodes[fk], self.nodes[fi])

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

        # finalize
        self.set_twin()
        self.set_nodes_info()
        self.set_faces_info()
        self.blocked_edges = Edge.get_all_blocked(self.edges)

    def set_twin(self):
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

    def set_nodes_info(self):
        for e in self.edges:
            if e.twin is None:
                self.nodes[e.origin.idx].border = True
                self.nodes[e.to.idx].border = True
                e.is_wall = True

    def set_faces_info(self):
        for f in self.faces:
            f.set_adj_faces()
            f.set_center()

    def clear(self):
        self.faces.clear()
        self.edges.clear()
        self.nodes.clear()

    def get_node_by_vid(self, vid):
        for n in self.nodes:
            if n.vid == vid:
                return n
        return None


# alias
Point = Node
Vertex = Node
Line = Edge
