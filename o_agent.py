import numpy as np

from u_geometry import add_vertex, closet_position_on_edge, del_vertex
from f_primitives import RPoint, REdge, RFace


class Agent:
    def __init__(self, edge, location):
        self.bind_edge = edge
        self.center = location
        self.dir = edge.get_dir()
        self.length = 0.1
        self.ori = edge.ori.xy.copy()
        self.edge_len = edge.get_length()
        # self.rooms = []

        self.move_limit = [
            self.length / 2 / self.edge_len,
            1 - self.length / 2 / self.edge_len,
        ]  # lower and upper limit

        self.new_verts = []
        self.new_edges = []
        self.new_faces = []

        self.is_active = False

    def _correct_location(self):
        if self.bind_edge is None:
            return
        self.center = closet_position_on_edge(self.bind_edge, self.center)

    def activate(self):
        self._correct_location()
        cut_p0 = self.center + self.dir * self.length / 2
        cut_p1 = self.center - self.dir * self.length / 2
        self.new_verts, self.new_edges, self.new_faces = add_vertex(
            self.bind_edge, cut_p0, Point=RPoint, Edge=REdge, Face=RFace
        )

        v, e, f = add_vertex(
            self.bind_edge, cut_p1, Point=RPoint, Edge=REdge, Face=RFace
        )
        self.new_verts.extend(v)
        self.new_edges.extend(e)
        self.new_faces.extend(f)

        e[0].is_blocked = False
        e[1].is_blocked = False  # twin of e[0]

        self.is_active = True

    def move_by(self, delta):
        new_center = self.center + delta * self.dir
        if self.in_limit(new_center):
            self.center = new_center
            for v in self.new_verts:
                v.xy += delta * self.dir

    def set_pos(self, pos):
        self.center = pos
        self.new_verts[0].xy = pos + self.dir * self.length / 2
        self.new_verts[1].xy = pos - self.dir * self.length / 2

    def in_limit(self, pos):
        return self.move_limit[0] <= self.fraction(pos) <= self.move_limit[1]

    def fraction(self, pos):
        return np.linalg.norm(self.ori - pos) / self.edge_len

    def step(self):
        pass

    def deactivate(self):
        # 1 -> 0 is working, but 0 -> 1 is not working
        v_del, e_del, f_del = del_vertex(self.new_verts[1])
        # print("===================")
        v, e, f = del_vertex(self.new_verts[0])
        v_del.extend(v)
        e_del.extend(e)
        f_del.extend(f)

        # for f in f_del:
        #     print(f.fid)

        # for v in v_del:
        #     self.new_verts.remove(v)
        # for e in e_del:
        #     self.new_edges.remove(e)
        # for f in f_del:
        #     self.new_faces.remove(f)

        return v_del, e_del, f_del
