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

    def get_guid(self):
        return self.__guid

    def _replace(self, in_list: list, old, new):
        for i, obj in enumerate(in_list):
            if obj == old:
                in_list[i] = new

    def remove_duplicate(self):
        _GeoBase.obj_list = set(_GeoBase.obj_list)

    @staticmethod
    def clear():
        pass

    @staticmethod
    def clear_all(self):
        _GeoBase.obj_list = []
        _GeoBase.__guid = 0


class _GInfo:
    def __init__(self):
        self.is_visited = False
        self.is_blocked = False

    def reset_all_visited(self):
        for obj in _GeoBase.obj_list:
            obj.is_visited = False

    def reset_visited(self):
        self.is_visited = False

    @property
    def is_wall(self):
        return self.is_blocked

    @property
    def can_pass(self):
        return not self.is_blocked


class Vertex(_GeoBase, _GInfo):
    __vid = 0
    node_list = []

    def __init__(self, pos):
        super().__init__()
        Vertex.node_list.append(self)

        self.pos = np.array(pos)
        self.half_edges = []

        self.vid = Vertex.__vid
        Vertex.__vid += 1

    def set_pos(self, new_pos):
        self.pos = new_pos

    def set_edges(self, half_edges):
        self.half_edges = half_edges

    def remove_edges(self, *half_edges):
        for half_edge in half_edges:
            self.half_edges.remove(half_edge)

    def replace_edge(self, old_edge, new_edge):
        self._replace(self.half_edges, old_edge, new_edge)

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
    def faces(self):
        return set([e.face for e in self.half_edges])

    @property
    def edges(self):
        return set(self.half_edges)

    @property
    def dim(self):
        return len(self.pos)

    def __eq__(self, other: "Vertex"):
        return self.vid == other.vid
        # return np.allclose(self.xy, other.xy)

    def __sub__(self, other):
        if isinstance(other.pos, np.ndarray):
            return self.pos - other.pos
        return [self.x - other.x, self.y - other.y]

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
        self.half_edges = set(self.half_edges)

    @xy.setter
    def xy(self, value):
        self._xy = value

    @staticmethod
    def get_by_vid(nid):
        for n in Vertex.node_list:
            if n.vid == nid:
                return n
        return None

    @staticmethod
    def clear():
        Vertex.node_list = []
        Vertex.__vid = 0


class Edge(_GeoBase, _GInfo):
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
        return (self.to.xy - self.ori.xy) / np.linalg.norm(
            self.to.xy - self.ori.xy
        )

    def get_orth(self):
        return np.array([self.get_dir()[1], -self.get_dir()[0]])

    def get_mid(self):
        return (self.ori.xy + self.to.xy) / 2

    def get_length(self):
        return np.linalg.norm(self.to.xy - self.ori.xy)

    def intersect(self, other):
        pass

    @property
    def eid(self):
        return self.__eid

    @property
    def diagonal_vertex(self):
        return self.__diagonal_vertex

    @property
    def is_outer_wall(self):
        return not self.twin

    @staticmethod
    def get_by_eid(eid):
        for e in Edge.edge_list:
            if e.eid == eid:
                return e
        return None

    # geometry utils
    def disconnect(self):
        if self.is_outer_wall:
            return

        self.prev.next = self.twin.next
        self.next.prev = self.twin.prev
        self.twin.prev.next = self.next
        self.twin.next.prev = self.prev

    def remove_duplicate(self):
        Edge.edge_list = set(Edge.edge_list)

    @staticmethod
    def clear():
        Edge.edge_list = []
        Edge.__eid = 0


class Face(_GeoBase, _GInfo):
    __fid = 0
    face_list = []

    def __init__(self):
        super().__init__()
        Face.face_list.append(self)

        self.half_edges = []
        self.adjs = []

        # private
        self.__fid = Face.__fid
        Face.__fid += 1

    def auto_set_adj_faces(self):
        self.adjs = []
        for e in self.half_edges:
            if e.twin:
                self.adjs.append(e.twin.face)
        return self.adjs

    def set_edges(self, half_edges):
        self.half_edges = half_edges

    def set_adjs(self, adj_faces):
        self.adjs = adj_faces

    def replace_edge(self, old_edge, new_edge):
        self._replace(self.half_edges, old_edge, new_edge)

    def replace_adj_face(self, old_face, new_face):
        self._replace(self.adjs, old_face, new_face)

    def remove_duplicate(self):
        self.adjs = set(self.adjs)
        self.half_edges = set(self.half_edges)
        Face.face_list = set(Face.face_list)

    @property
    def verts(self):
        return [e.ori for e in self.half_edges]

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
    def edges(self):
        return self.half_edges

    @property
    def flipped(self):
        return self.area < 0

    @property
    def neighbors(self):
        return self.adjs

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

    @staticmethod
    def clear():
        Face.face_list = []
        Face.__fid = 0


# alias
Point = Vertex
# Vertex = Node
Line = Edge
