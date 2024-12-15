import numpy as np


class _GeoBase:
    __guid = 0
    obj_list = []

    def __init__(self):
        self.guid = _GeoBase.__guid
        _GeoBase.__guid += 1
        _GeoBase.obj_list.append(self)

    @staticmethod
    def reset_guid():
        _GeoBase.__guid = 0

    @staticmethod
    def get_by_guid(guid):
        for obj in _GeoBase.obj_list:
            if obj.guid == guid:
                return obj
        return None


class Vertex(_GeoBase):
    __vid = 0
    node_list = []

    def __init__(self, pos):
        super().__init__()
        Vertex.node_list.append(self)

        # self.idx = idx
        self.pos = pos
        self.next = []
        self.prev = []

        self.edges = []
        self.faces = []
        self.border = False

        self.vid = Vertex.__vid
        Vertex.__vid += 1

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

    @property
    def dim(self):
        return len(self.pos)

    # @property
    # def vid(self):
    #     return self.__vid

    def __eq__(self, other: "Vertex"):
        return self.vid == other.vid
        # return np.allclose(self.xy, other.xy)

    def __sub__(self, other):
        return self.pos - other.pos

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

    def is_same_id(self, other):
        return self.vid == other.vid

    def remove_duplicate(self):
        self.next = set(self.next)
        self.prev = set(self.prev)
        self.edges = set(self.edges)
        self.faces = set(self.faces)

    @xy.setter
    def xy(self, value):
        self._xy = value

    @staticmethod
    def get_by_vid(nid):
        for n in Vertex.node_list:
            if n.vid == nid:
                return n
        return None


class Edge(_GeoBase):
    __eid = 0
    edge_list = []

    def __init__(self, origin, to, is_blocked=False):
        super().__init__()
        Edge.edge_list.append(self)

        # half edge with direction origin -> to
        self.ori = origin
        self.to = to
        self.face = None
        self.twin = None
        self.next = None
        self.prev = None

        self.is_blocked = is_blocked

        # Private
        self.__diagonal_vertex = None  # for triangulation (Const)
        self.__eid = Edge.__eid
        Edge.__eid += 1

    def set_properties(self, face, twin, prev, next, diag_vertex=None):
        self.face = face
        self.twin = twin
        self.next = next
        self.prev = prev
        if diag_vertex:
            self.set_diagonal_vertex(diag_vertex)

    def set_diagonal_vertex(self, vertex):
        if self.__diagonal_vertex is None:
            self.__diagonal_vertex = vertex
        else:
            raise ValueError("Diagonal vertex is already set")

    def get_dir(self):
        return (self.to.xy - self.ori.xy) / self.length()

    def get_orth(self):
        return np.array([dir[1], -dir[0]])

    def mid(self):
        return (self.ori.xy + self.to.xy) / 2

    def length(self):
        return np.linalg.norm(self.to.xy - self.ori.xy)

    def intersect(self, other):
        pass

    @staticmethod
    def get_all_blocked(edges: list):
        """deprecating, use blocked_edges instead"""
        return [e for e in edges if e.is_blocked]

    @property
    def eid(self):
        return self.__eid

    @property
    def diagonal_vertex(self):
        return self.__diagonal_vertex

    @property
    def outside(self):
        return not self.twin

    @property
    def gid(self):
        return self.face.gid

    @property
    def is_wall(self):
        return self.is_blocked

    @property
    def can_pass(self):
        return not self.is_blocked

    @staticmethod
    def get_by_eid(eid):
        for e in Edge.edge_list:
            if e.eid == eid:
                return e
        return None

    # geometry utils
    def disconnect(self):
        if self.outside:
            return

        self.prev.next = self.twin.next
        self.next.prev = self.twin.prev
        self.twin.prev.next = self.next
        self.twin.next.prev = self.prev

    # def cut(self, position, Point=Vertex, Edge="Edge", Face=Face):
    #     p_cut = Point(position)
    #     e_new = Edge(p_cut, self.to)
    #     e_new_t = Edge(self.to, p_cut)
    #     diag, diag_t = self.diagonal_vertex, self.twin.diagonal_vertex
    #     e0, e0_t = Edge(p_cut, diag), Edge(diag, p_cut)
    #     e1, e1_t = Edge(diag_t, p_cut), Edge(p_cut, diag_t)
    #     f0, f1 = Face(), Face()
    #
    #     # set properties[face, twin, prev, next, diag]
    #     e_new.set_properties(f0, e_new_t, self, self.next, diag)
    #     e_new_t.set_properties(f1, e_new, self.twin.prev, self.twin, diag_t)
    #     e0.set_properties(self.face, e0_t, self, self.prev, self.ori)
    #     e0_t.set_properties(f0, e0, self.next, e_new, self.to)
    #     e1.set_properties(
    #         self.twin.face, e1_t, self.twin.next, self.twin, self.ori
    #     )
    #     e1_t.set_properties(f1, e1, e_new_t, self.twin.prev, self.to)
    #
    #     # set vertices
    #     p_cut.edges = [e_new, e_new_t, e0, e0_t, e1, e1_t]
    #     p_cut.faces = [f0, f1, self.face, self.twin.face]
    #
    #     # set faces
    #     f0.half_edges = [self.next, e0_t, e_new]
    #     f1.half_edges = [e1_t, self.twin.prev, e_new_t]
    #     f1.adj_faces = [f0, self.twin.prev.face, self.twin.face]
    #     f0.adj_faces = [f1, self.next.face, self.face]
    #
    #     # update other
    #     self.face.adj_faces = [f0, self.prev.face, self.twin.face]
    #     self.twin.face.adj_faces = [f1, self.twin.next.face, self.face]
    #     self.face.half_edges = [self.prev, self, e0]
    #     self.twin.face.half_edges = [e1, self.twin, self.twin.next]
    #
    #     self.twin.ori = p_cut
    #     self.twin.prev = e1
    #     self.to = p_cut
    #     self.next = e0
    #
    #     # newly added Points, Edges, Faces
    #     return [p_cut], [e_new, e_new_t, e0, e0_t, e1, e1_t], [f0, f1]


