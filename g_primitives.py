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

    def _replace(self, target, old, new):
        if isinstance(target, list):  # in-place replacement
            target[target.index(old)] = new
        elif isinstance(target, set):
            target.remove(old)
            target.add(new)
        return False

    @classmethod
    def remove_duplicate(cls):
        _GeoBase.obj_list = set(cls.obj_list)

    @staticmethod
    def clear():
        pass

    @staticmethod
    def clear_all(self):
        _GeoBase.obj_list = []
        _GeoBase.__guid = 0

    def __hash__(self):
        return hash(self.guid)


class _GInfo:
    def __init__(self):
        self._is_visited = False
        self._is_blocked = False

    # visit actions
    def reset_all_visited(self):
        for obj in _GeoBase.obj_list:
            obj._is_visited = False

    def reset_visited(self):
        self._is_visited = False

    @property
    def is_visited(self):
        return self._is_visited

    @is_visited.setter
    def is_visited(self, value):
        if not isinstance(value, bool):
            raise ValueError("Value must be boolean")
        self._is_visited = value

    def visit(self):
        self._is_visited = True

    # block/fixed actions
    @property
    def is_blocked(self):
        return self._is_blocked

    @property
    def is_fixed(self):
        return self._is_blocked

    @is_blocked.setter
    def is_blocked(self, value):
        self._is_blocked = value

    @is_fixed.setter
    def is_fixed(self, value):
        self.is_blocked = value


class Vertex(_GeoBase, _GInfo):
    __vid = 0
    node_list = []

    def __init__(self, pos):
        super().__init__()
        Vertex.node_list.append(self)

        self.pos = np.array(pos)
        self.edges = set()

        self.vid = Vertex.__vid
        Vertex.__vid += 1

    # position actions
    def set_pos(self, new_pos):
        self.pos = new_pos

    # edge actions
    def set_edges(self, edges):
        self.edges = set(edges)

    def set_is_fixed(self, is_fixed):
        self.is_fixed = is_fixed

    def remove_edges(self, *half_edges):
        for half_edge in half_edges:
            self.edges.remove(half_edge)

    def replace_edge(self, old_edge, new_edge):
        self._replace(self.edges, old_edge, new_edge)

    def add_edges(self, new_edges):
        self.edges.update(new_edges)

    # properties and aliases
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
        return set([e.face for e in self.edges])

    @property
    def half_edges(self):
        return self.edges

    @property
    def dim(self):
        return len(self.pos)

    # other methods
    def __eq__(self, other: "Vertex"):
        return self.vid == other.vid
        # return np.allclose(self.xy, other.xy)

    def __sub__(self, other):
        if isinstance(other.pos, np.ndarray):
            return self.pos - other.pos
        return [self.x - other.x, self.y - other.y]

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_same_id(self, other):
        return self.vid == other.vid

    # def remove_duplicate(self):
    #     self.edges = set(self.edges)

    @xy.setter
    def xy(self, value):
        if len(value) != 2:
            raise ValueError("The input must have exactly two elements.")
        self.pos[:2] = value

    @staticmethod
    def get_by_vid(nid):
        return next((n for n in Vertex.node_list if n.vid == nid), None)

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
        self.is_visited = False

        # Private
        self.__eid = Edge.__eid
        Edge.__eid += 1

    def set_properties(self, face, twin, prev, next, diag_vertex=None):
        self.face = face
        self.twin = twin
        self.next = next
        self.prev = prev

    def get_dir(self):
        return (self.to.xy - self.ori.xy) / np.linalg.norm(
            self.to.xy - self.ori.xy
        )

    def get_orth(self):
        return np.array([self.get_dir()[1], -self.get_dir()[0]])

    def get_mid(self):
        return self.get_center()

    def get_center(self):
        return (self.ori.xy + self.to.xy) / 2

    def get_length(self):
        return np.linalg.norm(self.to.xy - self.ori.xy)

    @property
    def eid(self):
        return self.__eid

    @property
    def diagonal_vertex(self):
        if self.next.to == self.prev.ori:
            return self.next.to
        print(f"Edge{self.eid} info is not correct (diagonal_vertex)")
        print(f"Edge{self.eid} next: {self.next.eid} prev: {self.prev.eid}")
        return None

    @property
    def is_outer(self):
        return not self.twin

    @property
    def is_inner(self):
        return self.is_blocked and self.twin is not None

    @staticmethod
    def get_by_eid(eid):
        return next((e for e in Edge.edge_list if e.eid == eid), None)

    # geometry utils
    def disconnect(self):
        if self.is_outer:
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

        self.edges = []  # order matters, do not use set

        # private
        self.__fid = Face.__fid
        Face.__fid += 1

    @property
    def adjs(self):
        """Get adjacent faces"""
        return set([e.twin.face for e in self.edges if e.twin])

    @property
    def half_edges(self):
        return self.edges

    def set_edges(self, edges):
        self.edges = list(edges)

    def replace_edge(self, old_edge, new_edge):
        self._replace(self.edges, old_edge, new_edge)

    @property
    def verts(self):
        return [e.ori for e in self.edges]

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
    def half_edges(self):
        return self.edges

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
        return next((f for f in Face.face_list if f.fid == fid), None)

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
Line = Edge
