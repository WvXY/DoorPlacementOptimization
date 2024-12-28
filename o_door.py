import numpy as np

from u_geometry import add_vertex, closet_position_on_edge, del_vertex
from f_primitives import FPoint, FEdge, FFace


class FDoor:
    def __init__(self, edge, fp=None):
        self.bind_edge = edge

        self.dir = edge.get_dir()
        self.len = 0.1
        self.edge_len = edge.get_length()
        self.ratio = 0
        # self.rooms = []

        self.move_limit = [
            self.len / 2.0 / self.edge_len, # lower limit
            1 - self.len / 2.0 / self.edge_len, # upper limit
        ]

        self.new_verts = []
        self.new_edges = []
        self.new_faces = []

        self.fp = fp
        self.is_active = False

        self.__history = {
            "bind_edge": None,
            "ratio": 0.0,
            "center": None,
        }

    def _correct_location(self, loc):
        if self.bind_edge is None:
            return None
        return closet_position_on_edge(self.bind_edge, loc)

    def activate(self, center=None):
        if center is None:
            if self.__history["ratio"] > 0.5:
                new_center = (self.bind_edge.to.xy
                              - self.move_limit[0] * self.dir * self.edge_len)
            else:
                new_center = (self.bind_edge.ori.xy
                              + self.move_limit[0] * self.dir * self.edge_len)
        else:
            new_center = self._correct_location(center)
        self.ratio = self._cal_ratio(new_center)
        cut_p0 = new_center + self.dir * self.len / 2
        cut_p1 = new_center - self.dir * self.len / 2
        self.new_verts, self.new_edges, self.new_faces = add_vertex(
            self.bind_edge, cut_p0, Point=FPoint, Edge=FEdge, Face=FFace
        )

        v, e, f = add_vertex(
            self.bind_edge, cut_p1, Point=FPoint, Edge=FEdge, Face=FFace
        )
        self.new_verts.extend(v)
        self.new_edges.extend(e)
        self.new_faces.extend(f)

        e[0].is_blocked = False
        e[1].is_blocked = False  # twin of e[0]

        self.is_active = True

    def move_by(self, delta):
        if self._in_limit(self.ratio + delta):
            self.save_history()

            self.ratio += delta / self.edge_len
            for v in self.new_verts:
                v.xy += delta * self.dir
            return True
        else:
            return False

    def set_pos(self, pos):
        new_center = pos # closet_position_on_edge(self.bind_edge, pos)
        p = self._cal_ratio(new_center)
        if not self._in_limit(p):
            return False

        self.save_history()
        self.new_verts[0].xy = new_center + self.dir * self.len / 2
        self.new_verts[1].xy = new_center - self.dir * self.len / 2
        self.ratio = p

    def _in_limit(self, ratio):
        # print(f"fraction: {self.fraction(pos)} pos: {pos}")
        return self.move_limit[0] <= ratio <= self.move_limit[1]

    def _cal_ratio(self, pos):
        frac = np.linalg.norm(self.bind_edge.ori.xy - pos) / self.edge_len
        if (self.bind_edge.ori.xy - pos) @ self.dir > 0:
            return -frac
        else:
            return frac

    def step(self):
        # delta = np.random.normal(0, 0.05)
        delta = -0.05
        ratio = self.ratio + delta
        self.save_history()
        if not self._in_limit(ratio):
            self.deactivate()
            self.next_edge(ratio)
            self._update_properties()
            self.activate()
            self.update_fp()
            print(f"bind_edge: {self.bind_edge.eid} | ratio: {self.ratio} | ori: {self.bind_edge.ori.vid}")
        else:
            self.ratio = ratio
            for v in self.new_verts:
                v.xy += delta * self.dir

    def next_edge(self, ratio):
        def search_next_edge(vertex):
            for e in vertex.half_edges:
                if (e.is_inner and
                        not (self.bind_edge is e or
                             e is self.bind_edge.twin)):
                    return e
            return None

        if ratio >= self.move_limit[1]:
            v = self.bind_edge.to
            e = search_next_edge(v)
            self.bind_edge = e if e.ori is v else e.twin
        elif ratio <= self.move_limit[0]:
            v = self.bind_edge.ori
            e = search_next_edge(v)
            self.bind_edge = e if e.to is v else e.twin

    def _update_properties(self):
        self.dir = self.bind_edge.get_dir()
        self.edge_len = self.bind_edge.get_length()
        self.move_limit = [
            self.len / 2.0 / self.edge_len, # lower limit
            1 - self.len / 2.0 / self.edge_len, # upper limit
        ]
        self.ratio = self._cal_ratio(self.center)

    @property
    def center(self):
        return (self.new_verts[0].xy + self.new_verts[1].xy) / 2

    def deactivate(self):
        # 1 -> 0 is working, but 0 -> 1 is not working
        v_del, e_del, f_del = del_vertex(self.new_verts[1])
        # print("===================")
        v, e, f = del_vertex(self.new_verts[0])
        v_del.extend(v)
        e_del.extend(e)
        f_del.extend(f)

        return v_del, e_del, f_del

    def set_fp(self, fp):
        self.fp = fp

    def update_fp(self):
        self.fp.append(self.new_verts, self.new_edges, self.new_faces)

    # history
    def save_history(self):
        self.__history["bind_edge"] = self.bind_edge
        self.__history["ratio"] = self.ratio
        self.__history["center"] = self.center

    def load_history(self):
        self.bind_edge = self.__history["bind_edge"]
        self.ratio = self.__history["ratio"]
        self.activate(self.__history["center"])


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    from f_primitives import FPoint, FEdge, FFace
    from u_data_loader import Loader
    from f_layout import FLayout
    from u_geometry import add_vertex


    # settings
    case_id = "0a"

    np.random.seed(0)
    ld = Loader(".")
    ld.load_w_walls_case(case_id)
    ld.optimize()

    nm = FLayout()
    nm.set_default_types(FPoint, FEdge, FFace)
    nm.create_mesh(ld.vertices, ld.edges, 0)
    # nm.reconnect_closed_edges()
    # nm.create_rooms()

    inner_walls = nm.inner_fixed_edges

    e0 = nm.get_by_eid(0)
    agent = FDoor(e0, np.array([0.5, 0.8]))
    agent.activate()
    nm.append(agent.new_verts, agent.new_edges, agent.new_faces)

    for i in range(10):
        agent.move_by(0.02)
        agent.set_pos(np.array([0.5, 0.8]))
        print(f"agent.center: {agent.center} "
              f"| agent.ys {agent.new_verts[0].y:.4f} {agent.new_verts[1].y:.4f}")