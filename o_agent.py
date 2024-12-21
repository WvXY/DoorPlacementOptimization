from u_geometry import split_edge, closet_position_on_edge
from f_primitives import RPoint, REdge, RFace


class Agent:
    def __init__(self, edge, location):
        self.bind_edge = edge
        self.center = location
        self.length = 0.1
        # self.rooms = []

        self.new_verts = []
        self.new_edges = []
        self.new_faces = []

    def correct_location(self):
        if self.bind_edge is None:
            return
        self.center = closet_position_on_edge(self.bind_edge, self.center)

    def activate(self):
        self.correct_location()
        cut_p0 = self.center + self.bind_edge.get_dir() * self.length / 2
        cut_p1 = self.center - self.bind_edge.get_dir() * self.length / 2
        self.new_verts, self.new_edges, self.new_faces = split_edge(
            self.bind_edge, cut_p0, Point=RPoint, Edge=REdge, Face=RFace
        )

        v, e, f = split_edge(
            self.bind_edge, cut_p1, Point=RPoint, Edge=REdge, Face=RFace
        )
        self.new_verts.extend(v)
        self.new_edges.extend(e)
        self.new_faces.extend(f)

        e[0].is_blocked = False
        e[1].is_blocked = False  # twin of e[0]

    def step(self):
        pass

    def deactivate(self):
        pass