class Face(_GeoBase):
    __fid = 0
    face_list = []

    def __init__(self):
        super().__init__()
        Face.face_list.append(self)

        self.verts = []
        self.half_edges = []
        self.adj_faces = []

        # private
        self.__fid = Face.__fid
        Face.__fid += 1

    def set_adj_faces(self):
        self.adj_faces = []
        for e in self.half_edges:
            if e.twin:
                self.adj_faces.append(e.twin.face)
        return self.adj_faces

    def remove_duplicate(self):
        self.verts = set(self.verts)
        self.half_edges = set(self.half_edges)

    @property
    def area(self):
        area = 0
        for i in range(len(self.verts)):
            j = (i + 1) % 3
            area += (
                self.verts[i].x * self.verts[j].y
                - self.verts[j].x * self.verts[i].y
            )
        return area / 2

    @property
    def flipped(self):
        return self.area < 0

    @property
    def neighbors(self):
        return self.adj_faces

    @property
    def fid(self):
        return self.__fid

    @property
    def xy(self):
        return self.center

    @property
    def x(self):
        return self.center[0]

    @property
    def y(self):
        return self.center[1]

    @property
    def center(self):
        xys = [n.xy for n in self.verts]
        return np.average(xys, axis=0)

    def get_shared_edge(self, other: "Face"):
        for e in self.half_edges:
            if e.twin and e.twin.face == other:
                return e
        return None

    @staticmethod
    def get_by_fid(fid):
        for f in Face.face_list:
            if f.fid == fid:
                return f
        return None

    def __gt__(self, other):
        return self.fid > other.fid

    def __lt__(self, other):
        return self.fid < other.fid


# alias
Point = Vertex
# Vertex = Node
Line = Edge
