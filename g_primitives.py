import numpy as np

from u_cdt import CDT


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


class Node(_GeoBase):
    __vid = 0
    node_list = []

    def __init__(self, pos, idx=None):
        super().__init__()
        Node.node_list.append(self)

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

    @property
    def dim(self):
        return len(self.pos)

    # @property
    # def vid(self):
    #     return self.__vid

    def __eq__(self, other: "Node"):
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
        for n in Node.node_list:
            if n.vid == nid:
                return n
        return None


class Edge(_GeoBase):
    __eid = 0
    edge_list = []

    def __init__(self, origin, to):
        super().__init__()
        Edge.edge_list.append(self)

        # half edge with direction origin -> to
        self.origin = origin
        self.to = to
        self.face = None
        self.twin = None
        self.next = None
        self.prev = None

        self.is_blocked = False

        self.eid = Edge.__eid
        Edge.__eid += 1

    def dir(self):
        return (self.to.xy - self.origin.xy) / self.length()

    def orth(self):
        return np.array([dir[1], -dir[0]])

    def mid(self):
        return (self.origin.xy + self.to.xy) / 2

    def length(self):
        return np.linalg.norm(self.to.xy - self.origin.xy)

    def intersect(self, other):
        pass

    @staticmethod
    def get_all_blocked(edges: list):
        """deprecating, use blocked_edges instead"""
        return [e for e in edges if e.is_blocked]

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


class Face(_GeoBase):
    __fid = 0
    face_list = []

    def __init__(self):
        super().__init__()
        Face.face_list.append(self)

        self.nodes = []
        self.half_edges = []
        self.adj_faces = []
        self.center = None

        self.fid = Face.__fid
        Face.__fid += 1

    @property
    def area(self):
        area = 0
        for i in range(3):
            j = (i + 1) % 3
            area += (
                self.nodes[i].x * self.nodes[j].y
                - self.nodes[j].x * self.nodes[i].y
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

    def __gt__(self, other):
        return self.gid > other.gid

    def __lt__(self, other):
        return self.gid < other.gid

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


# alias
Point = Node
Vertex = Node
Line = Edge
