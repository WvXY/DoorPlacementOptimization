import numpy as np

from u_geometry import add_vertex, closet_position_on_edge, del_vertex
from f_primitives import RPoint, REdge, RFace


class Agent:
    def __init__(self, edge):
        self.bind_edge = edge

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

    def _correct_location(self, loc):
        if self.bind_edge is None:
            return None
        return closet_position_on_edge(self.bind_edge, loc)

    def activate(self, center):
        new_center = self._correct_location(center)
        cut_p0 = new_center + self.dir * self.length / 2
        cut_p1 = new_center - self.dir * self.length / 2
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
            for v in self.new_verts:
                v.xy += delta * self.dir
            return True
        else:
            return False

    def set_pos(self, pos):
        new_center = pos # closet_position_on_edge(self.bind_edge, pos)
        if not self.in_limit(new_center):
            return False
        self.new_verts[0].xy = new_center + self.dir * self.length / 2
        self.new_verts[1].xy = new_center - self.dir * self.length / 2

    def in_limit(self, pos):
        # print(f"fraction: {self.fraction(pos)} pos: {pos}")
        return self.move_limit[0] <= self.fraction(pos) <= self.move_limit[1]

    # TODO: use fraction to determine in or out of limit
    def fraction(self, pos):
        frac = np.linalg.norm(self.ori - pos) / self.edge_len
        if (self.ori - pos) @ self.dir > 0:
            return -frac
        else:
            return frac

    def step(self):
        pass

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

        # for f in f_del:
        #     print(f.fid)

        # for v in v_del:
        #     self.new_verts.remove(v)
        # for e in e_del:
        #     self.new_edges.remove(e)
        # for f in f_del:
        #     self.new_faces.remove(f)

        return v_del, e_del, f_del


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    from f_primitives import RPoint, REdge, RFace
    from u_data_loader import Loader
    from f_layout import FloorPlan
    from u_geometry import add_vertex


    # settings
    case_id = "0a"

    np.random.seed(0)
    ld = Loader(".")
    ld.load_w_walls_case(case_id)
    ld.optimize()

    nm = FloorPlan()
    nm.set_default_types(RPoint, REdge, RFace)
    nm.create_mesh(ld.vertices, ld.edges, 0)
    # nm.reconnect_closed_edges()
    # nm.create_rooms()

    inner_walls = nm.inner_fixed_edges

    e0 = nm.get_by_eid(0)
    agent = Agent(e0, np.array([0.5, 0.8]))
    agent.activate()
    nm.append(agent.new_verts, agent.new_edges, agent.new_faces)

    for i in range(10):
        agent.move_by(0.02)
        agent.set_pos(np.array([0.5, 0.8]))
        print(f"agent.center: {agent.center} "
              f"| agent.ys {agent.new_verts[0].y:.4f} {agent.new_verts[1].y:.4f}")